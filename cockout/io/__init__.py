from enum import Enum
from typing import List, Union

from gpiozero import CompositeDevice, Motor
from gpiozero.exc import PinInvalidFunction
from gpiozero import Pin as GPin

from cockout import Place
from cockout.exceptions import *


class CustomEnum(Enum):
    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.value == other.value
        elif other.__class__.__name__ == "int":
            return self.value == other

        return False

    @staticmethod
    def has_key(key):
        key = str(key)

        return key in PinState or key.rsplit(".")[-1] in PinState.__members__

    @staticmethod
    def has_value(value):
        return value in [item.value for item in PinState]


class PinState(CustomEnum):
    LOW = 0
    HIGH = 1


class PinType(CustomEnum):
    type: str = None
    INPUT = 0
    OUTPUT = 1


class Pin(GPin):
    state: PinState = 0

    def __init__(self, number: int):
        super().__init__()
        self.number = number

    def _get_function(self):
        return self.state

    def _set_function(self, value: Union[PinState, int]):
        if not PinState.has_key(value) and not PinState.has_value(value):
            raise PinInvalidFunction("Cannot set the function of pin %r to %s" % (self, value))

    def _get_state(self) -> PinState:
        return self.state


class Pump(Motor):
    def __init__(self, high_pin: Pin, low_pin: Pin, place: Place, strength: int):
        super().__init__(forward=high_pin.number, backward=low_pin.number)
        self.place = place
        self.is_forward = True
        self.time100ml = strength

    """
    Between 0 and 100
    """
    def set_speed(self, speed_percent: int):
        if speed_percent < 0 or speed_percent > 100:
            raise AttributeError("speed_percent for Pump.set_speed has to be between 0 and 100.")

        speed = speed_percent / 100
        if self.is_forward:
            self.forward(speed)
        else:
            self.backward(speed)

    """
    Between 0 and 1
    """
    def speed(self):
        return self.value

    """
    Between 0 and 100
    """
    def speed_percent(self):
        return self.speed() * 100

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.high_pin == other.high_pin and \
                   self.low_pin == other.low_pin and \
                   self.place == other.place


class DcPump(Pump):
    def __init__(self, high_pin: Pin, low_pin: Pin, place: Place = None, strength: """TODO""" = None):
        super().__init__(high_pin=high_pin, low_pin=low_pin, place=place, strength=strength)


class MotorController(CompositeDevice):
    def __init__(self):
        super().__init__()
        self.pumps: List[Pump] = []

    def add_pump(self, pump: Pump):
        for existing_pump in self.pumps:
            if existing_pump == pump:
                raise DuplicatePinError()

        self.pumps.append(pump)

    def set_speed(self, pump_place: int, speed_percent: int):
        for pump in filter(lambda pump: pump.place == pump_place, self.pumps):
            return pump.set_speed(speed_percent)

        raise NoSuchElement(f"Pump with place {pump_place} not found for {self}")


class L298N(MotorController):
    def __init__(self):
        super().__init__()
