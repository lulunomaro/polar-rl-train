"""Finish verified source staging after a missing optional package-index refusal; no restage."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent;OLD=B/'MOD4_S3_E1_RESET_EVIDENCE_REVIEW_20261009'
names=['isaac/mod4/e1_terrain_training_health.py','isaac/mod4/test_e1_terrain_health_cpu.py','isaac/mod4/train_e1_route_health_resume_ppo.py','supervise_e1_route_health_review.py']
source=(OLD/'prepare_route_health_recovery_once.py').read_text()
# Preserve the first preparation refusal; resume only its unexecuted upload/CPU/dispatch phase.
(R/'PREPARATION_MISSING_OPTIONAL_PACKAGE_INDEX_REJECTED.md').write_text('First staging copied all 306 original source files exactly, then refused missing E1_FROZEN_BEHAVIOR_PACKAGES.json. No new worker/CPU/PPO dispatch had run. The optional old-skill publish function is unused for this bounded route observer recovery. Original error retained; no production task changed.\n',encoding='utf8')
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+D.name;old='/home/egde/rl_candidates/'+OLD.name
try:
 with c.open_sftp() as sf:
  for n in names:sf.put(str(D/n),root+'/'+n);assert sf.open(root+'/'+n).read()==(D/n).read_bytes()
  for n in ('E1_ROUTE_TRUNCATION_SAVED_EXIT_AUDITED.json','E1_RESET_EVIDENCE_CPU_PASSED.json','REUSED_E1_NATIVE_COMPACT.json'):
   local=OLD/'reports'/n
   if local.exists():sf.put(str(local),root+'/reports/'+n)
  sf.put(str(R/'PREPARATION_MISSING_OPTIONAL_PACKAGE_INDEX_REJECTED.md'),root+'/reports/PREPARATION_MISSING_OPTIONAL_PACKAGE_INDEX_REJECTED.md')
 code=r'''
from pathlib import Path
import json,hashlib,shutil
D=Path(ROOT);OLD=Path(OLDROOT);R=D/'reports';assert not (R/'SOURCE_FREEZE.json').exists() and not (R/'E1_ROUTE_HEALTH_DISPATCH_LAUNCHED.json').exists()
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==306
for n,h in f.items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h,n
for n in ('SELECTED_E0_FOR_E1_BEHAVIOR_SOURCE.json','E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json','E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json','E1_FULL_TARGET_CPU_PASSED.json','E1_RESET_EVIDENCE_CPU_PASSED.json','REUSED_E1_NATIVE_COMPACT.json'):shutil.copy2(OLD/'reports'/n,R/n)
for a,b in (('E1_NATIVE20K_PASSED.json','REUSED_E1_NATIVE20K_PASSED.json'),('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'),('E1_ATTENTION.json','PREDECESSOR_ROUTE_HEALTH_ATTENTION_RETAINED.json')):shutil.copy2(OLD/'reports'/a,R/b)
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 # This is the exact, not-yet-executed CPU/freeze/dispatch code from the retained staging source.
 start=source.index(" code=r'''\nfrom pathlib import Path\nimport sys,json,hashlib,ast,time,torch,subprocess")
 end=source.index("'''.replace('OLDROOT'",start)
 code=source[start+len(" code=r'''\n"):end].replace('OLDROOT',repr(old)).replace('ROOT',repr(root)).replace('NEW',repr(names))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('SOURCE_FREEZE.json','E1_ROUTE_HEALTH_CPU_PASSED.json','E1_ROUTE_HEALTH_DISPATCH_LAUNCHED.json'):sf.get(root+'/reports/'+n,str(R/n))
 print(raw.decode())
finally:c.close()
