from tkinter import font


class FontTheme:
    def __init__(self):
        self.italicUnderline = font.Font(family='Helvetica', size=9, underline=True, slant="italic")
        self.footnote = font.Font(family='Helvetica', size=7, slant="italic")
        self.warning = font.Font(family='Helvetica', size=10, slant="italic")
        self.textNotification = font.Font(family='Helvetica', size=16)
        self.header1 = font.Font(family='Helvetica', size=22, weight="bold")
        self.header2 = font.Font(family='Helvetica', size=18, weight="bold")
        self.header3 = font.Font(family='Helvetica', size=16, weight="bold")
        self.buttons = font.Font(family='Helvetica', size=15, weight="bold")
        self.closeX = font.Font(family='Helvetica', size=40, weight="bold")
        self.menubar = font.Font(family='Helvetica', size=15)
        self.primary = font.Font(family='Helvetica', size=20)
        self.primaryBoldUnderlined = font.Font(family='Helvetica', size=20, weight="bold", underline=True)
        self.primary2 = font.Font(family='Helvetica', size=14)
        self.dropdown = font.Font(family='Helvetica', size=20)
        self.setupFormText = font.Font(family='Helvetica', size=18)
