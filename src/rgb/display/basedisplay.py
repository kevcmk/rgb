

from rgb.hzel_samplebase import SampleBaseMatrixFactory
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Union

import numpy as np
from PIL import Image
from rgbmatrix import FrameCanvas, RGBMatrix
import sys
from PIL import ImageTk
from tkinter import Canvas, Tk, NW
import atexit 
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class BaseDisplay(ABC):

    width: int
    height: int

    @abstractmethod
    def __init__(self, dimensions: Tuple[int, int]):
        self.width = dimensions[0]
        self.height = dimensions[1]

    @abstractmethod
    def display(self, image: Union[Image.Image, np.ndarray]):
        pass
    

