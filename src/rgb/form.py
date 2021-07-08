
from abc import ABC, abstractmethod
from typing import Dict, Union
import numpy as np
from PIL import Image


class Form(ABC):

    @abstractmethod
    def step(self, dt: float) -> Union[Image.Image,np.ndarray]:
        pass

    def midi_handler(self, value: Dict):
        pass

    def cleanup(self):
        pass
