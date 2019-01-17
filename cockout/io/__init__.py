from enum import Enum
from logging import Logger
from typing import Any, Set

from gpiozero import CompositeDevice, OutputDevice, PWMOutputDevice

from cockout import Place
from cockout.exceptions import *


class CustomEnum(Enum):
    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.value == other.value
        elif other.__class__.__name__ == "int":
            return self.value == other

        return False

    def has_key(self, key: Any) -> bool:
        """
        :type key: Any
        :rtype: bool
        """
        key = str(key)

        return key in self or key.rsplit(".")[-1] in self.__members__

    def has_value(self, value: Any) -> bool:
        return value in [item.value for item in self.__members__]


class Pin(OutputDevice):
    def __init__(self, number: int):
        self.number = number
        super().__init__(number)
        # self.log.debug(f"Instaniate pin {number}")

    def __hash__(self):
        return hash(self.number)

    def __repr__(self):
        return f"<Pin {self.number}>"


class Pump(PWMOutputDevice):
    def __init__(self, pin_number: int, place: Place, strength: int, ingredient_id: int):
        super().__init__(pin=pin_number)
        self.log.debug(f"Instaniate pump {id}")
        self.ingredient_id = ingredient_id
        self.set_speed(0)
        self.place = place
        self.time100ml = strength  # seconds

    def set_speed(self, speed_percent: int):
        """
        Between 0 and 100
        """
        if speed_percent < 0 or speed_percent > 100:
            exception_message = "speed_percent for Pump.set_speed has to be between 0 and 100."
            self.log.exception(exception_message)
            raise AttributeError(exception_message)

        self.value = speed_percent / 100

    def set_ml(self, milliliter: int):
        time = milliliter / self.time100ml

    def speed(self) -> float:
        """
        Between 0 and 1
        """
        return self.value

    def start(self):
        self.on()

    def stop(self):
        self.off()

    def speed_percent(self) -> int:
        """
        Between 0 and 100
        """
        return int(self.speed() * 100)

    def __hash__(self):
        return hash(self.place)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.high_pin == other.high_pin and \
                   self.low_pin == other.low_pin and \
                   self.place == other.place

        return False


class PumpController(CompositeDevice):
    def __init__(self, id: int, enable_pins: Set[Pin] = None):
        self.log = Logger(f"pump_controller <{id}>")
        self.log.debug(f"Instaniate pump controller {id}")
        super().__init__()
        self.id = id
        self.enable_pins = enable_pins or set()
        self.pumps: Set[Pump] = []

    def add_pump(self, pump: Pump):
        for existing_pump in self.pumps:
            if existing_pump.place.number == pump.place.number:
                raise DuplicatePinError()

        self.pumps.add(pump)

    def set_speed(self, pump: Pump, speed_percent: int):
        for pump in filter(lambda other: other.place.number == pump.place, self.pumps):
            return pump.set_speed(speed_percent)

        exception_message = "Pump with place {} not found for {}".format(pump.place, self)
        self.log.exception(exception_message)
        raise NoSuchElement(exception_message)

    def enable_pump(self, pump: Pump):
        for pump in filter(lambda other_pump: pump.place == other_pump.place, self.pumps):
            return pump.start()

        exception_message = "Pump with place {} not found for {}".format(pump.place, self)
        self.log.exception(exception_message)
        raise NoSuchElement(exception_message)

    def disable_pump(self, pump: Pump):
        for pump in filter(lambda other_pump: pump.place == other_pump.place, self.pumps):
            return pump.stop()

        exception_message = "Pump with place {} not found for {}".format(pump.place, self)
        self.log.exception(exception_message)
        raise NoSuchElement(exception_message)

    def enable_all(self) -> bool:
        return all(pin.on() for pin in self.enable_pins)

    def disable_all(self) -> bool:
        return all(pin.off() for pin in self.enable_pins)

    def __repr__(self):
        pump_ids = " | ".join([pump.id for pump in self.pumps])

        return "<{}: {}>".format(self.__class__.__name__, pump_ids)

    def __str__(self):
        return self.__repr__()


class L298N(PumpController):
    def __init__(self, id: int, enable_pin_1: Pin, enable_pin_2: Pin):
        super().__init__(id, enable_pins={enable_pin_1, enable_pin_2})

    def __repr__(self):
        pump_ids = " | ".join([pump.id for pump in self.pumps])

        return "<{}: {}>".format(self.__class__.__name__, pump_ids)
