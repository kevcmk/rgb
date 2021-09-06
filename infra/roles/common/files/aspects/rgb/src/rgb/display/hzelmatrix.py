     
from rgb.display.basedisplay import BaseDisplay
import logging 
from rgb.hzel_samplebase import SampleBaseMatrixFactory
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Union

import numpy as np
from PIL import Image
from rgbmatrix import FrameCanvas, RGBMatrix
import sys

import os

import logging
log = logging.getLogger(__name__)


class HzelMatrix(BaseDisplay):

    def parse_hzeller_rgb_args(self):
        rgb_args = {k:v for k,v in os.environ.items() if k.startswith("RUN_ARG_")}
        for k,v in rgb_args.items():
            log.debug(f"Parsing rgb_arg: {k}: {v}")
            argparse_style_arg = "--" + k.replace("RUN_ARG_", "").replace("_", "-").lower()
            log.info(f"Arg-parsing: {argparse_style_arg}: {v}")
            sys.argv.extend([argparse_style_arg, v])

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.parse_hzeller_rgb_args()
        self.matrix: RGBMatrix = SampleBaseMatrixFactory().from_argparse()
        # Documentation: https://github.com/hzeller/rpi-rgb-led-matrix/blob/dfc27c15c224a92496034a39512a274744879e86/include/led-matrix.h#L204
        # for explanation
        # Explanation: https://github.com/hzeller/rpi-rgb-led-matrix/blob/dfc27c15c224a92496034a39512a274744879e86/bindings/python/samples/rotating-block-generator.py#L42
        self.offset_canvas: FrameCanvas = self.matrix.CreateFrameCanvas()
        
    def display(self, image: Union[Image.Image, np.ndarray]):
        if isinstance(image, np.ndarray):
            log.debug("Casting image to PIL PhotoImage")
            pil_image = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            pil_image = image
        else: 
            raise ValueError(f"Invalid type for {image}")
        self.offset_canvas.SetImage(pil_image)
        self.offset_canvas = self.matrix.SwapOnVSync(self.offset_canvas)
