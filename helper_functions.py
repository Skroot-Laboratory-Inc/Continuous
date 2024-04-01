def frequencyToIndex(zeroPoint, frequencyVector):
    return [100*(1 - val/zeroPoint) for val in frequencyVector]

def zeroAtEquilibration(zeroX, x, y):
    newX = [xval for xval in x if xval >= zeroX/120]
    newY = y[-len(newX):]
    return newX, newY