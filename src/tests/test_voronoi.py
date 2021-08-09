import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from rgb.utilities import loopwait
from rgb.form.voronoi_diagram import *
import time

w = 32
h = 64
@pytest.mark.parametrize("points", [
    [(0,0)], 
    [(w/2,h/2)], 
    [(0,0), (w,h)], 
    [(0,0), (w, 0), (0, h), (w,h)]
])
def test_no_fail(points):
    f = VoronoiDiagram((w, h))
    polygons = f.get_polygons(tuple(points))
    assert len(polygons) == len(points)
    