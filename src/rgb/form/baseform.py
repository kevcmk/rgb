
import logging
from abc import ABC, abstractmethod
from typing import Dict, Union
import time
import numpy as np
from PIL import Image
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class BaseForm(ABC):

    def _instrumented_step(self, dt: float) -> Union[Image.Image,np.ndarray]:
        a = time.time()
        res = self.step(dt)
        dt = time.time() - a
        log.debug(f"Step dt: {dt}")
        return res

    @abstractmethod
    def step(self, dt: float) -> Union[Image.Image,np.ndarray]:
        pass

    def midi_handler(self, value: Dict):
        pass

    def cleanup(self):
        pass