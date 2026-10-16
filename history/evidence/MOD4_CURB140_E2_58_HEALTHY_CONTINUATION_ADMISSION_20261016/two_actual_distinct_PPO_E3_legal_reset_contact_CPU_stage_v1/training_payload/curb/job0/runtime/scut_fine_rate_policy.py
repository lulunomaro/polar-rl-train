"""Rate-only intermediate commands after the actual 10 -> 4pi task failure."""
import math

TARGET = 4 * math.pi
LEVELS = (3., 4., 5., 6., 7., 8., 10., 11., 12., TARGET)

def validate_limit(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Nonfinite rate command')
    matches = [item for item in LEVELS if abs(value - item) < 1e-8]
    if len(matches) != 1:
        raise ValueError('Unregistered rate command')
    return matches[0]

def next_limit(value):
    index = LEVELS.index(validate_limit(value))
    return LEVELS[index + 1] if index + 1 < len(LEVELS) else None
