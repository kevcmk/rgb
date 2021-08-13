from functools import lru_cache
import time
from rgb.form.transitions import transition_ease_in
from rgb.parameter_tuner import ParameterTuner
from rgb.form.sustainobject import SimpleSustainObject
from rgb.form.keyawareform import Press
import logging
import os
import colorsys
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Iterable, List, Set, Tuple, Union
from rgb.constants import NUM_NOTES, NUM_PIANO_KEYBOARD_KEYS, MIDI_DIAL_MAX
from scipy.spatial import Voronoi, voronoi_plot_2d
from itertools import chain

import numpy as np

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

PRIMES = [2213,	2221,	2237,	2239,	2243,	2251,	2267,	2269,	2273,	2281, 2287, 2293]

def show_voronoi_diagram(v: Voronoi):
    import matplotlib.pyplot as plt
    voronoi_plot_2d(v)
    plt.show()
    
class VoronoiDiagram(SimpleSustainObject):
    
    def get_base_point_array_list(self, a: np.ndarray) -> np.ndarray:
        return np.concatenate((self.base_points, a), axis=0) if a.size != 0 else self.base_points
    
    @lru_cache
    def get_polygons(self, a: Tuple[Tuple[int,int]]) -> List[List[Tuple[int,int]]]:
        base_points_to_ignore = len(self.base_points)
        
        input_vertices = self.get_base_point_array_list(np.array(list(a)))
        # Also include companion points to intoduce sparsity
        companion_points_units = list(chain.from_iterable([VoronoiDiagram.get_press_companion_points(p, count=self.num_companion_points) for p in self.presses.values()]))
        companion_points_coordinates = self.companion_points_to_coordinates(companion_points_units)
        concatenated = np.concatenate((input_vertices, companion_points_coordinates), axis=0) if companion_points_coordinates else input_vertices
        v: Voronoi = Voronoi(concatenated)
        output_polygons = []
        for nth_polygon in range(base_points_to_ignore, base_points_to_ignore + len(a)):
            region_index = v.point_region[nth_polygon]
            region_vertex_indices = v.regions[region_index]
            region_vertices = []
            for vertex_index in region_vertex_indices:
                numpy_vertex = v.vertices[vertex_index]
                region_vertices.append((numpy_vertex[0], numpy_vertex[1]))
            output_polygons.append(region_vertices)
        self.voronoi = v
        return output_polygons

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        w = self.matrix_width
        h = self.matrix_height
        # These points are outside the window of view, but evenly surround the space. Without them we get QH6214 qhull input error:
        self.base_points = np.array([ (-10 * w, h/2), (11*w, h/2), (w/2, -10 * h), (w/2, 11 *h)])
        self.polygon_coordinate_map: Dict[int, List[Tuple[int,int]]] = {}
        self.num_companion_points = 2
    
    @staticmethod
    def get_press_companion_points(p: Press, count: int) -> List[Tuple[float,float]]:
        assert count <= 6
        h = hash(p)
        acc = []
        for i in range(count):
            x_modulus = PRIMES[i]
            y_modulus = PRIMES[-i]
            acc.append(((h % x_modulus) / x_modulus, (h % y_modulus) / y_modulus))
        return acc

    def companion_points_to_coordinates(self, points: List[Tuple[float,float]]) -> List[Tuple[int,int]]: 
        return [(int(p[0] * self.matrix_width), int(p[1] * self.matrix_height)) for p in points]

    def midi_handler(self, value: Dict):
        super().midi_handler(value)
        if value['type'] == 'control_change' and value['control'] == 15: 
            self.num_companion_points = int(ParameterTuner.linear_scale(value['value'] / MIDI_DIAL_MAX, minimum=0, maximum=6))

    def step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        arr = tuple(self.calculate_xy_position(x) for x in self.presses.values())
        polygon_results = self.get_polygons(arr)
        self.polygon_coordinate_map = {}
        for key, polygon in zip(self.presses.keys(), polygon_results):
            self.polygon_coordinate_map[key] = polygon
        return super().step(dt)
        
    def draw_shape(self, draw_context, press: Press, r: float):
        coordinates = self.polygon_coordinate_map[press.note]
        color = self.calculate_color(press)
        draw_context.polygon(coordinates, fill=color, outline=None)
        # draw_context.rectangle((0,0,1,1), fill=self.calculate_color(press))

class ValueVoronoiDiagram(VoronoiDiagram):
    def calculate_color(self, p: Press):
        dt = time.time() - p.t 
        x = transition_ease_in(dt / self.attack_time) if self.attack_time != 0 else 1.0
        hue = (p.note % NUM_NOTES) / NUM_NOTES
        rgb = colorsys.hsv_to_rgb(hue, 1.0, x)
        return (int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2]))
    
class RedSaturationVoronoiDiagram(VoronoiDiagram):
    def calculate_color(self, p: Press):
        v = (p.note % NUM_NOTES) / NUM_NOTES
        rgb = colorsys.hsv_to_rgb(1, v, 1.0)
        return (int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2]))


class RedStationarySaturationVoronoiDiagram(RedSaturationVoronoiDiagram):
    def calculate_xy_fractional_position(self, p: Press) -> Tuple[float, float]:
        x = 0.5
        y = (p.note % NUM_NOTES) / NUM_NOTES
        return (x,y)

class RedValueVoronoiDiagram(VoronoiDiagram):
    def calculate_color(self, p: Press):
        v = (p.note % NUM_NOTES) / NUM_NOTES
        rgb = colorsys.hsv_to_rgb(1, 1.0, v)
        return (int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2]))

class SparseRedValueVoronoiDiagram(VoronoiDiagram):
    def calculate_color(self, p: Press):
        v = (p.note % NUM_NOTES) / NUM_NOTES if p.note < NUM_PIANO_KEYBOARD_KEYS else 0.0
        rgb = colorsys.hsv_to_rgb(1, 1.0, v)
        return (int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2]))