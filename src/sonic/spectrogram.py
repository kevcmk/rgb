#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""
import sys
import os 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rgb')))
print(sys.path)

import argparse
import math
import shutil
from imaqt import IMAQT
import numpy as np
import json
import sounddevice as sd

usage_line = ' press <enter> to quit, +<enter> or -<enter> to change scaling '


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

ima = IMAQT.factory()
mqtt_channel = os.environ.get("MIDI_INPUT_MQTT_CHANNEL", "black")
ima.connect()

columns = 80

default_device = None
default_block_duration=50    
default_gain=10
low, high = [100, 2000]

# A4 is 17
keys = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
note_state = [False for _ in range(12)]
def musical_key(index: int) -> str:
    print(f"Index: {index}" )
    return keys[(index - 5) % 12]
def midi_key(index: int) -> int:
    return (index - 5) % 12



# Create a nice output gradient using ANSI escape sequences.
# Stolen from https://gist.github.com/maurisvh/df919538bcef391bc89f
colors = 30, 34, 35, 91, 93, 97
chars = ' :%#\t#%:'
gradient = []
for bg, fg in zip(colors, colors[1:]):
    for char in chars:
        if char == '\t':
            bg, fg = fg, bg
        else:
            gradient.append('\x1b[{};{}m{}'.format(fg, bg + 10, char))


samplerate = sd.query_devices(default_device, 'input')['default_samplerate']

delta_f = (high - low) / (columns - 1)
fftsize = math.ceil(samplerate / delta_f)
low_bin = math.floor(low / delta_f)

def callback(indata, frames, time, status):
    # if status:
    #     text = ' ' + str(status) + ' '
    #     print('\x1b[34;40m', text.center(columns, '#'),
    #             '\x1b[0m', sep='')
    if any(indata):
        ms = int(time.inputBufferAdcTime * 100)
        if ms % 4 != 0:
            # Only emit 1/n of the time
            return
        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
        magnitude *= default_gain / fftsize
        
        # print(f"Max magnitude: {magnitude[np.argmax(magnitude)]}")
        # print(type(magnitude))
        # indices_above_threshold = np.where(magnitude > 0.2)[0]
        # print(type(indices_above_threshold))
        # print(f"INdices above: {indices_above_threshold}")
        # enabled_keys = np.array([musical_key(x) for x in indices_above_threshold])
        
        print(magnitude[low_bin:low_bin + columns])
        print(f"Count: {len(magnitude[low_bin:low_bin + columns])}")
        ima.client.publish(mqtt_channel, json.dumps({"message": "spectrum", "index": 0, "state": magnitude[low_bin:low_bin + columns].tolist()}))
    else:
        print('no input')

with sd.InputStream(device=default_device, channels=1, callback=callback,
                    blocksize=int(samplerate * default_block_duration / 1000),
                    samplerate=samplerate):
    while True:
        response = input()
        if response in ('', 'q', 'Q'):
            break
        for ch in response:
            if ch == '+':
                default_gain *= 2
            elif ch == '-':
                default_gain /= 2
            else:
                print('\x1b[31;40m', usage_line.center(columns, '#'),
                        '\x1b[0m', sep='')
                break