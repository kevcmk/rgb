from dataclasses import dataclass
import logging

log = logging.getLogger(__name__)


@dataclass
class Dimensions:
    width: int
    height: int
 
def constrain(x, lower, upper):
    if not 0 <= x <= 1:
        log.warning(f"Input, {x}, outside of acceptable bounds of [{lower}, {upper}]")
        return min(upper, max(lower, x))
    return x