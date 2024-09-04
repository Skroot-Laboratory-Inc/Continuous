from src.app.model.result_set.result_set_data_point import ResultSetDataPoint


class ResultSet:
    def __init__(self):
        self.time = []
        self.maxFrequency = []
        self.maxVoltsSmooth = []
        self.maxFrequencySmooth = []
        self.filenames = []
        self.timestamps = []

        self.denoiseTimeSmooth = []
        self.denoiseTime = []
        self.denoiseFrequencySmooth = []
        self.denoiseFrequency = []

    def getTime(self):
        return self.time

    def getMaxFrequency(self):
        return self.maxFrequency

    def getMaxVoltsSmooth(self):
        return self.maxVoltsSmooth

    def getMaxFrequencySmooth(self):
        return self.maxFrequencySmooth

    def getFilenames(self):
        return self.filenames

    def getTimestamps(self):
        return self.timestamps

    def getDenoiseTime(self):
        return self.denoiseTime

    def getDenoiseTimeSmooth(self):
        return self.denoiseTimeSmooth

    def getDenoiseFrequency(self):
        return self.denoiseFrequency

    def getDenoiseFrequencySmooth(self):
        return self.denoiseFrequencySmooth

    def resetRun(self):
        self.time = self.time[-1:]
        self.maxVoltsSmooth = self.maxVoltsSmooth[-1:]
        self.maxFrequency = self.maxFrequency[-1:]
        self.maxFrequencySmooth = self.maxFrequencySmooth[-1:]
        self.filenames = self.filenames[-1:]
        self.timestamps = self.timestamps[-1:]

        self.denoiseFrequency = self.denoiseFrequency[-1:]
        self.denoiseFrequencySmooth = self.denoiseFrequencySmooth[-1:]
        self.denoiseTime = self.denoiseTime[-1:]
        self.denoiseTimeSmooth = self.denoiseTimeSmooth[-1:]

    def setValues(self, values: ResultSetDataPoint):
        self.time.append(values.time)
        self.maxFrequency.append(values.maxFrequency)
        self.maxVoltsSmooth.append(values.maxVoltsSmooth)
        self.maxFrequencySmooth.append(values.maxFrequencySmooth)
        self.filenames.append(values.filename)
        self.timestamps.append(values.timestamp)

        # Denoise values change with time, so the entire array gets set at once.
        self.denoiseTime = values.denoiseTime
        self.denoiseTimeSmooth = values.denoiseTimeSmooth
        self.denoiseFrequency =values.denoiseFrequency
        self.denoiseFrequencySmooth =values.denoiseFrequencySmooth