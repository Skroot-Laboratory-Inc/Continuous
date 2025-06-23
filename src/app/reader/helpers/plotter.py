import tkinter

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.data_helpers import frequencyToIndex, convertListToPercent, convertToPercent
from src.app.model.result_set.result_set import ResultSet
from src.app.model.sweep_data import SweepData
from src.app.ui_manager.theme.colors import Colors
from src.app.widget.figure import FigureCanvas


class Plotter:
    def __init__(self, readerNumber, FileManager: ReaderFileManager, frequencyFrame: tkinter.Frame):
        self.FileManager = FileManager
        self.readerNumber = readerNumber
        self.frequencyFrame = frequencyFrame
        self.ReaderFigureCanvas = FigureCanvas(
            f'Signal Check Reader {self.readerNumber}',
            'Frequency (MHz)',
            None,
            f'Signal Check Reader {self.readerNumber}'
        )

    def plotFrequencies(self, resultSet: ResultSet, zeroPoint, sweepData: SweepData):
        if len(resultSet.getTime()) > 0:
            if self.ReaderFigureCanvas.showSgi.value:
                self.plotGrowthIndex(resultSet, zeroPoint)
            else:
                self.plotSignal(resultSet, sweepData)
            self.frequencyFrame.update()
            self.frequencyFrame.update_idletasks()

    def plotGrowthIndex(self, resultSet: ResultSet, zeroPoint):
        self.ReaderFigureCanvas.setYAxisLabel('Skroot Growth Index (SGI)')
        self.ReaderFigureCanvas.setXAxisLabel('Time (hours)')
        self.ReaderFigureCanvas.setTitle(f'SGI Reader {self.readerNumber}')
        self.ReaderFigureCanvas.redrawPlot()
        yPlot = frequencyToIndex(zeroPoint, resultSet.getDenoiseFrequencySmooth())
        self.ReaderFigureCanvas.scatter(resultSet.getDenoiseTimeSmooth(), yPlot, 20, Colors().lightPrimaryColor)
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
