from typing import Dict, Type
from src.app.ui_manager.theme.color_theme import ColorTheme, IBITheme, SkrootTheme, WilsonWolfTheme


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

        # Register custom theme
        theme_mgr.register_theme('custom', MyCustomTheme)
        theme_mgr.set_theme('custom')
    """

    _instance = None
    _current_theme: ColorTheme = None
    _available_themes: Dict[str, Type[ColorTheme]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize with branded themes (Skroot is default)"""
        self._available_themes = {
            'ibi': IBITheme,
            'skroot': SkrootTheme,
            'wilson-wolf': WilsonWolfTheme,
            'default': SkrootTheme,
        }
        self._current_theme = SkrootTheme()

    def get_theme(self) -> ColorTheme:
        """Get the current active theme"""
        return self._current_theme

    def set_theme(self, theme_name: str) -> None:
        """
        Set the active theme by name.

        Args:
            theme_name: Name of registered theme ('ibi', 'skroot', 'wilson-wolf', 'default')

        Raises:
            ValueError: If theme_name is not registered
        """
        if theme_name not in self._available_themes:
            available = ', '.join(self._available_themes.keys())
            raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")

        theme_class = self._available_themes[theme_name]
        self._current_theme = theme_class()

    def register_theme(self, name: str, theme_class: Type[ColorTheme]) -> None:
        """
        Register a custom theme class.

        Args:
            name: Name to register the theme under
            theme_class: ColorTheme subclass to register
        """
        if not issubclass(theme_class, ColorTheme):
            raise TypeError(f"theme_class must be a subclass of ColorTheme")

        self._available_themes[name] = theme_class

    def get_available_themes(self) -> list:
        """Get list of all registered theme names"""
        return list(self._available_themes.keys())

    def create_custom_theme(self, name: str, **widget_colors) -> None:
        """
        Create and register a custom theme from widget color specifications.

        Args:
            name: Name for the custom theme
            **widget_colors: Keyword arguments for each widget type
                            e.g., header={'background': '#FF0000'}, buttons={'text': '#FFFFFF'}

        Example:
            theme_mgr.create_custom_theme(
                'my_theme',
                header={'background': '#FF0000', 'text': '#FFFFFF'},
                buttons={'background': '#00FF00', 'text': '#000000'}
            )
        """
        from src.app.ui_manager.theme.color_theme import (
            HeaderColors, BodyColors, ButtonColors, PlotColors, StatusColors, InputColors
        )

        class CustomTheme(ColorTheme):
            def __init__(self):
                super().__init__()
                # Override each specified widget color group
                if 'header' in widget_colors:
                    self.header = HeaderColors(**widget_colors['header'])
                if 'body' in widget_colors:
                    self.body = BodyColors(**widget_colors['body'])
                if 'buttons' in widget_colors:
                    self.buttons = ButtonColors(**widget_colors['buttons'])
                if 'plot' in widget_colors:
                    self.plot = PlotColors(**widget_colors['plot'])
                if 'status' in widget_colors:
                    self.status = StatusColors(**widget_colors['status'])
                if 'inputs' in widget_colors:
                    self.inputs = InputColors(**widget_colors['inputs'])
                if 'keyboard' in widget_colors:
                    self.keyboard = InputColors(**widget_colors['keyboard'])

        self.register_theme(name, CustomTheme)


# Convenience function for quick access
def get_current_theme() -> ColorTheme:
    """Convenience function to get current theme without instantiating ThemeManager"""
    return ThemeManager().get_theme()
