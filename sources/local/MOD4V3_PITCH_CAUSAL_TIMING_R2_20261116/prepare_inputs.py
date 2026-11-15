from pathlib import Path
import sys,json,hashlib,shlex,time
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
c=connect()
try:
 sf=c.open_sftp()
 def mkdir(x):
  try:sf.stat(x)
  except FileNotFoundError:mkdir(x.rsplit('/',1)[0]);sf.mkdir(x)
 try:sf.stat(REMOTE);raise RuntimeError('Existing new root; inspect first')
 except FileNotFoundError:pass
 mkdir(REMOTE)
 files=[T/x for x in ['PLAN.json','launch.py','comprehensive_keep_teacher.pt','teacher_movement_balanced_demos.pt','high_stance_comprehensive_anchors.pt','rearward_reference_dataset.pt']]+[x for x in (T/'support').rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc']
 index={}
 for x in files:
  rel=x.relative_to(T).as_posix();dst=REMOTE+'/'+rel;mkdir(dst.rsplit('/',1)[0]);sf.put(str(x),dst);index[rel]=hashlib.sha256(x.read_bytes()).hexdigest()
 sf.put(str(T/'weights/parent_comprehensive.pt'),P['parent']);index['parent_comprehensive.pt']=P['parent_sha256']
 code="from pathlib import Path;import json,hashlib;root=Path("+repr(REMOTE)+");d="+repr(index)+";assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in d.items());print(json.dumps(dict(verified_inputs=len(d),parent_sha256=d['parent_comprehensive.pt'])))"
 check=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));(T/'evidence/PROBE_INPUTS.json').write_text(json.dumps(dict(verified=check,files=index),indent=2)+'\n')
 print('R2_INPUTS_VERIFIED '+str(check),flush=True)
finally:c.close()
