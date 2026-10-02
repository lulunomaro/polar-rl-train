"""Profile-controlled isolated entry; training requires explicit flags and original deadline."""
from pathlib import Path
import argparse,json,os,sys,runpy,time
r=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--profile',required=True);p.add_argument('--mode',choices=['evaluate','ppo_smoke','train'],default='evaluate');p.add_argument('--allow-training',action='store_true')
a,rest=p.parse_known_args();profile=Path(a.profile).resolve()
if not profile.is_file():raise SystemExit('Missing profile')
env=json.loads((r/'isaac/mod4/env.json').read_text());os.environ.update({k:str(v) for k,v in env.items()})
os.environ['RM_DR_OFF']='1';os.environ['MOD4_DR_PROFILE_PATH']=str(profile);os.environ['RM_KEEP_STD']='1'
os.environ.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
if a.mode!='evaluate':
 if not a.allow_training:raise SystemExit('Training not enabled without --allow-training')
 source=Path(json.loads((r/'candidate_contract.json').read_text())['active_source'])
 state=json.loads((source/'status.json').read_text());deadline=state['deadline_epoch']
 if time.time()>=deadline:raise SystemExit('Original budget expired')
 os.environ['RM_RESCUE_DEADLINE']=str(deadline)
 if a.mode=='ppo_smoke':
  rest += ['--additional_iterations','2','--num_envs','128','--save_interval','1','--steps_per_env','24','--run_name','explicit_dr_smoke','--log_root',str(r/'smoke_logs')]
 else:
  raise SystemExit('Full DR training needs audited live handover and large-env smoke; not armed by this delivery')
 script='train_mod4_ppo.py'
else:script='validate_speed.py'
sys.path.insert(0,str(r/'isaac/mod4'));sys.argv=[script]+rest
runpy.run_path(str(r/'isaac/mod4'/script),run_name='__main__')
