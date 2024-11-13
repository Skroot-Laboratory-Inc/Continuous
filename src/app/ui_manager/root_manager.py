import subprocess
import threading
import tkinter as tk

from src.app.helper.helper_functions import isMenuOptionPresent, getOperatingSystem
from src.app.theme.font_theme import FontTheme


class RootManager:
    def __init__(self):
        self.root = tk.Tk()  # everything in the application comes after this
        # self.root.bind('<FocusIn>', self.lowerWindow)
        self.fonts = FontTheme()
        self.menubar = tk.Menu(self.root, font=self.fonts.menubar)
        # if getOperatingSystem() == "linux":
        #     self.root.bind_class("Entry", "<FocusIn>", self.openKeyboard)
        self.setMenubar()

    def updateIdleTasks(self):
        self.root.update_idletasks()

    def instantiateNewMenubarRibbon(self):
        return tk.Menu(self.menubar, tearoff=0, font=self.fonts.menubar, border=10)

    def addMenubarCascade(self, label, menu):
        if not isMenuOptionPresent(self.menubar, label):
            self.menubar.add_cascade(label=label, menu=menu, font=self.fonts.menubar)

    def setMenubar(self):
        self.root.config(menu=self.menubar)

    def deleteMenubar(self, menubarId):
        self.menubar.delete(menubarId)

    def createTopLevel(self):
        return tk.Toplevel(self.root, bg='white', padx=25, pady=25)

    def createFrame(self, backgroundColor) -> tk.Frame:
        return tk.Frame(self.root, bg=backgroundColor)

    def createPaddedFrame(self, backgroundColor) -> tk.Frame:
        return tk.Frame(self.root, bg=backgroundColor, padx=15, pady=15)

    def callMainLoop(self):
        self.root.mainloop()  # everything comes before this

    def raiseAboveRoot(self, window):
        window.tkraise(self.root)

    def raiseRoot(self):
        self.root.tkraise()

    def waitForWindow(self, window):
        self.root.wait_window(window)

    def destroyRoot(self):
        self.root.destroy()

    def getRoot(self):
        return self.root

    def setState(self, state):
        self.root.state(state)

    def setAttribute(self, attribute, state):
        self.root.attributes(attribute, state)

    def setFullscreen(self):
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

    def setProtocol(self, protocol, invokeFn):
        self.root.protocol(protocol, invokeFn)

    def setTitle(self, title):
        self.root.title(title)

    def setBackgroundColor(self, backgroundColor):
        self.root.configure(background=backgroundColor)

    def generateEvent(self, event):
        self.root.event_generate(event)

    def registerEvent(self, event, eventFn):
        self.root.bind(event, eventFn)

    def lowerWindow(self, event):
        self.root.lower()

    def openKeyboard(self, event):
        stopReaderThread = threading.Thread(target=self.openKeyboardThread, args=(), daemon=True)
        stopReaderThread.start()

    def openKeyboardThread(self):
        topLevel = self.createTopLevel()
        frame = tk.Frame(topLevel)
        frame.pack()
        processId = subprocess.Popen(['onboard', "-e"], stdout=subprocess.PIPE)
        output = processId.stdout.readlines()
        subprocess.Popen(['xdotool', "windowreparent", f"{output}, f{frame.winfo_id()}"])
