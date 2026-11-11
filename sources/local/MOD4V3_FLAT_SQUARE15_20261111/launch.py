"""Finite original-framework launcher for the isolated Flat1.5 symmetric speed-square experiment."""
import argparse,os,json,subprocess,hashlib,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--kind',choices=['timing','evaluate','parallel','train','probe'],required=True)
p.add_argument('--checkpoint');p.add_argument('--seconds',type=int,default=2400);p.add_argument('--num-envs',type=int)
p.add_argument('--learning-rate',type=float,default=3e-5)
a=p.parse_args()
base=Path(__file__).resolve().parent
plan=json.loads((base/'PLAN.json').read_text())
job=base/a.name;log=base/(a.name+'.log');pid_file=base/(a.name+'.pid')
if any(x.exists() for x in [job,log,pid_file]):raise SystemExit('Refusing to reuse an existing job')
parent=Path(a.checkpoint) if a.checkpoint else Path(plan['parent'])
sha=hashlib.sha256(parent.read_bytes()).hexdigest()
if not a.checkpoint and sha!=plan['parent_sha256']:raise SystemExit('Parent mismatch')
# GPU is shared; only launch when no compute owner is present.
r=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
if r.stdout.strip():raise SystemExit('GPU currently owned by another compute process')
env=dict(os.environ)
root=Path(plan['root'])
env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),
    PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',
    JOINT_FRICTION_SCALE='1.0',SPRING_DAMPING_FRACTION='1.0',EXTERNAL_DR_FRACTION='1.0',OBS_NOISE_FRACTION='1.0',
    PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',
    PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',PHYSICAL_DELAY_TRACE='1' if a.kind=='timing' else '0')
mode='evaluate' if a.kind in ('evaluate','parallel') else ('train' if a.kind=='train' else 'probe')
n=a.num_envs or (4096 if a.kind=='train' else 70 if a.kind=='parallel' else 10 if a.kind=='evaluate' else 4)
cmd=[plan['python'],'-B','-u','-m','mod4v3_ppo_v1.scut_flat_train','--plan',str(base/'PLAN.json'),'--profile','flat_remaining_mixed_dr',
    '--mode',mode,'--job',str(job),'--num-envs',str(n),'--seconds',str(a.seconds),'--iterations','100000',
    '--resume',str(parent),'--expected-parent-sha',sha,'--learning-rate',str(a.learning_rate),'--lr-schedule','fixed','--clip-param','0.1','--learning-epochs','3']
if a.kind=='timing':cmd+=['--timing-probe']
if a.kind=='evaluate':cmd+=['--fixed-suite']
if a.kind=='parallel':cmd+=['--parallel-suite']
with log.open('xb',buffering=0) as out:
    child=subprocess.Popen(cmd,cwd=base/'support',env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
pid_file.write_text(str(child.pid)+'\n')
receipt=dict(epoch=time.time(),pid=child.pid,kind=a.kind,job=str(job),log=str(log),cmd=cmd,parent_sha=sha,
    env={k:v for k,v in env.items() if k.startswith(('PHYSICAL_','JOINT_FRICTION','SPRING_DAMPING','EXTERNAL_DR','OBS_NOISE'))})
(base/(a.name+'_LAUNCH.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps(receipt,ensure_ascii=False))
