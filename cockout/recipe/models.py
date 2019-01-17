from typing import Set


class Glass:
    def __init__(self, size: int):
        self.size = size


class Ingredient:
    def __init__(self, id: int, rank: int, share: int):
        self.share = share
        self.rank = rank
        self.id = id

    def __hash__(self):
        return hash(self.id * self.rank * self.share)


class Recipe:
    def __init__(self, id: int, ingredients: Set[Ingredient], glass: Glass):
        self.id = id
        self.ingredients = ingredients
        self.glass = glass
