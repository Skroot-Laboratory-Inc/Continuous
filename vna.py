import os
import time
from bisect import bisect_left

import numpy as np
import pandas
import serial

import logger


class VnaScanning:
    def takeScan(self):
        return self.readVna(self.startFreq, self.stopFreq, self.nPoints, f'{self.savePath}/{self.scanNumber}.csv',
                            self.port, self.calFileLocation)

    def readVna(self, start_freq, stop_freq, num_points, output_file_name, port, calibration_file_name=None):
        try:
            freqs, trans_loss = '', ''
            while self.AppModule.currentlyScanning == True:
                time.sleep(0.1)
            self.AppModule.currentlyScanning = True
            khz2dds = 10737.4182
            df = (stop_freq - start_freq) * 1.0 / num_points
            if self.socket == None:
                self.socket = serial.Serial(port, 115200, timeout=1.5)
            sleep_time = 0.1
            # self.socket.write(b"%d\r" % (power_level)) # Maybe place this here?
            # time.sleep(sleep_time)
            self.socket.write(b"2\r")
            time.sleep(sleep_time)
            self.socket.write(b"%d\r" % (start_freq * 1e3 * khz2dds))
            time.sleep(sleep_time)
            self.socket.write(b"%d\r" % num_points)
            time.sleep(sleep_time)
            self.socket.write(b"%d\r" % (df * 1e3 * khz2dds))
            time.sleep(sleep_time)
            ans = b''.join(self.socket.readlines())
            a = np.frombuffer(ans, dtype=np.uint16)
            mag = a[1::2]
            phase = a[::2] * np.pi / 1024
            freqs = start_freq + df * np.arange(0, num_points)
            trans_loss = list(mag)
            phase_list = list(phase)
            calibration_TL = []
            if 'Calibration.csv' not in output_file_name:
                readings = pandas.read_csv(calibration_file_name)
                calibration_TL = list(readings['Transmission Loss(dB)'].values.tolist())
                calibration_Freq = readings['Frequency(Hz)'].values.tolist()

            def find_nearest_internal(freqList, freq, dBlist):
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

            with open(output_file_name, "w+") as file:
                file.write(f"Frequency(Hz),Transmission Loss(dB),Phase\n")
                for ind in range(len(freqs)):
                    if not calibration_TL:
                        pass
                    else:
                        calibration_offset = find_nearest_internal(calibration_Freq, freqs[ind] * 1000000,
                                                                   calibration_TL)
                        # this might be the technical value - Note: np.log(0) will throw an error and must be acknowledged
                        # trans_loss[ind] = np.log(np.abs(trans_loss[ind] - calibration_offset)) * 20
                        trans_loss[ind] = -(trans_loss[ind] - calibration_offset) / 12.5
                    file.write(f"{freqs[ind] * 1000000},{trans_loss[ind]},{phase_list[ind]}\n")
            if len(freqs) == len(trans_loss):
                self.scanFrequency = freqs
                self.scanMagnitude = trans_loss
            self.AppModule.currentlyScanning = False
            return True
        except:
            self.socket = None
            if freqs != '':
                logger.info(f'pointsNeeded: {len(freqs)}, pointsReceived: {len(trans_loss)}')
            logger.exception("Failed to take scan")
            self.AppModule.currentlyScanning = False
            raise

    def deleteScanFile(self):
        os.remove(f'{self.savePath}/{self.scanNumber}.csv')

    def incrementScan(self):
        self.scanNumber += self.scanRate
