"""Upload only this experiment; native preflight and train are separate gates."""
from pathlib import Path
import sys,json,hashlib,shlex,argparse,time
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','probe','train','sync-source'],required=True);a=p.parse_args();E=T/'evidence'
def put(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
c=connect()
try:
 sf=c.open_sftp()
 if a.stage in ['prepare','sync-source']:
  if a.stage=='prepare':execute(c,P['python']+' -B -c '+shlex.quote('from pathlib import Path;Path('+repr(REMOTE)+').mkdir(parents=True,exist_ok=False)'))
  inputs=[T/'PLAN.json',T/'launch.py',T/'deadline_watch.py',T/'comprehensive_keep_teacher.pt',T/'weights/model_step000.pt',T/'normal_bank.npz',T/'skill_dataset/history_skills.npz',T/'skill_dataset/MANIFEST.json']+[f for f in(T/'support').rglob('*')if f.is_file()and '__pycache__'not in f.parts]
  checks={}
  for f in inputs:
   rel='model_step000.pt'if f.name=='model_step000.pt'else f.relative_to(T).as_posix();dest=REMOTE+'/'+rel;execute(c,'mkdir -p -- '+shlex.quote(dest.rsplit('/',1)[0]));sf.put(str(f),dest+'.partial');sf.posix_rename(dest+'.partial',dest);checks[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
  result=execute(c,P['python']+' -B -c '+shlex.quote('from pathlib import Path;import hashlib,json;p=Path('+repr(REMOTE)+');checks='+repr(checks)+';assert all(hashlib.sha256((p/k).read_bytes()).hexdigest()==v for k,v in checks.items());print(json.dumps(dict(passed=True,files=len(checks))))'))
  put(E/('UPLOADED_'+a.stage+'.json'),dict(epoch=time.time(),files=checks,result=json.loads(result)));print(result)
 else:
  if a.stage=='train':
   gate=json.loads((T/'preflight/LOCAL_READY.json').read_text());assert gate['passed'];sf.put(str(T/'preflight/LOCAL_READY.json'),REMOTE+'/LOCAL_READY.json')
  receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' --kind '+a.stage));put(E/('NATIVE_PREFLIGHT_LAUNCH.json'if a.stage=='probe'else'TRAIN_LAUNCH.json'),receipt);print(json.dumps(receipt),flush=True)
finally:c.close()
