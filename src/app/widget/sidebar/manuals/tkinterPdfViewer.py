import math
import tkinter as tk
from tkinter import ttk

import fitz
from PIL import Image, ImageTk

from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme


class ShowPdf:
    img_object_li = []
    tkimg_object_li = []
    open_pdf = None  # Store the currently opened PDF

    def close_pdf(self):
        if self.open_pdf is not None:
            self.open_pdf.close()
            self.open_pdf = None
            self.img_object_li.clear()
            self.tkimg_object_li.clear()
            self.frame.destroy()

    def pdf_view(self, master, width=1200, height=600, pdf_location="", bar=False, load="after", dpi=100):
        self.frame = tk.Frame(master, width=width, height=height, bg="white")
        header_frame = tk.Frame(self.frame, bg=Colors().secondaryColor)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        close_button = tk.Button(header_frame, text="×", font=FontTheme().closeX,
                                 bg=Colors().secondaryColor, fg="black", bd=0, padx=20, pady=10,
                                 command=lambda: self._close_toplevel(master))
        close_button.pack(side=tk.RIGHT)
        scroll_y = ttk.Scrollbar(self.frame, orient="vertical")
        scroll_y.pack(fill="y", side="right")

        percentage_load = tk.StringVar()
        if bar == True and load == "after":
            self.display_msg = ttk.Label(textvariable=percentage_load)
            self.display_msg.pack(pady=10)
            loading = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
            loading.pack(side=tk.TOP, fill=tk.X)

        self.text = tk.Text(self.frame, yscrollcommand=scroll_y.set, width=width, height=height)

        # Configure text widget to minimize padding
        self.text.configure(spacing1=0, spacing2=0, spacing3=0, padx=0, pady=0)

        self.text.pack(fill="x")
        scroll_y.config(command=self.text.yview)

        # Add drag scroll functionality for touchscreen
        self.prev_y = 0
        self.dragging = False

        def on_press(event):
            # Record the position when user first presses
            self.prev_y = event.y
            self.dragging = True
            # Change cursor to indicate dragging is possible
            self.text.config(cursor="fleur")

        def on_drag(event):
            if not self.dragging:
                return

            # Calculate how far we've moved
            delta_y = self.prev_y - event.y

            # Update position for next event
            self.prev_y = event.y

            # Instead of using units, use fractions for more precise control
            # Get current view positions
            y_fraction = self.text.yview()

            # Calculate new positions - adjust these multipliers to control sensitivity
            # Using very small values for smooth scrolling
            new_y_fraction = y_fraction[0] + (delta_y * 0.002)

            # Apply the new positions
            self.text.yview_moveto(new_y_fraction)

        def on_release(event):
            # Stop dragging
            self.dragging = False
            # Reset cursor
            self.text.config(cursor="")

        # Bind touch/drag events to the text widget
        self.text.bind("<ButtonPress-1>", on_press)
        self.text.bind("<B1-Motion>", on_drag)
        self.text.bind("<ButtonRelease-1>", on_release)

        # Method to add media from the PDF
        def add_img():
            percentage_view = 0
            self.close_pdf()  # Close the previously opened PDF if any
            self.open_pdf = fitz.open(pdf_location)
            total_pages = len(self.open_pdf)

            for i, page in enumerate(self.open_pdf):
                pix = page.get_pixmap(dpi=dpi)
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                self.img_object_li.append(img)
                self.tkimg_object_li.append(ImageTk.PhotoImage(img))

                if bar and load == "after":
                    percentage_view += 1
                    percentage_load.set(
                        f"Please wait!, your pdf is loading {int(math.floor(percentage_view * 100 / total_pages))}%")
                    loading['value'] = percentage_view * 100 / total_pages

            if bar and load == "after":
                loading.pack_forget()
                self.display_msg.pack_forget()

            # Insert all images with minimal spacing
            for i, im in enumerate(self.tkimg_object_li):
                self.text.image_create(tk.END, image=im)

                # Only add a very small space between pages, not at the end
                if i < len(self.tkimg_object_li) - 1:
                    # Create a thin separator line instead of a full line break
                    self.text.insert(tk.END, "\n")

                    # Calculate appropriate line length based on widget width
                    # Get current width in pixels and convert to approximate characters
                    widget_width = self.text.winfo_width()
                    # Use a divisor that approximates the width of the "─" character
                    # Typical char width is around 7-10 pixels depending on font
                    char_count = max(50, widget_width // 8)  # Minimum 50 chars, adjust divisor as needed

                    self.text.insert(tk.END, "─" * char_count)  # Dynamic horizontal line
                    self.text.insert(tk.END, "\n")

            self.text.configure(state="disabled")

        def start_pack():
            # Call add_img in the main thread
            master.after(0, add_img)

        if load == "after":
            master.after(250, start_pack)
        else:
            start_pack()

        return self.frame

    # Method to close the toplevel
    def _close_toplevel(self, window):
        self.close_pdf()
        if isinstance(window, tk.Toplevel):
            window.destroy()
        else:
            # If it's not a toplevel, find the toplevel parent
            parent = window.winfo_toplevel()
            if parent != window:  # Make sure we're not destroying the main window
                parent.destroy()