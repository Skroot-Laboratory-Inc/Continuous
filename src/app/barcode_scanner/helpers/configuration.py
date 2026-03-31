import tkinter as tk

from src.app.barcode_scanner.helpers.constants import BarcodeConstants
from src.app.helper_methods.helper_functions import setBoolEnvFlag, getBoolEnvFlag
from src.app.properties.dev_properties import DevProperties


class BarcodeConfiguration:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if not DevProperties().isDevMode:
                initialValue = getBoolEnvFlag(
                    BarcodeConstants().barcodeConfiguration,
                    BarcodeConstants().defaultBarcode,
                )
            else:
                initialValue = DevProperties().barcodeEnabled
            cls._instance.barcodeEnabled = tk.BooleanVar(value=initialValue)
            cls._instance.barcodeEnabled.trace_add("write", cls._instance.setConfig)
        return cls._instance

    def setConfig(self, *args):
        setBoolEnvFlag(BarcodeConstants().barcodeConfiguration, self.barcodeEnabled.get())

    def getConfig(self):
        return self.barcodeEnabled.get()
