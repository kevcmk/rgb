from dataclasses import dataclass
from typing import List
from rgb.utilities import clamp
import logging
import os
log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


@dataclass
class Parameters:
    dials: List[float]

class ParameterTuner:

    def __init__(self, num_dials):
        self._dials = [0.5 for _ in range(num_dials)]

    # def set_dial(self, index: int, value: float):
    #     if not 0 <= value <= 1.0:
    #         log.warning(f"Value, {value}, outside of [0,1] on index {index}.")
    #         value = clamp(value, 0, 1)
    #     self._dials[index] = value

    # def discrete(self, index: int, options: List):
    #     index = int(self._dials[index] * len(options))
    #     return options[index]

    @staticmethod
    def linear_scale(v: float, minimum: float, maximum: float) -> float:
        delta = maximum - minimum
        return minimum + v * delta

    @staticmethod
    def exponential_scale(v: float, exponent: float, minimum: float, maximum: float) -> float:
        delta = maximum - minimum
        return minimum + v ** exponent * delta