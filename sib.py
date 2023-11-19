import csv
import time  # for sleep()
from bisect import bisect_left

import numpy as np
import pandas
import sibcontrol
from typing import List

import logger
import text_notification
from reader_interface import ReaderInterface


class Sib(ReaderInterface):
    def __init__(self, calibrationFilename, port, AppModule, readerNumber, calibrationRequired=False):
        self.startFreqMHz = 0.1
        self.stopFreqMHz = 350
        self.nPoints = 3000
        self.readerNumber = readerNumber
        self.AppModule = AppModule
        self.sib = sibcontrol.SIB350(port)
        self.setStartFrequency(self.startFreqMHz)
        self.setStopFrequency(self.stopFreqMHz)
        self.setNumberOfPoints(self.nPoints)
        self.sib.amplitude_mA = 31.6  # The synthesizer output amplitude is set to 31.6 mA by default
        self.sib.open()
        if calibrationRequired:
            self.takeCalibrationScan(calibrationFilename)
        self.calibrationFrequency, self.calibrationMagnitude, self.calibrationPhase = loadCalibrationFile(
            calibrationFilename)

    def takeScan(self, outputFilename) -> (List[float], List[float], List[float], bool):
        try:
            while self.AppModule.currentlyScanning:
                time.sleep(0.1)
            self.AppModule.currentlyScanning = True
            magnitude = self.performSweepAndWaitForComplete()
            frequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.nPoints)
            calibratedMagnitude, calibratedPhase = self.calibrationComparison(frequency, magnitude, [])
            createScanFile(outputFilename, frequency, calibratedMagnitude, calibratedPhase)
            return frequency, magnitude, [], True
        except sibcontrol.SIBException:
            text_notification.setText("Failed to perform sweep for reader, check reader connection.")
            logger.exception("Failed to perform sweep for reader, check reader connection.")
            return [], [], [], False
        finally:
            self.AppModule.currentlyScanning = False

    def takeCalibrationScan(self, calibrationFilename) -> bool:
        try:
            self.sib.start_MHz = 0.1
            self.sib.stop_MHz = 350
            self.sib.num_pts = 10000
            while self.AppModule.currentlyScanning:
                time.sleep(0.1)
            self.AppModule.currentlyScanning = True
            magnitude = self.performSweepAndWaitForComplete()
            self.setNumberOfPoints(self.nPoints)
            self.setStartFrequency(self.startFreqMHz)
            self.setStopFrequency(self.stopFreqMHz)
            frequency = calculateFrequencyValues(0.1, 350, 10000)
            createScanFile(calibrationFilename, frequency, magnitude, [])
            return True
        except:
            text_notification.setText("Failed to perform calibration.")
            logger.exception("Failed to perform calibration.")
            return False
        finally:
            self.AppModule.currentlyScanning = False

    def setStartFrequency(self, startFreqMHz) -> bool:
        if 0 <= startFreqMHz <= 350 and startFreqMHz < self.stopFreqMHz:
            self.startFreqMHz = startFreqMHz
            self.sib.start_MHz = startFreqMHz
            return True
        else:
            text_notification.setText(f"Invalid value, start frequency must be between 0 and 350."
                                      f"\n start frequency not changed.")
            return False

    def setStopFrequency(self, stopFreqMHz) -> bool:
        if 0 <= stopFreqMHz <= 350 and stopFreqMHz > self.startFreqMHz:
            self.stopFreqMHz = stopFreqMHz
            self.sib.stop_MHz = stopFreqMHz
            return True
        else:
            text_notification.setText(f"Invalid value, stop frequency must be between 0 and 350."
                                      f"\n stop frequency not changed.")
            return False

    def setNumberOfPoints(self, nPoints) -> bool:
        try:
            self.nPoints = nPoints
            self.sib.num_pts = nPoints
            return True
        except:
            return False

    def close(self) -> bool:
        try:
            self.sib.close()
            return True
        except:
            return False

    """ End of required implementations, SIB specific below"""

    def performHandshake(self) -> bool:
        data = 500332  # Some random 32-bit value
        try:
            return_val = self.sib.handshake(data)
            if return_val == data:
                self.getFirmwareVersion()
                return True
            else:
                return False
        except sibcontrol.SIBException as e:
            logger.exception("Failed to perform handshake")
            return False

    def getFirmwareVersion(self) -> str:
        try:
            firmware_version = self.sib.version()
            logger.info(f'The SIB Firmware is version: {firmware_version}')
            return firmware_version
        except sibcontrol.SIBException as e:
            logger.exception("Failed to set firmware version")
            return ''

    def sleep(self) -> None:
        self.sib.sleep()

    def wake(self) -> None:
        self.sib.wake()

    def checkAndSendConfiguration(self) -> bool:
        if self.sib.valid_config():
            try:
                self.sib.write_start_ftw()  # Send the start frequency ot the SIB
                self.sib.write_stop_ftw()  # Send the stop frequency to the SIB
                self.sib.write_num_pts()  # Send the number of points to the SIB
                self.sib.write_asf()  # Send the signal amplitude to the SIB
                return True
            except sibcontrol.SIBException:
                text_notification.setText("Failed to set reader configuration, check reader connection.")
                logger.exception("Failed to set reader configuration, check reader connection.")
                return False
        else:
            text_notification.setText("Reader configuration is not valid. Change the reader frequency or number of "
                                      "points.")
            return False

    def performSweepAndWaitForComplete(self) -> List[str]:
        self.checkAndSendConfiguration()
        self.wake()
        self.sib.write_sweep_command()
        conversion_results, sweep_complete = list(), False
        while not sweep_complete:
            try:
                if self.sib.data_waiting() > 0:
                    ack_msg, tmp_data = self.sib.read_sweep_response()

                    if ack_msg == 'ok':
                        # SIB has sent the sweep complete command.
                        sweep_complete = True
                    elif ack_msg == 'send_data':
                        # SIB is sending measurement data. Add it to the conversion results array
                        conversion_results.extend(tmp_data)
                    else:
                        logger.info(f"SIB Received an unexpected command. Something is wrong. ack_msg: {ack_msg}")
                else:
                    # This is where you put code to check if the user would like to stop the sweep
                    # or anything else.
                    time.sleep(0.01)
            except:
                logger.exception("An error occurred while waiting for scan to complete")
        self.sleep()
        return conversion_results

    def calibrationComparison(self, frequency, magnitude, phase):
        """Phase is filler for if it will be required/output for SIB or not."""
        calibratedMagnitude, calibratedPhase = [], []
        for i in range(len(frequency)):
            calibrationMagnitudeOffset = find_nearest(frequency[i], self.calibrationFrequency,
                                                      self.calibrationMagnitude)
            # calibrationPhaseOffset = find_nearest(frequency[i], self.calibrationFrequency, self.calibrationPhase)
            calibratedMagnitude.append(
                -(convertLinearValueToDb(magnitude[i]) - convertLinearValueToDb(calibrationMagnitudeOffset)))
            # calibratedPhase.append(phase[i] - calibrationPhaseOffset)
        return calibratedMagnitude, calibratedPhase


