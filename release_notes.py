import tkinter as tk
import tkinter.ttk as ttk


class ReleaseNotes:
    def __init__(self, releaseNotes, root):
        self.releaseNotes = releaseNotes
        self.windowRoot = tk.Toplevel(root, bg='white', borderwidth=0, pady=25, padx=25)
        self.windowRoot.maxsize(width=450, height=550)
        scrollbar = tk.Scrollbar(self.windowRoot, orient=tk.VERTICAL)
        self.windowCanvas = tk.Canvas(
            self.windowRoot, bg='white', yscrollcommand=scrollbar.set, width=400, height=500, borderwidth=0,
            highlightthickness=0
        )
        self.window = tk.Frame(self.windowRoot, bg='white', borderwidth=0)
        self.windowCanvas.create_window(0, 0, anchor="nw", window=self.window)
        row = self.fillInVersions()
        self.createDownloadAndCancelButtons(row)
        scrollbar.config(command=self.windowCanvas.yview)
        self.windowCanvas.grid(row=0, column=0, sticky="ns")
        self.windowCanvas.update()
        self.window.update()
        bounds = self.window.grid_bbox()
        self.windowCanvas.configure(scrollregion=(0, 0, bounds[2] + 25, bounds[3] + 25))
        scrollbar.grid(row=0, column=1, sticky="ns")
        scrollbar.update()
        self.windowCanvas.bind_all("<MouseWheel>", self.on_mousewheel)
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
                tk.Label(self.window, text=f"- {feature}", bg='white', font='Helvetica 10').grid(row=row, column=0,
                                                                                                 sticky='w')
                row += 1
            row = self.createSpacer(row)
        return row

    def createBugFixesSection(self, notes, row):
        if "bugfixes" in notes:
            tk.Label(self.window, text="Bug Fixes:", bg='white', font='Helvetica 10 bold').grid(row=row, column=0,
                                                                                                sticky='w')
            row += 1
            for index, bugfix in notes['bugfixes'].items():
                tk.Label(self.window, text=f"- {bugfix}", bg='white', font='Helvetica 10').grid(row=row, column=0,
                                                                                                sticky='w')
                row += 1
            row = self.createSpacer(row)
        return row

    def createDownloadAndCancelButtons(self, row):
        row = self.createSpacer(row)
        downloadButton = ttk.Button(self.window, text="Download", command=lambda: self.setDownload(True))
        downloadButton['style'] = 'W.TButton'
        downloadButton.grid(row=row, column=0, sticky='w')
        cancelButton = ttk.Button(self.window, text="Cancel", command=lambda: self.setDownload(False))
        cancelButton['style'] = 'W.TButton'
        cancelButton.grid(row=row, column=1, sticky='w')

    def setDownload(self, value):
        self.download = value
        self.windowRoot.destroy()

    def on_mousewheel(self, event):
        scroll = -1 if event.delta > 0 else 1
        self.windowCanvas.yview_scroll(scroll, "units")

    def createSpacer(self, row):
        tk.Label(self.window, text='', bg='white', font='Helvetica 10').grid(row=row, column=0, sticky='w')
        row += 1
        return row

    def createSeparatorLine(self, row):
        ttk.Separator(self.window, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew')
        row += 1
        return row

# root = tk.Tk()
# ReleaseNotes({
#     "v1.0.1": {
#         "features": {"1": "Updated inoculation to zero out y-axis",
#                      "2": "Updated plotting to use Skroot Growth Index (SGI)"},
#         "bugfixes": {"1": "Fixed AWS Integrations"}},
#     "v1.1.2": {
#         "features": {"1": "Updated inoculation to zero out y-axis",
#                      "2": "Updated plotting to use Skroot Growth Index (SGI)"},
#         "bugfixes": {"1": "Fixed AWS Integrations"}},
#     "v1.1.1": {
#         "features": {"1": "Updated inoculation to zero out y-axis",
#                      "2": "Updated plotting to use Skroot Growth Index (SGI)"},
#         "bugfixes": {"1": "Fixed AWS Integrations"}},
#     "v1.1.0": {
#         "features": {"1": "Updated inoculation to zero out y-axis",
#                      "2": "Updated plotting to use Skroot Growth Index (SGI)"},
#         "bugfixes": {"1": "Fixed AWS Integrations"}}}, root)
# root.mainloop()
