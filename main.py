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


def main(pins: List[Pin]):
    gin_ingredient_id = 0
    tonic_ingredient_id = 1

    bot = CockBot()
    controller = L298N(enable_pin_1=pins[0], enable_pin_2=pins[1])
    controller.enable_all()
    strength = 100
    pump1 = Pump(pin=Pin(4), place=Place(1), strength=strength, ingredient_id=gin_ingredient_id)
    pump2 = Pump(pin=Pin(15), place=Place(2), strength=strength, ingredient_id=tonic_ingredient_id)
    controller.add_pump(pump1)
    controller.add_pump(pump2)
    bot.add_motor_controller(controller)

    pump1.is_forward = False
    pump2.is_forward = False
    controller.set_speed(1, 100)
    controller.set_speed(2, 100)
    controller.set_speed(1, 0)
    controller.set_speed(2, 0)


if __name__ == "__main__":
    pins = [Pin(3), Pin(14), Pin(2), Pin(4), Pin(15), Pin(18)]
    try:
        main(pins)
    except Exception as e:
        print("E: {}".format(e))
    [p.close() for p in pins]
