"""Native free-leg hold workspace including gas spring and the existing PD limits."""
import json,time,numpy as np
from scipy.optimize import brentq
from native_linearize import NativeReduced,ROOT,G
start=time.perf_counter();angles=np.linspace(-1.3,1.3,14);pitches=np.array([-.4,0.,.4]);table=[]
for pitch in pitches:
 row=[]
 for theta in angles:
  def residual(L):
   n=NativeReduced(L,L);n.terms(np.r_[0,0,pitch,theta+pitch,theta+pitch],np.zeros(5));G.set_context(n.m,n.d);active=n.q0[0]+theta;tau=G.projected('left',*active,'qfrc_bias')-G.projected('left',*active,'qfrc_passive');target=active+tau/60.;return target[0]-target[1]-.17265192458887935
  L=brentq(residual,.1155,.22,xtol=1e-8);row.append(L)
 table.append(row)
 print('WORKSPACE',float(pitch),min(row),max(row),flush=True)
(ROOT/'FREE_WORKSPACE.json').write_text(json.dumps(dict(body_theta_rad=angles.tolist(),pitch_rad=pitches.tolist(),minimum_static_free_length_m=table,method='Full native MJCF projected gravity-passive torque and exact zero-speed 60/2 PD inverse; lower target delta unchanged',wall_seconds=time.perf_counter()-start),indent=2)+chr(10))
