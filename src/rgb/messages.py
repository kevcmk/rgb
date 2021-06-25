from typing import NamedTuple

class Button(NamedTuple):
    index: int
    state: bool

class Switch(NamedTuple):
    index: int
    state: bool

class Dial(NamedTuple):
    index: int
    state: float
