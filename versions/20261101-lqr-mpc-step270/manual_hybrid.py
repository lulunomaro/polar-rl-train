import json,sys,numpy as np
from hybrid_trial import run
from control_core import ROOT
base={'step':True,'duration':4.,'start_x':-.7,'start_delta':-.4,'push_at':.6,'push_for':.13,'push_delta':.4,'hip_shift':-.6,'speed':1.2,'push_kp':350,'push_kd':3,'wheel_push':3,'push_pitch':20,'push_pitch_d':4,'tuck_delta':-.95,'tuck_hip':.1,'air_kp':80,'air_kd':3,'air_pitch':35,'air_pitch_d':5,'extend_after':.28}
r,rows=run(base,True)
folder=ROOT/'results/manual_hybrid_v1';folder.mkdir(exist_ok=False);(folder/'result.json').write_text(json.dumps(r,indent=2));(folder/'trajectory.json').write_text(json.dumps(rows))
for row in rows[::10]:print(json.dumps({k:row[k] for k in ['time','xyz','state','wheel_xyz','phase','tops','nonwheel']}),flush=True)
print(json.dumps(r),flush=True)
