"""Launch isolated owners or collect evidence with an explicit task namespace."""
import argparse
import json
from pathlib import Path
import shlex
import sys

T=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--access-dir',required=True)
p.add_argument('--mode',choices=['admit','demos','train','evaluate','status','collect'],required=True)
p.add_argument('--job',default='')
p.add_argument('--checkpoint')
p.add_argument('--num-envs',type=int,default=256)
a=p.parse_args()
sys.path.insert(0,a.access_dir)
from ssh72 import connect,execute
plan=json.loads((T/'PLAN.json').read_bytes())
root=plan['root']
client=connect()
try:
    if a.mode=='collect':
        s=client.open_sftp()
        def visit(remote,local):
            local.mkdir(parents=True,exist_ok=True)
            import stat
            for entry in s.listdir_attr(remote):
                if entry.filename in ('kit_isolation','__pycache__'): continue
                path=remote+'/'+entry.filename
                if stat.S_ISDIR(entry.st_mode): visit(path,local/entry.filename)
                elif entry.filename.endswith(('.json','.jsonl','.log','.py','.npz','.pt')):
                    destination=(T/'weights'/(a.job+'__'+entry.filename)) if entry.filename.endswith('.pt') else local/entry.filename
                    if not destination.exists() or destination.stat().st_size!=entry.st_size or entry.filename=='LATEST_PROGRESS.json':
                        s.get(path,str(destination))
        visit(root+'/'+a.job,T/'evidence'/a.job)
        s.get(root+'/'+a.job+'.log',str(T/'evidence'/a.job/'console.log'))
        for name in ('PLAN.json','TRAINING_OWNER.json'):
            try:s.get(root+'/'+name,str(T/'evidence'/('REMOTE_'+name)))
            except FileNotFoundError:pass
        s.close()
        print(json.dumps(dict(collected=a.job)))
    elif a.mode=='status':
        script='''
import json,subprocess
from pathlib import Path
r=Path(ROOT)
result={}
for d in sorted(r.iterdir()):
 if d.is_dir() and (d.name.startswith(('admit','teacher_demos','train','eval'))):
  row={}
  for f in ('TRAINING_STARTED.json','LATEST_PROGRESS.json','FIRST_UPDATE.json','FINAL.json','RESULT.json','ERROR.json','SAFE_CLOSED.json'):
   p=d/f
   if p.exists():
    v=json.loads(p.read_text())
    if f=='RESULT.json':v={k:v[k] for k in ('summary','metadata','checkpoint_sha256','iteration','optimizer_updates') if k in v}
    if f=='FIRST_UPDATE.json':v={'changes':v['changes'],'iteration':v['iteration']}
    row[f]=v
  result[d.name]=row
result['GPU']=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout
print(json.dumps(result))
'''.replace('ROOT',repr(root))
        status,out,err=execute(client,'python3 -c '+shlex.quote(script),30)
        print(out,err);assert status==0
    else:
        assert a.job and a.job.replace('_','').isalnum()
        gpu=0 if a.mode in ('train','admit') else 1
        uuid=['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'][gpu]
        request=dict(root=root,mode=a.mode,job=a.job,gpu=gpu,uuid=uuid,checkpoint=a.checkpoint,num_envs=a.num_envs)
        script='''
import hashlib,json,os,subprocess,time
from pathlib import Path
q=REQUEST
r=Path(q['root']);plan=json.loads((r/'PLAN.json').read_text());job=r/q['job'];log=r/(q['job']+'.log')
assert not job.exists() and not log.exists()
owners=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout
assert q['uuid'] not in owners,'Selected GPU occupied: '+owners
assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan['parent_sha256']
if q['mode']=='train':
 assert not (r/'TRAINING_OWNER.json').exists()
 admission=json.loads((r/'admit_repair/ADMISSION.json').read_text())
 assert admission['passed'] and json.loads((r/'admit_repair/SAFE_CLOSED.json').read_text())['outcome']=='complete'
 demos=json.loads((Path(plan['jump_bc']['dataset']).parent/'RESULT.json').read_text())
 assert demos['dataset_sha256']==plan['jump_bc']['dataset_sha256']
 nominal=[e for e in demos['episodes'] if e['nominal']]
 assert nominal and all(e['retracted'] for e in nominal) and any(e['success'] and not e['terminated'] for e in nominal)
 assert plan['training_round']['seconds']==7200
env=dict(os.environ,CUDA_VISIBLE_DEVICES=q['uuid'],PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
module={'demos':'collect_jump_demos','evaluate':'jump_eval'}.get(q['mode'],'jump_train')
cmd=[plan['python'],'-u','-c','import sys;sys.path.insert(0,'+repr(plan['support'])+');from mod4v3_ppo_v1.'+module+' import main;main()','--plan',str(r/'PLAN.json'),'--job',str(job),'--num-envs',str(q['num_envs'])]
if q['mode'] in ('train','admit'):cmd+=['--mode',q['mode']]
if q['checkpoint']:cmd+=['--checkpoint',q['checkpoint']]
with log.open('xb',buffering=0) as stream:
 child=subprocess.Popen(cmd,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,physical_gpu=q['gpu'],uuid=q['uuid'],job=str(job),mode=q['mode'],cmd=cmd)
(r/('LAUNCH_'+q['job']+'.json')).write_text(json.dumps(receipt,indent=2)+chr(10))
if q['mode']=='train':(r/'TRAINING_OWNER.json').write_text(json.dumps(receipt,indent=2)+chr(10))
print(json.dumps(receipt))
'''.replace('REQUEST',repr(request))
        status,out,err=execute(client,'python3 -c '+shlex.quote(script),30)
        print(out,err);assert status==0
        (T/'evidence'/('LAUNCH_'+a.job+'.json')).write_text(json.dumps(json.loads(out),indent=2)+'\n')
finally:client.close()
