import subprocess


def frequencyToIndex(zeroPoint, frequencyVector):
    return [100*(1 - val/zeroPoint) for val in frequencyVector]


def openFileExplorer(path):
    # TODO Once all customers are on >= v2.3.0 remove this, it is bad practice
    try:
        import startfile
    except:
        subprocess.run(['pip3', 'install', 'universal-startfile'])
        import startfile
    startfile.startfile(path)


def truncateByX(minX, maxX, x, y):
    truncatedX, truncatedY = [], []
    for index, xval in enumerate(x):
        if minX < xval < maxX:
            truncatedX.append(xval)
            truncatedY.append(y[index])
    return truncatedX, truncatedY

