from threading import Timer
from typing import Callable, Optional


class SignOutTimer:
    def __init__(self, duration: float, signOutFn: Callable):
        self.duration = duration
        self.signOutFn = signOutFn
        self.timer: Optional[Timer] = None
        self.isRunning = False

    def start(self):
        self.isRunning = True
        self.timer = Timer(self.duration, self._executeSignOut)
        self.timer.start()

    def refresh(self):
        if self.isRunning:
            self.timer.cancel()
            self.timer = Timer(self.duration, self._executeSignOut)
            self.timer.start()

    def stop(self):
        if self.isRunning and self.timer:
            self.timer.cancel()
            self.isRunning = False

    def _executeSignOut(self):
        self.isRunning = False
        self.signOutFn()
