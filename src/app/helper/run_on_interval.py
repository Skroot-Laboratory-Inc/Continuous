import threading
import time


class RunOnInterval:
    def __init__(self, runFn, delaySeconds, initialDelay=0):
        self.timer_runs = threading.Event()
        self.initialDelay = initialDelay
        self.timer_runs.set()
        self.runFn = runFn
        self.delaySeconds = delaySeconds
        self.running = False
        self.t = threading.Thread(target=self.timer)

    def timer(self):
        time.sleep(self.initialDelay)
        while self.timer_runs.is_set():
            self.runFn()
            time.sleep(self.delaySeconds)

    def stopFn(self):
        self.timer_runs.clear()
        self.running = False

    def startFn(self):
        self.t.start()
        self.running = True

