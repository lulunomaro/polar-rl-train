"""Explicit diagnostic-only V2Plant; original driver and sensor values retained.
Not selected by runtime_v2.py unless a separate diagnostic runner injects it.
"""
from actuation_telemetry_v1 import ActuationTelemetryMixin
from SENSOR_TIME_METADATA_V1.publisher import SensorTimeMetadataMixin
from bridge_v2 import V2Plant

class ObservedV2Plant(ActuationTelemetryMixin,SensorTimeMetadataMixin,V2Plant):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,motor_telemetry=True,**kwargs)
        self.configure_sensor_time_metadata(True)
