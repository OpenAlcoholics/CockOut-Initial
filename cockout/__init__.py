class Place:
    def __init__(self, number: int):
        self.number = number

    def __hash__(self):
        return hash(self.number)
