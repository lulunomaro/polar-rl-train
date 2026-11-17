"""Upload and launch the human-authorized7200s run once."""
from pathlib import Path
import sys,json,hashlib,shlex,time
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T))
from remote_run import connect,execute,P,REMOTE
assert P['PPO_training_authorized'] and P['authorized_PPO_seconds']==7200
assert not (T/'evidence/LAUNCH.json').exists()
c=connect()
try:
    execute(c,P['python']+' -B -c '+shlex.quote('from pathlib import Path;Path('+repr(REMOTE)+').mkdir(parents=True,exist_ok=False)'))
    files=[(T/'PLAN.json','PLAN.json'),(T/'weights/model_step000.pt','model_step000.pt'),(T/'c874_reference.pt','c874_reference.pt'),(T/'deadline_watchdog.py','deadline_watchdog.py')]
    files += [(f,f.relative_to(T).as_posix()) for f in (T/'support').rglob('*') if f.is_file() and f.suffix in ('.py','.json') and '__pycache__' not in f.parts]
    hashes={}
    with c.open_sftp() as sf:
        for f,rel in files:
            dest=REMOTE+'/'+rel
            execute(c,'mkdir -p -- '+shlex.quote(dest.rsplit('/',1)[0]))
            sf.put(str(f),dest+'.partial');sf.posix_rename(dest+'.partial',dest)
            hashes[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
    verify='from pathlib import Path;import hashlib,json;p=Path('+repr(REMOTE)+');h='+repr(hashes)+';assert all(hashlib.sha256((p/k).read_bytes()).hexdigest()==v for k,v in h.items());print(json.dumps(dict(verified=True,files=len(h))))'
    receipt=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(verify)))
    (T/'evidence/UPLOAD.json').write_text(json.dumps(dict(files=hashes,verification=receipt),indent=2)+'\n')
    launch=r"""from pathlib import Path
import os,subprocess,json,time
root=Path(ROOT);plan=json.loads((root/'PLAN.json').read_text());assert plan['authorized_PPO_seconds']==7200
job=root/'train_route2_2h';assert not job.exists()
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>16000,free
owners=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip().splitlines()
env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for d in ['cache/warp','tmp']:(root/d).mkdir(parents=True,exist_ok=True)
cmd=[plan['python'],'-B','-u','-m','mod4v3_ppo_v1.route2_train','--plan',str(root/'PLAN.json'),'--mode','train','--profile','rough_scut_v1','--num-envs','2048','--seconds','7200','--job',str(job)]
with (root/'train_route2_2h.log').open('xb',buffering=0) as log:
    child=subprocess.Popen(cmd,cwd=root/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
with (root/'watchdog.log').open('xb',buffering=0) as log:
    guard=subprocess.Popen([plan['python'],'-B','-u',str(root/'deadline_watchdog.py'),str(root),str(child.pid)],cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
r=dict(epoch=time.time(),pid=child.pid,watchdog_pid=guard.pid,job=str(job),requested_seconds=7200,other_GPU_owners_preserved=owners,automatic_restart=False)
(root/'LAUNCH.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
""".replace('ROOT',repr(REMOTE))
    result=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(launch)))
    (T/'evidence/LAUNCH.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:c.close()
