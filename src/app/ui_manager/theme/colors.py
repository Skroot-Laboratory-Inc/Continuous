"""
Colors class that delegates to ThemeManager for dynamic theming.

Usage:
    colors = Colors()
    header_bg = colors.header.background
    button_hover = colors.buttons.hover
    plot_grid = colors.plot.gridlines

Theme switching:
    ThemeManager().set_theme('skroot')
    # All Colors() instances automatically update
"""
from src.app.ui_manager.theme.theme_manager import get_current_theme


class Colors:
    """
    Colors class that delegates to the current theme.

    Provides access to widget-specific color groups that automatically
    reflect the currently active theme from ThemeManager.
    """

    def __init__(self):
        self._get_theme = get_current_theme

    @property
    def header(self):
        """Header widget colors (background, text, border)"""
        return get_current_theme().header

    @property
    def keyboard(self):
        """Header widget colors (background, text, border)"""
        return get_current_theme().keyboard

    @property
    def body(self):
        """Body widget colors (background, text, secondary_background)"""
        return get_current_theme().body

    @property
    def buttons(self):
        """Button widget colors (background, text, hover, disabled, border)"""
        return get_current_theme().buttons

    @property
    def plot(self):
        """Plot widget colors (gridlines, axes, lines, points, background, toggle_button)"""
        return get_current_theme().plot

    @property
    def status(self):
        """Status indicator colors (error, warning, success, info)"""
        return get_current_theme().status

    @property
    def inputs(self):
        """Input widget colors (background, text, border, focus_border, disabled)"""
        return get_current_theme().inputs

    @property
    def reportLabPrimary(self):
        """ReportLab primary color for PDF generation"""
        return get_current_theme().reportLabPrimary

    @property
    def reportLabLightPrimary(self):
        """ReportLab light primary color for PDF generation"""
        return get_current_theme().reportLabLightPrimary
