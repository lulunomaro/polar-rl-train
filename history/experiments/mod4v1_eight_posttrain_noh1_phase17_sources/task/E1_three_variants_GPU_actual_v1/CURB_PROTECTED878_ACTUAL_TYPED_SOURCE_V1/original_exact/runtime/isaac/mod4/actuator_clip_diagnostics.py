"""Torque diagnostics in actuator-local order, independent of policy slot order.

This does not alter the actuator or its applied torque. Mod4DCMotor first applies
the nominal hardware envelope, then episode/step gains, and finally clips again.
The diagnostic compares raw requested PD torque times those gains to final torque.
It therefore includes both envelope clips. Snapshot timing remains 10 ms.
"""


def rating_clipped(actuator, threshold=0.1):
    requested = actuator.computed_effort * actuator.episode_scale * actuator.step_scale
    return (requested - actuator.applied_effort).abs() > threshold

