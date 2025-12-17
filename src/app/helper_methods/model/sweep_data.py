import numpy as np


class SweepData:
    def __init__(self, frequency, magnitude):
        self.frequency = frequency
        self.magnitude = magnitude

    def getFrequency(self) -> np.array:
        return self.frequency

    def getMagnitude(self) -> np.array:
        return self.magnitude