def loadCalibrationFile(calibrationFilename) -> (List[str], List[str], List[str]):
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationMagnitude = list(readings['Signal Strength (dB)'].values.tolist())
        # calibrationPhase = list(readings['Phase'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationMagnitude, []
    except KeyError or ValueError:
        text_notification.setText("IMPORTANT!!! Software updated; calibration required.",
                                  ('Courier', 9, 'bold'), "black", "red")
        logger.exception("Column did not exist")
    except Exception:
        logger.exception("Failed to load in calibration")


def createScanFile(outputFileName, frequency, magnitude, phase):
    # Phase is not currently implemented in the SIB
    # with open(outputFileName, 'w', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['Frequency (MHz)', 'Signal Strength (dB)', 'Phase'])
    #     writer.writerows(zip(frequency, magnitude, phase))
    # return
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', 'Signal Strength (dB)'])
        writer.writerows(zip(frequency, magnitude))
    return


def convertLinearValueToDb(value):
    """Filler for any changes required to adjust the value returned by the SIB"""
    return value


def calculateFrequencyValues(startFreqMHz, stopFreqMHz, nPoints) -> List[str]:
    df = (stopFreqMHz - startFreqMHz) * 1.0 / nPoints
    frequency = startFreqMHz + df * np.arange(0, nPoints)
    return frequency


def find_nearest(freq, freqList, dBlist):
    pos = bisect_left(freqList, freq)
    if pos == 0:
        return dBlist[0]
    if pos == len(freqList):
        return dBlist[-1]
    before = freqList[pos - 1]
    after = freqList[pos]
    if after - freq < freq - before:
        return dBlist[pos]
    else:
        return dBlist[pos - 1]

# ports = list_ports.comports()
# portNums = [int(ports[i][0][3:]) for i in range(len(ports))]
# if portNums:
#     port = f'COM{max(portNums)}'
# Sib = Sib(port)
# succeeded = Sib.performHandshake()
# resultDb = Sib.performSweep()
# firmwareVersion = Sib.getFirmwareVersion()
# Sib.sib.close()
