import os

from rgb.controlloop import ControlLoop
from rgb.display.hzelmatrix import HzelMatrix
from rgb.form import gravity, sustainobject, voronoi_diagram
from rgb.form.stars import Stars

if __name__ == "__main__":
    dimensions = (
        int(os.environ.get("MATRIX_WIDTH", 32)),
        int(os.environ.get("MATRIX_HEIGHT", 64)),
    )

    forms = (
        sustainobject.RandomVerticalWaveReverseSlow(dimensions),
        sustainobject.RandomVerticalWaveReverseSlowDarkerLows(dimensions),
        sustainobject.RandomVerticalWaveReverseSlowDarkerLowsRed(dimensions),
        # stripes.Stripes(dimensions),
        sustainobject.VerticalWaves(dimensions),
        sustainobject.VerticalNotes(dimensions),
        sustainobject.VerticalNotesSlowSpectrum(dimensions),
        sustainobject.VerticalKeys(dimensions),
        sustainobject.RandomIcon(dimensions),
        # gravity.Gravity(dimensions, 0.006),
        gravity.GravityKeys(dimensions, 0.006),
        gravity.GravityKeysMultiNozzle(dimensions, 0.006),
        sustainobject.RandomWaveShape(dimensions),
        sustainobject.RandomWaveShapeReverseSlow(dimensions),
        sustainobject.RandomVerticalWaveReverseSlow(dimensions),
        sustainobject.RandomSolidShape(dimensions),
        sustainobject.RandomSolidShapeSlowSpectrum(dimensions),
        sustainobject.RandomIcon(dimensions),
        sustainobject.RandomWord(dimensions),
        sustainobject.RandomJapaneseWord(dimensions),
        sustainobject.TextStars(dimensions),
        sustainobject.TextSparkles(dimensions),
        voronoi_diagram.VoronoiDiagram(dimensions),
        voronoi_diagram.ValueVoronoiDiagram(dimensions),
        voronoi_diagram.RedSaturationVoronoiDiagram(dimensions),
        voronoi_diagram.RedValueVoronoiDiagram(dimensions),
        voronoi_diagram.SparseRedValueVoronoiDiagram(dimensions),
        # sustainobject.RandomNumber(dimensions),
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
