from tkinter import NW, Canvas, Tk
from typing import Tuple, Union

import numpy as np
from PIL import Image, ImageTk
from rgb.display.basedisplay import BaseDisplay
import logging

log = logging.getLogger(__name__)


class TkCanvas(BaseDisplay):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.matrix_width = dimensions[0]
        self.matrix_height = dimensions[1]
        self.canvas_scale = 6
        self.root = Tk()
        self.canvas = Canvas(
            self.root, width=self.matrix_width * self.canvas_scale, height=self.matrix_height * self.canvas_scale
        )
        self.canvas.pack()

    def display(self, image: Union[Image.Image, np.ndarray]):
        if isinstance(image, np.ndarray):
            log.debug("Casting image to PIL PhotoImage")
            pil_image = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            pil_image = image
        else:
            raise ValueError(f"Invalid type for {image}")
        pil_image_larger = pil_image.resize(
            (self.matrix_width * self.canvas_scale, self.matrix_height * self.canvas_scale), resample=0
        ).transpose(Image.FLIP_TOP_BOTTOM)
        pi = ImageTk.PhotoImage(pil_image_larger)
        self.canvas.create_image(0, 0, anchor=NW, image=pi)
        self.canvas.update()
