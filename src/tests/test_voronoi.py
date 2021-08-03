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
    np.array([(0,0)]), 
    np.array([(w/2,h/2)]), 
    np.array([(0,0), (w,h)]), 
    np.array([(0,0), (w, 0), (0, h), (w,h)])
])
def test_no_fail(points):
    f = VoronoiDiagram((w, h))
    f.get_polygons(points)
    
def test_correct_polygon():

    """
    self.voronoi.points
    array([[ -64.,   32.],
       [  96.,   32.],
       [  16., -128.],
       [  16.,  192.],
       [   0.,    0.],
       [  32.,   64.]])
       
    self.voronoi.point_region
    array([6, 4, 1, 3, 5, 2])
    
    self.voronoi.regions
    [[], [-1, 1, 0], [5, 3, 2, 4], [4, -1, 2], [3, 1, -1, 2], [5, 0, 1, 3], [5, 0, -1, 4]]

    vertices
    array([[-77.33333333, -74.66666667],
       [ 72.        , -56.        ],
       [109.33333333, 138.66666667],
       [ 48.        ,  16.        ],
       [-40.        , 120.        ],
       [-16.        ,  48.        ]])
    
    """

    f = VoronoiDiagram((w, h))
    points = np.array([(0,0), (w,h)])
    polygons = f.get_polygons(points)
    polygon_0 = np.array(
            [
                np.array([-16.        ,  48.        ]), 
                np.array([-77.33333333, -74.66666667]),
                np.array([ 72.        , -56.        ]),
                np.array([ 48.        ,  16.        ])
            ]
        )
    polygon_1 = np.array(
            [
                np.array([-16.        ,  48.        ]), 
                np.array([ 48.        ,  16.        ]),  
                np.array([109.33333333, 138.66666667]),
                np.array([-40.        , 120.        ])
            ]
        )
    assert np.isclose(polygons[0], polygon_0).all()
    assert np.isclose(polygons[1], polygon_1).all()