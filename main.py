from concurrent.futures import ProcessPoolExecutor
from logging import Logger
from typing import Set, List

from cockout import Place
from cockout.io import L298N, PumpController, Pin, Pump, NoSuchElement
from cockout.recipe import Ingredient, Recipe
from cockout.recipe.models import Glass


class CockBot:
    def __init__(self, motor_controllers: Set[L298N] = None):
        self.log = Logger("CockBot")
        if not motor_controllers:
            self.motor_controllers = set()

    def add_motor_controller(self, motor_controller: PumpController):
        self.motor_controllers.add(motor_controller)

    def check_pouring_capability(self, recipe: Recipe):
        self.check_glass_existence()
        flattened_ingredients = [item for sublist in recipe.ingredients for item in sublist]
        self.check_ingredient_availability(flattened_ingredients)

    def pour(self, recipe: Recipe):
        self.check_pouring_capability(recipe)

        for ingredient_rank in recipe.ingredients:
            self.pour_ingredients(ingredient_rank, recipe.glass.size)

    def pour_ingredients(self, ingredients: List[Ingredient], glass_size: int):
        executor = ProcessPoolExecutor(max_workers=len(ingredients))
        for ingredient in ingredients:
            executor.submit(self.pour_ingredient, ingredient, glass_size)

    def _pump_for_ingredient(self, ingredient: Ingredient) -> Pump:
        for pump in [pump for pump in self.pumps() if pump.ingredient_id == ingredient.id]:
            return pump

        exception_message = f"Pump with ingredient {ingredient} not found"
        self.log.exception(exception_message)
        raise NoSuchElement(exception_message)

    def pour_ingredient(self, ingredient: Ingredient, glass_size: int):
        pump = self._pump_for_ingredient(ingredient)  # Function will throw an error on missing pump
        milliliter = (ingredient.share / 100) * glass_size
        self.log.info(f"Pump {milliliter} for {ingredient} on {pump}.")

        pump.set_ml(milliliter)

    def check_glass_existence(self):
        return False

    def check_ingredient_availability(self, flattened_ingredients: List[Ingredient]):
        for controller in self.motor_controllers:
            for pump in controller.pumps:
                if pump.ingredient_id not in flattened_ingredients:
                    return False

        return True

    def pumps(self) -> List[Pump]:
        return [item for sublist in self.motor_controllers for item in sublist.pumps]


def main():
    gin_ingredient_id = 0
    tonic_ingredient_id = 1

    recipe = Recipe(1, {Ingredient(0, 0, 50), Ingredient(1, 0, 50)}, Glass(400))

    bot = CockBot()
    controller = L298N(0, enable_pin_1=Pin(3), enable_pin_2=Pin(14))
    controller.enable_all()
    strength = 100
    pump1 = Pump(pin_number=4, place=Place(1), strength=strength, ingredient_id=gin_ingredient_id)
    pump2 = Pump(pin_number=15, place=Place(2), strength=strength, ingredient_id=tonic_ingredient_id)
    controller.add_pump(pump1)
    controller.add_pump(pump2)
    bot.add_motor_controller(controller)

    pump1.is_forward = False
    pump2.is_forward = False

    # bot.pour(recipe=recipe)
    bot.pumps()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        Logger("main").exception(f"{e}")
