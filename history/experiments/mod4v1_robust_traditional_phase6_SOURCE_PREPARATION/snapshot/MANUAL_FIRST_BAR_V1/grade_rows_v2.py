"""New private diagnostic distinguishes first flight from post-contact rebound.
Old v1 records/scores remain untouched. Same original forces/geometry bounds.
"""
from .grade_rows import BoundsRows as V1

class BoundsRows(V1):
    def bind(self,plant):
        super().bind(plant)
        self.first_flight_main_rear_crossing_s=None
    def append(self,row):
        before_first_landing=self.plant.first_landing is None
        super().append(dict(row,private_before_first_landing=bool(before_first_landing)))
        if (before_first_landing and row['air_qualified']and self.first_bar
            and self.last_bounds['exact_main_rear_x_m']>self.first_bar['back_x_m']
            and self.first_flight_main_rear_crossing_s is None):
            self.first_flight_main_rear_crossing_s=float(row['stage_time_s'])
