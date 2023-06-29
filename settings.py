import math
import tkinter as tk
import tkinter.ttk as ttk

import matplotlib as mpl

import logger
from readers import Reader, FoamingReader


class Settings:
    def __init__(self, AppModule):
        self.AppModule = AppModule

    def foamThreshSetting(self):
        foamThresh = tk.simpledialog.askfloat("Input",
                                              "Threshold for when defoamer notification is needed: \nRange: (1-100)",
                                              parent=self.AppModule.root, minvalue=1, maxvalue=100)
        if foamThresh != None:
            self.AppModule.foamThresh = foamThresh
            logger.info(f'foamThresh changed to {foamThresh}')

    def foamEmailSetting(self):
        receiver_email = ""
        if self.AppModule.emailSetting == False:
            self.AppModule.emailSetting = tk.messagebox.askyesno('Email Setting',
                                                                 'Would you like to receive email notifications?')
            if self.AppModule.emailSetting == True:
                receiver_email = tk.simpledialog.askstring("Email recipient",
                                                           "What email should the notification be sent to? \nKeep an eye on the spam folder.",
                                                           show='*@gmail.com')
        else:
            receiver_email = tk.simpledialog.askstring("Email recipient",
                                                       "What email should the notification be sent to? \nKeep an eye on the spam folder.",
                                                       show='*@gmail.com')
        for Reader in self.AppModule.Readers:
            if receiver_email != "":
                Reader.updateEmailReceiver(receiver_email)

    def freqRangeSetting(self):
        startFreq = tk.simpledialog.askfloat("Input", "Start Frequency (MHz): \nRange: (0.1-250MHz)",
                                             parent=self.AppModule.root, minvalue=0.1, maxvalue=250)
        stopFreq = tk.simpledialog.askfloat("Input", "Stop Frequency (MHz): \nRange: (0.1-250MHz)",
                                            parent=self.AppModule.root, minvalue=0.1, maxvalue=250)
        if startFreq is not None:
            for Reader in self.AppModule.Readers:
                Reader.startFreq = startFreq
            self.AppModule.startFreq = startFreq
            logger.info(f'startFreq changed to {startFreq}')
        if stopFreq is not None:
            for Reader in self.AppModule.Readers:
                Reader.stopFreq = stopFreq
            self.AppModule.stopFreq = stopFreq
            logger.info(f'stopFreq changed to {stopFreq}')

    def nPointsSetting(self):
        nPoints = tk.simpledialog.askfloat("Input", "Number of points per scan: \nRange: (1,000-7,000)",
                                           parent=self.AppModule.root, minvalue=1000, maxvalue=7000)
        if nPoints is not None:
            for Reader in self.AppModule.Readers:
                Reader.nPoints = nPoints
            self.AppModule.nPoints = nPoints
            logger.info(f'nPoints changed to {nPoints}')

    def saveFilesSetting(self):
        disableSaveFullFiles = tk.messagebox.askyesno("Disable Full File Save",
                                                      "Are you sure you would like to disable entire file save? \n",
                                                      parent=self.AppModule.root)
        if disableSaveFullFiles is not None:
            self.AppModule.disableSaveFullFiles = disableSaveFullFiles
            logger.info(f'disableSaveFullFiles changed to {disableSaveFullFiles}')

    def rateSetting(self):
        scanRate = tk.simpledialog.askfloat("Input", "Scan Rate (minutes between scans): \nRange: (0.1 - 10)",
                                            parent=self.AppModule.root, minvalue=0.1, maxvalue=10.0)
        if scanRate is not None:
            for Reader in self.AppModule.Readers:
                Reader.scanRate = scanRate
            self.AppModule.scanRate = scanRate
            logger.info(f'scanRate changed to {scanRate}')

    def denoiseSetting(self):
        self.AppModule.denoiseSet = tk.messagebox.askyesno('Denoise Setting',
                                                           'Would you like to denoise and smooth the results before displaying them?')
        logger.info(f'denoiseSet changed to {self.AppModule.denoiseSet}')

    def freqToggleSetting(self, toggle):
        self.AppModule.freqToggleSet = toggle
        logger.info(f'freqToggleSet changed to {toggle}')

    def splineToggleSetting(self):
        self.AppModule.splineToggleSet = tk.messagebox.askyesno('Quadratic/Spline',
                                                                'Would you like to switch analysis to spline? (yes for Spline no for Quadratic) ')
        logger.info(f'splineToggleSet changed to {self.AppModule.denoiseSet}')

    def weakSignalToggleSetting(self):
        self.AppModule.weakSignalToggleSet = tk.messagebox.askyesno('Ignore Weak Signal',
                                                                    'Are you sure you would like to ignore the weak signal warning?')
        logger.info(f'weakSignalToggleSet changed to {self.AppModule.denoiseSet}')

    def setNumReaders(self):
        numReaders = tk.simpledialog.askinteger("Input", "Number of readers used: \nRange: (1 - 12)",
                                                parent=self.AppModule.root, minvalue=1, maxvalue=12)
        logger.info(f'numReaders changed to {numReaders}')
        if numReaders != '':
            self.AppModule.numReaders = numReaders

    def createReaders(self, numReaders):
        self.AppModule.ColorCycler.reset()
        self.addReaderNotes()
        self.addReaderSecondAxis()
        if self.AppModule.cellApp:
            self.addInoculation()
        if numReaders is not None:
            self.AppModule.outerFrames = []
            numScreens = math.ceil(numReaders / 4)
            readersOnLastScreen = numReaders % 4
            if readersOnLastScreen == 0:
                readersOnLastScreen = 4
            for i in range(numScreens):
                self.AppModule.outerFrames.append(tk.Frame(self.AppModule.root, bg=self.AppModule.white))
            if self.AppModule.foamingApp:
                for readerNumber in range(1, numReaders + 1):
                    readerColor = self.AppModule.ColorCycler.getNext()
                    screenNumber = math.ceil(readerNumber / 4) - 1
                    outerFrame = self.AppModule.outerFrames[screenNumber]
                    if screenNumber == numScreens - 1:
                        readersOnScreen = readersOnLastScreen
                    else:
                        readersOnScreen = 4
                    self.AppModule.Readers.append(FoamingReader( \
                        self.AppModule, readerNumber, self.AppModule.airFreq, self.AppModule.waterFreq, \
                        self.AppModule.waterShift, outerFrame, numReaders, self.AppModule.nPoints,
                        self.AppModule.startFreq, self.AppModule.stopFreq, self.AppModule.scanRate,
                        self.AppModule.savePath, readerColor) \
                        )
            elif self.AppModule.cellApp:
                for readerNumber in range(1, numReaders + 1):
                    readerColor = self.AppModule.ColorCycler.getNext()
                    screenNumber = math.ceil(readerNumber / 4) - 1
                    outerFrame = self.AppModule.outerFrames[screenNumber]
                    if screenNumber == numScreens - 1:
                        readersOnScreen = readersOnLastScreen
                    else:
                        readersOnScreen = 4
                    self.AppModule.Readers.append(Reader( \
                        self.AppModule, readerNumber, outerFrame, readersOnScreen, \
                        self.AppModule.nPoints, self.AppModule.startFreq, self.AppModule.stopFreq,
                        self.AppModule.scanRate, self.AppModule.savePath, readerColor) \
                        )
            self.createNextAndPreviousFrameButtons()
            self.AppModule.showFrame(self.AppModule.outerFrames[0])
            self.updateFontSize()

    def createNextAndPreviousFrameButtons(self):
        for screenNumber in range(len(self.AppModule.outerFrames)):
            if (screenNumber + 1) != len(self.AppModule.outerFrames):
                # nextReaders = ttk.Button(self.AppModule.outerFrames[screenNumber], text="Next", command = lambda: self.AppModule.showFrame(self.AppModule.outerFrames[screenNumber+1]))
                # nextReaders.place(relx=0.85, rely=0.94, relwidth=0.15, relheight=0.04)
                # nextReaders['style'] = 'W.TButton'
                nextReaders = tk.Canvas(self.AppModule.outerFrames[screenNumber], bg='gray93', highlightthickness=1,
                                        highlightbackground='black')
                nextReaders.place(relx=0.85, rely=0.94, relwidth=0.15, relheight=0.04)
                nextReaders.bind("<Button>", lambda event, frame=self.AppModule.outerFrames[
                    screenNumber + 1]: self.AppModule.showFrame(frame))
                nextText = ttk.Label(nextReaders, text="Next", font=("Arial", 12), background='gray93', borderwidth=0)
                nextText.place(anchor='center', relx=.5, rely=0.5)
                nextText.bind("<Button>", lambda event, frame=self.AppModule.outerFrames[
                    screenNumber + 1]: self.AppModule.showFrame(frame))
            else:
                nextReaders = tk.Canvas(self.AppModule.outerFrames[screenNumber], bg='gray93', highlightthickness=1,
                                        highlightbackground='black')
                nextReaders.place(relx=0.85, rely=0.94, relwidth=0.15, relheight=0.04)
                nextReaders.bind("<Button>",
                                 lambda event, frame=self.AppModule.outerFrames[0]: self.AppModule.showFrame(frame))
                nextText = ttk.Label(nextReaders, text="Next", font=("Arial", 12), background='gray93', borderwidth=0)
                nextText.place(anchor='center', relx=.5, rely=0.5)
                nextText.bind("<Button>",
                              lambda event, frame=self.AppModule.outerFrames[0]: self.AppModule.showFrame(frame))

            previousReaders = tk.Canvas(self.AppModule.outerFrames[screenNumber], bg='gray93', highlightthickness=1,
                                        highlightbackground='black')
            previousReaders.place(relx=0, rely=0.94, relwidth=0.15, relheight=0.04)
            previousReaders.bind("<Button>", lambda event, frame=self.AppModule.outerFrames[
                screenNumber - 1]: self.AppModule.showFrame(frame))
            previousText = ttk.Label(previousReaders, text="Previous", font=("Arial", 12), background='gray93',
                                     borderwidth=0)
            previousText.place(anchor='center', relx=0.5, rely=0.5)
            previousText.bind("<Button>", lambda event, frame=self.AppModule.outerFrames[
                screenNumber - 1]: self.AppModule.showFrame(frame))

    def addReaderNotes(self):
        try:
            self.AppModule.menubar.delete("Experiment Notes")
        except:
            pass
        if self.AppModule.Readers:
            settingsMenuNotes = tk.Menu(self.AppModule.menubar, tearoff=0)
            for Reader in self.AppModule.Readers:
                Reader.addExperimentNotesMenubar(settingsMenuNotes)
            self.AppModule.menubar.add_cascade(label="Experiment Notes", menu=settingsMenuNotes)

    def addReaderSecondAxis(self):
        try:
            self.AppModule.menubar.delete("Second Axis")
        except:
            pass
        if self.AppModule.Readers:
            settingsMenuSecondAxis = tk.Menu(self.AppModule.menubar, tearoff=0)
            for Reader in self.AppModule.Readers:
                Reader.addSecondAxisMenubar(settingsMenuSecondAxis)
            self.AppModule.menubar.add_cascade(label="Second Axis", menu=settingsMenuSecondAxis)

    def addInoculation(self):
        try:
            self.AppModule.menubar.delete("Inoculation")
        except:
            pass
        settingsMenuNotes = tk.Menu(self.AppModule.menubar, tearoff=0)
        settingsMenuNotes.add_command(label=f"All readers inoculated", command=lambda: self.inoculateAllReaders())
        for Reader in self.AppModule.Readers:
            Reader.addInoculationMenuBar(settingsMenuNotes)
        self.AppModule.menubar.add_cascade(label="Inoculation", menu=settingsMenuNotes)

    def inoculateAllReaders(self):
        for Reader in self.AppModule.Readers:
            Reader.updateInoculation()

    def updateFontSize(self):
        numberReaders = len(self.AppModule.Readers)
        if numberReaders > 1:
            fontsize = 9
        else:
            fontsize = 13
        mpl.rcParams.update({'font.size': fontsize})

    def selectCell(self):
        logger.info('cell selected')
        self.AppModule.cellApp = True
        self.AppModule.foamingApp = False

    def selectFoaming(self):
        logger.info('foaming selected')
        self.AppModule.cellApp = False
        self.AppModule.foamingApp = True
