class DevColorCycler:
    def __init__(self):
        self.index = 0
        # unused colors are 'k', 'r', 'c''
        self.colors = ['blue', 'orange', 'pink', 'purple', 'yellow', 'cyan']

    def getNext(self):
        self.index += 1
        if self.index > len(self.colors) - 1:
            self.index = 0
        return self.colors[self.index]

    def reset(self):
        self.index = 0