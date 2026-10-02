"""Profile-controlled isolated entry; training requires explicit flags and original deadline."""
from pathlib import Path
import argparse,json,os,sys,runpy,time
r=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--profile',required=True);p.add_argument('--mode',choices=['evaluate','ppo_smoke','train'],default='evaluate');p.add_argument('--allow-training',action='store_true');p.add_argument('--readiness')
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
 if '--init_checkpoint' not in rest:raise SystemExit('Complete warm-start checkpoint is required')
 os.environ['RM_RESCUE_DEADLINE']=str(deadline)
 if a.mode=='ppo_smoke':
  rest += ['--additional_iterations','2','--num_envs','128','--save_interval','1','--steps_per_env','24','--run_name','explicit_dr_smoke','--log_root',str(r/'smoke_logs')]
 else:
  if not a.readiness:raise SystemExit('Full DR training requires a verified readiness JSON')
  proof=json.loads(Path(a.readiness).read_text())
  import hashlib
  if proof['profile_sha256']!=hashlib.sha256(profile.read_bytes()).hexdigest():raise SystemExit('Readiness profile mismatch')
  if proof['deadline_epoch']!=deadline:raise SystemExit('Readiness budget mismatch')
  # A parameter smoke is mandatory at the actual training environment count.
  full=json.loads(Path(proof['large_env_parameter_report']).read_text())
  if not full.get('parameters_pass') or full['num_envs']!=20000:raise SystemExit('20k material/memory/parameter smoke missing')
  smoke=Path(proof['ppo_smoke_checkpoint'])
  if not smoke.is_file():raise SystemExit('PPO smoke checkpoint missing')
  pair=json.loads(Path(proof['paired_report']).read_text())
  ck=Path(rest[rest.index('--init_checkpoint')+1]).resolve()
  if str(ck)!=pair['checkpoint'] or hashlib.sha256(ck.read_bytes()).hexdigest()!=pair['sha256']:
   raise SystemExit('Paired evaluation does not cover this starting checkpoint')
  if len(pair.get('results',[]))<2:raise SystemExit('Two paired seeds required')
  if not proof.get('physics_safe_for_learning'):raise SystemExit('Physics safety audit is missing')
  for item in pair['results']:
   if not item['nominal']['accepted']:raise SystemExit('Nominal control not accepted')
  for proc in Path('/proc').glob('[0-9]*/cmdline'):
   try:args=proc.read_bytes().split(b'\0')
   except OSError:continue
   if any(x.endswith(b'/train_mod4_ppo.py') for x in args):raise SystemExit('A trainer still exists; finish safe handover first')
  rest += ['--num_envs','20000','--steps_per_env','24','--save_interval','25',
           '--additional_iterations','100000','--run_name','explicit_mild_dr','--log_root',str(r/'logs')]
 script='train_mod4_ppo.py'
else:script='validate_speed.py'
sys.path.insert(0,str(r/'isaac/mod4'));sys.argv=[script]+rest
if a.mode!='evaluate':os.execv(sys.executable,[sys.executable,str(r/'isaac/mod4'/script)]+rest)
runpy.run_path(str(r/'isaac/mod4'/script),run_name='__main__')
