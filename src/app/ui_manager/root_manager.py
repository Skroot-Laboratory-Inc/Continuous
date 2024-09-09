import tkinter as tk


class RootManager:
    def __init__(self):
        self.root = tk.Tk()  # everything in the application comes after this

    def instantiateMenubar(self):
        return tk.Menu(self.root)

    def addMenubar(self, menubar):
        self.root.config(menu=menubar)

    def createTopLevel(self):
        return tk.Toplevel(self.root, bg='white', padx=25, pady=25)

    def createFrame(self, backgroundColor) -> tk.Frame:
        return tk.Frame(self.root, bg=backgroundColor)

    def createPaddedFrame(self, backgroundColor) -> tk.Frame:
        return tk.Frame(self.root, bg=backgroundColor, padx=15, pady=15)

    def callMainLoop(self):
        self.root.mainloop()  # everything comes before this

    def raiseAboveRoot(self, window):
        window.tkraise(self.root)

    def raiseRoot(self):
        self.root.tkraise()

    def waitForWindow(self, window):
        self.root.wait_window(window)

    def destroyRoot(self):
        self.root.destroy()

    def getRoot(self):
        return self.root

    def setState(self, state):
        self.root.state(state)

    def setAttribute(self, attribute, state):
        self.root.attributes(attribute, state)

    def setProtocol(self, protocol, invokeFn):
        self.root.protocol(protocol, invokeFn)

    def setTitle(self, title):
        self.root.title(title)

    def setBackgroundColor(self, backgroundColor):
        self.root.configure(background=backgroundColor)

    def generateEvent(self, event):
        self.root.event_generate(event)

    def registerEvent(self, event, eventFn):
        self.root.bind(event, eventFn)
