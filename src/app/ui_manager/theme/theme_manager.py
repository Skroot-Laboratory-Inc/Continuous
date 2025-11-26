from enum import Enum
from typing import Dict, Type

from src.app.ui_manager.theme.color_theme import ColorTheme, IBITheme, SkrootTheme, WilsonWolfTheme


class Theme(Enum):
    """ Theme options by default. These values correspond to folders present in resources/media"""
    IBI = "ibi"
    Skroot = "skroot"
    WW = "wilson-wolf"
    Default = "default"


class ThemeManager:
    """
    Singleton manager for application-wide theme management.

    Usage:
        # Get the theme manager instance
        theme_mgr = ThemeManager()

        # Get current theme
        theme = theme_mgr.get_theme()
        color = theme.header.background

        # Switch themes
        theme_mgr.set_theme('skroot')
        theme = theme_mgr.get_theme()  # Now returns SkrootTheme
    """

    _instance = None
    _current_theme: ColorTheme = None
    _current_theme_name: Theme = None
    _available_themes: Dict[str, Type[ColorTheme]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize with branded themes (Skroot is default)"""
        self._available_themes = {
            Theme.IBI.value: IBITheme,
            Theme.Skroot.value: SkrootTheme,
            Theme.WW.value: WilsonWolfTheme,
            Theme.Default.value: SkrootTheme,
        }
        self._current_theme_name = Theme.Default
        self._current_theme = SkrootTheme()

    def get_theme(self) -> ColorTheme:
        """Get the current active theme"""
        return self._current_theme

    def get_theme_name(self) -> str:
        return self._current_theme_name.value

    def set_theme(self, theme_name: Theme) -> None:
        """
        Set the active theme by name.

        Args:
            theme_name: Name of registered theme ('ibi', 'skroot', 'wilson-wolf', 'default')

        Raises:
            ValueError: If theme_name is not registered
        """
        if theme_name.value not in self._available_themes:
            available = ', '.join(self._available_themes.keys())
            raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")

        theme_class = self._available_themes[theme_name.value]
        self._current_theme = theme_class()
        self._current_theme_name = theme_name

    def get_available_themes(self) -> list:
        """Get list of all registered theme names"""
        return list(self._available_themes.keys())


# Convenience functions for quick access
def get_current_theme() -> ColorTheme:
    """Convenience function to get current theme without instantiating ThemeManager"""
    return ThemeManager().get_theme()


def get_current_theme_name() -> str:
    """Convenience function to get current theme name without instantiating ThemeManager"""
    return ThemeManager().get_theme_name()
