from rgb.constants import MIDI_DIAL_MAX
import logging
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Union
import time
import numpy as np
from PIL import Image
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class BaseForm(ABC):

    _dials = [0.5 for _ in range(8)]

    def __init__(self, dimensions: Tuple[int, int]):
        (self.matrix_width, self.matrix_height) = dimensions

    def _instrumented_step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        a = time.time()
        res = self.step(dt)
        dt = time.time() - a
        log.debug(f"Step dt: {dt}")
        return res

    @classmethod
    def dials(cls, index: int) -> float:
        return cls._dials[index]

    @abstractmethod
    def step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        pass

    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value["type"] == "control_change" and 14 <= value["control"] <= 17:
            # VMini is [14,17]
            self._dials[value["control"] - 14] = value["value"] / MIDI_DIAL_MAX
        elif value["type"] == "control_change" and 1 <= value["control"] <= 8:
            # LPD8 is [1,8]
            self._dials[value["control"] - 1] = value["value"] / MIDI_DIAL_MAX

    def cleanup(self):
        pass
