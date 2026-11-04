"""One bounded metadata observer after W2 has CLOSED. No admission/lock/GPU/model operations."""
from pathlib import Path
import json,time,sys,shlex
D=Path(__file__).resolve().parent
marker=D/'FDN_AFTER_W2_ORIGINAL_AUTHORITY_WATCH_ONCE.json';report=D/'FDN_AFTER_W2_ORIGINAL_AUTHORITY_WATCH_RESULT.json'
assert not marker.exists() and not report.exists()
closed=str(D/'reports'/'FDN_W2_20261104_180353'/'CLOSED_RESULT.json');assert Path(closed).is_file()  # Original inner+outer actual waits already collected before this script was created.
marker.write_text(json.dumps(dict(epoch=time.time(),purpose='observe original canonical owner None after CLOSED W2; not an extension/replay of its 1800s admission window',closed_result_pointer=closed,interval_seconds=30,max_observer_seconds=1800,read_only=True),indent=2),encoding='utf8')
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code='''from pathlib import Path
import json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');until=time.monotonic()+1800;last=None;gaps=0;v=None
while time.monotonic()<until:
 try:
  c=json.loads(p.read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026';a=c['active_segment'];owner=None if a is None else {k:a[k] for k in ('owner_run_id','owner_parent_pid','started_epoch') if k in a};v=dict(epoch=time.time(),owner=owner,remaining_training_seconds=c['remaining_training_seconds'],charged_training_seconds=c['charged_training_seconds']);key=json.dumps(owner,sort_keys=True)
  if key!=last:print(json.dumps(dict(event='OWNER_METADATA_CHANGE',**v)),flush=True);last=key
  if a is None:print(json.dumps(dict(event='FINAL',status='ORIGINAL_CANONICAL_OWNER_NONE_OBSERVED',**v,reader_gaps=gaps,read_only=True,locks_GPU_models_SDK_or_canonical_writes=0,does_not_prove_GPU_or_lock_eligibility=True)),flush=True);break
 except (json.JSONDecodeError,KeyError,AssertionError) as e:
  gaps+=1
  if gaps>=3:raise RuntimeError('Original canonical schema/read integrity gap; never infer release') from e
 time.sleep(30)
else:print(json.dumps(dict(event='FINAL',status='BOUNDED_READONLY_OBSERVER_EXPIRED',latest_metadata=v,reader_gaps=gaps,read_only=True,locks_GPU_models_SDK_or_canonical_writes=0)),flush=True)
'''
c=connect72();lines=[]
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1900);i.close()
 for line in o:
  x=line.strip()
  if x:lines.append(x);print(x,flush=True)
 err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(epoch=time.time(),returncode=rc,events=[json.loads(x) for x in lines],stderr=err,no_admission_or_training_dispatched=True);report.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(report=str(report),returncode=rc)),flush=True);assert rc==0,err
finally:c.close()
