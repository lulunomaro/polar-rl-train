"""Operate only this task's processes/files on the authorized Host72."""
import argparse
import json
from pathlib import Path
import shlex
import stat
import sys
import time

T = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--access-dir', required=True)
    p.add_argument('--mode', choices=['admit', 'train', 'status', 'collect'], required=True)
    p.add_argument('--job')
    p.add_argument('--num-envs', type=int, default=64)
    a = p.parse_args()
    sys.path.insert(0, a.access_dir)
    from ssh72 import connect, execute
    plan = json.loads((T / 'PLAN.json').read_bytes())
    client = connect()
    try:
        if a.mode == 'collect':
            s = client.open_sftp()
            destination = T / 'evidence'

            def visit(remote, local):
                local.mkdir(parents=True, exist_ok=True)
                for entry in s.listdir_attr(remote):
                    path = remote + '/' + entry.filename
                    if stat.S_ISDIR(entry.st_mode):
                        if entry.filename == 'kit_isolation' or entry.filename.startswith('revision_'):
                            continue
                        visit(path, local / entry.filename)
                    elif entry.filename.endswith(('.json', '.jsonl', '.log', '.npz', '.pt')):
                        target = T / 'weights' / (local.name + '__' + entry.filename) if entry.filename.endswith('.pt') else local / entry.filename
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if not target.exists() or target.stat().st_size != entry.st_size or entry.filename in ('LATEST_PROGRESS.json', 'SUPERVISION.jsonl'):
                            s.get(path, str(target))

            visit(plan['task_root'], destination / 'remote')
            s.close()
            print(json.dumps(dict(collected=True, epoch=time.time())))
            return
        if a.mode == 'status':
            script = '''
import json,subprocess
from pathlib import Path
r=Path(ROOT)
result={}
for d in sorted(r.iterdir()):
 if d.is_dir() and not d.name.startswith('revision_'):
  row={}
  for name in ('STARTUP.json','ADMISSION.json','TRAINING_STARTED.json','FIRST_UPDATE.json','LATEST_PROGRESS.json','RESULT.json','FINAL.json','ERROR.json','SAFE_CLOSED.json'):
   p=d/name
   if not p.exists():continue
   value=json.loads(p.read_bytes())
   if name=='STARTUP.json':value={k:value[k] for k in ('mode','num_envs','observation_schema','adaptation')}
   if name=='RESULT.json':value={k:value[k] for k in ('mode','summary','checkpoint_sha256','optimizer_updates')}
   if name=='FIRST_UPDATE.json':value={'changes':value['changes'],'iteration':value['iteration']}
   row[name]=value
  result[d.name]=row
result['GPU']=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout
print(json.dumps(result))
'''.replace('ROOT', repr(plan['task_root']))
        else:
            assert a.job and a.job.replace('_', '').isalnum()
            request = dict(mode=a.mode, job=a.job, num_envs=a.num_envs,
                           plan=plan['root'] + '/PLAN.json')
            script = '''
import hashlib,json,os,subprocess,time
from pathlib import Path
q=REQUEST
p=json.loads(Path(q['plan']).read_bytes())
r=Path(p['task_root']);job=r/q['job'];gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
assert not job.exists() and not (r/(q['job']+'.log')).exists()
owners=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout
assert gpu not in owners,'Training GPU occupied: '+owners
assert hashlib.sha256(Path(p['parent']).read_bytes()).hexdigest()==p['parent_sha256']
for row in p['input_manifest']:
 assert hashlib.sha256((Path(p['root'])/row['path']).read_bytes()).hexdigest()==row['sha256']
if q['mode']=='train':
 if p.get('repair_continuation'):
  assert (r/'TRAINING_OWNER.json').exists()
  assert not (r/'REPAIR_CONTINUATION_OWNER.json').exists()
  assert json.loads((r/p['invalid_segment']/'SAFE_CLOSED.json').read_bytes())['outcome']=='complete'
  assert json.loads((r/'INVALID_PHYSICS_R1.json').read_bytes())['physics_valid']==False
  assert p['budget_deadline_epoch']>time.time()
 else:assert not (r/'TRAINING_OWNER.json').exists(),'A canonical owner already exists'
 assert p['training_round']['seconds']==7200
 admission=json.loads((r/p['admission_job']/'ADMISSION.json').read_bytes())
 assert admission['passed'] and admission['source_archive_sha256']==p['source_archive_sha256']
 assert admission.get('num_envs',0)>=q['num_envs'] and admission.get('physics_console_checked')
 assert json.loads((r/p['admission_job']/'SAFE_CLOSED.json').read_bytes())['outcome']=='complete'
env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
cmd=[p['python'],'-u','-c','import sys;sys.path.insert(0,'+repr(p['root'])+');from autonomous_stair.run import main;main()', '--plan',q['plan'],'--job',str(job),'--mode',q['mode'],'--num-envs',str(q['num_envs'])]
with (r/(q['job']+'.log')).open('xb',buffering=0) as stream:
 child=subprocess.Popen(cmd,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,physical_gpu=0,job=str(job),mode=q['mode'],cmd=cmd)
(r/('LAUNCH_'+q['job']+'.json')).write_text(json.dumps(receipt,indent=2)+chr(10))
if q['mode']=='train':
 owner='REPAIR_CONTINUATION_OWNER.json' if p.get('repair_continuation') else 'TRAINING_OWNER.json'
 (r/owner).write_text(json.dumps(receipt,indent=2)+chr(10))
 with (r/('supervision_'+q['job']+'.log')).open('xb',buffering=0) as stream:
  monitor=subprocess.Popen([p['python'],'-u',str(Path(p['root'])/'supervise.py'),'--plan',q['plan'],'--train-job',str(job)],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)
 receipt['supervisor_pid']=monitor.pid
print(json.dumps(receipt))
'''.replace('REQUEST', repr(request))
        status, out, err = execute(client, 'python3 -c ' + shlex.quote(script), 30)
        assert status == 0, out + err
        value = json.loads(out)
        if a.mode in ('admit', 'train'):
            (T / 'evidence' / ('LAUNCH_' + a.job + '.json')).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')
        print(json.dumps(value, indent=2))
    finally:
        client.close()


if __name__ == '__main__':
    main()
