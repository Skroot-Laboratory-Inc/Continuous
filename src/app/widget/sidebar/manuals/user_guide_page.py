from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.sidebar.manuals.tkinterPdfViewer import ShowPdf


class UserGuidePage:
    def __init__(self, rootManager: RootManager):
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(pady=0, padx=10)
        self.RootManager = rootManager
        self.Fonts = FontTheme()
        self.Colors = Colors()
        self.windowRoot.geometry(f"{self.RootManager.getRoot().winfo_screenwidth()}x{self.RootManager.getRoot().winfo_screenheight()}")
        # Decrease the dpi to zoom in on the PDF
        ShowPdf().pdf_view(
            self.windowRoot, pdf_location=CommonFileManager().userGuideDoc
        ).pack(pady=10)
        self.RootManager.waitForWindow(self.windowRoot)
