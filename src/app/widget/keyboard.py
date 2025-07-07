import tkinter as tk
from tkinter import font, ttk


class Keyboard:
    def __init__(self, root, hidePassword: bool):
        self.root = root
        self.bg_color = "#C7C7CC"  # Off grey
        self.normal_key_color = "#F7F7F7"  # off white
        self.highlight_color = "#4682B4"  # Steel blue
        self.normal_text_color = "#000000"  # Black
        self.caps_on = False
        self.shift_pressed = False
        self.hidePassword = hidePassword

        # Create keyboard window but keep it withdrawn initially
        self.keyboard_window = tk.Toplevel(root, background=self.bg_color)
        self.keyboard_window.withdraw()  # Hide immediately

        # Prevent window from showing during any updates
        self.keyboard_window.overrideredirect(True)

        # Get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the keyboard to take up the bottom half of the screen
        keyboard_height = 7 * screen_height // 8
        self.keyboard_window.geometry(f"{screen_width}x{keyboard_height}+0+{screen_height - keyboard_height}")
        self.keyboard_window.resizable(False, False)
        self.width = screen_width
        self.height = keyboard_height

        # Key layout - standard QWERTY keyboard with special characters row
        self.keys = [
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"],
            ["Caps", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "\\"],
            ["Clear", "a", "s", "d", "f", "g", "h", "j", "k", "l", "Enter"],
            ["Shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
        ]

        # Map of shift combinations for special characters
        self.shift_map = {
            "!": "1", "@": "2", "#": "3", "$": "4", "%": "5",
            "^": "6", "&": "7", "*": "8", "(": "9", ")": "0",
            "-": "_", "=": "+", "[": "{", "]": "}",
            ",": "<", ".": ">", "/": "?"
        }

        # Special key widths (as multipliers of standard key width)
        self.special_keys = {
            "Backspace": 2,
            "Caps": 1.5,
            "Clear": 1.75,
            "Enter": 2,
            "Shift": 2.25,
        }

        self.special_keys_color = {
            "Enter": "#99ef6c",  # Light green
            "Clear": "#ce5c6c"  # Light red
        }

        self.special_keys_font_color = {
            "Enter": "#FFFFFF",
            "Clear": "#FFFFFF"
        }

        # Store references to key widgets
        self.key_widgets = {}

        # Setup fonts
        self.regular_font = font.Font(family="Ubuntu", size=12)
        self.large_font = font.Font(family="Ubuntu", size=16, weight="bold")
        self.entry_font = font.Font(family="Ubuntu", size=20)

        # Initialize the keyboard layout
        self._create_keyboard_layout()

        # Bind events
        self.keyboard_window.bind("<KeyPress>", self.highlight_key_pressed)
        self.keyboard_window.bind("<KeyRelease>", self.physical_key_release)

    def _create_keyboard_layout(self):
        """Create the complete keyboard layout while window is hidden"""
        # Use full window space - entry gets proportional space at top
        entry_height = 80  # Fixed height for entry
        entry_margin = 20

        # Create the text entry widget to fill width with margins
        self.entry_frame = tk.Frame(
            self.keyboard_window,
            bg=self.bg_color,
            width=self.width - (entry_margin * 2),
            height=entry_height
        )
        self.entry_frame.place(x=entry_margin, y=entry_margin)
        self.entry_frame.pack_propagate(False)

        if self.hidePassword:
            self.entry = tk.Entry(
                self.entry_frame,
                font=self.entry_font,
                bd=2,
                show="*",
                relief=tk.SUNKEN,
            )
            self.entry.pack(fill=tk.BOTH, expand=True, side="left")
            self.showPasswordButton = ttk.Button(self.entry_frame, text="Show", command=self.togglePassword,
                                                 style='Entry.TButton')
            self.showPasswordButton.pack(side="left", padx=10, fill=tk.Y)
        else:
            self.entry = tk.Entry(
                self.entry_frame,
                font=self.entry_font,
                bd=2,
                relief=tk.SUNKEN,
            )
            self.entry.pack(fill=tk.BOTH, expand=True, side="left")

        # Create keyboard frame - use remaining space below entry
        keyboard_margin = 20
        keyboard_y = entry_margin + entry_height + entry_margin  # Below entry with margin
        keyboard_width = self.width - (keyboard_margin * 2)
        keyboard_height = self.height - keyboard_y - keyboard_margin  # Fill remaining space

        self.keyboard_frame = tk.Frame(
            self.keyboard_window,
            bg=self.bg_color,
            width=keyboard_width,
            height=keyboard_height
        )
        self.keyboard_frame.place(x=keyboard_margin, y=keyboard_y)

        # Store keyboard dimensions for use in key creation
        self.keyboard_width = keyboard_width
        self.keyboard_height = keyboard_height

        # Create all keyboard keys
        self._create_all_keys()

    def _create_all_keys(self):
        """Create all keyboard keys at once with performance optimizations"""
        # Use the stored keyboard dimensions
        kb_width = self.keyboard_width
        kb_height = self.keyboard_height

        # Calculate key dimensions to fill available space
        key_margin = 5

        # Calculate the total width units for each row (accounting for special key widths)
        row_widths = []
        for row in self.keys:
            total_width_units = sum(self.special_keys.get(key, 1) for key in row)
            row_widths.append(total_width_units)

        # Use the widest row to determine base key width
        max_width_units = max(row_widths)
        available_width = kb_width - (key_margin * 2)  # Account for margins

        # Calculate standard key width to fill available space
        total_margin_space = key_margin * (len(self.keys[0]) - 1)  # Approximate
        standard_key_width = (available_width - total_margin_space) // max_width_units

        # Calculate key height to fill available vertical space
        num_rows = len(self.keys)
        available_height = kb_height - (key_margin * 2)  # Account for top/bottom margins
        total_vertical_margins = key_margin * (num_rows - 1)  # Margins between rows
        key_height = (available_height - total_vertical_margins) // num_rows

        # Starting position with margins
        base_x, base_y = key_margin, key_margin

        # Collect widgets to place at the end for better performance
        widgets_to_place = []

        for row_index, row in enumerate(self.keys):
            # Calculate total width units for this row
            row_width_units = sum(self.special_keys.get(key, 1) for key in row)

            # Calculate spacing to center this row
            total_row_width = row_width_units * standard_key_width + (len(row) - 1) * key_margin
            row_start_x = base_x + (available_width - total_row_width) // 2

            x = row_start_x
            y = base_y + row_index * (key_height + key_margin)

            for key in row:
                # Get key properties
                width_multiplier = self.special_keys.get(key, 1)
                key_width = int(standard_key_width * width_multiplier)
                key_color = self.special_keys_color.get(key, self.normal_key_color)
                font_color = self.special_keys_font_color.get(key, self.normal_text_color)

                # Choose font based on key length
                key_font = self.regular_font if len(key) > 1 else self.large_font

                # Create single button widget instead of frame+label
                key_button = tk.Button(
                    self.keyboard_frame,
                    text=key,
                    width=key_width//10,  # Button width is in characters
                    height=key_height//25,  # Button height is in text lines
                    bg=key_color,
                    fg=font_color,
                    font=key_font,
                    relief=tk.RAISED,
                    bd=2,
                    activebackground=self.highlight_color,
                    command=lambda k=key: self.virtual_key_press(k)
                )

                # Add to placement queue instead of placing immediately
                widgets_to_place.append((key_button, x, y, key_width, key_height))

                # Store widget reference
                self.key_widgets[key] = key_button

                # Move to next key position
                x += key_width + key_margin

        # Place all widgets at once for better performance
        for button, x, y, width, height in widgets_to_place:
            button.place(x=x, y=y, width=width, height=height)

    def show_keyboard(self):
        """Show the keyboard after it's fully loaded"""
        # Ensure all layout is complete
        self.keyboard_window.update_idletasks()

        # Restore normal window behavior and show
        self.keyboard_window.overrideredirect(False)
        self.keyboard_window.deiconify()
        self.keyboard_window.focus_set()
        self.entry.focus_set()

    def toggle_shift(self):
        self.shift_pressed = not self.shift_pressed
        self.update_key_visuals()

    def update_key_visuals(self):
        """Update the visual display of keys based on shift/caps state"""
        # Batch update to minimize redraws
        updates = []

        for key in self.key_widgets:
            if key in ["Backspace", "Enter", "Clear", "Caps", "Shift"]:
                continue  # Skip special function keys

            button = self.key_widgets[key]
            new_text = key  # default

            if key.isalpha():
                # Handle letter keys
                if (self.caps_on and not self.shift_pressed) or (self.shift_pressed and not self.caps_on):
                    new_text = key.upper()
                else:
                    new_text = key.lower()
            elif key in self.shift_map and self.shift_pressed:
                # Show special character when shift is pressed
                new_text = self.shift_map[key]
            elif key in self.shift_map.values() and self.shift_pressed:
                # Show the special character for number keys
                for special, number in self.shift_map.items():
                    if number == key:
                        new_text = special
                        break

            updates.append((button, new_text))

        # Apply all updates at once
        for button, text in updates:
            button.config(text=text)

    def togglePassword(self):
        if self.entry.cget('show') == "*":
            self.entry.config(show="")
            self.showPasswordButton.config(text="Hide")
        else:
            self.entry.config(show="*")
            self.showPasswordButton.config(text="Show")

    def get_key_output(self, key):
        """Determine what character should be output for a given key based on shift/caps state"""
        # Handle special characters that have shift variants
        if key in self.shift_map and self.shift_pressed:
            return self.shift_map[key]
        elif key in self.shift_map.values() and self.shift_pressed:
            # Find the special character for this number
            for special, number in self.shift_map.items():
                if number == key:
                    return special

        # Handle letter case
        if key.isalpha():
            if (self.caps_on and not self.shift_pressed) or (self.shift_pressed and not self.caps_on):
                return key.upper()
            else:
                return key.lower()

        # For other characters, return as-is
        return key

    def virtual_key_press(self, key):
        # Handle virtual key press (when clicking on keyboard)
        if key == "Backspace":
            current_text = self.entry.get()
            if current_text:
                self.entry.delete(len(current_text) - 1, tk.END)
        elif key == "Enter":
            self.close_keyboard()
        elif key == "Clear":
            self.entry.delete(0, tk.END)
        elif key == "Shift":
            self.toggle_shift()
        elif key == "Caps":
            self.caps_on = not self.caps_on
            # Highlight Caps key if on
            caps_button = self.key_widgets["Caps"]
            if self.caps_on:
                caps_button.config(bg=self.highlight_color)
            else:
                caps_button.config(bg=self.normal_key_color)
            # Update visuals for all keys when caps changes
            self.update_key_visuals()
        else:
            # For regular keys, insert the character
            output_char = self.get_key_output(key)
            self.entry.insert(tk.INSERT, output_char)

        # Reset shift after key press (except for Shift and Caps keys)
        if self.shift_pressed and key != "Shift" and key != "Caps":
            self.toggle_shift()

        # Update shift key appearance
        shift_button = self.key_widgets["Shift"]
        if self.shift_pressed:
            shift_button.config(bg=self.highlight_color)
        else:
            shift_button.config(bg=self.normal_key_color)

        # Flash the key to show it's been pressed
        self.flash_key(key)

    def flash_key(self, key):
        """Simplified key flash animation"""
        if key not in self.key_widgets:
            return

        button = self.key_widgets[key]

        # Skip if it's the Caps key and it's already highlighted
        if key == "Caps" and self.caps_on:
            return

        # Store original color
        original_bg = button.cget("bg")

        # Highlight the key
        button.config(bg=self.highlight_color, relief=tk.SUNKEN)

        # Schedule return to normal state after a delay
        if not ((key == "Caps" and self.caps_on) or (key == "Shift" and self.shift_pressed)):
            self.keyboard_window.after(100, lambda: self.restore_key(key, original_bg))

    def restore_key(self, key, original_bg):
        """Restore key to original appearance"""
        # Skip if it's the Caps key and it's toggled on, or Shift and it's pressed
        if (key == "Caps" and self.caps_on) or (key == "Shift" and self.shift_pressed):
            return

        if key in self.key_widgets:
            button = self.key_widgets[key]
            button.config(bg=original_bg, relief=tk.RAISED)

    def highlight_key_pressed(self, event):
        # Map key events to our key names
        key_char = event.char.upper() if event.char.isalpha() else event.char
        key_sym = event.keysym

        # Handle special keys
        key_name = None
        if key_sym == "BackSpace":
            key_name = "Backspace"
        elif key_sym == "Caps_Lock":
            key_name = "Caps"
            self.caps_on = not self.caps_on
        elif key_sym == "Return":
            key_name = "Enter"
        elif key_sym == "backslash":
            key_name = "\\"
        elif key_sym == "Shift_L" or key_sym == "Shift_R":
            key_name = "Shift"
        elif key_sym == "comma":
            key_name = ","
        elif key_sym == "period":
            key_name = "."
        elif key_sym == "slash":
            key_name = "/"
        elif key_sym == "bracketleft":
            key_name = "["
        elif key_sym == "bracketright":
            key_name = "]"
        elif key_sym == "minus":
            key_name = "-"
        elif key_sym == "equal":
            key_name = "="
        elif len(key_char) == 1:
            key_name = key_char

        # Highlight the pressed key
        if key_name in self.key_widgets:
            button = self.key_widgets[key_name]
            button.config(bg=self.highlight_color, relief=tk.SUNKEN)

    def physical_key_release(self, event):
        # Map key events to our key names (same as in key_press)
        key_char = event.char.upper() if event.char.isalpha() else event.char
        key_sym = event.keysym

        # Handle special keys
        key_name = None
        if key_sym == "BackSpace":
            key_name = "Backspace"
        elif key_sym == "Tab":
            key_name = "Tab"
        elif key_sym == "Caps_Lock":
            key_name = "Caps"
            # Don't reset caps key if it's toggled on
            if self.caps_on:
                return
        elif key_sym == "Return":
            self.close_keyboard()
        elif key_sym == "space":
            key_name = "Space"
        elif key_sym == "backslash":
            key_name = "\\"
        elif key_sym == "Shift_L" or key_sym == "Shift_R":
            key_name = "Shift"
        elif key_sym == "comma":
            key_name = ","
        elif key_sym == "period":
            key_name = "."
        elif key_sym == "slash":
            key_name = "/"
        elif key_sym == "bracketleft":
            key_name = "["
        elif key_sym == "bracketright":
            key_name = "]"
        elif key_sym == "minus":
            key_name = "-"
        elif key_sym == "equal":
            key_name = "="
        elif len(key_char) == 1:
            key_name = key_char

        if key_name != "Shift" and self.shift_pressed:
            self.shift_pressed = False

        # Return key to normal state, except Caps Lock if it's on
        valid_conditions = (
                key_name in self.key_widgets and
                (key_name != "Caps" or not self.caps_on) and
                (key_name != "Shift" or not self.shift_pressed)
        )

        if valid_conditions:
            button = self.key_widgets[key_name]
            button.config(bg=self.normal_key_color, relief=tk.RAISED)

    def close_keyboard(self):
        """Closes the on-screen keyboard."""
        self.keyboard_window.withdraw()
        self.final_entry.config(state='normal')
        self.final_entry.delete(0, tk.END)
        self.final_entry.insert(tk.END, self.entry.get())

    def set_entry(self, entry_widget):
        """Sets the entry widget where the keyboard will type."""
        self.final_entry = entry_widget
        self.final_entry.config(state='disabled')

        # Clear and populate entry field
        self.entry.delete(0, tk.END)
        self.entry.insert(tk.END, entry_widget.get())

        # Show the keyboard now that everything is ready
        self.show_keyboard()