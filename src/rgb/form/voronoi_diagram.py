from rgb.form.sustainobject import SimpleSustainObject
from rgb.form.keyawareform import Press
import logging
import os
import colorsys
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Set, Tuple, Union
from rgb.constants import NUM_NOTES, NUM_PIANO_KEYBOARD_KEYS, MIDI_DIAL_MAX
from scipy.spatial import Voronoi, voronoi_plot_2d

import numpy as np

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

def show_voronoi_diagram(v: Voronoi):
    import matplotlib.pyplot as plt
    voronoi_plot_2d(v)
    plt.show()
    
class VoronoiDiagram(SimpleSustainObject):
    
    def get_base_point_array_list(self, a: np.ndarray) -> np.ndarray:
        return np.concatenate((self.base_points, a), axis=0)
    
    def get_polygons(self, a: np.ndarray) -> List[List[Tuple[int,int]]]:
        base_points_to_ignore = len(self.base_points)
        input_vertices = self.get_base_point_array_list(a)
        v: Voronoi = Voronoi(input_vertices)
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
        
    def midi_handler(self, value: Dict):
        super().midi_handler(value)
        if value['type'] in ('note_on', 'note_off'):
            # For any change, restart it.
            
            # If a note is actuated, update.
            if len(self.presses) == 0:
                log.info("Restarting polygon coordinate map")
                self.polygon_coordinate_map = {}
            else:
                arr = np.array([self.calculate_xy_position(x) for x in self.presses.values()])
                polygon_results = self.get_polygons(arr)
                self.polygon_coordinate_map = {}
                for key, polygon in zip(self.presses.keys(), polygon_results):
                    print(f"placing key: {key}")
                    self.polygon_coordinate_map[key] = polygon
                    log.info(f"{key}: {polygon}")
    
    def draw_shape(self, draw_context, press: Press, r: float):
        print(f"draw_shape: {press.note}")
        coordinates = self.polygon_coordinate_map[press.note]
        color = self.calculate_color(press)
        log.info(f"Rendering {press} with {coordinates}")
        draw_context.polygon(coordinates, fill=color, outline=None)
        # draw_context.rectangle((0,0,1,1), fill=self.calculate_color(press))

class RedSaturationVoronoiDiagram(VoronoiDiagram):
    def calculate_color(self, p: Press):
        v = (p.note % NUM_NOTES) / NUM_NOTES
        rgb = colorsys.hsv_to_rgb(1, v, 1.0)
        return (int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2]))

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