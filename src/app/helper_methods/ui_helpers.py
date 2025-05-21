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
    windowRoot.minsize(width=800, height=475)
    windowRoot.maxsize(width=800, height=475)
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

    # Create a class to store state to avoid issues with closures
    class ScrollState:
        def __init__(self):
            self.prev_y = 0
            self.dragging = False

    # Initialize state object
    state = ScrollState()

    def on_press(event):
        # Store the position when user first presses
        state.prev_y = event.y
        state.dragging = True
        # Change cursor to indicate dragging is possible
        windowCanvas.config(cursor="fleur")
        # Prevent event from propagating to avoid conflicts
        return "break"

    def on_drag(event):
        if not state.dragging:
            return

        # Calculate how far we've moved
        delta_y = state.prev_y - event.y

        # Update position for next event
        state.prev_y = event.y

        # Use fractions for more precise control
        # Get current view positions
        y_fraction = windowCanvas.yview()

        # Calculate new positions - adjust multiplier to control sensitivity
        new_y_fraction = y_fraction[0] + (delta_y * 0.001)

        # Keep within bounds
        new_y_fraction = max(0.0, min(1.0, new_y_fraction))

        # Apply the new positions
        windowCanvas.yview_moveto(new_y_fraction)

        # Prevent event from propagating
        return "break"

    def on_release(event):
        # Stop dragging
        state.dragging = False
        # Reset cursor
        windowCanvas.config(cursor="")
        # Prevent event from propagating
        return "break"

    # Bind touch/drag events to canvas
    windowCanvas.bind("<ButtonPress-1>", on_press)
    windowCanvas.bind("<B1-Motion>", on_drag)
    windowCanvas.bind("<ButtonRelease-1>", on_release)

    # Also bind to child elements to make sure they don't block the events
    def bind_recursive(widget):
        if not widget.winfo_class() in ("Button", "TButton"):
            widget.bind("<ButtonPress-1>", on_press)
            widget.bind("<B1-Motion>", on_drag)
            widget.bind("<ButtonRelease-1>", on_release)
        for child in widget.winfo_children():
            bind_recursive(child)

    # This will bind the events to window and all its children
    bind_recursive(window)

    # Configure grid weights to make canvas expandable
    windowRoot.grid_rowconfigure(0, weight=1)
    windowRoot.grid_columnconfigure(0, weight=1)

    fillOutWindowFn(window)
    windowCanvas.grid(row=0, column=0, sticky="nsew")
    windowCanvas.update()
    window.update()
    bounds = window.grid_bbox()
    windowCanvas.configure(scrollregion=(0, 0, bounds[2] + 25, bounds[3] + 25))

    # Need to bind to any new widgets that were created by fillOutWindowFn
    bind_recursive(window)

    return windowRoot, window


def datetimeToDisplay(dt: datetime.datetime):
    """ Converts a datetime to a string. i.e. Mon Jan 3rd 5:50 PM """
    if dt is not None:
        return dt.strftime('%a %b %d %I:%M %p')
    else:
        return None

