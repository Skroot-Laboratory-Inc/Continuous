import datetime
import tkinter as tk

from src.app.properties.screen_properties import ScreenProperties
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.custom_dropdown import CustomDropdownMenu
from src.app.widget.keyboard import Keyboard


def launchKeyboard(outputEntry: tk.Entry, master, label: str = "", hidePassword: bool = False):
    """Launch the on-screen keyboard when an Entry widget is clicked."""
    Keyboard(master, hidePassword, label).set_entry(outputEntry)


def datetimeToDisplay(dt: datetime.datetime):
    """ Converts a datetime to a string. i.e. Mon Jan 3rd 5:50 PM """
    if dt is not None:
        return dt.strftime('%a %b %d %I:%M %p')
    else:
        return None


def centerWindowOnFrame(window: tk.Toplevel, frame):
    """ Centers a window on a tkinter frame."""
    window.update_idletasks()
    if window.state() == 'withdrawn':
        window_width = window.winfo_reqwidth()
        window_height = window.winfo_reqheight()
    else:
        window.update()  # Only update if not withdrawn
        window_width = window.winfo_width()
        window_height = window.winfo_height()
    frame_x = frame.winfo_x()
    frame_y = frame.winfo_y()
    center_x = frame_x + (frame.winfo_width() // 2)
    center_y = frame_y + (frame.winfo_height() // 2)
    x = center_x - (window_width // 2)
    y = center_y - (window_height // 2)
    window.geometry('+%d+%d' % (x, y))


def styleDropdownOption(option):
    return f"{option}".center(45)


def createDropdown(root, entryVariable, options, outline=False):
    entryValue = entryVariable.get()

    dropdown_button = tk.Button(
        root,
        text=entryValue if entryValue else options[0],
        bg="white",
        borderwidth=1 if outline else 0,
        highlightthickness=1 if outline else 0,
        font=FontTheme().primary,
        anchor="center",
        padx=10
    )

    custom_menu = CustomDropdownMenu(
        root,
        item_justify = "center",
        bg="white",
        fg="black",
        font=FontTheme().primary,
        item_padding_y=WidgetTheme().internalPadding,
        borderwidth=1 if outline else 2,
        border_color="black",
        min_width=400,
    )

    for option in options:
        custom_menu.add_command(
            label=option,
            command=lambda opt=option: select_option(opt)
        )
        if option != options[-1]:
            custom_menu.add_separator()

    def select_option(option):
        entryVariable.set(option)
        dropdown_button.config(text=option)

    def show_dropdown():
        # Update the button to get its actual size
        dropdown_button.update_idletasks()
        button_width = dropdown_button.winfo_width()

        # Update the custom menu's min_width
        custom_menu.min_width = button_width

        x = dropdown_button.winfo_rootx()
        y = dropdown_button.winfo_rooty() + dropdown_button.winfo_height()
        custom_menu.tk_popup(x, y)

    dropdown_button.config(command=show_dropdown)
    return dropdown_button


import tkinter as tk


def makeToplevelScrollable(windowRoot, fillOutWindowFn):
    """ Makes a tkinter toplevel into a scrollable window with fixed height and width"""
    windowRoot.minsize(width=ScreenProperties().resolution['width'], height=ScreenProperties().resolution['height'])
    windowRoot.maxsize(width=ScreenProperties().resolution['width'], height=ScreenProperties().resolution['height'])

    # Create main container frame
    main_frame = tk.Frame(windowRoot, bg='white')
    main_frame.grid(row=0, column=0, sticky="nsew")

    windowCanvas = tk.Canvas(
        main_frame, bg='white', borderwidth=0,
        highlightthickness=0
    )

    # Create scroll buttons frame (positioned at the right)
    scroll_buttons_frame = tk.Frame(main_frame, bg='white', width=50)
    scroll_buttons_frame.grid(row=0, column=1, sticky="ns", padx=2)
    scroll_buttons_frame.grid_propagate(False)  # Maintain fixed width

    # Create scroll to top button
    scroll_top_btn = tk.Button(
        scroll_buttons_frame,
        text="▲",
        font=("Arial", 32, "bold"),
        bg=Colors().primaryColor,
        fg=Colors().secondaryColor,
        activebackground=Colors().primaryColor,
        relief='raised',
        command=lambda: windowCanvas.yview_moveto(0.0)
    )
    scroll_top_btn.pack(side="top", fill="x", padx=2, pady=2)

    # Create scroll to bottom button
    scroll_bottom_btn = tk.Button(
        scroll_buttons_frame,
        text="▼",
        font=("Arial", 32, "bold"),
        bg=Colors().primaryColor,
        fg=Colors().secondaryColor,
        activebackground=Colors().primaryColor,
        relief='raised',
        command=lambda: windowCanvas.yview_moveto(1.0)
    )
    scroll_bottom_btn.pack(side="bottom", fill="x", padx=2, pady=2)

    window = tk.Frame(windowRoot, bg='white', borderwidth=0)
    windowCanvas.create_window(ScreenProperties().resolution['width'] / 2, 0, anchor="n", window=window)

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
        # Lower fraction to reduce scroll speed
        new_y_fraction = y_fraction[0] + (delta_y * 0.0006)

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
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    fillOutWindowFn(window)
    windowCanvas.grid(row=0, column=0, sticky="nsew")
    windowCanvas.update()
    window.update()
    bounds = window.grid_bbox()
    windowCanvas.configure(scrollregion=(0, 0, bounds[2] + 25, bounds[3] + 25))

    # Need to bind to any new widgets that were created by fillOutWindowFn
    bind_recursive(window)

    return windowRoot, window
