"""Use saved firstepisode packets to identify early RL residual/phase deviations."""
from pathlib import Path
import hashlib
import io
import json
import time
import numpy as np

P=Path(__file__).resolve().parent;T=P.parent
N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
E=T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102'
read=lambda path:json.loads(path.read_bytes())
receipt=read(E/'reports/ROOT404_SELECTED_REPLAY_TRANSFERS.json')
command=read(N/'feedforward389.json')
table=np.asarray(command['commands'])[:,[1,0,4,3,2,5]]/np.asarray([.5,.5,.5,.5,10.,10.])
with np.load(N/'reference389.npz',allow_pickle=False)as data:reference=data['state78'].copy()
cases=[]
for row in receipt['cases']:
 raw=Path(row['local_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA']
 with np.load(io.BytesIO(raw),allow_pickle=False)as data:packet={key:data[key].copy()for key in data.files}
 count=row['controls'];phase=np.arange(count);base=table[np.minimum(phase,249)].copy();base[phase>249,4:]=0
 action=packet['action6'];delta=action-np.clip(base,-6,6);root=packet['root13']
 x,y,z,w=root[:,3:7].T;pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1))
 origin=np.asarray(row['origin']);relative=root[:,:3]-origin
 timed=[]
 for step in(0,4,9,19,29,34,39,44,count-1):
  if step>=count:continue
  label=reference[min(step,249),:3]+[.8,0,0]
  timed.append(dict(control=step+1,seconds=(step+1)*.02,root_position=relative[step].tolist(),
   reference_position=label.tolist(),pitch_rad=float(pitch[step]),
   root_velocity=root[step,7:10].tolist(),base_action=base[step].tolist(),
   applied_policy_action=action[step].tolist(),learned_residual=delta[step].tolist(),
   motor_q=packet['motor_q'][step].tolist(),motor_dq=packet['motor_dq'][step].tolist(),
   motor_pos_target=packet['motor_pos_target'][step].tolist(),motor_vel_target=packet['motor_vel_target'][step].tolist()))
 crossing=np.flatnonzero(np.abs(pitch)>.2)
 cases.append(dict(env=row['env'],seconds=row['seconds'],terminal=row['result']['episode_terminal'],
   residual_mean_abs6=np.abs(delta).mean(0).tolist(),residual_max_abs6=np.abs(delta).max(0).tolist(),
   residual_near_bound_counts6=(np.abs(delta)>.95).sum(0).tolist(),
   first_pitch_over_02_s=float((crossing[0]+1)*.02)if len(crossing)else None,
   first20_residual_mean_abs6=np.abs(delta[:20]).mean(0).tolist(),
   action_order=['crankL','hipL','crankR','hipR','wheelL','wheelR'],
   actual_motor_order=['hipL','crankL','wheelL','hipR','crankR','wheelR'],samples=timed))
native=dict(image=str(E/'RECORDED404_NATIVE_FRAMES/ACTUAL404_RL_BODY_POSE_SEQUENCE.png'),
 actual_model_native_viewed=True,
 observation='env0/40around.98s and1/41around.90-.94s airborne and strongly tilted before platform; no wholefootprint/toplanding visible',
 not_all80_visual_claim=True)
value=dict(epoch=time.time(),passed=True,scope='Saved404actualRLfirstepisodeactions/root/q/targets;0NN/SDK/physics',
 modelSHA=receipt['model_SHA'],cases=cases,native_review=native,
 hypothesis='Savedresidualmagnitude/timing versus fixedprocessedcommands may disturb learnedpush; savedfacts alone do not establish counterfactualcausality',
 next='Finite samefinal RLfullresidual versus scaledresidual contrast with explicit sameDR pair protocol; no newtraininguntil actualcontrast',
 model_reads=0,network=0,SDK=0,physics_steps=0)
path=P/'reports/DIAG406_ACTUAL_RL404_EARLY_RESIDUAL_PHASE_AND_NATIVE_REVIEW.json'
with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,cases=[{key:row[key]for key in('env','seconds','residual_mean_abs6','first20_residual_mean_abs6','first_pitch_over_02_s')}for row in cases],nativeviewed=True)),flush=True)
