"""Launch independent native probe or once-only bounded history experiment."""
from pathlib import Path
import sys,json,argparse,subprocess,os,time,hashlib
p=argparse.ArgumentParser();p.add_argument('--kind',choices=['probe','train'],required=True);a=p.parse_args();T=Path(__file__).resolve().parent;P=json.loads((T/'PLAN.json').read_text());name=P.get('native_preflight_job','history_native_preflight') if a.kind=='probe' else P['training_job'];job=T/name;log=T/(name+'.log');assert not job.exists()and not log.exists()
assert P['training_round']['seconds']==P['budget_total_training_seconds']==2400
assert hashlib.sha256(Path(P['parent']).read_bytes()).hexdigest()==P['parent_sha256']
owners=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip();assert not owners,'GPU busy; preserve other tasks: '+owners
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>16000
if a.kind=='train':
 gate=json.loads((T/P['native_preflight_job']/'HISTORY_NATIVE_PREFLIGHT.json').read_text());assert gate['passed']and gate['optimizer_updates']==0
 assert(T/P['native_preflight_job']/'SAFE_CLOSED.json').exists()
 gate=json.loads((T/'LOCAL_READY.json').read_text());assert gate['passed']and gate['flat60_passed']==60
 (T/'TRAIN_ONCE.json').write_text(json.dumps(dict(epoch=time.time(),authorized_seconds=2400,automatic_restart=False,source_parent='original010m normal + contact history skill warmup'))+'\n',encoding='utf8')
env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(T/'cache/warp'),XDG_CACHE_HOME=str(T/'cache'),TMPDIR=str(T/'tmp'),TMP=str(T/'tmp'),TEMP=str(T/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for d in ['cache/warp','tmp']:(T/d).mkdir(parents=True,exist_ok=True)
cmd=[P['python'],'-B','-u','-m','mod4v3_ppo_v1.history_train','--plan',str(T/'PLAN.json'),'--profile','rough_scut_v1','--mode',a.kind,'--job',str(job),'--num-envs','2048','--seconds','2400','--resume',P['parent'],'--expected-parent-sha',P['parent_sha256'],'--learning-rate','0.0001','--lr-schedule','fixed','--clip-param','0.1','--learning-epochs','3']
with log.open('xb',buffering=0)as output:child=subprocess.Popen(cmd,cwd=T/'support',env=env,stdin=subprocess.DEVNULL,stdout=output,stderr=output,start_new_session=True)
if a.kind=='train':
 with(T/'deadline_watch.log').open('xb',buffering=0)as output:watch=subprocess.Popen([P['python'],'-B',str(T/'deadline_watch.py'),str(job),str(child.pid)],cwd=T,stdin=subprocess.DEVNULL,stdout=output,stderr=output,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,name=name,kind=a.kind,job=str(job),log=str(log),cmd=cmd);(T/(name+'_LAUNCH.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
