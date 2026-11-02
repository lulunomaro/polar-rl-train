"""Reviewed integer-microsecond clock; 50 Hz policy control and fixed 5 ms bins."""
import math

def validate_clock(dt, control_s=.02, bin_s=.005):
    if not isinstance(dt, (int, float)) or not math.isfinite(dt) or dt not in (.0005, .001, .002, .0025, .005):
        raise ValueError('Unreviewed physical timestep')
    if abs(control_s-.02)>1e-12 or abs(bin_s-.005)>1e-12:
        raise ValueError('Control or impulse window changed')
    us=round(dt*1000000);decimation=20000//us
    if decimation*us!=20000:raise ValueError('Noninteger control clock')
    aligned=5000%us==0
    return dict(physics_dt_s=float(dt),control_period_s=control_s,policy_hz=50.,decimation=decimation,
                contact_bin_s=bin_s,contact_bin_samples=5000//us if aligned else None,
                cross_bin_required=not aligned,physics_dt_us=us,contact_bin_us=5000)

def fragments(tick, dt_us):
    if not isinstance(tick,int) or tick<1 or dt_us not in (500,1000,2000,2500,5000):raise ValueError('Invalid tick')
    start=(tick-1)*dt_us;end=start+dt_us;boundary=(start//5000+1)*5000
    if end<=boundary:return [(dt_us,end==boundary)]
    return [(boundary-start,True),(end-boundary,False)]
