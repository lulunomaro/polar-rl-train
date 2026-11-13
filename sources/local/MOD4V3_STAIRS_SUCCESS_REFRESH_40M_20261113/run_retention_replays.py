"""Frozen paired original Rough-v1 retention replay after training releases the GPU."""
from pathlib import Path
import json,sys,hashlib,time,shlex
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute
from native_cache_lifecycle import cleanup_closed_cache
P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));REMOTE=P['root']
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def read(sf,p):
 try:
  with sf.open(p) as f:return json.loads(f.read())
 except FileNotFoundError:return None
def main(candidate):
 candidate=Path(candidate);E=T/'evidence/rough_retention';E.mkdir(exist_ok=True)
 c=connect()
 try:
  sf=c.open_sftp()
  try:sf.mkdir(REMOTE+'/retention_eval_terrain')
  except IOError:pass
  for src,rel in [(T/'rough_retention_replay.py','rough_retention_replay.py'),(T/'retention_eval_terrain/rough_scut_v1_terrain.py','retention_eval_terrain/rough_scut_v1_terrain.py'),(candidate,'retention_candidate.pt')]:
   sf.put(str(src),REMOTE+'/'+rel);digest=execute(c,'sha256sum -- '+shlex.quote(REMOTE+'/'+rel)).split()[0];assert digest==hashlib.sha256(src.read_bytes()).hexdigest()
  models=dict(parent=P['teacher_retention']['keep_teacher'],candidate=REMOTE+'/retention_candidate.pt')
  put(E/'MODELS.json',models);sf.put(str(E/'MODELS.json'),REMOTE+'/RETENTION_MODELS.json')
 finally:c.close()
 reports=[];cache_records=[];pending_cache=[REMOTE+'/train040m_success_refresh_r1']
 for skill,level in [('traverse',0),('traverse',9),('gyro',5),('landing',5)]:
  name='paired_retention_'+skill+'_L'+str(level)+'_r1';dest=E/name;dest.mkdir(exist_ok=True);job=REMOTE+'/'+name
  while True:
   c=connect()
   try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
   finally:c.close()
   if not owners:break
   time.sleep(2)
  c=connect()
  try:
   sf=c.open_sftp()
   for previous_job in pending_cache:cache_records.append(cleanup_closed_cache(c,REMOTE,previous_job,P['python']))
   pending_cache=[];put(E/'DERIVED_CACHE_LIFECYCLE.json',cache_records)
   try:sf.stat(job);exists=True
   except FileNotFoundError:exists=False
   if not exists:
    args=[P['python'],'-B','-u',REMOTE+'/rough_retention_replay.py','--plan',REMOTE+'/PLAN.json','--support',P['support'],'--out',job,'--version','continuous200mm_retained_roughv1_400Hz_wheel','--models',REMOTE+'/RETENTION_MODELS.json','--level',str(level),'--skill',skill]
    code='import subprocess,json,os;cmd='+repr(args)+';log=open('+repr(job+'.log')+',"xb",buffering=0);env=dict(os.environ);env.update(OMNI_KIT_ACCEPT_EULA="YES",ISAACSIM_ACCEPT_EULA="Y",CUDA_VISIBLE_DEVICES="0");p=subprocess.Popen(cmd,cwd='+repr(REMOTE)+',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({"pid":p.pid,"cmd":cmd}))'
    receipt=json.loads(execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code)));put(dest/'LAUNCH.json',receipt)
  finally:c.close()
  while True:
   c=connect()
   try:
    sf=c.open_sftp();closed=read(sf,job+'/SAFE_CLOSED.json')
    if closed:
     for item in sf.listdir_attr(job):
      if item.filename.endswith(('.json','.npz')):sf.get(job+'/'+item.filename,str(dest/item.filename))
     sf.get(job+'.log',str(dest/'run.log'));entry=dict(job=name,skill=skill,level=level,complete=bool(closed.get('result')) and not closed.get('error'),result=str(dest/'RESULT.json'));reports.append(entry);put(E/'STATUS.json',dict(epoch=time.time(),reports=reports));pending_cache=[job];break
   finally:c.close()
   time.sleep(5)
 while True:
  c=connect()
  try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
  finally:c.close()
  if not owners:break
  time.sleep(2)
 c=connect()
 try:
  for previous_job in pending_cache:cache_records.append(cleanup_closed_cache(c,REMOTE,previous_job,P['python']))
  put(E/'DERIVED_CACHE_LIFECYCLE.json',cache_records)
 finally:c.close()
 return reports
if __name__=='__main__':print(json.dumps(main(sys.argv[1])),flush=True)
