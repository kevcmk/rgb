import os
from rgb.display.hzelmatrix import HzelMatrix
from rgb.controlloop import ControlLoop
from rgb.form import (audio_spectrogram, gravity, orbit, sustainobject, stars, timer, basenoise, voronoi_diagram)

if __name__ == "__main__":
    dimensions = (int(os.environ.get("MATRIX_WIDTH", 32)), int(os.environ.get("MATRIX_HEIGHT", 64)))
        
    forms = (
        # stripes.Stripes(dimensions),
        voronoi_diagram.VoronoiDiagram(dimensions),
        voronoi_diagram.ValueVoronoiDiagram(dimensions),
        # voronoi_diagram.RedSaturationVoronoiDiagram(dimensions),
        voronoi_diagram.RedValueVoronoiDiagram(dimensions),
        sustainobject.VerticalNotes(dimensions), 
        sustainobject.VerticalKeys(dimensions),
        sustainobject.RandomIcon(dimensions),
        gravity.Gravity(dimensions, 0.006), 
        gravity.GravityKeys(dimensions, 0.006), 
        gravity.GravityKeysMultiNozzle(dimensions, 0.006), 
        sustainobject.RandomSolidShape(dimensions), 
        sustainobject.RandomIcon(dimensions),
        sustainobject.RandomWord(dimensions),
        sustainobject.RandomJapaneseWord(dimensions),
        sustainobject.RandomNumber(dimensions),
        # randomobject.RandomOutlineShape(dimensions), 
        # randomobject.RandomOutlineCircle(dimensions), 
        # basenoise.WhispNoise(dimensions),
        # basenoise.HueNoise(dimensions),
        # basenoise.BaseNoise(dimensions),
        # timer.Timer(dimensions),
        # audio_spectrogram.AudioSpectrogram(dimensions),
        # stars.Stars(dimensions), 
        # orbit.Orbit(dimensions, fast_forward_scale=60 * 60 * 24 * 30), 
    )

    display = HzelMatrix(dimensions=dimensions)


    rgb2d = ControlLoop(display=display, forms=forms)
    rgb2d.initialize_mqtt()
    rgb2d.blocking_loop()
