

# TODO Incorporate
def transition_ease_in(x: float) -> float:
    # When a key is pressed, the https://easings.net/#easeInCubic
    if x < 0:
        raise ValueError("Can't handle negative time")
    elif x < 1.0:
        return x ** 3
    else:
        return 1

def transition_ease_in_reverse(x: float) -> float:
    # When a key is pressed, the https://easings.net/#easeOutCubic
    if x < 0:
        raise ValueError("Can't handle negative time")
    elif x < 1.0:
        return transition_ease_in(1 - x)
    else:
        return 0    

def transition_ease_out_exponential(x: float, exponent: float = 3) -> float:
    # https://easings.net/#easeOutCubic
    if x < 0:
        raise ValueError("Can't handle negative time")
    elif x < 1.0:
        return 1 - (1-x) ** exponent
    else:
        return 1