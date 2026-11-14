"""Operate this task's isolated runs on Host72 only."""
import argparse
import json
from pathlib import Path
import shlex
import stat
import sys
import time

T = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--access-dir', required=True)
    parser.add_argument('--mode', choices=['admit', 'train', 'evaluate', 'status', 'collect', 'stop'], required=True)
    parser.add_argument('--job')
    parser.add_argument('--num-envs', type=int, default=256)
    args = parser.parse_args()
    sys.path.insert(0, args.access_dir)
    from ssh72 import connect, execute
    plan = json.loads((T / 'PLAN.json').read_bytes())
    client = connect()
    try:
        if args.mode == 'collect':
            sftp = client.open_sftp()

            def visit(remote, local):
                local.mkdir(parents=True, exist_ok=True)
                for entry in sftp.listdir_attr(remote):
                    source = remote + '/' + entry.filename
                    if stat.S_ISDIR(entry.st_mode):
                        if entry.filename == 'kit_isolation' or entry.filename.startswith('revision_'):
                            continue
                        visit(source, local / entry.filename)
                    elif entry.filename.endswith(('.json', '.jsonl', '.log', '.npz', '.pt')):
                        target = T / 'weights' / (local.name + '__' + entry.filename) if entry.filename.endswith('.pt') else local / entry.filename
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if not target.exists() or target.stat().st_size != entry.st_size or entry.filename.endswith('.json'):
                            sftp.get(source, str(target))

            visit(plan['task_root'], T / 'evidence/remote')
            sftp.close()
            print(json.dumps(dict(collected=True, epoch=time.time())))
            return
        if args.mode == 'stop':
            script = '''
import json,time
from pathlib import Path
p=PLAN
r=Path(p['task_root'])
j=r/p['training_job']
assert j.is_dir() and (j/'TRAINING_STARTED.json').exists()
assert not (j/'SAFE_CLOSED.json').exists()
with (j/'REQUEST_STOP').open('x') as stream:stream.write('Save complete state and close at PPO update boundary'+chr(10))
print(json.dumps(dict(epoch=time.time(),job=str(j),requested=True,process_killed=False)))
'''.replace('PLAN', repr(plan))
        elif args.mode == 'status':
            script = '''
import json,subprocess
from pathlib import Path
r=Path(ROOT)
result={}
for d in sorted(r.iterdir()):
 if not d.is_dir() or d.name.startswith('revision_'):continue
 row={}
 for name in ('STARTUP.json','ADMISSION.json','TRAINING_STARTED.json','FIRST_UPDATE.json','LATEST_PROGRESS.json','RESULT.json','FINAL.json','ERROR.json','SAFE_CLOSED.json'):
  f=d/name
  if not f.exists():continue
  v=json.loads(f.read_bytes())
  if name=='STARTUP.json':v={k:v[k] for k in ('mode','num_envs','observation_schema','adaptation')}
  if name=='RESULT.json':v={k:v[k] for k in ('mode','summary','checkpoint_sha256','optimizer_updates')}
  if name=='FIRST_UPDATE.json':v={'changes':v['changes'],'iteration':v['iteration']}
  row[name]=v
 result[d.name]=row
result['GPU']=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout
print(json.dumps(result))
'''.replace('ROOT', repr(plan['task_root']))
        else:
            assert args.job and '/' not in args.job and '..' not in args.job
            request = dict(plan=plan['root'] + '/PLAN.json', mode=args.mode, job=args.job, num_envs=args.num_envs)
            script = '''
import hashlib,json,os,subprocess,time
from pathlib import Path
q=REQUEST
p=json.loads(Path(q['plan']).read_bytes())
r=Path(p['task_root'])
job=r/q['job']
assert not job.exists() and not (r/('LAUNCH_'+q['job']+'.json')).exists(),'Existing attempt cannot be replayed'
gpu_index=1 if q['mode']=='evaluate' else 0
gpu=subprocess.run(['nvidia-smi','-i',str(gpu_index),'--query-gpu=uuid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
owners=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout
assert gpu not in owners,'Requested GPU is occupied: '+owners
assert hashlib.sha256(Path(p['parent']).read_bytes()).hexdigest()==p['parent_sha256']
for row in p['input_manifest']:
 assert hashlib.sha256((Path(p['root'])/row['path']).read_bytes()).hexdigest()==row['sha256']
if q['mode']=='train':
 if p.get('repair_continuation'):
  assert (r/'TRAINING_OWNER.json').exists()
  assert not (r/('TRAINING_OWNER_R'+str(p['revision'])+'.json')).exists()
  assert json.loads((r/p['previous_training_job']/'SAFE_CLOSED.json').read_bytes())['outcome']=='complete'
  assert time.time()<p['budget_deadline_epoch']
 else:assert not (r/'TRAINING_OWNER.json').exists(),'A canonical owner already exists'
 assert p['training_round']['seconds']==7200 and q['num_envs']==2048
 admission=json.loads((r/p['admission_job']/'ADMISSION.json').read_bytes())
 assert admission['passed'] and admission['source_archive_sha256']==p['source_archive_sha256']
 assert admission['num_envs']>=q['num_envs'] and admission['physics_console_checked']
 assert json.loads((r/p['admission_job']/'SAFE_CLOSED.json').read_bytes())['outcome']=='complete'
 assert json.loads((r/p['baseline_job']/'RESULT.json').read_bytes())['checkpoint_sha256']==p['parent_sha256']
 assert json.loads((r/p['baseline_job']/'SAFE_CLOSED.json').read_bytes())['outcome']=='complete'
env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
cmd=[p['python'],'-u','-c','import sys;sys.path.insert(0,'+repr(p['root'])+');from flat_height.run import main;main()', '--plan',q['plan'],'--job',str(job),'--mode',q['mode'],'--num-envs',str(q['num_envs'])]
with (r/(q['job']+'.log')).open('xb',buffering=0) as stream:
 child=subprocess.Popen(cmd,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,physical_gpu=gpu_index,job=str(job),mode=q['mode'],cmd=cmd)
(r/('LAUNCH_'+q['job']+'.json')).write_text(json.dumps(receipt,indent=2)+chr(10))
if q['mode']=='train':
 owner='TRAINING_OWNER_R'+str(p['revision'])+'.json' if p.get('repair_continuation') else 'TRAINING_OWNER.json'
 with (r/owner).open('x') as stream:json.dump(receipt,stream,indent=2)
 with (r/('supervision_'+q['job']+'.log')).open('xb',buffering=0) as stream:
  monitor=subprocess.Popen([p['python'],'-u',str(Path(p['root'])/'supervise.py'),'--plan',q['plan'],'--train-job',str(job)],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)
 receipt['supervisor_pid']=monitor.pid
print(json.dumps(receipt))
'''.replace('REQUEST', repr(request))
        code, out, err = execute(client, 'python3 -c ' + shlex.quote(script), 40)
        assert code == 0, out + err
        value = json.loads(out)
        if args.mode not in ('status', 'collect'):
            name = 'STOP_REQUEST_' + plan['training_job'] if args.mode == 'stop' else 'LAUNCH_' + args.job
            (T / 'evidence' / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')
        print(json.dumps(value, indent=2))
    finally:
        client.close()


if __name__ == '__main__':
    main()
