import tkinter as tk

from reactivex.subject import BehaviorSubject

from src.app.properties.screen_properties import ScreenProperties
from src.app.ui_manager.popup_background import PopupBackground
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.widget import text_notification


class RootManager:
    def __init__(self):
        self.root = tk.Tk()  # everything in the application comes after this
        self.fonts = FontTheme()
        self.menubar = tk.Menu(self.root, font=self.fonts.primary)
        self.validateInteger = (self.root.register(validate_integer), '%P')
        self.validateIntegerError = (self.root.register(show_validation_error))
        self.setMenubar()
        self.popupDisplayed = BehaviorSubject(False)
        self.popupBackground = PopupBackground(self)

    def instantiateNewMenubarRibbon(self):
        return tk.Menu(self.menubar, tearoff=0, font=self.fonts.primary, border=10)

    def addMenubarCascade(self, label, menu):
        if not isMenuOptionPresent(self.menubar, label):
            self.menubar.add_cascade(label=label, menu=menu, font=self.fonts.primary)

    def setMenubar(self):
        self.root.config(menu=self.menubar)

    def createTopLevel(self):
        self.popupDisplayed.on_next(True)
        topLevel = tk.Toplevel(self.root, bg='white', padx=25, pady=25)
        topLevel.withdraw()
        return topLevel

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
        window.update_idletasks()
        window.update()
        window.deiconify()
        self.root.wait_window(window)
        self.popupDisplayed.on_next(False)

    def getRoot(self):
        return self.root

    def setState(self, state):
        self.root.state(state)

    def setAttribute(self, attribute, state):
        self.root.attributes(attribute, state)

    def setFullscreen(self):
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

    def setWindowSize(self):
        self.root.overrideredirect(True)
        self.root.geometry(f"{ScreenProperties().resolution['width']}x{ScreenProperties().resolution['height']}+0+0")

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

    def updateIdleTasks(self):
        self.root.update_idletasks()


def isMenuOptionPresent(menu_bar, menu_label):
    """
    Function to check if a menu is already present in the menubar.

    Parameters:
    - menu_bar (tk.Menu): The menubar to check.
    - menu_label (str): The label of the menu to check for.

    Returns:
    - bool: True if the menu is present, False otherwise.
    """
    for index in range(menu_bar.index("end") + 1):
        if menu_bar.type(index) == "cascade" and menu_bar.entrycget(index, "label") == menu_label:
            return True
    return False


def show_validation_error():
    text_notification.setText("Invalid Input, configurations must be integer days")


def validate_integer(P):
    if P.isdigit() or P == "":
        return True
    else:
        return False
