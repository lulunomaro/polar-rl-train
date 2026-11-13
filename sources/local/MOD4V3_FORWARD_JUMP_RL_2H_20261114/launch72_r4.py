"""Launch only the isolated jump owner or a no-update task evaluation."""
import argparse
import json
from pathlib import Path
import shlex
import sys

T = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
parser.add_argument('--mode',choices=['admit','train','evaluate'],required=True)
parser.add_argument('--job',required=True)
parser.add_argument('--num-envs',type=int,default=128)
parser.add_argument('--checkpoint')
parser.add_argument('--control',choices=['actor','teacher'],default='actor')
parser.add_argument('--fixed-eval',action='store_true')
args = parser.parse_args()
assert args.job.replace('_','').isalnum()
sys.path.insert(0,args.access_dir)
from ssh72 import connect,execute
plan = json.loads((T/'PLAN_R4.json').read_bytes())
gpu = 0 if args.mode in ('train','admit') else 1
uuid = ['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'][gpu]
request = dict(root=plan['root'],python=plan['python'],mode=args.mode,job=args.job,num_envs=args.num_envs,
               checkpoint=args.checkpoint,control=args.control,gpu=gpu,uuid=uuid,fixed_eval=args.fixed_eval)
assert not args.fixed_eval or (args.mode=='evaluate' and args.control=='actor' and args.checkpoint)
script = '''
import hashlib,json,os,subprocess,time
from pathlib import Path
q=REQUEST
r=Path(q['root']);plan=json.loads((r/'PLAN_R4.json').read_text())
job=r/q['job'];log=r/(q['job']+'.log')
assert not job.exists() and not log.exists()
owners=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout
assert q['uuid'] not in owners,'Selected GPU has an existing compute owner: '+owners
assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan['parent_sha256']
if q['mode']=='train':
    admission=json.loads((r/'admit_r2/ADMISSION.json').read_text())
    assert admission['passed']
    assert plan['training_round']['seconds']==7200 and plan['optimizer_owners']==1
    assert q['num_envs']==plan['training_round']['num_envs'] and q['control']=='actor'
    assert not plan.get('draft',True),'R4final input binding required'
    previous=json.loads((r/'train_cont_r3/SAFE_CLOSED.json').read_text())
    assert previous['outcome']=='complete'
    assert time.time()<plan['original_training_start_epoch']+7200
    assert not (r/'CONTINUATION_OWNER_R4.json').exists(),'A continuation owner is already recorded'
env=dict(os.environ,CUDA_VISIBLE_DEVICES=q['uuid'],PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
cmd=[q['python'],'-u','-c','import sys; sys.path.insert(0,'+repr(str(r/'support_r4'))+'); from mod4v3_ppo_v1.jump_train import main; main()','--plan',str(r/'PLAN_R4.json'),'--job',str(job),'--mode',q['mode'],'--num-envs',str(q['num_envs']),'--control',q['control']]
if q['checkpoint']:cmd+=['--checkpoint',q['checkpoint']]
if q['fixed_eval']:
    cmd=[q['python'],'-u','-c','import sys; sys.path.insert(0,'+repr(str(r/'support_r4'))+'); from mod4v3_ppo_v1.jump_eval import main; main()','--plan',str(r/'PLAN_R4.json'),'--job',str(job),'--checkpoint',q['checkpoint'],'--num-envs',str(q['num_envs'])]
with log.open('xb',buffering=0) as stream:
    child=subprocess.Popen(cmd,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,job=str(job),mode=q['mode'],control=q['control'],physical_gpu=q['gpu'],uuid=q['uuid'],cmd=cmd,training_seconds=7200 if q['mode']=='train' else 0)
(r/('LAUNCH_'+q['job']+'.json')).write_text(json.dumps(receipt,indent=2)+'\\n')
if q['mode']=='train':(r/'CONTINUATION_OWNER_R4.json').write_text(json.dumps(receipt,indent=2)+'\\n')
print(json.dumps(receipt))
'''.replace('REQUEST',repr(request))
client = connect()
try:
    status,out,err = execute(client,'python3 -c '+shlex.quote(script),30)
    print(out,err)
    assert status == 0
    receipt = json.loads(out)
    (T/'evidence'/('LAUNCH_'+args.job+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
finally:
    client.close()
