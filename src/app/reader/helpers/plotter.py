from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import frequencyToIndex, convertListToPercent, convertToPercent
from src.app.model.result_set import ResultSet
from src.app.model.sweep_data import SweepData
from src.app.reader.helpers.second_axis import SecondAxis
from src.app.theme.colors import Colors
from src.app.widget.figure import FigureCanvas


class Plotter:
    def __init__(self, readerColor, readerNumber, denoiseSet, FileManager: ReaderFileManager, experimentNotes, secondAxisTitle=""):
        self.SecondAxis = SecondAxis(readerNumber, secondAxisTitle, FileManager)
        self.ExperimentNotes = experimentNotes
        colors = Colors()
        self.FileManager = FileManager
        self.readerNumber = readerNumber
        self.denoiseSet = denoiseSet
        self.secondaryColor = colors.secondaryColor
        self.frequencyPlot = None
        self.frequencyCanvas = None
        self.frequencyFrame = None
        self.readerColor = readerColor
        self.ReaderFigureCanvas = FigureCanvas(
            readerColor,
            f'Signal Check Reader {self.readerNumber}',
            'Frequency (MHz)',
            None,
            f'Signal Check Reader {self.readerNumber}',
            self.SecondAxis.getTitle()
        )

    def plotFrequencies(self, resultSet: ResultSet, zeroPoint, sweepData: SweepData, freqToggleSet):
        if len(resultSet.getTime()) > 0:
            if freqToggleSet == "SGI":
                self.plotGrowthIndex(resultSet, zeroPoint)
            elif freqToggleSet == "Signal Check":
                self.plotSignal(resultSet, sweepData)

    def plotGrowthIndex(self, resultSet: ResultSet, zeroPoint):
        self.ReaderFigureCanvas.setYAxisLabel('Skroot Growth Index (SGI)')
        self.ReaderFigureCanvas.setXAxisLabel('Time (hours)')
        self.ReaderFigureCanvas.setTitle(f'SGI Reader {self.readerNumber}')
        self.ReaderFigureCanvas.redrawPlot()
        if self.denoiseSet:
            yPlot = frequencyToIndex(zeroPoint, resultSet.getDenoiseFrequencySmooth())
            self.ReaderFigureCanvas.scatter(resultSet.getDenoiseTimeSmooth(), yPlot, 20, self.readerColor)
        else:
            yPlot = frequencyToIndex(zeroPoint, resultSet.getMaxFrequencySmooth())
            self.ReaderFigureCanvas.scatter(resultSet.getTime(), yPlot, 20, self.readerColor)
        for xvalue in self.ExperimentNotes.getTimestamps(self.readerNumber):
            self.ReaderFigureCanvas.addVerticalLine(xvalue)
        self.ReaderFigureCanvas.addSecondAxis(self.SecondAxis.getTime(), self.SecondAxis.getValues())
        self.ReaderFigureCanvas.drawCanvas(self.frequencyFrame)
        self.ReaderFigureCanvas.saveAs(self.FileManager.getReaderPlotJpg())

    def plotSignal(self, resultSet: ResultSet, sweepData: SweepData):
        self.ReaderFigureCanvas.setYAxisLabel('Signal Check')
        self.ReaderFigureCanvas.setXAxisLabel('Frequency (MHz)')
        self.ReaderFigureCanvas.setTitle(f'Signal Check Reader {self.readerNumber}')
        self.ReaderFigureCanvas.redrawPlot()
        self.ReaderFigureCanvas.scatter(sweepData.getFrequency(), convertListToPercent(sweepData.getMagnitude()), 20, 'black')
        self.ReaderFigureCanvas.scatter(
            resultSet.getMaxFrequencySmooth()[-1],
            convertToPercent(resultSet.getMaxVoltsSmooth()[-1]),
            30,
            'red'
        )
        self.ReaderFigureCanvas.drawCanvas(self.frequencyFrame)
        self.ReaderFigureCanvas.saveAs(self.FileManager.getReaderPlotJpg())
