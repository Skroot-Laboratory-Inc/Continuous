import tkinter as tk

from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.buttons.plus_icon_button import PlusIconButton
from src.app.widget.kpi_form import KpiForm
from src.app.widget.setup_reader_form import SetupReaderForm
from src.app.widget.timer import RunningTimer


class ReaderFrame:
    def __init__(self,
                 frame: tk.Frame,
                 mainPlottingFrame: tk.Frame,
                 plotFrame: tk.Frame,
                 kpiForm: KpiForm,
                 setupFrame: tk.Frame,
                 setupReaderForm: SetupReaderForm,
                 header: tk.Label,
                 timer: RunningTimer,
                 indicator,
                 indicatorCanvas: tk.Canvas,
                 startButton: GenericButton,
                 stopButton: GenericButton,
                 calibrateButton: GenericButton,
                 createButton: PlusIconButton):
        self.frame = frame
        self.createButton = createButton
        self.mainPlottingFrame = mainPlottingFrame
        self.plotFrame = plotFrame
        self.kpiForm = kpiForm
        self.setupFrame = setupFrame
        self.setupReaderForm = setupReaderForm
        self.calibrateButton = calibrateButton
        self.indicatorCanvas = indicatorCanvas
        self.header = header
        self.timer = timer
        self.indicator = indicator
        self.startButton = startButton
        self.stopButton = stopButton

    def hidePlotFrame(self):
        self.mainPlottingFrame.grid_remove()

    def showPlotFrame(self):
        self.mainPlottingFrame.grid()

    def hideSetupFrame(self):
        self.setupFrame.grid_remove()

    def showSetupFrame(self):
        formResults, _ = self.setupReaderForm.getConfiguration()
        self.setupReaderForm.resetFlowRate()
        self.setupFrame.grid()

    def updateHeader(self):
        formResults, _ = self.setupReaderForm.getConfiguration()
        self.header.configure(text=f"{formResults.getLotId()}")

    def resetSetupForm(self):
        configuration = self.setupReaderForm.updateConfiguration()
        self.header.configure(text=f"{configuration.getLotId()}")


