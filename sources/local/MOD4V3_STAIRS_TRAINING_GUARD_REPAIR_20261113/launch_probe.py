"""One native functional replay; this launcher has no training branch."""
from pathlib import Path
import hashlib,json,subprocess,os,time
T=Path(__file__).resolve().parent;plan=json.loads((T/'PLAN.json').read_text());job=T/'native_probe_r1';log=T/'native_probe_r1.log'
assert not job.exists() and not log.exists()
assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan['parent_sha256']
gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
if gpu.stdout.strip():raise RuntimeError('GPU is still occupied: '+gpu.stdout.strip())
env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(T/'cache/warp'),XDG_CACHE_HOME=str(T/'cache'),TMPDIR=str(T/'tmp'),TMP=str(T/'tmp'),TEMP=str(T/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for n in ['cache/warp','tmp']:(T/n).mkdir(parents=True,exist_ok=True)
cmd=[plan['python'],'-B','-u','-m','mod4v3_ppo_v1.continuous_stair_train','--plan',str(T/'PLAN.json'),'--profile','rough_scut_v1','--mode','probe','--rough-probe','--job',str(job),'--num-envs','2048','--resume',plan['parent'],'--expected-parent-sha',plan['parent_sha256']]
with log.open('xb',buffering=0) as out:child=subprocess.Popen(cmd,cwd=T/'support',env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,cmd=cmd,job=str(job),log=str(log),no_optimizer_update=True,parent_sha256=plan['parent_sha256'])
(T/'NATIVE_PROBE_LAUNCH.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
