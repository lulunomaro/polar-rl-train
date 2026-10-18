"""Read existing trajectories only; preserve readiness rejection and all original results."""
from pathlib import Path
import json,time,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports'
def longest(mask):
 n=best=0
 for x in mask:n=n+1 if x else 0;best=max(best,n)
 return best
v=json.loads((R/'FIRST_SCUT_FUDAN_HOUR_LOCAL_MUJOCO_BEHAVIOR_V2_ACTUAL.json').read_bytes());rows=[]
for e in v['episodes']:
 a=np.load(e['raw']['path'])['callback'];assert a.shape[1]==46 and np.isfinite(a).all();normal=a[a[:,1]<100];j=a[(a[:,1]>=100)&(a[:,1]<180)]
 def prepared(x):return (x[:,28:30]>1).all(1)&(x[:,33]<=1)&(x[:,32]>=-.001)&(np.abs(x[:,15])<=.2)&(np.linalg.norm(x[:,13:15],axis=1)<=.2)&(np.abs(x[:,34:36])<np.pi/12).all(1)
 # Descriptive clearance/flight never grants attempt/readiness or a strict event.
 air=(j[:,28:30]<=1).all(1)&(j[:,30:32]>.005).all(1)&(j[:,32]>0)&(j[:,33]<=1)
 rows.append(dict(source=e['source'],public4_requested=e['public4_requested'],yaw=e['yaw'],strict_counts=e['counts'],ready_before_request=e['ready_before_request'],attempt_any=bool(a[:,43].any()),normal_longest_prepared_callbacks=longest(prepared(normal)),original_preparation_required=80,normal_planar_peak=float(np.linalg.norm(normal[:,13:15],axis=1).max()),normal_abs_vz_peak=float(np.abs(normal[:,15]).max()),request_both_wheel_clearance_peak_m=float(j[:,30:32].min(1).max()) if len(j) else None,request_upward_chassis_speed_peak=float(j[:,15].max()) if len(j) else None,descriptive_only_clean_air_longest_callbacks=longest(air),descriptive_only_clean_air_seconds=.0025*longest(air),first_failure=e['first_failure'],survived15s=e['survived15s'],raw=e['raw']))
out=dict(epoch=time.time(),read_only_existing_raw_no_replay=True,rows=rows,conclusion='Original attempt readiness was absent for every requested local episode, so strict0/0/0 remains. New-source two local jump trajectories show both-wheel clearance but no qualified jump or recovery. Both new normal and jump cases survive15s; old local jump prefixes stop on0.75rad tilt. Descriptive matched-local comparison only, not unique causality or PhysX qualification.',limitations=['Only two deterministic yaw variants per source/schedule; no stochastic population or significance.', 'Original local player MuJoCo .5ms/nominal PD and flat-reset geometry differ from20k PhysX DR.', 'Actual chassis body velocity and local collider/contact integration are diagnostic adapters, not source SDK numerical qualification.', 'No reference switch, threshold relaxation, readiness override, selected reset or second GPU case.'])
with (R/'FIRST_REWARD_LOCAL_TRAJECTORY_READINESS_AND_CLEARANCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(rows,indent=2))
