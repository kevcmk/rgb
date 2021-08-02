import os
from rgb.display.hzelmatrix import HzelMatrix
from rgb.controlloop import ControlLoop
from rgb.form import (audio_spectrogram, gravity, keys, orbit, randomobject, stars, timer, basenoise)

if __name__ == "__main__":
    dimensions = (int(os.environ.get("MATRIX_WIDTH", 32)), int(os.environ.get("MATRIX_HEIGHT", 64)))
        
    forms = (
        # stripes.Stripes(dimensions),
        keys.Keys(dimensions), 
        gravity.Gravity(dimensions, 0.006), 
        gravity.GravityKeys(dimensions, 0.006), 
        gravity.GravityKeysMultiNozzle(dimensions, 0.006), 
        randomobject.RandomIcon(dimensions),
        randomobject.RandomWord(dimensions),
        randomobject.RandomJapaneseWord(dimensions),
        randomobject.RandomNumber(dimensions),
        randomobject.RandomSolidShape(dimensions), 
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
