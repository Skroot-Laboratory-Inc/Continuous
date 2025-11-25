"""
Theme module Skroot applications.

Provides flexible color theming organized by widget type
"""

# Main theme classes
from src.app.ui_manager.theme.color_theme import (
    ColorTheme,
    IBITheme,
    SkrootTheme,
    WilsonWolfTheme,
)

# Colors class
from src.app.ui_manager.theme.colors import Colors

# Widget-specific color classes
from src.app.ui_manager.theme.color_theme import (
    WidgetColors,
    HeaderColors,
    BodyColors,
    ButtonColors,
    PlotColors,
    StatusColors,
    InputColors,
)

# Theme management
from src.app.ui_manager.theme.theme_manager import (
    ThemeManager,
    get_current_theme,
)

__all__ = [
    # Main themes
    'ColorTheme',
    'IBITheme',
    'SkrootTheme',
    'WilsonWolfTheme',
    'Colors',  # Legacy alias

    # Widget color classes
    'WidgetColors',
    'HeaderColors',
    'BodyColors',
    'ButtonColors',
    'PlotColors',
    'StatusColors',
    'InputColors',

    # Theme manager
    'ThemeManager',
    'get_current_theme',
]
