import csv

import numpy as np

from src.app.properties.dev_properties import DevProperties


def frequencyToIndex(zeroPoint, frequencyVector):
    """ This converts a frequency vector into SGI """
    if DevProperties().isDevMode and DevProperties().mode == "GUI":
        return frequencyVector
        # return [100 * (1 - val/frequencyVector[0]) for val in frequencyVector]
    return [100 * (1 - val / zeroPoint) for val in frequencyVector]


def truncateByX(minX, maxX, x, y):
    """ This truncates all values from two vectors based on a min and max value for x. """
    truncatedX, truncatedY = [], []
    for index, xval in enumerate(x):
        if minX < xval < maxX:
            truncatedX.append(xval)
            truncatedY.append(y[index])
    return truncatedX, truncatedY


def convertListToPercent(lst):
    """ This function converts a vector of values to percentages, i.e. 1.08 converts to 8% """
    return [convertToPercent(item) for item in lst]


def convertListFromPercent(lst):
    """ This function converts a vector of percentages to values, i.e. 8% into 1.08 """
    return [convertFromPercent(item) for item in lst]


def convertToPercent(item):
    """ This converts a single value into a percent i.e. 1.08 into 8%"""
    return (item - 1) * 100


def convertFromPercent(item):
    """ This converts a single value from a percent i.e. 8% into 1.08"""
    return (item / 100) + 1


def createCsv(data, csvFilename):
    with open(csvFilename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def gaussian(x, amplitude, centroid, std):
    """ Standard gaussian fit. """
    return amplitude * np.exp(-(x - centroid) ** 2 / (2 * std ** 2))
