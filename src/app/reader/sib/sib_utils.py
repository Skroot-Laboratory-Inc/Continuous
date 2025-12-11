"""Shared utility functions for SIB implementations."""
import csv
import logging
import os
from bisect import bisect_left
from typing import List

import numpy as np
import pandas

from src.app.factory.use_case_factory import ContextFactory
from src.app.helper_methods.data_helpers import truncateByX
from src.app.widget import text_notification


def loadCalibrationFile(calibrationFilename) -> (List[float], List[float]):
    """Load calibration data from CSV file.

    Returns tuple of (calibrationFrequency, calibrationVolts).
    Returns ([], []) if file cannot be loaded.
    """
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationVolts = list(readings['Signal Strength (V)'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationVolts
    except KeyError or ValueError:
        logging.exception("Column did not exist", extra={"id": calibrationFilename})
        return [], []
    except FileNotFoundError:
        logging.exception("No previous calibration found.", extra={"id": calibrationFilename})
        text_notification.setText("No previous calibration found, please calibrate.")
        return [], []
    except Exception:
        logging.exception("Failed to load in calibration", extra={"id": calibrationFilename})
        return [], []


def createCalibrationFile(outputFileName, frequency, volts):
    """Create a calibration CSV file with frequency and voltage data."""
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', 'Signal Strength (V)'])
        writer.writerows(zip(frequency, volts))


def createReferenceFile(outputFileName, referenceStrength, frequencyStrength):
    """Create a reference CSV file for RollerBottle and Tunair implementations."""
    if not os.path.exists(os.path.dirname(outputFileName)):
        os.mkdir(os.path.dirname(outputFileName))
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Reference Strength (V)', 'Frequency Strength (V)'])
        writer.writerows(zip(referenceStrength, frequencyStrength))


def calculateFrequencyValues(startFreqMHz, stopFreqMHz, df) -> List[float]:
    """Calculate frequency values for a sweep."""
    nPoints = getNumPointsFrequency(startFreqMHz, stopFreqMHz)
    return startFreqMHz + df * np.arange(0, nPoints)


def find_nearest(freq, freqList, dBlist):
    """Find the nearest value in dBlist corresponding to freq in freqList using binary search."""
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


def createCalibrationDirectoryIfNotExists(filename):
    """Create calibration directory structure if it doesn't exist."""
    if not os.path.exists(os.path.dirname(os.path.dirname(filename))):
        os.mkdir(os.path.dirname(os.path.dirname(filename)))
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))


def convertAdcToVolts(adcList):
    """Convert ADC values to voltage values."""
    return [float(adcValue) * (3.3 / 2 ** 10) for adcValue in adcList]


def getNumPointsFrequency(startFreq, stopFreq):
    """Calculate number of points including endpoint for frequency array."""
    return int((stopFreq - startFreq) * (1 / ContextFactory().getSibProperties().stepSize) + 1)


def getNumPointsSweep(startFreq, stopFreq):
    """Calculate number of points for sweep (excluding endpoint)."""
    return int((stopFreq - startFreq) * (1 / ContextFactory().getSibProperties().stepSize))


def findSelfResonantFrequency(frequency, volts, scanRange, threshold):
    """Find the self-resonant frequency within a scan range above a threshold."""
    inRangeFrequencies, inRangeVolts = truncateByX(scanRange[0], scanRange[1], frequency, volts)
    for index, yval in enumerate(inRangeVolts):
        if yval > threshold:
            return inRangeFrequencies[index]


def removeInitialSpike(frequency, volts, initialSpikeMhz, stepSize):
    """Remove initial spike points from frequency and voltage arrays."""
    pointsRemoved = int(initialSpikeMhz / stepSize)
    return frequency[pointsRemoved:], volts[pointsRemoved:]


def normalizeToReference(volts, referenceVolts):
    """Normalize voltage to reference voltage."""
    return volts / referenceVolts
