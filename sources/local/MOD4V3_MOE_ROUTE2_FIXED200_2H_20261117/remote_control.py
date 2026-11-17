"""One explicit upload/probe/train operation; native precheck is mandatory before training."""
from pathlib import Path
import json,sys,hashlib,shlex,argparse
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
p=argparse.ArgumentParser();p.add_argument('action',choices=['upload','probe','train']);p.add_argument('--probe-job',default='native_fixed200_probe_r1');a=p.parse_args();c=connect()
try:
 if a.action=='upload':
  code="from pathlib import Path;import json;r=Path("+repr(REMOTE)+");assert not (r/"+repr(P['training_job'])+").exists();r.mkdir(parents=True,exist_ok=True)"
  execute(c,P['python']+' -B -c '+shlex.quote(code))
  files=[(T/'PLAN.json','PLAN.json'),(T/'weights/model_step000.pt','model_step000.pt'),(T/'c874_reference.pt','c874_reference.pt'),(T/'probe_samples.npz','probe_samples.npz'),(T/'deadline_watchdog.py','deadline_watchdog.py')]
  files +=[(f,f.relative_to(T).as_posix())for f in (T/'support').rglob('*')if f.is_file()and f.suffix in ['.py','.json']and'__pycache__'not in f.parts]
  hashes={}
  with c.open_sftp()as sf:
   for f,rel in files:
    target=REMOTE+'/'+rel;execute(c,'mkdir -p -- '+shlex.quote(target.rsplit('/',1)[0]));sf.put(str(f),target+'.partial');sf.posix_rename(target+'.partial',target);hashes[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
  code="from pathlib import Path;import hashlib,json;r=Path("+repr(REMOTE)+");h="+repr(hashes)+";assert all(hashlib.sha256((r/k).read_bytes()).hexdigest()==v for k,v in h.items());print(json.dumps(dict(verified=True,files=len(h))))"
  checked=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));(T/'evidence/UPLOAD.json').write_text(json.dumps(dict(hashes=hashes,verification=checked),indent=2)+'\n');print(json.dumps(checked))
 else:
  probe=a.action=='probe';jobname=a.probe_job if probe else P['training_job']
  launch=r"""from pathlib import Path
import json,subprocess,os,time,hashlib
r=Path(ROOT);p=json.loads((r/'PLAN.json').read_text());probe=PROBE;job=r/JOB
assert not job.exists()
if not probe:
 pre=json.loads((r/PROBE_JOB/'ROUTE2_NATIVE_PREFLIGHT.json').read_text());assert pre['passed'] and pre['PPO_updates']==0 and pre['optimizer_updates']==0
 assert (r/PROBE_JOB/'SAFE_CLOSED.json').exists()
 assert all(hashlib.sha256((r/'support'/k).read_bytes()).hexdigest()==v for k,v in pre['source_sha256'].items())
 assert p['authorized_PPO_seconds']==7200 and p['early_stop']['at_seconds']==2400
assert hashlib.sha256((r/'model_step000.pt').read_bytes()).hexdigest()==p['locked_v1_sha256']
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>12000,free
owners=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip().splitlines()
env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(r/'cache/warp'),XDG_CACHE_HOME=str(r/'cache'),TMPDIR=str(r/'tmp'),TMP=str(r/'tmp'),TEMP=str(r/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for d in ['cache/warp','tmp']:(r/d).mkdir(parents=True,exist_ok=True)
module='mod4v3_ppo_v1.route2_native_probe'if probe else'mod4v3_ppo_v1.route2_train'
cmd=[p['python'],'-B','-u','-m',module,'--plan',str(r/'PLAN.json'),'--mode','probe'if probe else'train','--profile','rough_scut_v1','--num-envs','2048','--seconds','0'if probe else'7200','--job',str(job)]
with (r/(job.name+'.log')).open('xb',buffering=0)as log:child=subprocess.Popen(cmd,cwd=r/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,job=str(job),probe=probe,PPO_updates=0,optimizer_updates=0,other_GPU_owners_preserved=owners)
if not probe:
 with (r/'watchdog.log').open('xb',buffering=0)as log:guard=subprocess.Popen([p['python'],'-B','-u',str(r/'deadline_watchdog.py'),str(r),str(child.pid)],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
 receipt['watchdog_pid']=guard.pid
(r/(job.name+'_LAUNCH.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
""".replace('PROBE_JOB',repr(a.probe_job)).replace('ROOT',repr(REMOTE)).replace('PROBE',repr(probe)).replace('JOB',repr(jobname))
  result=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(launch)));(T/'evidence'/(jobname+'_LAUNCH.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
finally:c.close()
