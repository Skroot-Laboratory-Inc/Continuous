import tkinter

import numpy as np

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.data_helpers import frequencyToIndex, convertListToPercent, convertToPercent
from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.model.result_set.result_set import ResultSet
from src.app.model.sweep_data import SweepData
from src.app.reader.analyzer.secondary_axis_tracker import SecondaryAxisTracker
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.figure_styles import FigureStyles
from src.app.widget.figure import FigureCanvas


class Plotter:
    def __init__(self, readerNumber, FileManager: ReaderFileManager, frequencyFrame: tkinter.Frame, secondaryAxisTracker: SecondaryAxisTracker):
        self.FileManager = FileManager
        self.readerNumber = readerNumber
        self.frequencyFrame = frequencyFrame
        self.SecondaryAxisTracker = secondaryAxisTracker
        self.ReaderFigureCanvas = FigureCanvas(
            f'Signal Check',
            'Frequency (MHz)',
            None,
            f'Signal Check'
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
        self.ReaderFigureCanvas.setTitle(f'SGI')
        self.ReaderFigureCanvas.redrawPlot()
        yPlot = frequencyToIndex(zeroPoint, resultSet.getDenoiseFrequencySmooth())
        self.ReaderFigureCanvas.setYAxisLimits(
            bottom=np.nanmin(yPlot)*1.1,
            top=max(FigureStyles().y_soft_max, np.nanmax(yPlot) * 1.1),
        )
        self.ReaderFigureCanvas.setXAxisLimits(
            right=max(FigureStyles().x_soft_max, np.nanmax(resultSet.getDenoiseTimeSmooth()) * 1.1),
        )
        if self.SecondaryAxisTracker.getTimestamps():
            zeroTime = resultSet.getTimestamps()[0]
            self.ReaderFigureCanvas.addSecondAxis(
                self.SecondaryAxisTracker.getTimes(zeroTime),
                self.SecondaryAxisTracker.getValues(),
            )
        self.ReaderFigureCanvas.scatter(resultSet.getDenoiseTimeSmooth(), yPlot, 20, Colors().lightPrimaryColor)
        self.ReaderFigureCanvas.drawCanvas(self.frequencyFrame)
        self.ReaderFigureCanvas.saveAs(self.FileManager.getReaderPlotJpg())

    def plotSignal(self, resultSet: ResultSet, sweepData: SweepData):
        self.ReaderFigureCanvas.setYAxisLabel('Signal Check')
        self.ReaderFigureCanvas.setXAxisLabel('Frequency (MHz)')
        self.ReaderFigureCanvas.setTitle(f'Signal Check')
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
