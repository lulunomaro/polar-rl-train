"""Explicit MOD4 S0P clock contract:100Hz control, fixed5ms impulse bins."""
import math
def validate_clock(dt,control_s=.01,bin_s=.005):
 if not isinstance(dt,(int,float)) or not math.isfinite(dt) or dt not in (.0005,.001,.0025,.005):raise ValueError('Unreviewed physical timestep')
 if abs(control_s-.01)>1e-12 or abs(bin_s-.005)>1e-12:raise ValueError('Control or impulse window changed')
 decimation=round(control_s/dt);samples=round(bin_s/dt)
 if decimation<1 or samples<1 or abs(decimation*dt-control_s)>1e-12 or abs(samples*dt-bin_s)>1e-12:raise ValueError('Noninteger clock division')
 return dict(physics_dt_s=float(dt),control_period_s=control_s,policy_hz=100.,decimation=decimation,contact_bin_s=bin_s,contact_bin_samples=samples)
