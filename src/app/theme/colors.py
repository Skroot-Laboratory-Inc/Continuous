class Colors:
    def __init__(self):
        self.red = '#CD0000'  # red
        self.yellow = '#FFFE71'  # pastel yellow
        self.green = '#5CA904'  # leaf green
        self.lightRed = '#FF474C'  # light red
        self.white = '#FFFFFF'


class ColorCycler:
    def __init__(self):
        self.index = 0
        # unused colors are 'k', 'r', 'c''
        self.colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink',
                       'tab:gray', 'tab:olive', 'tab:cyan', 'b', 'g', 'm', 'y']

    def getNext(self):
        self.index += 1
        if self.index > len(self.colors) - 1:
            self.index = 0
        return self.colors[self.index]

    def reset(self):
        self.index = 0
