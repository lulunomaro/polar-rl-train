"""Admit only physically qualified MOD4 executions as 35 -> 6 skill labels."""
from pathlib import Path
import json,hashlib
import numpy as np
T=Path(__file__).resolve().parent
SOURCES=[('mod4_transfer_probe_r3','jump_force','jump'),('mod4_transfer_probe_r4','step07_full_force_traction','stair07'),('mod4_transfer_20cm_r5','step20_vmc_capture_force_balance_nominal','stair20')]

def build():
 output=T/'skill_dataset';output.mkdir(exist_ok=True)
 xs=[];ys=[];episodes=[];groups=[];entries=[]
 for episode,(folder,case,skill)in enumerate(SOURCES):
  root=T/folder;result=json.loads((root/'RESULT.json').read_text());meta=next(r for r in result['rows']if r['case']==case)
  assert meta['success'] and meta['hold_s']>=.4-1e-8 and meta['PPO_updates']==0
  assert meta['reason']=='qualified_stable_landing'
  pair=np.load(root/'paired_student_obs_actions.npz')
  x=pair[case+'_obs'].astype(np.float32);y=pair[case+'_actions'].astype(np.float32);active=pair[case+'_skill_mask'].astype(bool)
  assert x.shape==(len(y),35) and y.shape==(len(x),6) and np.isfinite(x).all() and np.isfinite(y).all() and abs(y).max()<=6.
  # The existing jump request clock is capped after the demonstrated landing phase.
  jump=x[:,-3]>.5;x[jump,-1]=np.minimum(x[jump,-1],1.5)
  group=np.where(active,1,np.where(np.arange(len(x))<np.where(active)[0][0],0,2))
  xs.append(x);ys.append(y);episodes.extend([episode]*len(x));groups.extend(group)
  entries.append(dict(episode=episode,skill=skill,source_case=case,result_file=str((root/'RESULT.json').relative_to(T)),frames=len(x),qualified=True,source_actor_sha256='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617',observation_action_file_sha256=hashlib.sha256((root/'paired_student_obs_actions.npz').read_bytes()).hexdigest()))
 obs=np.concatenate(xs);actions=np.concatenate(ys);episode=np.asarray(episodes,np.int64);phase=np.asarray(groups,np.int64)
 weights=np.zeros(len(obs),np.float32)
 for eid in np.unique(episode):
  for p in np.unique(phase[episode==eid]):
   mask=(episode==eid)&(phase==p);weights[mask]=1./mask.sum()
 weights/=weights.sum()
 path=output/'qualified_mod4_skills.npz';np.savez_compressed(path,obs=obs,actions=actions,episode=episode,phase_group=phase,sampling_weight=weights)
 manifest=dict(actor_observations=35,critic_observations=78,actions=6,action_order=['left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint'],entries=entries,frames=len(obs),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sampling='balanced successful episode and pre/active/landing groups',PPO_updates=0,student_updates=0,source_FSM_phase_added_to_actor=False,failed_trajectories_excluded=True,existing_mode_payload=['normal','stair','slope','recover','jump','jump_height_scaled5','elapsed_request_clock_capped1.5s'],limitations=['Only nominal MuJoCo teacher executions. No independent learned student validation.','200mm final teacher passed1/3 shifted starts; no full DR claim.','Nominal jump,7cm and200mm are single independent successful episodes, not train/validation splits.'])
 (output/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2));return manifest
if __name__=='__main__':build()
