import os
from rgb.controlloop import ControlLoop
from rgb.form import gravity, sustainobject, voronoi_diagram
from rgb.form.sustainobject import RandomIcon, RandomWaveShape, VerticalWaves, WaveSustainObject
from rgb.utilities import loopwait
from rgb.display.tkcanvas import TkCanvas
import time

hz = 60
max_dt = 1 / hz

events = {
    20: {"type": "note_on", "note": 42, "velocity": 105},
    30: {"type": "note_on", "note": 45, "velocity": 105},
    # Sustain note 44 and 45
    35: {
        "type": "control_change",
        "time": 0,
        "control": 64,
        "value": 127,
        "channel": 0,
    },
    40: {"type": "note_on", "note": 48, "velocity": 105},
    50: {"type": "note_on", "note": 51, "velocity": 105},
    90: {"type": "note_off", "note": 42, "velocity": 105},
    100: {"type": "note_off", "note": 45, "velocity": 105},
    # Release note 44 and 45
    105: {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 0},
    110: {"type": "note_off", "note": 51, "velocity": 105},
    120: {"type": "note_off", "note": 48, "velocity": 105},
}

# events = {
#     20: {"type": "note_on", "note": 42, "velocity": 105 },
#     # Sustain note 44 and 45
#     100: {"type": "note_off", "note": 42, "velocity": 105 },

#     # Release note 44 and 45
#     150: {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 0},
# }

event_mod = max(events.keys()) + 1

# if __name__ == "__main__":
#     matrix_width = int(os.environ.get("MATRIX_WIDTH", 32))
#     matrix_height = int(os.environ.get("MATRIX_HEIGHT", 64))
#     display = TkCanvas(dimensions=(matrix_width, matrix_height))
#     # f = VerticalWaves((matrix_width, matrix_height))
#     f = RandomWaveShape((matrix_width, matrix_height))
#     i = 0
#     t_last = time.time()
#     # f.midi_handler({"type": "note_on", "note": 48, "velocity": 105 })
#     while True:
#         i += 1
#         if i % event_mod in events:
#             event = events[i % event_mod]
#             f.midi_handler(event)
#         t_last, total_elapsed_since_last_frame = loopwait(t_last=t_last, max_dt=max_dt)
#         step = f.step(total_elapsed_since_last_frame)
#         display.display(step)

if __name__ == "__main__":
    dimensions = (
        int(os.environ.get("MATRIX_WIDTH", 32)),
        int(os.environ.get("MATRIX_HEIGHT", 64)),
    )

    forms = (
        
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

    display = TkCanvas(dimensions=(32, 64))

    rgb2d = ControlLoop(display=display, forms=forms)
    rgb2d.initialize_mqtt()
    rgb2d.blocking_loop()
