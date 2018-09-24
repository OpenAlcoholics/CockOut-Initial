from typing import Set

from cockout.io import L298N


class CockBot:
    def __init__(self, motor_controllers: Set[L298N] = None):
        if not motor_controllers:
            self.motor_controllers = set()


if __name__ == "__main__":
    pass
