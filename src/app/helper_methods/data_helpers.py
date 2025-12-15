import csv
from typing import Optional, Tuple, List

import numpy as np
from scipy.optimize import curve_fit

from src.app.properties.dev_properties import DevProperties


def frequencyToIndex(zeroPoint, frequencyVector) -> list:
    """ This converts a frequency vector into SGI """
    if DevProperties().isDevMode and DevProperties().mode == "GUI":
        return frequencyVector
        # return [100 * (1 - val/frequencyVector[0]) for val in frequencyVector]
    return [100 * (1 - val / zeroPoint) for val in frequencyVector]


def truncateByX(minX, maxX, x, y) -> Tuple[list, list]:
    """ This truncates all values from two vectors based on a min and max value for x. """
    truncatedX, truncatedY = [], []
    for index, xval in enumerate(x):
        if minX < xval < maxX:
            truncatedX.append(xval)
            truncatedY.append(y[index])
    return truncatedX, truncatedY


def convertListToPercent(lst) -> List[float]:
    """ This function converts a vector of values to percentages, i.e. 1.08 converts to 8% """
    return [convertToPercent(item) for item in lst]


def convertListFromPercent(lst) -> List[float]:
    """ This function converts a vector of percentages to values, i.e. 8% into 1.08 """
    return [convertFromPercent(item) for item in lst]


def convertToPercent(item) -> float:
    """ This converts a single value into a percent i.e. 1.08 into 8%"""
    return (item - 1) * 100


def convertFromPercent(item) -> float:
    """ This converts a single value from a percent i.e. 8% into 1.08"""
    return (item / 100) + 1


def createCsv(data, csvFilename) -> None:
    with open(csvFilename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def gaussian(x, amplitude, centroid, std) -> np.ndarray:
    """ Standard gaussian fit. """
    return amplitude * np.exp(-(x - centroid) ** 2 / (2 * std ** 2))


def findMaxGaussian(x, y, pointsOnEachSide: Optional[int] = 50) -> Tuple[float, float, float]:
    """
    Find the peak using Gaussian curve fitting.

    Args:
        x: Frequency array (list or numpy array)
        y: Magnitude array (list or numpy array)
        pointsOnEachSide: Number of points on each side of the peak to use for fitting.
                         If None, uses all available points. Defaults to 50.

    Returns:
        Tuple of (amplitude, centroid_frequency, peak_width)
    """
    x = np.asarray(x)
    y = np.asarray(y)

    max_idx = np.argmax(y)

    if pointsOnEachSide is None:
        # Use all points
        xAroundPeak = x
        yAroundPeak = y
    elif pointsOnEachSide < max_idx < len(y) - pointsOnEachSide:
        xAroundPeak = x[max_idx - pointsOnEachSide:max_idx + pointsOnEachSide]
        yAroundPeak = y[max_idx - pointsOnEachSide:max_idx + pointsOnEachSide]
    elif max_idx > pointsOnEachSide and max_idx > len(y) - pointsOnEachSide:
        xAroundPeak = x[max_idx - pointsOnEachSide:max_idx]
        yAroundPeak = y[max_idx - pointsOnEachSide:max_idx]
    else:
        xAroundPeak = x[max_idx:max_idx + pointsOnEachSide]
        yAroundPeak = y[max_idx:max_idx + pointsOnEachSide]

    popt, _ = curve_fit(
        gaussian,
        xAroundPeak,
        yAroundPeak,
        p0=(max(y), x[max_idx], 1),
        bounds=([min(y), min(xAroundPeak), 0], [max(y), max(xAroundPeak), np.inf]),
    )

    amplitude = popt[0]
    centroid = popt[1]
    peakWidth = popt[2]

    return amplitude, centroid, peakWidth
