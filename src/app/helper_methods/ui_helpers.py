import datetime
import tkinter as tk

from src.app.theme.font_theme import FontTheme
from src.app.widget.keyboard import Keyboard


def launchKeyboard(outputEntry: tk.Entry, master, hidePassword: bool = False):
    """Launch the on-screen keyboard when an Entry widget is clicked."""
    Keyboard(master, hidePassword).set_entry(outputEntry)


def centerWindowOnFrame(window, frame):
    """ Centers a window on a tkinter frame."""
    window.update()
    frame_x = frame.winfo_x()
    frame_y = frame.winfo_y()
    center_x = frame_x + (frame.winfo_width() // 2)
    center_y = frame_y + (frame.winfo_height() // 2)
    x = center_x - (window.winfo_width() // 2)
    y = center_y - (window.winfo_height() // 2)
    window.geometry('+%d+%d' % (x, y))


def styleDropdownOption(option):
    return f"             {option}             "


def createDropdown(root, entryVariable, options, addSpace):
    if addSpace:
        options = [styleDropdownOption(option) for option in options]
    scanRateValue = entryVariable.get()
    optionMenu = tk.OptionMenu(root, entryVariable, *options)
    optionMenu.config(bg="white", highlightthickness=0, indicatoron=False, font=FontTheme().dropdown)
    optionMenu["menu"].config(bg="white")
    entryVariable.set(scanRateValue)
    return optionMenu


def makeToplevelScrollable(windowRoot, fillOutWindowFn):
    """ Makes a tkinter toplevel into a scrollable window with fixed height and width"""
    windowRoot.minsize(width=650, height=550)
    windowRoot.maxsize(width=800, height=550)
    windowCanvas = tk.Canvas(
        windowRoot, bg='white', borderwidth=0,
        highlightthickness=0
    )
    window = tk.Frame(windowRoot, bg='white', borderwidth=0)
    windowCanvas.create_window(0, 0, anchor="nw", window=window)
    # Linux uses Button-5 for scroll down and Button-4 for scroll up
    window.bind_all('<Button-4>', lambda e: windowCanvas.yview_scroll(int(-1 * e.num), 'units'))
    window.bind_all('<Button-5>', lambda e: windowCanvas.yview_scroll(int(e.num), 'units'))
    # Windows uses MouseWheel for scrolling
    window.bind_all('<MouseWheel>',
                         lambda e: windowCanvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    fillOutWindowFn(window)
    windowCanvas.grid(row=0, column=0, sticky="nsew")
    windowCanvas.update()
    window.update()
    bounds = window.grid_bbox()
    windowCanvas.configure(scrollregion=(0, 0, bounds[2] + 25, bounds[3] + 25))
    return windowRoot, window


def datetimeToDisplay(dt: datetime.datetime):
    """ Converts a datetime to a string. i.e. Mon Jan 3rd 5:50 PM """
    if dt is not None:
        return dt.strftime('%a %b %d %I:%M %p')
    else:
        return None

