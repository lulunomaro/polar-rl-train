"""Launch only the explicitly authorized isolated stair-specialist run or required read-only data/probe."""
from pathlib import Path
import sys,argparse,json,hashlib,subprocess,os,time
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--kind',choices=['demo','probe','train'],required=True);p.add_argument('--num-envs',type=int,default=2048);a=p.parse_args();T=Path(__file__).resolve().parent;plan=json.loads((T/'PLAN.json').read_text());job=T/a.name;log=T/(a.name+'.log')
assert not job.exists() and not log.exists()
assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan['parent_sha256']
r=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
if r.stdout.strip():raise RuntimeError('GPU has another compute owner: '+r.stdout.strip())
env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(T/'cache/warp'),XDG_CACHE_HOME=str(T/'cache'),TMPDIR=str(T/'tmp'),TMP=str(T/'tmp'),TEMP=str(T/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for name in ['cache/warp','tmp']:(T/name).mkdir(parents=True,exist_ok=True)
cmd=[plan['python'],'-B','-u','-m','mod4v3_ppo_v1.continuous_stair_train','--plan',str(T/'PLAN.json'),'--profile','rough_scut_v1','--mode','train' if a.kind=='train' else 'probe','--job',str(job),'--num-envs',str(a.num_envs),'--seconds',str(plan['training_round']['seconds']),'--resume',plan['parent'],'--expected-parent-sha',plan['parent_sha256'],'--learning-rate','0.00003','--lr-schedule','fixed','--clip-param','0.1','--learning-epochs','3']
if a.kind=='demo':cmd+=['--teacher-demo']
if a.kind=='probe':cmd+=['--rough-probe']
with log.open('xb',buffering=0) as out:child=subprocess.Popen(cmd,cwd=T/'support',env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=out,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,name=a.name,kind=a.kind,job=str(job),log=str(log),cmd=cmd,parent_sha256=plan['parent_sha256']);(T/(a.name+'_LAUNCH.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
