import tkinter as tk
from tkinter import font, ttk

from src.app.properties.screen_properties import ScreenProperties
from src.app.ui_manager.theme import Colors


class Keyboard:
    def __init__(self, root, hidePassword: bool, label_text: str = ""):
        self.root = root
        self.shift_state = 0  # 0 = normal, 1 = shift, 2 = caps lock
        self.symbols_mode = False
        self.hidePassword = hidePassword
        self.label_text = label_text

        # Create keyboard window
        self.keyboard_window = tk.Toplevel(root, background=Colors().keyboard.background)
        self.keyboard_window.withdraw()
        self.keyboard_window.overrideredirect(True)

        screen_width = ScreenProperties().resolution['width']
        screen_height = ScreenProperties().resolution['height']
        self.keyboard_window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.keyboard_window.resizable(False, False)
        self.width = screen_width
        self.height = screen_height

        # Key layouts
        self.letters_layout = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["↑", "z", "x", "c", "v", "b", "n", "m", "⌫"],
            ["!#1", "?", "Space", ".", "↩"]
        ]

        self.symbols_layout = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["+", "×", "÷", "=", "/", "_", "<", ">", "[", "]"],
            ["!", "@", "#", "$", "%", "^", "&", "*", "?"],
            ["-", "'", "\"", ":", ";", ",", "(", ")", "⌫"],
            ["ABC", "?", "Space", ".", "↩"]
        ]

        self.keys = self.letters_layout

        # Shift mappings for number row
        self.shift_map = {
            "1": "!", "2": "@", "3": "#", "4": "$", "5": "%",
            "6": "^", "7": "&", "8": "*", "9": "(", "0": ")"
        }

        # Special key configurations
        self.special_keys = {
            "↩": {"width": 1.5, "color": Colors().keyboard.enter, "font_color": "#FFFFFF"},
            "!#1": {"width": 1.5, "color": Colors().keyboard.specialCharacters, "font_color": Colors().keyboard.specialCharactersFont},
            "ABC": {"width": 1.5, "color": Colors().keyboard.specialCharacters, "font_color": Colors().keyboard.specialCharactersFont},
            "Space": {"width": 4.0},
        }

        # Widget storage
        self.key_widgets = {}
        self.key_positions = {}

        # Fonts
        self.regular_font = font.Font(family="Ubuntu", size=12)
        self.label_font = font.Font(family="Ubuntu", size=30)
        self.large_font = font.Font(family="Ubuntu", size=16, weight="bold")
        self.symbol_font = font.Font(family="Arial Unicode MS", size=16, weight="bold")
        self.entry_font = font.Font(family="Ubuntu", size=20)

        self._create_layout()

    def _create_layout(self):
        """Create the complete keyboard layout"""
        entry_height = 80
        entry_margin = 20

        # Entry container
        entry_container = tk.Frame(
            self.keyboard_window,
            bg=Colors().keyboard.background,
            width=self.width - (entry_margin * 2),
            height=entry_height
        )
        entry_container.place(x=entry_margin, y=entry_margin)
        entry_container.pack_propagate(False)

        # Label if provided
        if self.label_text:
            self.label = tk.Label(
                entry_container,
                text=self.label_text,
                font=self.label_font,
                bg=Colors().keyboard.background,
                fg=Colors().keyboard.text,
                anchor="e"
            )
            self.label.pack(side="left", padx=(0, 10), fill=tk.Y)

        # Entry frame
        self.entry_frame = tk.Frame(entry_container, bg=Colors().keyboard.background)
        self.entry_frame.pack(side="left", fill=tk.BOTH, expand=True)

        # Entry widget
        self.entry = tk.Entry(
            self.entry_frame,
            font=self.entry_font,
            bd=2,
            show="*" if self.hidePassword else "",
            relief=tk.SUNKEN,
        )
        self.entry.pack(fill=tk.BOTH, expand=True, side="left")

        # Bind Enter key to submit action
        self.entry.bind('<Return>', self._on_enter_key)

        # Password toggle button
        if self.hidePassword:
            self.showPasswordButton = ttk.Button(
                self.entry_frame,
                text="Show",
                command=self._toggle_password
            )
            self.showPasswordButton.pack(side="left", padx=10, fill=tk.Y)

        # Keyboard frame
        keyboard_margin = 20
        keyboard_y = entry_margin + entry_height + entry_margin
        keyboard_width = self.width - (keyboard_margin * 2)
        keyboard_height = self.height - keyboard_y - keyboard_margin

        self.keyboard_frame = tk.Frame(
            self.keyboard_window,
            bg=Colors().keyboard.background,
            width=keyboard_width,
            height=keyboard_height
        )
        self.keyboard_frame.place(x=keyboard_margin, y=keyboard_y)

        self.keyboard_width = keyboard_width
        self.keyboard_height = keyboard_height

        self._create_keys()

    def _on_enter_key(self, event):
        """Handle physical Enter key press"""
        self.close_keyboard()
        return 'break'  # Prevent default Enter key behavior

    def _create_keys(self):
        """Create all keyboard keys"""
        key_margin = 5

        # Calculate dimensions
        max_width_units = max(
            sum(self.special_keys.get(key, {}).get("width", 1) for key in row)
            for row in self.keys
        )

        available_width = self.keyboard_width - (key_margin * 2)
        # Account for margins between keys when calculating standard width
        max_keys_in_row = max(len(row) for row in self.keys)
        total_margin_space = key_margin * (max_keys_in_row - 1)
        standard_key_width = (available_width - total_margin_space) // max_width_units

        num_rows = len(self.keys)
        available_height = self.keyboard_height - (key_margin * 2)
        key_height = (available_height - key_margin * (num_rows - 1)) // num_rows

        # Create keys
        for row_index, row in enumerate(self.keys):
            row_width_units = sum(self.special_keys.get(key, {}).get("width", 1) for key in row)
            actual_margin_space = key_margin * (len(row) - 1)
            total_row_width = row_width_units * standard_key_width + actual_margin_space
            row_start_x = key_margin + (available_width - total_row_width) // 2

            x = row_start_x
            y = key_margin + row_index * (key_height + key_margin)

            for col_index, key in enumerate(row):
                pos = (row_index, col_index)
                self.key_positions[pos] = key

                # Key properties
                key_config = self.special_keys.get(key, {})
                key_width = int(standard_key_width * key_config.get("width", 1))
                key_color = key_config.get("color", Colors().keyboard.key)
                font_color = key_config.get("font_color", Colors().keyboard.text)

                # Font selection
                if key in ["↑", "↩", "⌫"]:
                    key_font = self.symbol_font
                elif key in ["!#1", "ABC", "Space"]:
                    key_font = self.regular_font
                else:
                    key_font = self.large_font

                # Create button
                key_button = tk.Button(
                    self.keyboard_frame,
                    text=key,
                    bg=key_color,
                    fg=font_color,
                    font=key_font,
                    relief=tk.RAISED,
                    bd=2,
                    activebackground=Colors().keyboard.highlight,
                    command=lambda k=key, p=pos: self._key_press(k, p)
                )

                key_button.place(x=x, y=y, width=key_width, height=key_height)
                self.key_widgets[pos] = key_button

                x += key_width + key_margin

    def show_keyboard(self):
        """Show the keyboard"""
        self.keyboard_window.update_idletasks()
        self.keyboard_window.overrideredirect(False)
        self.keyboard_window.deiconify()
        self.keyboard_window.focus_set()
        self.entry.focus_set()

    def _toggle_password(self):
        """Toggle password visibility"""
        if self.entry.cget('show') == "*":
            self.entry.config(show="")
            self.showPasswordButton.config(text="Hide")
        else:
            self.entry.config(show="*")
            self.showPasswordButton.config(text="Show")

    def _toggle_mode(self):
        """Toggle between letters and symbols mode"""
        self.symbols_mode = not self.symbols_mode
        self.keys = self.symbols_layout if self.symbols_mode else self.letters_layout
        self.shift_state = 0  # Reset shift when switching modes
        self._update_keys()

    def _update_keys(self):
        """Update all key labels and properties"""
        for row_index, row in enumerate(self.keys):
            for col_index, key in enumerate(row):
                pos = (row_index, col_index)
                if pos in self.key_widgets:
                    button = self.key_widgets[pos]
                    self.key_positions[pos] = key

                    # Update properties
                    key_config = self.special_keys.get(key, {})
                    key_color = key_config.get("color", Colors().keyboard.key)
                    font_color = key_config.get("font_color", Colors().keyboard.text)

                    # Font selection
                    if key in ["↑", "↩", "⌫"]:
                        key_font = self.symbol_font
                    elif key in ["!#1", "ABC", "Space"]:
                        key_font = self.regular_font
                    else:
                        key_font = self.large_font

                    button.config(
                        text=key,
                        bg=key_color,
                        fg=font_color,
                        font=key_font,
                        command=lambda k=key, p=pos: self._key_press(k, p)
                    )

        self._update_shift_appearance()
        self._update_visuals()

    def _toggle_shift(self):
        """Toggle shift state (letters mode only)"""
        if not self.symbols_mode:
            self.shift_state = (self.shift_state + 1) % 3
            self._update_shift_appearance()
            self._update_visuals()

    def _update_shift_appearance(self):
        """Update shift key appearance"""
        shift_pos = self._find_key_position("↑")
        if not shift_pos or self.symbols_mode:
            return

        button = self.key_widgets[shift_pos]

        if self.shift_state == 2:  # Caps lock
            button.config(text="⇈", bg=Colors().keyboard.highlight)
        elif self.shift_state == 1:  # Shift
            button.config(text="↑", bg=Colors().keyboard.highlight)
        else:  # Normal
            button.config(text="↑", bg=Colors().keyboard.key)

    def _update_visuals(self):
        """Update key visuals based on shift state"""
        if self.symbols_mode:
            return

        for pos, button in self.key_widgets.items():
            key = self.key_positions[pos]

            if key in ["⌫", "↩", "↑", "!#1", "ABC", "Space"]:
                continue

            new_text = self._get_display_text(key)
            button.config(text=new_text)

    def _get_display_text(self, key):
        """Get the text to display on a key based on shift state"""
        if self.symbols_mode:
            return key

        if key.isalpha():
            return key.upper() if (self.shift_state == 1 or self.shift_state == 2) else key.lower()
        elif key in self.shift_map and self.shift_state == 1:
            return self.shift_map[key]

        return key

    def _get_output_char(self, key):
        """Get the character to output for a key"""
        if self.symbols_mode:
            return key

        if key.isalpha():
            return key.upper() if (self.shift_state == 1 or self.shift_state == 2) else key.lower()
        elif key in self.shift_map and self.shift_state == 1:
            return self.shift_map[key]

        return key

    def _find_key_position(self, target_key):
        """Find the position of a key"""
        for pos, key in self.key_positions.items():
            if key == target_key:
                return pos
        return None

    def _key_press(self, key, pos):
        """Handle key press"""
        if key == "⌫":  # Backspace
            current_text = self.entry.get()
            if current_text:
                self.entry.delete(len(current_text) - 1, tk.END)
        elif key == "↩":  # Enter
            self.close_keyboard()
        elif key == "↑":  # Shift
            self._toggle_shift()
        elif key in ["!#1", "ABC"]:  # Mode toggle
            self._toggle_mode()
        elif key == "Space":  # Space
            self.entry.insert(tk.INSERT, " ")
        else:  # Regular key
            output_char = self._get_output_char(key)
            self.entry.insert(tk.INSERT, output_char)

        # Reset shift after letter input
        if (self.shift_state == 1 and not self.symbols_mode and
                key.isalpha() and key not in ["↑", "!#1", "ABC", "Space"]):
            self.shift_state = 0
            self._update_shift_appearance()
            self._update_visuals()

        self._flash_key(pos)

    def _flash_key(self, pos):
        """Flash a key to show it's pressed"""
        if pos not in self.key_widgets:
            return

        button = self.key_widgets[pos]
        key = self.key_positions[pos]

        # Skip if shift key is in special state
        if key == "↑" and self.shift_state > 0:
            return

        original_bg = button.cget("bg")
        button.config(bg=Colors().keyboard.highlight, relief=tk.SUNKEN)

        # Restore after delay
        if not ((key == "↑" and self.shift_state > 0)):
            self.keyboard_window.after(100, lambda: self._restore_key(pos, original_bg))

    def _restore_key(self, pos, original_bg):
        """Restore key appearance"""
        if pos in self.key_widgets:
            key = self.key_positions[pos]
            if not (key == "↑" and self.shift_state > 0):
                button = self.key_widgets[pos]
                button.config(bg=original_bg, relief=tk.RAISED)

    def close_keyboard(self):
        """Close the keyboard"""
        self.keyboard_window.withdraw()
        self.final_entry.config(state='normal')
        self.final_entry.delete(0, tk.END)
        self.final_entry.insert(tk.END, self.entry.get())

    def set_entry(self, entry_widget):
        """Set the target entry widget"""
        self.final_entry = entry_widget
        self.final_entry.config(state='disabled')

        self.entry.delete(0, tk.END)
        self.entry.insert(tk.END, entry_widget.get())

        self.show_keyboard()