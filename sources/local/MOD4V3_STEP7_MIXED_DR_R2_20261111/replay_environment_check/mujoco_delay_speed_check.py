"""Frozen local MuJoCo check: same weight, reset seeds, 0/5ms delay and speed definitions."""
from pathlib import Path
import json,sys,time,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DIAG=ROOT.parent/'MOD4V3_STEP7_DELAY_DIAG_20261110'
sys.path.insert(0,str(DIAG))
from replay_delay_diagnostic import Simulation,args_for,DelayReplay,run_case
out=Path(__file__).resolve().parent
model=ROOT/'weights/model_020m.pt'
result={'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'no_optimizer':True,'modes':[]}
assert result['model_sha256']=='15775671f430cda69b1f268a230d85c5d1a74878760d26625afefb759e792c20'
for delay in [0,5]:
 sim=Simulation(args_for(str(model)));replay=DelayReplay(sim,delay,delay,'sent','sensors')
 row={'action_ms':delay,'sensor_ms':delay,'physics_dt':sim.env.dt,'plant_sha256':hashlib.sha256(Path(sim.args.xml).read_bytes()).hexdigest(),'cases':[]}
 original_step=sim.step
 speed=[]
 def step(keys):
  value=original_step(keys)
  env=sim.env;r=env.d.xmat[env.base_id].reshape(3,3);world=env.d.qvel[:3];body=r.T@world
  pitch=np.arcsin(np.clip(-r[2,0],-1.,1.))
  speed.append([float(value['vx']),float(body[0]),float(body[0]*np.cos(pitch)),float(pitch),*np.asarray(world).tolist()])
  return value
 sim.step=step
 try:
  for vx in [2.0,2.2]:
   for seed in range(10):
    speed=[]
    case=run_case(sim,replay,seed,vx,600,200)
    tail=np.asarray(speed[-200:]);pre=np.asarray(speed[180:299])
    case['speed_columns']=['horizontal_forward','body_forward','reward_body_forward_cos_pitch','pitch_rad','world_vx','world_vy','world_vz']
    case['pre_speed_mean']=pre.mean(0).tolist();case['post_speed_mean']=tail.mean(0).tolist()
    case['max_horizontal_body_difference_tail']=float(np.max(np.abs(tail[:,0]-tail[:,1])))
    row['cases'].append(case)
  result['modes'].append(row)
 finally:sim.close()
 (out/'MUJOCO_PROGRESS.json').write_text(json.dumps({'finished_delay_ms':delay}))
result['inputs_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),DIAG/'replay_delay_diagnostic.py',Path(sim.args.xml),Path(sim.args.runtime),Path(sim.args.semantics),Path(sim.args.bank)]}
(out/'MUJOCO_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for row in result['modes']:
 for vx in [2.,2.2]:
  cases=[x for x in row['cases'] if x['cmd_vx']==vx]
  print(json.dumps({'delay_ms':row['action_ms'],'command':vx,'mean_pre':np.mean([x['pre_speed_mean'] for x in cases],0).tolist(),'mean_post':np.mean([x['post_speed_mean'] for x in cases],0).tolist(),'resets':sum(x['reset_count'] for x in cases)}),flush=True)
