import datetime
import platform
from tkinter import ttk

import tkcalendar
from dateutil.relativedelta import relativedelta
from tkcalendar import Calendar

from src.app.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.helper_methods.ui_helpers import centerWindowOnFrame
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme


class DateRangePicker:
    def __init__(self, rootManager: RootManager):
        self.now = datetime.datetime.now()
        self.startDate: datetime.datetime.date = None
        self.endDate: datetime.datetime.date = None
        self.cancelled = False
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.withdraw()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.startDateEntry = self.createStartDate()
        self.endDateEntry = self.createEndDate()
        self.downloadButton = self.createSubmitButton()
        self.cancelButton = self.createCancelButton()

        self.windowRoot.update_idletasks()
        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        self.windowRoot.deiconify()
        rootManager.waitForWindow(self.windowRoot)
        if self.cancelled:
            raise UserConfirmationException

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Export Date Range",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew',
                                                                 pady=10)

    def createStartDate(self):
        ttk.Label(
            self.windowRoot,
            text="Start Date",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=3, column=0)

        startDateCalendar = Calendar(self.windowRoot,
                                     foreground=Colors().secondaryColor,
                                     background=Colors().primaryColor,
                                     font="Helvetica 24",
                                     year=self.now.year - 1,
                                     month=self.now.month,
                                     day=self.now.day,
                                     headersbackground=Colors().lightPrimaryColor,
                                     headersforeground=Colors().secondaryColor,
                                     showweeknumbers=False,
                                     showothermonthdays=False,
                                     )
        startDateCalendar.update_idletasks()
        startDateCalendar.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
        prev_month_btn = ttk.Button(self.windowRoot,
                                    text="◀ Previous Month",
                                    style='Default.TButton',
                                    command=lambda: previousMonth(startDateCalendar))

        next_month_btn = ttk.Button(self.windowRoot,
                                    text="Next Month ▶",
                                    style='Default.TButton',
                                    command=lambda: nextMonth(startDateCalendar))
        prev_month_btn.grid(row=5, column=0, padx=5, pady=2, sticky="w")
        next_month_btn.grid(row=5, column=0, padx=5, pady=2, sticky="e")
        return startDateCalendar

    def createEndDate(self):
        ttk.Label(
            self.windowRoot,
            text="End Date",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=3, column=1)

        endDateCalendar = Calendar(self.windowRoot,
                                   foreground=Colors().secondaryColor,
                                   background=Colors().primaryColor,
                                   font="Helvetica 24",
                                   year=self.now.year,
                                   month=self.now.month,
                                   day=self.now.day,
                                   headersbackground=Colors().lightPrimaryColor,
                                   headersforeground=Colors().secondaryColor,
                                   showweeknumbers=False,
                                   showothermonthdays=False,
                                   )
        endDateCalendar.update_idletasks()
        endDateCalendar.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
        prev_month_btn = ttk.Button(self.windowRoot,
                                    text="◀ Previous Month",
                                    style='Default.TButton',
                                    command=lambda: previousMonth(endDateCalendar))
        next_month_btn = ttk.Button(self.windowRoot,
                                    text="Next Month ▶",
                                    style='Default.TButton',
                                    command=lambda: nextMonth(endDateCalendar))

        prev_month_btn.grid(row=5, column=1, padx=5, pady=2, sticky="w")
        next_month_btn.grid(row=5, column=1, padx=5, pady=2, sticky="e")
        return endDateCalendar

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.confirmDates).button
        submitButton.grid(row=6, column=1, pady=20, columnspan=2, sticky="e")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=6, column=0, pady=20, sticky="w")
        return cancelButton

    def cancel(self):
        self.cancelled = True
        self.windowRoot.destroy()

    def confirmDates(self):
        self.startDate = self.startDateEntry.selection_get()
        self.endDate = self.endDateEntry.selection_get()
        self.windowRoot.destroy()


def nextMonth(cal: tkcalendar.Calendar):
    month, year = cal.get_displayed_month()
    cal.see(datetime.date(month=month, year=year, day=15) + relativedelta(months=1))


def previousMonth(cal: tkcalendar.Calendar):
    month, year = cal.get_displayed_month()
    cal.see(datetime.date(month=month, year=year, day=15) - relativedelta(months=1))
