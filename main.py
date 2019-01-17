from typing import Set, List

from gpiozero import OutputDevice

from cockout import Place
from cockout.io import L298N, PumpController, Pin, Pump
from cockout.recipe import Recipe


class CockBot:
    def __init__(self, motor_controllers: Set[L298N] = None):
        if not motor_controllers:
            self.motor_controllers = set()

    def add_motor_controller(self, motor_controller: PumpController):
        self.motor_controllers.add(motor_controller)

    def pour(self, recipe: Recipe):
        pass


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
