"""One authorized isolated2400s native PPO launch; no restart or default promotion."""
from pathlib import Path
import sys,json,hashlib,shlex,time,traceback
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
E=T/'evidence';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def put(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not(E/'TRAIN_LAUNCH.json').exists(),'Existing launch; inspect only'
assert json.loads((E/'LOCAL_PREFLIGHT.json').read_text())['passed']
assert P['training_round']['seconds']==2400 and P['continuous_stair']['heights_m']==[.2] and not P['continuous_stair']['curriculum_enabled']
client=connect()
try:
 execute(client,P['python']+' -B -c '+shlex.quote('from pathlib import Path;p=Path('+repr(REMOTE)+');p.mkdir(parents=True,exist_ok=False);print("Isolated remote directory created")'))
 sf=client.open_sftp();uploaded={}
 def send(src,rel):
  dst=REMOTE+'/'+rel;parent=str(Path(rel).parent).replace('\\','/')
  if parent!='.':execute(client,'mkdir -p -- '+shlex.quote(REMOTE+'/'+parent))
  sf.put(str(src),dst+'.partial');sf.rename(dst+'.partial',dst);uploaded[rel]=sha(src)
 for name in ['PLAN.json','launch.py','comprehensive_keep_teacher.pt']:send(T/name,name)
 send(T/'weights/parent_comprehensive.pt','parent_comprehensive.pt')
 for f in sorted((T/'support').rglob('*')):
  if f.is_file() and '__pycache__'not in f.parts:send(f,f.relative_to(T).as_posix())
 for f in sorted((T/'skill_dataset').iterdir()):send(f,f.relative_to(T).as_posix())
 remotecheck='from pathlib import Path;import hashlib,json;p=Path('+repr(REMOTE)+');files='+repr(uploaded)+';assert all(hashlib.sha256((p/k).read_bytes()).hexdigest()==v for k,v in files.items());print(json.dumps(dict(all_hashes_match=True,files=len(files))))'
 checked=json.loads(execute(client,P['python']+' -B -c '+shlex.quote(remotecheck),timeout=60));put(E/'UPLOADED_INPUTS.json',dict(files=uploaded,remote=REMOTE,verification=checked))
 receipt=json.loads(execute(client,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+P['training_job']+' --kind train --num-envs 2048',timeout=60));put(E/'TRAIN_LAUNCH.json',receipt)
 print('REMOTE_PROCESS_LAUNCHED',receipt['pid'],'budget_seconds',2400,'Await TRAINING_CLOCK/FIRST_UPDATE before claiming updates',flush=True)
except Exception:
 put(E/'LAUNCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),automatic_restart=False));raise
finally:client.close()
