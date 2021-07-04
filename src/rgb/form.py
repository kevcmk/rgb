
from abc import ABC, abstractmethod
from typing import Dict
from PIL import Image

class Form(ABC):

    @abstractmethod
    def step(self, dt: float) -> Image.Image:
        pass

    def midi_handler(self, value: Dict):
        pass

    def cleanup(self):
        pass
    
    