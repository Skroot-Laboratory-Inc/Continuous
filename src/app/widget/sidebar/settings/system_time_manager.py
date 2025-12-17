import datetime
import platform
import tkinter as tk
from tkinter import ttk

import tkcalendar
from dateutil.relativedelta import relativedelta
from tkcalendar import Calendar

from src.app.helper_methods.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.helper_methods.helper_functions import setDatetimeTimezone, getTimezone, getTimezoneOptions
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, createDropdown, launchKeyboard, formatPopup
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme


class SystemTimeManager:
    def __init__(self, rootManager: RootManager, user: str = ""):
        self.now = datetime.datetime.now()
        self.user = user
        self.date: datetime.datetime.date = self.now.date()
        self.hours = tk.StringVar(value=self.now.strftime("%I"))
        self.hours.trace('w', lambda *args: self.format_hours())
        self.minutes = tk.StringVar(value=self.now.strftime("%M"))
        self.minutes.trace('w', lambda *args: self.format_minutes())
        self.am_pm = tk.StringVar(value=self.now.strftime("%p"))
        self.timezone = tk.StringVar(value=getTimezone())
        self.ubuntu_timezone = "America/Chicago"
        self.cancelled = False
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.grid_columnconfigure(0, weight=0)
        self.windowRoot.grid_columnconfigure(1, weight=1)
        self.windowRoot.grid_columnconfigure(2, weight=0, minsize=200)
        self.windowRoot.grid_rowconfigure(2, weight=1, minsize=60)
        self.windowRoot.withdraw()
        formatPopup(self.windowRoot)
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.createTime(2)
        self.timezoneEntry = self.createTimezone(2)
        self.dateEntry = self.createAutomaticSyncNote(3)
        self.dateEntry = self.createDate(4)
        self.downloadButton = self.createSubmitButton(6)
        self.cancelButton = self.createCancelButton(6)

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
            text="Current Date and Time",
            font=FontTheme().header1,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createTime(self, row):
        timeFrame = tk.Frame(self.windowRoot, bg=Colors().body.background)
        hours = tk.Entry(
            timeFrame,
            width=3,
            font=FontTheme().primary,
            textvariable=self.hours,
            justify="center",
            borderwidth=0,
        )
        hours.bind("<Button-1>", lambda event: launchKeyboard(event.widget, self.RootManager.getRoot(), "Hours:  "))
        minutes = tk.Entry(
            timeFrame,
            width=3,
            font=FontTheme().primary,
            textvariable=self.minutes,
            justify="center",
            borderwidth=0,
        )
        minutes.bind("<Button-1>", lambda event: launchKeyboard(event.widget, self.RootManager.getRoot(), "Minutes:  "))
        am_pm = createDropdown(timeFrame, self.am_pm, ["AM", "PM"], addSpace=False)
        hours.grid(row=0, column=0, ipadx=WidgetTheme().internalPadding, sticky="nsew")
        ttk.Label(timeFrame, text=":", font=FontTheme().primary, background=Colors().body.background, foreground=Colors().body.text).grid(row=0, column=1, padx=10)
        minutes.grid(row=0, column=2, ipadx=WidgetTheme().internalPadding, sticky="nsew")
        am_pm.grid(row=0, column=3, padx=(5, 0))
        timeFrame.grid(row=row, column=0, columnspan=2, pady=WidgetTheme().externalPadding, sticky="nsew")

    def createTimezone(self, row):
        timezoneEntry = createDropdown(self.windowRoot, self.timezone, getTimezoneOptions(), addSpace=False)
        timezoneEntry.grid(row=row, column=2, pady=WidgetTheme().externalPadding, sticky="nsew")
        return timezoneEntry

    def createAutomaticSyncNote(self, row: int) -> ttk.Label:
        note = ttk.Label(
            self.windowRoot,
            text="Note: Only the timezone can be changed when internet is connected."
                 "\nTime and date are automatically synced.",
            font=FontTheme().warning,
            foreground=Colors().status.error,
            background=Colors().body.background)
        note.grid(row=row, column=0, columnspan=3, sticky="nsew")
        return note

    def createDate(self, row):
        calendar = Calendar(self.windowRoot,
                            foreground=Colors().body.background,
                            background=Colors().buttons.background,
                            font="Helvetica 24",
                            year=self.now.year,
                            month=self.now.month,
                            day=self.now.day,
                            headersbackground=Colors().buttons.hover,
                            headersforeground=Colors().body.background,
                            showweeknumbers=False,
                            showothermonthdays=False,
                            )
        calendar.update_idletasks()
        calendar.grid(row=row, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        prev_month_btn = ttk.Button(self.windowRoot,
                                    text="◀ Previous Month",
                                    style='Default.TButton',
                                    command=lambda: previousMonth(calendar))

        next_month_btn = ttk.Button(self.windowRoot,
                                    text="Next Month ▶",
                                    style='Default.TButton',
                                    command=lambda: nextMonth(calendar))
        prev_month_btn.grid(row=row + 1, column=0, padx=5, pady=2, sticky="w")
        next_month_btn.grid(row=row + 1, column=2, padx=5, pady=2, sticky="e")
        return calendar

    def createCancelButton(self, row):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=row, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def createSubmitButton(self, row):
        submitButton = GenericButton("Submit", self.windowRoot, self.submit).button
        submitButton.grid(row=row, column=2, pady=WidgetTheme().externalPadding, sticky="e")
        return submitButton

    def cancel(self):
        self.cancelled = True
        self.windowRoot.destroy()

    def submit(self):
        hours_12 = int(self.hours.get())
        minutes = int(self.minutes.get())
        am_pm = self.am_pm.get()
        if am_pm == "AM":
            hours_24 = hours_12 if hours_12 != 12 else 0
        else:
            hours_24 = hours_12 if hours_12 == 12 else hours_12 + 12

        self.date = datetime.datetime.combine(
            self.dateEntry.selection_get(),
            datetime.time(hours_24, minutes)
        )

        setDatetimeTimezone(self.date, self.timezone.get(), self.user)
        self.windowRoot.destroy()

    def format_hours(self):
        """Format hours to 2 digits when value changes"""
        value = self.hours.get()
        if value == "":
            return
        try:
            num_value = int(value)
            if 1 <= num_value <= 12:
                formatted = f"{num_value:01d}"
                if formatted != value:
                    self.hours.set(formatted)
            else:
                self.hours.set("12")
        except ValueError:
            self.hours.set("12")

    def format_minutes(self):
        """Format minutes to 2 digits when value changes"""
        value = self.minutes.get()
        if value == "":
            return
        try:
            num_value = int(value)
            if 0 <= num_value <= 59:
                formatted = f"{num_value:02d}"
                if formatted != value:
                    self.minutes.set(formatted)
            else:
                self.minutes.set("00")
        except ValueError:
            self.minutes.set("00")


def nextMonth(cal: tkcalendar.Calendar):
    month, year = cal.get_displayed_month()
    cal.see(datetime.date(month=month, year=year, day=15) + relativedelta(months=1))


def previousMonth(cal: tkcalendar.Calendar):
    month, year = cal.get_displayed_month()
    cal.see(datetime.date(month=month, year=year, day=15) - relativedelta(months=1))


if __name__ == "__main__":
    rootManager = RootManager()
    rootManager.setWindowSize()
    SystemTimeManager(rootManager)
    rootManager.callMainLoop()