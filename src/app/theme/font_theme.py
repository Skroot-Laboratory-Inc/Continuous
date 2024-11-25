from tkinter import font


class FontTheme:
    def __init__(self):
        self.italicUnderline = font.Font(family='Helvetica', size=9, underline=True, slant="italic")
        self.footnote = font.Font(family='Helvetica', size=7, slant="italic")
        self.primary = font.Font(family='Helvetica', size=10)
        self.header1 = font.Font(family='Helvetica', size=14, weight="bold")
        self.header2 = font.Font(family='Helvetica', size=12, weight="bold")
        self.menubar = font.Font(family='Helvetica', size=15)
        self.header3 = font.Font(family='Helvetica', size=10, weight="bold")
        self.buttons = font.Font(family='Helvetica', size=9, weight="bold")
        self.setupFormText = font.Font(family='Helvetica', size=12)

