import tkinter as tk
from abc import ABC, abstractmethod


class PopupInterface(ABC):

    @abstractmethod
    def fillOutWindowFn(self, window: tk.Frame):
        """ This populates the popup with whatever widgets are required. """
