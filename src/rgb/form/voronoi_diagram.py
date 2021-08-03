from rgb.form.sustainobject import SimpleSustainObject
from rgb.form.keyawareform import Press
import logging
import os
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
                region_vertices.append(v.vertices[vertex_index])
            output_polygons.append(region_vertices)
        self.voronoi = v
        return output_polygons

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        w = self.matrix_width
        h = self.matrix_height
        # These points are outside the window of view, but without them we get QH6214 qhull input error:
        # self.base_points = np.array([(-w, -h), (-w, h/2), (-w, 2 * h), 
        #                              (2 * w, -h), (2*w, h/2), (2 * w, 2 * h),
        #                              (w/2, -h), (w/2, 2*h)])
        self.base_points = np.array([ (-2 * w, h/2),
                                     (3*w, h/2), 
                                     (w/2, -2 * h), 
                                     (w/2, 3 *h)])

        self.polygon_map = {}
        
        a = np.array([(0,0), (10,10), (15,15), (25,20)])
        a = np.array([(0,0), (32,64)])
        self.get_polygons(a)
        
    def midi_handler(self, value: Dict):
        super().midi_handler(value)
        if value['type'] in ('note_on', 'note_off'):
            # If a note is actuated, update.
            if len(self.presses) == 0:
                print("0 points")
            elif len(self.presses) > 1:
                print("1 point")
            elif len(self.presses) > 3:
                points = np.array([self.calculate_xy_position(x) for x in self.presses.values()])
                print(points)
                self.voronoi = Voronoi(points)
                voronoi_plot_2d(self.voronoi)

    def step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        return super().step(dt)
        # if self.presses:
        #     points = [self.calculate_xy_position(x) for x in self.presses.values()]
        #     print(points)
        #     vor = Voronoi(points)
        #     print(vor)
        #     self.voronoi = vor
        # else:
        #     return 
    
    def draw_shape(self, draw_context, press: Press, r: float):
        xy = self.polygon_map[press.note]
        draw_context.polygon(xy, fill=None, outline=None)
        draw_context.rectangle((0,0,1,1), fill=self.calculate_color(press))