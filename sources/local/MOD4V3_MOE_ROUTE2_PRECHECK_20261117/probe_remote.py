"""Upload this Route2 diagnostic only. There is no training launch path."""
from pathlib import Path
import sys,json,hashlib,shlex,time
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
assert not P['PPO_training_authorized'] and P['authorized_PPO_seconds']==0
job=REMOTE+'/route2_native_probe_r1';c=connect()
try:
 code="from pathlib import Path;p=Path("+repr(REMOTE)+");p.mkdir(parents=True,exist_ok=False)";execute(c,P['python']+' -B -c '+shlex.quote(code));sf=c.open_sftp();inputs=[(T/'PLAN.json','PLAN.json'),(T/'weights/model_probe.pt','model_probe.pt'),(T/'c874_reference.pt','c874_reference.pt'),(T/'probe_samples.npz','probe_samples.npz')]
 excluded={'contact_policy.py','history_train.py','history_aux.py','history_model.py','history_common.py','history_preflight.py','native_skill_bc.py'}
 inputs +=[(f,f.relative_to(T).as_posix())for f in(T/'support').rglob('*.py')if f.name not in excluded and not f.name.endswith('_train.py')and '__pycache__'not in f.parts]
 hashes={}
 for f,rel in inputs:
  dest=REMOTE+'/'+rel;execute(c,'mkdir -p -- '+shlex.quote(dest.rsplit('/',1)[0]));sf.put(str(f),dest+'.partial');sf.posix_rename(dest+'.partial',dest);hashes[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
 code="from pathlib import Path;import hashlib,json;p=Path("+repr(REMOTE)+");checks="+repr(hashes)+";assert all(hashlib.sha256((p/k).read_bytes()).hexdigest()==v for k,v in checks.items());print(json.dumps(dict(verified=True,files=len(checks))))";verified=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)))
 (T/'evidence/ROUTE2_UPLOAD.json').write_text(json.dumps(dict(files=hashes,verification=verified,scope='probe only',PPO_authorized=False),indent=2)+'\n')
 launch="""from pathlib import Path
import subprocess,os,json,time
root=Path(ROOT);plan=json.loads((root/'PLAN.json').read_text());assert not plan['PPO_training_authorized'] and plan['authorized_PPO_seconds']==0
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>16000,free
owners=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip().splitlines()
for owner in owners:
 cmd=(Path('/proc')/owner/'cmdline').read_bytes().replace(bytes([0]),b' ').decode(errors='replace');assert '/mnt/mod4_windows_data/hjq/00_integrated_transfer/train.py' in cmd,('unrecognized GPU owner',owner)
job=root/'route2_native_probe_r1';assert not job.exists();env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for d in ['cache/warp','tmp']:(root/d).mkdir(parents=True,exist_ok=True)
cmd=[plan['python'],'-B','-u','-m','mod4v3_ppo_v1.route2_native_probe','--plan',str(root/'PLAN.json'),'--mode','probe','--profile','rough_scut_v1','--num-envs','2048','--seconds','0','--job',str(job)]
with(root/'route2_native_probe_r1.log').open('xb',buffering=0)as out:child=subprocess.Popen(cmd,cwd=root/'support',env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=out,start_new_session=True)
r=dict(epoch=time.time(),pid=child.pid,job=str(job),PPO_updates=0,optimizer_updates=0,training_authorized=False,other_GPU_owners_preserved=owners);(root/'PROBE_LAUNCH.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
""".replace('ROOT',repr(REMOTE))
 receipt=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(launch)));(T/'evidence/NATIVE_PROBE_LAUNCH.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:c.close()
