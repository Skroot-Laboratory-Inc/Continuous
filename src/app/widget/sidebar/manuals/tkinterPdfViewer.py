import math
import tkinter as tk
from tkinter import ttk

import fitz
from PIL import Image, ImageTk

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme


class ShowPdf:
    """
    Embeds a PDF into a tkinter frame. By default, trims off 0.8 inches from all sides of the page.
    """
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

    def pdf_view(self, master, width=1200, height=600, pdf_location="", bar=False, load="after", dpi=170,
                 # New margin parameters
                 crop_margins=True, crop_left=80, crop_right=80, crop_top=80, crop_bottom=80,
                 add_padding=False, pad_left=20, pad_right=20, pad_top=20, pad_bottom=20,
                 page_margin=0):
        """
        PDF Viewer with manual margin control

        Parameters:
        - crop_margins: Whether to crop existing margins from PDF
        - crop_left/right/top/bottom: Pixels to crop from each side
        - add_padding: Whether to add custom padding around pages
        - pad_left/right/top/bottom: Pixels of padding to add
        - page_margin: Margin between pages
        """

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

        # Method to process image margins
        def process_image_margins(img):
            """Apply cropping and padding to the image"""
            processed_img = img

            # Step 1: Crop margins if requested
            if crop_margins:
                width, height = processed_img.size
                left = max(0, crop_left)
                top = max(0, crop_top)
                right = max(left + 1, width - crop_right)
                bottom = max(top + 1, height - crop_bottom)

                # Ensure we don't crop more than the image size
                right = min(right, width)
                bottom = min(bottom, height)

                if left < right and top < bottom:
                    processed_img = processed_img.crop((left, top, right, bottom))

            # Step 2: Add padding if requested
            if add_padding:
                old_width, old_height = processed_img.size
                new_width = old_width + pad_left + pad_right
                new_height = old_height + pad_top + pad_bottom

                # Create new image with padding
                padded_img = Image.new(processed_img.mode, (new_width, new_height), "white")
                padded_img.paste(processed_img, (pad_left, pad_top))
                processed_img = padded_img

            return processed_img

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

                # Process margins
                processed_img = process_image_margins(img)

                self.img_object_li.append(processed_img)
                self.tkimg_object_li.append(ImageTk.PhotoImage(processed_img))

                if bar and load == "after":
                    percentage_view += 1
                    percentage_load.set(
                        f"Please wait!, your pdf is loading {int(math.floor(percentage_view * 100 / total_pages))}%")
                    loading['value'] = percentage_view * 100 / total_pages

            if bar and load == "after":
                loading.pack_forget()
                self.display_msg.pack_forget()

            # Insert all images with custom spacing
            for i, im in enumerate(self.tkimg_object_li):
                self.text.image_create(tk.END, image=im)

                # Add custom margin between pages
                if i < len(self.tkimg_object_li) - 1:
                    # Add specified number of newlines for page margin
                    margin_lines = max(1, page_margin // 10)  # Convert pixels to approximate lines
                    self.text.insert(tk.END, "\n" * margin_lines)

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