"""Generate feasible MOD4 reset poses using the delivered linkage solver; no physics."""
from pathlib import Path
import argparse,json,sys,importlib.util,math,hashlib
import numpy as np
p=argparse.ArgumentParser();p.add_argument("--package",required=True);p.add_argument("--out",required=True);a=p.parse_args()
package=Path(a.package);sys.path.insert(0,str(package))
import kinematics
api,legacy=kinematics._modules()
spec=json.loads((package/"semantics.json").read_text());rows=spec["coordinates"]["native_from_v2"];names=list(rows)
lo,hi=legacy.mechanical_delta_bounds("left")
# Avoid exact mechanical endpoints while preserving the usable operating branch.
grid=np.linspace(lo+1e-4,hi-1e-4,4097)
radii=[];angles0=[]
for delta in grid:
 _,pins=legacy.leg_configuration(0.,delta,side="left")
 w=pins["W"];radii.append(float(np.linalg.norm(w)));angles0.append(math.atan2(-w[0],-w[1]))
assert np.all(np.diff(radii)>0.)
max_length=float(max(radii));rng=np.random.default_rng(663321);out=[];vf=[];vr=[];lengths=[];angles=[];modes={}
def native(hip,front):
 q=np.zeros(len(names))
 for side in ["left","right"]:
  values,_=legacy.leg_configuration(hip,front,side=side,check_limits=True)
  for i,name in enumerate(names):
   row=rows[name]
   if name.startswith(side+"_") and row["source"].startswith(side+"_"):
    q[i]=values[row["source"][len(side)+1:]]+row["offset_si"]
 return q
for mode in ["normal","ground_positive","ground_negative"]:
 modes[mode]=[]
 for _ in range(1024):
  length=rng.uniform(.13,.32) if mode=="normal" else rng.uniform(.14,min(.36,max_length))
  if mode=="normal":theta=rng.uniform(-math.pi/2,3*math.pi/4)
  else:
   height=rng.uniform(-.06,.12) if mode=="ground_positive" else rng.uniform(-.06,0.)
   theta=math.acos(np.clip(height/length,-1+1e-6,1-1e-6))*(1 if mode=="ground_positive" else -1)
  delta=float(np.interp(length,radii,grid));offset=float(np.interp(delta,grid,angles0));hip=theta-offset;front=hip+delta
  q=native(hip,front);eps=1e-6
  dfront=(native(hip,front+eps)-native(hip,front-eps))/(2*eps)
  drear=(native(hip+eps,front)-native(hip-eps,front))/(2*eps)
  modes[mode].append(len(out));out.append(q.tolist());vf.append(dfront.tolist());vr.append(drear.tolist());lengths.append(length);angles.append(theta)
result=dict(summary=dict(generator="deliveredMOD4legacy.leg_configuration+1Dlength inversion; no SCUT link dimensions",seed=663321,poses=len(out),normal_length_m=[.13,.32],ground_requested_length_m=[.14,.36],ground_effective_length_m=[.14,min(.36,max_length)],native_feasible_length_m=[min(radii),max(radii)],side_tangent_epsilon=1e-6,mechanical_delta_rad=[lo,hi],source_package=str(package),source_kinematics_sha256=hashlib.sha256((package/"legacy/kinematics_v2.py").read_bytes()).hexdigest(),adaptation="reference uppergroundlength.36 exceeds MOD4 physicalreach; truncate to actual feasible max, no plant change"),joint_names=names,positions=out,velocity_front_tangent=vf,velocity_rear_tangent=vr,lengths=lengths,angles=angles,mode_indices=modes)
Path(a.out).write_text(json.dumps(result,separators=(",",":"))+"\n")
print(json.dumps(result["summary"]))
