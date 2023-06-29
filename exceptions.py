class weakSignal(Exception):
    def __init__(self, strength, message="Signal Strength > -0.3 dB"):
        self.message = message
        self.strength = strength
        super().__init__(self.message)

    def __str__(self):
        return f'{self.strength} -> {self.message}'


class badFit(Exception):
    def __init__(self, message="Couldn't fit the data"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
