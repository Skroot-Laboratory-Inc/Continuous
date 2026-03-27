import platform
import tkinter as tk

from src.resources.version.version import UseCase, Version


class ProductSelectionDialog:
    """First-launch dialog that prompts the user to select a product type.
    On Linux, writes the selection to device_config.json for all future launches.
    On Windows, the selection is kept in memory only for the current session."""

    def __init__(self):
        self.selected_use_case = None
        self.isWindows = platform.system() == "Windows"
        self.displayNames = {
            UseCase.WWContinuous: "WW Continuous",
            UseCase.SkrootContinuous: "Skroot Continuous",
            UseCase.FlowCell: "FlowCell",
            UseCase.SkrootFlowCell: "Skroot FlowCell",
            UseCase.Tunair: "Tunair",
            UseCase.RollerBottle: "Roller Bottle",
        }

    def show(self) -> UseCase:
        """Show the product selection dialog. Blocks until a selection is made.
        Returns the selected UseCase."""
        root = tk.Tk()
        root.title("Product Selection")
        root.configure(bg="#f0f0f0")

        window_width, window_height = 400, 380
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.resizable(False, False)

        header = tk.Label(
            root, text="Select Product Type",
            font=("TkDefaultFont", 16, "bold"), bg="#f0f0f0", pady=20
        )
        header.pack()

        if self.isWindows:
            subtitleText = "This selection applies to the current session only."
        else:
            subtitleText = "This selection will be saved for future launches."

        subtitle = tk.Label(
            root, text=subtitleText,
            font=("TkDefaultFont", 10), bg="#f0f0f0", fg="#666666"
        )
        subtitle.pack()

        button_frame = tk.Frame(root, bg="#f0f0f0", pady=15)
        button_frame.pack(fill="both", expand=True)

        def on_select(use_case):
            self.selected_use_case = use_case
            root.destroy()

        for use_case in UseCase:
            display_name = self.displayNames.get(use_case, use_case.value)
            btn = tk.Button(
                button_frame, text=display_name,
                font=("TkDefaultFont", 12), width=30, pady=8,
                command=lambda uc=use_case: on_select(uc)
            )
            btn.pack(pady=4)

        root.protocol("WM_DELETE_WINDOW", lambda: None)
        root.mainloop()

        return self.selected_use_case


def prompt_product_selection() -> UseCase:
    """Show product selection dialog and return the UseCase.
    On Linux, persists the choice to device_config.json.
    On Windows, stores the choice in memory only for the current session."""
    dialog = ProductSelectionDialog()
    use_case = dialog.show()
    if use_case is None:
        raise SystemExit("No product type selected. Exiting.")
    if platform.system() == "Windows":
        Version.setInMemoryUseCase(use_case)
    else:
        Version.setDeviceUseCase(use_case)
    return use_case
