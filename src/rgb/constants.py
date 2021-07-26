from typing import Mapping

NUM_NOTES = 12

MIDI_DIAL_MAX = 127

PAD_INDICES = [36, 38, 42, 46]
def pad(index: int, m: Mapping) -> bool:
    return m['type'] == 'note_on' and m['note'] == PAD_INDICES[index]
    
# def button_pitchdown(m: Mapping) -> bool:
#     # -128 -> -2816 -> 0
#     # {"type": "pitchwheel", "time": 0, "channel": 0, "pitch": -128, "midi_read_time": "2021-07-15 21:27:17.458029"}
#     # ...
#     # {"type": "pitchwheel", "time": 0, "channel": 0, "pitch": -2816, "midi_read_time": "2021-07-15 21:27:17.604886"}
#     # ...
#     # {"type": "pitchwheel", "time": 0, "channel": 0, "pitch": 0, "midi_read_time": "2021-07-15 21:27:17.638739"}
#     # Select first message, negative 128
#     return m.get("type", None) == "pitchwheel" and \
#         m.get("pitch", None) == -8192
        
# def button_pitchup(m: Mapping) -> bool:
#     # 128 -> 2944 (probably based on velocity) -> 0
#     # {"type": "pitchwheel", "time": 0, "channel": 0, "pitch": -128, "midi_read_time": "2021-07-15 21:27:17.458029"}
#     # ...
#     # {"type": "pitchwheel", "time": 0, "channel": 0, "pitch": -2816, "midi_read_time": "2021-07-15 21:27:17.604886"}
#     # ...
#     # {"type": "pitchwheel", "time": 0, "channel": 0, "pitch": 0, "midi_read_time": "2021-07-15 21:27:17.638739"}
#     # Select first message, positive 128
#     return m.get("type", None) == "pitchwheel" and \
#         m.get("pitch", None) == 8191
        
def button_mod(m: Mapping) -> bool:
    # Ramp from 1->18->0
    #{"type": "control_change", "time": 0, "control": 1, "value": 1, "channel": 0, "midi_read_time": "2021-07-15 21:27:21.803456"}
    #...
    #{"type": "control_change", "time": 0, "control": 1, "value": 18, "channel": 0, "midi_read_time": "2021-07-15 21:27:21.921819"}
    #...
    #{"type": "control_change", "time": 0, "control": 1, "value": 0, "channel": 0, "midi_read_time": "2021-07-15 21:27:21.974847"}
    return m.get("type", None) == "control_change" and \
        m.get("control", None) == 1 and \
        m.get("value", None) == 1
        
def button_sus(m: Mapping) -> bool:
    #{"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 0, "midi_read_time": "2021-07-15 21:27:24.211089"}
    return m.get("type", None) == "control_change" and \
        m.get("control", None) == 64 and \
        m.get("value", None) == 0