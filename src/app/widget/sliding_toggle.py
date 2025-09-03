import tkinter as tk
from tkinter import PhotoImage
from reactivex.subject import BehaviorSubject

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.theme.colors import Colors


class ToggleSwitch:
    def __init__(self, parent, behavior_subject: BehaviorSubject):
        """
        Create a toggle switch widget that works exclusively with ReactiveX BehaviorSubject

        Args:
            parent: The parent tkinter widget
            behavior_subject: ReactiveX BehaviorSubject that will receive toggle state changes
        """
        self.parent = parent
        self.behavior_subject = behavior_subject

        self.is_on = behavior_subject.value if hasattr(behavior_subject, 'value') else False
        self.on_image = PhotoImage(file=CommonFileManager().getSwitchOn())
        self.off_image = PhotoImage(file=CommonFileManager().getSwitchOff())

        initial_image = self.on_image if self.is_on else self.off_image
        self.button = tk.Button(
            parent,
            image=initial_image,
            bd=0,
            command=self._switch,
            highlightthickness=0,
            activebackground=Colors().secondaryColor,
            bg=Colors().secondaryColor
        )

        self._subscription = self.behavior_subject.subscribe(self._on_external_state_change)

    def _switch(self):
        """Internal method to handle the switch toggle - publishes to BehaviorSubject"""
        self.is_on = not self.is_on
        self._update_visual_state()
        self.behavior_subject.on_next(self.is_on)

    def _on_external_state_change(self, new_state: bool):
        """Handle external state changes from the BehaviorSubject"""
        if new_state != self.is_on:
            self.is_on = new_state
            self._update_visual_state()

    def _update_visual_state(self):
        """Update the button's visual appearance based on current state"""
        if self.is_on:
            self.button.config(image=self.on_image)
        else:
            self.button.config(image=self.off_image)

    def getWidget(self):
        """Get the underlying tkinter Button widget"""
        return self.button

    def get_state(self):
        """Get the current state of the toggle"""
        return self.is_on

    def set_state(self, state: bool):
        """
        Set the state of the toggle programmatically
        This will publish to the BehaviorSubject, maintaining reactive consistency
        """
        if state != self.is_on:
            self.behavior_subject.on_next(state)
            # Visual update will happen via the subscription

    def cleanup(self):
        """Clean up the subscription when done"""
        if hasattr(self, '_subscription'):
            self._subscription.dispose()

    def __del__(self):
        """Ensure cleanup happens"""
        self.cleanup()
