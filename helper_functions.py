def frequencyToIndex(zeroPoint, frequencyVector):
    return [100*(1 - val/zeroPoint) for val in frequencyVector]