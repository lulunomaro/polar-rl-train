"""Upload and queue only the authorized continuation, without touching current PPO."""
from pathlib import Path
import sys,json,time,hashlib,shlex,subprocess,os
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
previous=T.parent/'MOD4V3_ORDERED_REARWARD_FIX_40M_20261115'
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
source_hashes={q.relative_to(T/'support').as_posix():hashlib.sha256(q.read_bytes()).hexdigest()for q in(T/'support').rglob('*')if q.is_file()and '__pycache__'not in q.parts and q.suffix!='.pyc'}
assert all(hashlib.sha256((previous/'support'/k).read_bytes()).hexdigest()==v for k,v in source_hashes.items())
put(E/'UNCHANGED_TRAINING_SOURCE.json',dict(previous=str(previous/'support'),files=source_hashes,all_source_bytes_identical=True,probe_evidence_reused=str(previous/'evidence/probe64_r1'),asset_identity=P['asset_identity']))
c=connect()
try:
 sf=c.open_sftp()
 try:sf.stat(REMOTE)
 except FileNotFoundError:sf.mkdir(REMOTE)
 else:raise RuntimeError('Continuation root already exists; inspect it, do not relaunch')
 def mkdir(p):
  try:sf.stat(p)
  except FileNotFoundError:mkdir(p.rsplit('/',1)[0]);sf.mkdir(p)
 files=[T/n for n in ['PLAN.json','PLAN_QUEUED.json','launch.py','queued_continuation.py','comprehensive_keep_teacher.pt','teacher_movement_balanced_demos.pt','high_stance_comprehensive_anchors.pt','rearward_reference_dataset.pt']]
 files +=[q for q in(T/'support').rglob('*')if q.is_file()and '__pycache__'not in q.parts and q.suffix!='.pyc']
 hashes={}
 for q in files:
  rel=q.relative_to(T).as_posix();target=REMOTE+'/'+rel;mkdir(target.rsplit('/',1)[0]);sf.put(str(q),target);hashes[rel]=hashlib.sha256(q.read_bytes()).hexdigest()
 with sf.open(REMOTE+'/UPLOADED_INPUT_SHA256.json','w')as f:f.write(json.dumps(hashes))
 code="from pathlib import Path;import json,hashlib;root=Path("+repr(REMOTE)+");d=json.loads((root/'UPLOADED_INPUT_SHA256.json').read_text());assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in d.items());print(json.dumps(dict(verified_files=len(d))))"
 verified=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)))
 put(E/'UPLOADED_INPUTS.json',dict(epoch=time.time(),sha256=hashes,verification=verified))
 code="from pathlib import Path;import subprocess,json,time;root=Path("+repr(REMOTE)+");log=(root/'queued_continuation.log').open('xb',buffering=0);child=subprocess.Popen(["+repr(P['python'])+",'-B','-u',str(root/'queued_continuation.py')],cwd=root,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True);print(json.dumps(dict(epoch=time.time(),pid=child.pid,script=str(root/'queued_continuation.py'),total_budget_seconds=7200,previous_PPO_untouched=True)))"
 launch=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));put(E/'EXTENSION_QUEUED.json',launch);print(json.dumps(launch),flush=True)
finally:c.close()
