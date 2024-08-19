import tkinter as tk
import tkinter.ttk as ttk
from distutils.version import StrictVersion


class ReleaseNotes:
    def __init__(self, releaseNotes, root):
        self.releaseNotes = sortNotes(releaseNotes)
        self.windowRoot = tk.Toplevel(root, bg='white', borderwidth=0, pady=25, padx=25)
        self.windowRoot.minsize(width=650, height=550)
        self.windowRoot.maxsize(width=800, height=550)
        self.windowCanvas = tk.Canvas(
            self.windowRoot, bg='white', borderwidth=0,
            highlightthickness=0
        )
        self.window = tk.Frame(self.windowRoot, bg='white', borderwidth=0)
        self.windowCanvas.create_window(0, 0, anchor="nw", window=self.window)
        # Linux uses Button-5 for scroll down and Button-4 for scroll up
        self.window.bind_all('<Button-4>', lambda e: self.windowCanvas.yview_scroll(int(-1 * e.num), 'units'))
        self.window.bind_all('<Button-5>', lambda e: self.windowCanvas.yview_scroll(int(e.num), 'units'))
        # Windows uses MouseWheel for scrolling
        self.window.bind_all('<MouseWheel>', lambda e: self.windowCanvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        row = self.fillInVersions()
        self.createDownloadAndCancelButtons(row)
        self.windowCanvas.grid(row=0, column=0, sticky="ns")
        self.windowCanvas.update()
        self.window.update()
        bounds = self.window.grid_bbox()
        self.windowCanvas.configure(scrollregion=(0, 0, bounds[2] + 25, bounds[3] + 25))
        self.download = False
        root.wait_window(self.windowCanvas)

    def fillInVersions(self):
        row = 0
        tk.Label(self.window, text="Release Notes", bg='white', font='Helvetica 14 bold').grid(row=row, column=0,
                                                                                               sticky='w')
        row += 1
        row = self.createSeparatorLine(row)
        for version, notes in self.releaseNotes.items():
            tk.Label(self.window, text=version, bg='white', font='Helvetica 12 bold').grid(row=row, column=0,
                                                                                           sticky='w')
            row += 1
            row = self.createFeaturesSection(notes, row)
            row = self.createBugFixesSection(notes, row)
            row = self.createSeparatorLine(row)
        return row

    def createFeaturesSection(self, notes, row):
        if "features" in notes:
            tk.Label(self.window, text="New Features:", bg='white', font='Helvetica 10 bold').grid(row=row,
                                                                                                   column=0,
                                                                                                   sticky='w')
            row += 1
            for index, feature in notes['features'].items():
                (tk.Label(self.window, text=f"- {feature}", bg='white', font='Helvetica 10', wraplength=500, justify="left")
                 .grid(row=row, column=0, sticky='w'))
                row += 1
            row = self.createSpacer(row)
        return row

    def createBugFixesSection(self, notes, row):
        if "bugfixes" in notes:
            tk.Label(self.window, text="Bug Fixes:", bg='white', font='Helvetica 10 bold').grid(row=row, column=0,
                                                                                                sticky='w')
            row += 1
            for index, bugfix in notes['bugfixes'].items():
                (tk.Label(self.window, text=f"- {bugfix}", bg='white', font='Helvetica 10', wraplength=500, justify="left")
                 .grid(row=row, column=0,sticky='w'))
                row += 1
            row = self.createSpacer(row)
        return row

    def createDownloadAndCancelButtons(self, row):
        row = self.createSpacer(row)
        downloadButton = ttk.Button(self.window, text="Download", command=lambda: self.setDownload(True), style='W.TButton')
        downloadButton.grid(row=row, column=0, sticky='w')
        cancelButton = ttk.Button(self.window, text="Cancel", command=lambda: self.setDownload(False), style='W.TButton')
        cancelButton.grid(row=row, column=1, sticky='w')

    def setDownload(self, value):
        self.download = value
        self.windowRoot.destroy()

    def createSpacer(self, row):
        tk.Label(self.window, text='', bg='white', font='Helvetica 10').grid(row=row, column=0, sticky='w')
        row += 1
        return row

    def createSeparatorLine(self, row):
        ttk.Separator(self.window, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew')
        row += 1
        return row

def sortNotes(releaseNotes):
    keys = list(releaseNotes.keys())
    keysWithoutV = [k[1:] for k in keys]
    keysWithoutV.sort(key=StrictVersion)
    keys = keysWithoutV[::-1]
    return {f'v{i}': releaseNotes[f'v{i}'] for i in keys}
