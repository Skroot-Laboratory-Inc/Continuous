from typing import Dict
from reportlab.lib import colors as reportlab_colors


class WidgetColors:
    """Base class for widget-specific color definitions"""
    def to_dict(self) -> Dict[str, str]:
        """Convert color attributes to dictionary for easy iteration"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class HeaderColors(WidgetColors):
    """Colors for header elements (titles, section headers, etc.)"""

    def __init__(
            self,
            background='#0073A1',
            text='#FFFFFF',
            border='#000000'
    ):
        self.background = background
        self.text = text
        self.border = border


class BodyColors(WidgetColors):
    """Colors for body/content elements (labels, text areas, frames)"""

    def __init__(
            self,
            background='#FFFFFF',
            text='#000000',
            secondary_background='#F5F5F5'
    ):
        self.background = background
        self.text = text
        self.secondary_background = secondary_background


class ButtonColors(WidgetColors):
    """Colors for button elements"""

    def __init__(
            self,
            background='#0073A1',
            text='#FFFFFF',
            hover='#00AEEF',
            disabled='#CCCCCC',
            border='#000000'
    ):
        self.background = background
        self.text = text
        self.hover = hover
        self.disabled = disabled
        self.border = border


class PlotColors(WidgetColors):
    """Colors for plot/figure elements"""

    def __init__(
            self,
            gridlines='lightgray',
            axes='#000000',
            primary_line='#0073A1',
            secondary_line='#00AEEF',
            background='#FFFFFF',
            points='#0073A1',
            toggle_button='#0073A1',
            toggle_button_text='#FFFFFF'
    ):
        self.gridlines = gridlines
        self.axes = axes
        self.primary_line = primary_line
        self.secondary_line = secondary_line
        self.background = background
        self.points = points
        self.toggle_button = toggle_button
        self.toggle_button_text = toggle_button_text


class StatusColors(WidgetColors):
    """Colors for status indicators (error, warning, success, info)"""

    def __init__(
            self,
            error='#CD0000',
            warning='#FFFE71',
            success='#5CA904',
            info='#00AEEF',
            error_light='#FF474C'
    ):
        self.error = error
        self.warning = warning
        self.success = success
        self.info = info
        self.error_light = error_light


class InputColors(WidgetColors):
    """Colors for input elements (entry fields, dropdowns, etc.)"""

    def __init__(
            self,
            background='#FFFFFF',
            text='#000000',
            border='#CCCCCC',
            focus_border='#0073A1',
            disabled='#F5F5F5'
    ):
        self.background = background
        self.text = text
        self.border = border
        self.focus_border = focus_border
        self.disabled = disabled


class KeyboardColors(WidgetColors):
    """Colors for keyboard popup """

    def __init__(
            self,
            background='#C7C7CC',
            text='#000000',
            highlight='#4682B4',
            key='#F7F7F7',
            enter="#99ef6c",
            specialCharacters="#D1D1D6",
            specialCharactersFont="#000000",
    ):
        self.background = background
        self.text = text
        self.highlight = highlight
        self.key = key
        self.enter = enter
        self.specialCharacters = specialCharacters
        self.specialCharactersFont = specialCharactersFont


class ColorTheme:
    """
    Main color theme class organized by widget type.

    Usage:
        # New widget-based approach:
        theme = ColorTheme()
        header_bg = theme.header.background
        button_text = theme.buttons.text
        plot_grid = theme.plot.gridlines

        # Backward compatibility:
        old_primary = theme.primaryColor
        old_secondary = theme.secondaryColor
    """

    def __init__(self):
        self.header = HeaderColors()
        self.body = BodyColors()
        self.buttons = ButtonColors()
        self.plot = PlotColors()
        self.status = StatusColors()
        self.inputs = InputColors()
        self.keyboard = KeyboardColors()
        self.reportLabPrimary = reportlab_colors.Color(0.2, 0.3, 0.6)
        self.reportLabLightPrimary = reportlab_colors.Color(0.85, 0.9, 1)

    def get_widget_colors(self, widget_type: str) -> WidgetColors:
        """
        Get color group by widget type name.

        Args:
            widget_type: One of 'header', 'body', 'buttons', 'plot', 'status', 'inputs'

        Returns:
            WidgetColors subclass instance

        Raises:
            AttributeError: If widget_type doesn't exist
        """
        return getattr(self, widget_type)


class IBITheme(ColorTheme):
    def __init__(self):
        super().__init__()
        self.header = HeaderColors(
            background='#232323',
            text='#FFFFFF',
            border='#CCCCCC'
        )
        self.buttons = ButtonColors(
            background='#f7941d',
            text='#232323',
            hover='#F7A947',
            disabled='#CCCCCC',
            border='#232323'
        )
        self.plot = PlotColors(
            gridlines='lightgray',
            axes='#000000',
            primary_line='#f7941d',
            secondary_line='#F7A947',
            background='#000000',
            points='#f7941d',
            toggle_button='#f7941d',
            toggle_button_text='#000000'
        )
        self.inputs = InputColors(
            background='#f7941d',
            text='#FFFFFF',
            border='#CCCCCC',
            focus_border='#f7941d',
            disabled='#F5F5F5'
        )
        self.body = BodyColors(
            background='#232323',
            text='#FFFFFF'
        )
        self.keyboard = KeyboardColors(
            background='#232323',
            text='#FFFFFF',
            highlight='#F7A947',
            key='#464646',
            enter='#555D50',
            specialCharacters='#575757',
            specialCharactersFont='#FFFFFF'
        )
        self.reportLabPrimary = reportlab_colors.Color(0.2, 0.3, 0.6)
        self.reportLabLightPrimary = reportlab_colors.Color(0.85, 0.9, 1)


class SkrootTheme(ColorTheme):
    def __init__(self):
        super().__init__()
        self.header = HeaderColors(
            background='#203864',
            text='#FFFFFF',
            border='#000000'
        )
        self.buttons = ButtonColors(
            background='#203864',
            text='#FFFFFF',
            hover='#3B537F',
            disabled='#CCCCCC',
            border='#000000'
        )
        self.plot = PlotColors(
            gridlines='lightgray',
            axes='#000000',
            primary_line='#203864',
            secondary_line='#3B537F',
            background='#FFFFFF',
            points='#203864',
            toggle_button='#203864',
            toggle_button_text='#FFFFFF'
        )
        self.inputs = InputColors(
            background='#FFFFFF',
            text='#000000',
            border='#CCCCCC',
            focus_border='#203864',
            disabled='#F5F5F5'
        )
        self.reportLabPrimary = reportlab_colors.Color(0.2, 0.3, 0.6)
        self.reportLabLightPrimary = reportlab_colors.Color(0.85, 0.9, 1)


class WilsonWolfTheme(ColorTheme):
    def __init__(self):
        super().__init__()
        self.header = HeaderColors(
            background='#008876',
            text='#FFFFFF',
            border='#000000'
        )
        self.buttons = ButtonColors(
            background='#008876',
            text='#FFFFFF',
            hover='#0a6b5d',
            disabled='#CCCCCC',
            border='#000000'
        )
        self.plot = PlotColors(
            gridlines='lightgray',
            axes='#000000',
            primary_line='#008876',
            secondary_line='#0a6b5d',
            background='#FFFFFF',
            points='#008876',
            toggle_button='#008876',
            toggle_button_text='#FFFFFF'
        )
        self.inputs = InputColors(
            background='#FFFFFF',
            text='#000000',
            border='#CCCCCC',
            focus_border='#008876',
            disabled='#F5F5F5'
        )
        self.reportLabPrimary = reportlab_colors.Color(0, 0.533, 0.463)
        self.reportLabLightPrimary = reportlab_colors.Color(0.9, 0.97, 0.95)
