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
        self.keyboard_window = tk.Toplevel(root, background=self.bg_color)
        self.hidePassword = hidePassword

        # Get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the keyboard to take up the bottom half of the screen
        keyboard_height = 7 * screen_height // 8
        self.keyboard_window.geometry(f"{screen_width}x{keyboard_height}+0+{screen_height - keyboard_height}")
        self.keyboard_window.resizable(False, False)
        self.width = screen_width
        self.height = keyboard_height
        self.keyboard_window.withdraw()

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

        # Calculate dimensions for upper and lower sections
        self.upper_half_height = self.height // 8
        self.lower_half_height = 7 * self.height // 8

        # Create the text entry widget
        self.entry_frame = tk.Frame(
            self.keyboard_window,
            bg=self.bg_color,
            width=self.width - 100,
            height=60  # Taller entry field
        )
        entry_y_position = (self.upper_half_height - 30) // 2  # Center in upper half
        self.entry_frame.place(x=50, y=entry_y_position)
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
            self.showPasswordButton.pack(side="left", padx=10)
        else:
            self.entry = tk.Entry(
                self.entry_frame,
                font=self.entry_font,
                bd=2,
                relief=tk.SUNKEN,
            )
            self.entry.pack(fill=tk.BOTH, expand=True, side="left")

        # Create keyboard frame
        self.keyboard_frame = tk.Frame(
            self.keyboard_window,
            bg=self.bg_color,
            width=self.width - 40,
            height=self.lower_half_height - 20
        )
        self.keyboard_frame.place(x=20, y=self.upper_half_height + 10)
        self.draw_keyboard()
        self.keyboard_window.bind("<KeyPress>", self.highlight_key_pressed)
        self.keyboard_window.bind("<KeyRelease>", self.physical_key_release)

    def toggle_shift(self):
        self.shift_pressed = not self.shift_pressed
        self.update_key_visuals()

    def update_key_visuals(self):
        """Update the visual display of keys based on shift/caps state"""
        for key in self.key_widgets:
            if key in ["Backspace", "Enter", "Clear", "Caps", "Shift"]:
                continue  # Skip special function keys

            label_widget = self.key_widgets[key]['label']

            if key.isalpha():
                # Handle letter keys
                if (self.caps_on and not self.shift_pressed) or (self.shift_pressed and not self.caps_on):
                    label_widget.config(text=key.upper())
                else:
                    label_widget.config(text=key.lower())
            elif key in self.shift_map and self.shift_pressed:
                # Show special character when shift is pressed
                label_widget.config(text=self.shift_map[key])
            elif key in self.shift_map.values() and self.shift_pressed:
                # Show the special character for number keys
                for special, number in self.shift_map.items():
                    if number == key:
                        label_widget.config(text=special)
                        break
            else:
                # Default display
                label_widget.config(text=key)

    def togglePassword(self):
        if self.entry.cget('show') == "*":
            self.entry.config(show="")
            self.showPasswordButton.config(text="Hide")
        else:
            self.entry.config(show="*")
            self.showPasswordButton.config(text="Show")

    def draw_keyboard(self):
        # Get keyboard frame dimensions
        kb_width = self.width - 40
        kb_height = self.lower_half_height - 20

        # Calculate key dimensions based on available space (now 5 rows instead of 4)
        # Use 16 as the base since the top row has 13 keys but some are wider
        standard_key_width = kb_width // 14  # Divide by approximate number of keys in widest row
        key_margin = 3  # Reduced margin to save space
        key_height = kb_height // 4 - key_margin * 4  # 4 rows plus margins

        # Starting position
        base_x, base_y = 5, 5

        # Draw rows of keys
        for row_index, row in enumerate(self.keys):
            x = base_x  # Reset x position for each row

            # Adjust row starting positions for staggered layout
            if row_index == 2:  # Caps row (was row 1)
                x += standard_key_width * 0.2  # Reduced offset
            elif row_index == 3:  # Clear row (was row 2)
                x += standard_key_width * 0.4  # Reduced offset
            elif row_index == 4:  # Shift row (was row 3)
                x += standard_key_width * 0.6  # Reduced offset

            y = base_y + row_index * (key_height + key_margin)

            for key in row:
                # Get key width
                width_multiplier = self.special_keys.get(key, 1)
                key_width = int(standard_key_width * width_multiplier)
                key_color = self.special_keys_color.get(key, self.normal_key_color)
                font_color = self.special_keys_font_color.get(key, self.normal_text_color)
                # Create key frame with 3D effect
                key_frame = tk.Frame(
                    self.keyboard_frame,
                    width=key_width,
                    height=key_height,
                    bg=key_color,
                    relief=tk.RAISED,
                    bd=2
                )
                key_frame.place(x=x, y=y)

                # Keep key frame from resizing
                key_frame.pack_propagate(False)

                # Add key label
                if len(key) > 1:  # Special key
                    key_label = tk.Label(
                        key_frame,
                        text=key,
                        bg=key_color,
                        fg=font_color,
                        font=self.regular_font
                    )
                else:  # Regular key
                    key_label = tk.Label(
                        key_frame,
                        text=key,
                        bg=key_color,
                        fg=font_color,
                        font=self.large_font
                    )

                key_label.pack(expand=True)

                # Bind click events to virtual key press
                key_frame.bind("<Button-1>", lambda e, k=key: self.virtual_key_press(k))
                key_label.bind("<Button-1>", lambda e, k=key: self.virtual_key_press(k))

                # Store reference to key widgets
                self.key_widgets[key] = {
                    'frame': key_frame,
                    'label': key_label
                }

                # Move to next key position
                x += key_width + key_margin

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
            if self.caps_on:
                self.key_widgets["Caps"]['frame'].config(bg=self.highlight_color)
                self.key_widgets["Caps"]['label'].config(bg=self.highlight_color)
            else:
                self.key_widgets["Caps"]['frame'].config(bg=self.normal_key_color)
                self.key_widgets["Caps"]['label'].config(bg=self.normal_key_color)
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
        if self.shift_pressed:
            self.key_widgets["Shift"]['frame'].config(bg=self.highlight_color)
            self.key_widgets["Shift"]['label'].config(bg=self.highlight_color)
        else:
            self.key_widgets["Shift"]['frame'].config(bg=self.normal_key_color)
            self.key_widgets["Shift"]['label'].config(bg=self.normal_key_color)

        # Flash the key to show it's been pressed
        if key in self.key_widgets:
            key_frame = self.key_widgets[key]['frame']
            key_label = self.key_widgets[key]['label']

            # Skip if it's the Caps key and it's already highlighted
            if key == "Caps" and self.caps_on:
                return

            # Highlight the key
            original_bg = key_frame.cget("bg")
            key_frame.config(bg=self.highlight_color, relief=tk.SUNKEN)
            key_label.config(bg=self.highlight_color)

            # Schedule return to normal state after a delay
            if key != "Caps" or not self.caps_on and key != "Shift" or not self.shift_pressed:
                self.keyboard_window.after(100, lambda: self.restore_key(key, original_bg))

    def restore_key(self, key, original_bg):
        # Skip if it's the Caps key and it's toggled on
        if key == "Caps" and self.caps_on:
            return

        if key in self.key_widgets:
            key_frame = self.key_widgets[key]['frame']
            key_label = self.key_widgets[key]['label']
            key_frame.config(bg=original_bg, relief=tk.RAISED)
            key_label.config(bg=original_bg)

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
            key_frame = self.key_widgets[key_name]['frame']
            key_label = self.key_widgets[key_name]['label']
            key_frame.config(bg=self.highlight_color, relief=tk.SUNKEN)
            key_label.config(bg=self.highlight_color)

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
        if (key_name in self.key_widgets and key_name != "Caps" or (key_name == "Caps" and not self.caps_on)) and (
                key_name != "Shift" or (key_name == "Shift" and not self.shift_pressed)):
            key_frame = self.key_widgets[key_name]['frame']
            key_label = self.key_widgets[key_name]['label']
            key_frame.config(bg=self.normal_key_color, relief=tk.RAISED)
            key_label.config(bg=self.normal_key_color)

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
        self.entry.insert(tk.END, entry_widget.get())
        self.root.focus()
        self.entry.focus_set()
        self.keyboard_window.deiconify()