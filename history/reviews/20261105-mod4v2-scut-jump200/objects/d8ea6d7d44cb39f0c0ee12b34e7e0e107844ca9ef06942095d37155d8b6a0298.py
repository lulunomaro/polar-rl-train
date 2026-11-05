"""Closed actual trajectory diagnosis only; no model decode or physics."""
from pathlib import Path
import json,sys,time,numpy as np
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.config import reward_config
A=N/'supermimic_final881_host_replay02_1h';R=A/'reports'
f=json.loads((R/'POSTROUND_FULL_RETURNED.json').read_bytes())['files']
rows=f['evaluation/ALL80.json']['first_episodes'];curves=f['evaluation/CONTROL_CURVES.json']['curves']
cfg=reward_config()
arr=lambda key:np.asarray([r[key]for r in curves])
active=arr('active');quat=arr('root_quat')
w,x,y,z=np.moveaxis(quat,-1,0)
roll=np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y))
pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1))
roll_lim=getattr(cfg,'termination_roll_deg',40.)
pitch_lim=getattr(cfg,'termination_pitch_deg',40.)
perenv=[]
for i,row in enumerate(rows):
    k=row['controls']-1
    perenv.append(dict(env=i,controls=row['controls'],
        terminal_roll_deg=float(np.rad2deg(roll[k,i])),terminal_pitch_deg=float(np.rad2deg(pitch[k,i])),
        pitch_violation_controls=int(((np.abs(pitch[:,i])>np.deg2rad(pitch_lim))&active[:,i]).sum()),
        roll_violation_controls=int(((np.abs(roll[:,i])>np.deg2rad(roll_lim))&active[:,i]).sum()),
        rootx=row['root_pos'][0],rootz=row['root_pos'][2],
        guide06_force=float(np.linalg.norm(np.asarray(row['contact_force'])[29])),
        leg_length=row['leg_length']))
elapsed=f['OWNER_EXIT.json']['actual_elapsed_seconds']
progress=f['production/LATEST_PROGRESS.json']
report=dict(epoch=time.time(),production_PT_reads=0,physics_steps=0,SSH=0,
    termination_cfg=dict(roll_deg=roll_lim,pitch_deg=pitch_lim,
        duration=getattr(cfg,'termination_duration',None)),per_env=perenv,
    pitch_violation_envs=sum(r['pitch_violation_controls']>0 for r in perenv),
    roll_violation_envs=sum(r['roll_violation_controls']>0 for r in perenv),
    guide06_contact_at_termination_envs=sum(r['guide06_force']>1 for r in perenv),
    episode_reward=float(arr('reward')[active].sum()/80),
    mean_control_reward=float(arr('reward')[active].mean()),
    steps=progress['sim_steps'],real_controls=progress['controls'],
    actual_hour_samples_per_seconds_including_init_save_eval=progress['sim_steps']/elapsed,
    active_dynamics_seconds_before_final=progress['epoch']-f['GO_PRODUCTION.json']['learning_started_epoch'],
    train_numerical_resets=f['production/FINAL.json']['numerical_resets'],
    train_constraint_resets=f['production/FINAL.json']['constraint_resets'],
    full_train_log_warning_counts={key:f['WORKER.log']['text'].count(key)
        for key in ('solver iterations limit reached','NEWTON_NUMERICAL_EPISODE_RESET')},
    selected_observation='Spawn fall then forward tilt/extended legs, termination before edge; no top contact or whole-wheel clearance',
    all4_native_images_reviewed=True)
with(R/'FINAL1940_FAILURE_AND_SPEED_ANALYSIS.json').open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2)
print(json.dumps({k:v for k,v in report.items()if k!='per_env'}))
