import tkinter as tk


class CustomDropdownMenu:
    def __init__(self, master, **kwargs):
        self.master = master
        self.root = master.winfo_toplevel()

        # Basic styling
        self.bg = kwargs.get('bg', 'white')
        self.fg = kwargs.get('fg', 'black')
        self.font = kwargs.get('font', ('Arial', 9))
        self.relief = kwargs.get('relief', 'solid')
        self.borderwidth = kwargs.get('borderwidth', 1)
        self.disabledforeground = kwargs.get('disabledforeground', 'gray')
        self.border_color = kwargs.get('border_color', 'white')

        # Custom options
        self.item_padding_x = kwargs.get('item_padding_x', 10)
        self.item_padding_y = kwargs.get('item_padding_y', 8)
        self.item_justify = kwargs.get('item_justify', 'left')
        self.separator_color = kwargs.get('separator_color', 'gray')
        self.min_width = kwargs.get('min_width', 150)
        self.min_height = kwargs.get('min_height', 150)

        self.dropdown_frame = None
        self.items = []
        self.is_visible = False

    def add_command(self, label="", command=None, state="normal"):
        self.items.append({
            'type': 'command',
            'label': label,
            'command': command,
            'state': state
        })

    def add_separator(self):
        self.items.append({'type': 'separator'})

    def delete(self, start, end):
        if start == 0 and end == 'end':
            self.items.clear()

    def tk_popup(self, x, y):
        if self.is_visible:
            return

        self.is_visible = True

        # Create dropdown frame with proper border
        self.dropdown_frame = tk.Toplevel(self.root)
        self.dropdown_frame.overrideredirect(True)
        self.dropdown_frame.configure(
            bg=self.border_color,
            highlightbackground=self.border_color,
            highlightcolor=self.border_color,
            highlightthickness=self.borderwidth
        )

        # Create main container
        container = tk.Frame(
            self.dropdown_frame,
            bg=self.bg,
            relief='flat',
            bd=0
        )
        container.pack(fill=tk.BOTH, expand=True)

        # Create items
        for item in self.items:
            if item['type'] == 'separator':
                sep_frame = tk.Frame(container, height=1, bg=self.separator_color)
                sep_frame.pack(fill=tk.BOTH, padx=8, pady=4)
            else:
                anchor = tk.W if self.item_justify == tk.LEFT else tk.CENTER

                btn = tk.Button(
                    container,  # Pack directly to container, not btn_frame
                    text=item['label'],
                    font=self.font,
                    bg=self.bg,
                    fg=self.fg if item['state'] == tk.NORMAL else self.disabledforeground,
                    activebackground=self.bg,
                    activeforeground=self.fg if item['state'] == tk.NORMAL else self.disabledforeground,
                    relief=tk.FLAT,
                    bd=0,
                    padx=self.item_padding_x,
                    pady=self.item_padding_y,
                    highlightthickness=0,
                    anchor=anchor,
                    state=item['state'],
                    cursor='hand2' if item['state'] == tk.NORMAL else 'arrow'
                )

                if item['state'] == tk.NORMAL and item['command']:
                    btn.configure(command=lambda cmd=item['command']: self._execute_command(cmd))

                # Pack button to fill entire width with padding applied as internal padding
                btn.pack(fill=tk.BOTH, expand=True)

        # Update and get proper size
        self.dropdown_frame.update_idletasks()
        width = max(self.dropdown_frame.winfo_reqwidth(), self.min_width)
        height = max(self.dropdown_frame.winfo_reqheight(), self.min_height)

        # Check screen boundaries and adjust position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Adjust x if going off right edge
        if x + width > screen_width:
            x = screen_width - width - 10

        # Adjust y if going off bottom edge
        if y + height > screen_height:
            y = y - height - 30  # Show above the button instead

        # Ensure minimum positioning
        x = max(0, x)
        y = max(0, y)

        # Position and show
        self.dropdown_frame.geometry(f"{width}x{height}+{x}+{y}")

        # Close on click outside
        self.root.bind('<Button-1>', self._on_click, add='+')

    def _execute_command(self, command):
        self.unpost()
        command()

    def _on_click(self, event):
        if self.dropdown_frame:
            # Get click position
            click_x = event.x_root
            click_y = event.y_root

            # Get dropdown bounds
            dd_x = self.dropdown_frame.winfo_rootx()
            dd_y = self.dropdown_frame.winfo_rooty()
            dd_w = self.dropdown_frame.winfo_width()
            dd_h = self.dropdown_frame.winfo_height()

            # Close if click is outside
            if not (dd_x <= click_x <= dd_x + dd_w and dd_y <= click_y <= dd_y + dd_h):
                self.unpost()

    def unpost(self):
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None
        self.is_visible = False
        try:
            self.root.unbind('<Button-1>')
        except:
            pass

        # Call close callback if set
        if hasattr(self, 'close_callback') and self.close_callback:
            self.close_callback()

    def bind(self, event, callback):
        if event == "<Unmap>":
            self.close_callback = callback