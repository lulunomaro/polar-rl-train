"""Explicit yaw-rate goals. Hardware estimates are not skill acceptance."""
import math

TARGET = 4 * math.pi  # two chassis revolutions per second
LEVELS = (3., 4., 6., 8., 10., TARGET)


def validate_limit(value):
    if not any(abs(value - item) < 1e-8 for item in LEVELS):
        raise ValueError('Unregistered yaw curriculum limit')
    return value


def wheel_requirement(yaw, half_track, radius, body_speed=0.):
    if radius <= 0 or half_track <= 0:
        raise ValueError('Invalid wheel geometry')
    return (abs(yaw) * half_track + abs(body_speed)) / radius


def next_limit(value):
    i = LEVELS.index(validate_limit(value))
    return LEVELS[i + 1] if i + 1 < len(LEVELS) else None
