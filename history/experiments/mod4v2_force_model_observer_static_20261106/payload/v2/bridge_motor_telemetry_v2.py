"""Opt-in private motor telemetry for FUTURE new cases only.
No current runtime imports this adapter; old cases/results stay unchanged.
"""
from actuation_telemetry_v1 import ActuationTelemetryMixin
from bridge_v2 import V2Plant


class TelemetryV2Plant(ActuationTelemetryMixin, V2Plant):
    """Pass motor_telemetry=True explicitly; default is OFF.

    All q, sensor, D4, physics and contact work remains in the existing V2Plant.
    Private telemetry is not a published SensorPacket or controller input.
    """
    pass
