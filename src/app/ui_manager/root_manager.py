import platform
import subprocess
import threading
import tkinter as tk
from tkinter.constants import BOTH, TRUE

from PIL import Image, ImageTk

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper.helper_functions import isMenuOptionPresent
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme


class RootManager:
    def __init__(self):
        self.root = tk.Tk()  # everything in the application comes after this
        # self.root.bind('<FocusIn>', self.lowerWindow)
        image = Image.open(CommonFileManager().getSquareLogo())
        resizedImage = image.resize(
            (self.root.winfo_screenwidth(), self.root.winfo_screenheight()),
            Image.Resampling.LANCZOS
        )
        self.splashImage = ImageTk.PhotoImage(resizedImage)
        self.splash = self.createSplash()
        self.fonts = FontTheme()
        self.menubar = tk.Menu(self.root, font=self.fonts.menubar)
        # if platform.system() == "Linux":
        #     self.root.bind_class("Entry", "<FocusIn>", self.openKeyboard)
        self.setMenubar()

    def updateIdleTasks(self):
        self.root.update_idletasks()

    def createSplash(self):
        topLevel = self.createTopLevel()
        splash_label = tk.Label(topLevel, image=self.splashImage, background=Colors().secondaryColor)
        splash_label.pack(fill=BOTH, expand=TRUE)
        topLevel.wm_transient(self.root)
        if platform.system() == 'Windows':
            topLevel.state('zoomed')
        elif platform.system() == 'Linux':
            topLevel.attributes('-zoomed', True)
        return topLevel

    def destroySplash(self):
        self.splash.after(2000, lambda: self.splash.destroy())

    def instantiateNewMenubarRibbon(self):
        return tk.Menu(self.menubar, tearoff=0, font=self.fonts.menubar)

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
        self.root.update_idletasks()
        self.root.geometry(
            f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()-self.menubar.winfo_reqheight()}"
        )

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
