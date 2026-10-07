"""Read-only copy of actual accepted and rejected receipts and current frozen source."""
from pathlib import Path
import json,sys,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';OUT=R/'archive_actual';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S1A_HISTORY_LAUNCH_REVIEW_20261007'
c=connect()
try:
 with c.open_sftp() as s:
  index={}
  groups={
   'current':ROOT,
   'healthy_clock':'/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007',
   'accepted_sdk':'/home/egde/rl_candidates/MOD4_S1A_HISTORY_LABEL_LIFECYCLE_20261007',
   'launch_rejected':'/home/egde/rl_candidates/MOD4_S1A_MATCHED_HISTORY_TRAINING_20261007',
  }
  for name,root in groups.items():
   local=OUT/name;local.mkdir(exist_ok=True)
   names=s.listdir(root+'/reports')
   keep=[n for n in names if n.endswith('.json') and
    (name=='current' or n in ('SOURCE_FREEZE.json','HISTORY_SDK_PASSED.json','HISTORY_SDK_ATTENTION.json','history_sdk.json',
     'TEACHER_RESET_LIFECYCLE_REVIEW.json','SELECTED_CLOCK_REVIEW_READY.json','FORMAL_CLOCK_HEALTH_REVIEW.json',
     'CLOCK1000_LONGRUN_HEALTHY.json','SELECTED_CLOCK_BEHAVIOR_REVIEW.json','SELECTED_CLOCK_PPO_PREFLIGHT_PASSED.json',
     'S1A_HISTORY_ATTENTION.json','S1A_HISTORY_LAUNCHED.json','S1A_HISTORY_GUARDIAN_STARTED.json'))]
   for n in keep:
    remote=root+'/reports/'+n
    with s.open(remote,'rb') as f:raw=f.read()
    (local/n).write_bytes(raw);index[name+'/'+n]=dict(path=remote,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
  sources=OUT/'current_source';sources.mkdir(exist_ok=True)
  freeze=json.loads((OUT/'current/SOURCE_FREEZE.json').read_text())['sha256']
  for n in ('train_history_ppo.py','supervise_matched_history_launch_review_once.py','history_runtime_checkpoint.py',
    'history_actor_label_ppo.py','history_actor_ppo.py','history_latent_component.py','history_checkpoint.py',
    'history_label_adapter.py','history_observation_adapter.py','test_independent_runtime_rng.py'):
   with s.open(ROOT+'/'+n,'rb') as f:raw=f.read()
   h=hashlib.sha256(raw).hexdigest();assert h==freeze[n],n
   (sources/n).write_bytes(raw);index['current_source/'+n]=dict(path=ROOT+'/'+n,sha256=h,bytes=len(raw))
  (OUT/'ACTUAL_SOURCE_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
  print(json.dumps(dict(actual_receipts=len(index),current_source_count=len(freeze),source_exact=True)))
finally:c.close()
