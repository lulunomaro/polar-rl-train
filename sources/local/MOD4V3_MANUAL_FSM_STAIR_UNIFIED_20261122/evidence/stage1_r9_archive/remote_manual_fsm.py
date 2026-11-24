"""Stage, guard, inspect and collect this experiment on host72 GPU 0 only."""
from argparse import ArgumentParser
from datetime import datetime, timezone
import json
from pathlib import Path, PurePosixPath
import shlex
import sys
import tarfile
from fsm_paths import HERE,LOCAL,E0_PATH,E0_SHA,donor_imports
from fsm_io import put,sha256

donor_imports()
from remote_e0 import DEPS,PITCH,PLANT,connect,execute,remote_python

REMOTE=PurePosixPath('/home/lc01/Zonglin Li/zonglin2/tasks')/HERE.name
PYTHON='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
CODE=('train_manual_fsm.py','fsm_isaac_env.py','fsm_geometry.py','fsm_io.py',
      'manual_fsm_core.py','manual_fsm_model.py','fsm_reset_sensors.py')

GUARD=r'''
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
root,job,budget,python,lr,dr_schedule=sys.argv[1:]
root=Path(root);budget=int(budget);output=root/job
uuid='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
def put(path,obj):
    tmp=path.with_suffix(path.suffix+'.partial');tmp.write_text(json.dumps(obj,indent=2));tmp.replace(path)
def inventory():
    return subprocess.check_output(['nvidia-smi','-i','0','--query-gpu=index,uuid,memory.used,utilization.gpu',
        '--format=csv,noheader,nounits'],text=True).strip()
index,gpu,memory,util=[v.strip() for v in inventory().split(',')]
apps=subprocess.check_output(['nvidia-smi','-i','0','--query-compute-apps=gpu_uuid,pid',
    '--format=csv,noheader,nounits'],text=True)
if gpu!=uuid or int(memory)>=150 or int(util)!=0 or uuid in apps:
    raise RuntimeError('Assigned GPU 0 is not idle')
if budget:
    probe=json.loads((root/'probe/PROBE.json').read_text())
    closed=json.loads((root/'probe/SAFE_CLOSED.json').read_text())
    status=json.loads((root/'probe_EXIT.json').read_text())
    assert probe['passed'] and probe['steps']==600 and probe['envs']==2048
    assert probe['optimizer_steps']==probe['ppo_updates']==0 and probe['actor_unchanged'] and probe['e0_unchanged']
    assert closed['scene_closed'] and status['exit_code']==0 and not status['hard_kill']
    put(root/'TRAIN_PRECHECK.json',dict(passed=True,probe_sha256=hashlib.sha256((root/'probe/PROBE.json').read_bytes()).hexdigest()))
with (root/(job+'.log')).open('xb',buffering=0) as log:
    worker=subprocess.Popen([python,'-B','-u',str(root/'train_manual_fsm.py'),str(output),
        '--seconds',str(budget),'--lr',lr]+(['--dr-exposure-schedule'] if dr_schedule=='1' else []),cwd=root,
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1'),
        stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
    put(root/(job+'_REMOTE_LAUNCH.json'),dict(pid=worker.pid,guard_pid=os.getpid(),gpu_uuid=uuid,
        budget_seconds=budget,epoch=time.time()))
    start=time.monotonic();hard_epoch=None;kill=False
    while worker.poll() is None:
        if (output/'TRAIN_START.json').is_file():
            hard_epoch=json.loads((output/'TRAIN_START.json').read_text())['hard_stop_epoch']
        expired=(hard_epoch is not None and time.time()>=hard_epoch)
        expired|=(hard_epoch is None and time.monotonic()-start>(1200 if budget else 1800))
        if expired:
            try:os.killpg(worker.pid,signal.SIGKILL);kill=True
            except ProcessLookupError:pass
        time.sleep(.25)
    for _ in range(40):
        if str(worker.pid) not in subprocess.check_output(['nvidia-smi','-i','0','--query-compute-apps=pid',
                '--format=csv,noheader,nounits'],text=True).split():break
        time.sleep(.25)
    released=str(worker.pid) not in subprocess.check_output(['nvidia-smi','-i','0','--query-compute-apps=pid',
        '--format=csv,noheader,nounits'],text=True).split()
    put(root/(job+'_EXIT.json'),dict(exit_code=worker.returncode,hard_kill=kill,epoch=time.time(),
        own_gpu_process_released=released,inventory=inventory()))
    if not (output/'SAFE_CLOSED.json').exists():
        output.mkdir(exist_ok=True)
        put(output/'SAFE_CLOSED.json',dict(scene_closed=False,worker_exited=True,gpu_released=released,
            guard_fallback=True,exit_code=worker.returncode))
'''

def pack(tag,checkpoint):
    folder=HERE/'evidence'/tag
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/'inputs.tar.gz'
    if path.exists():raise FileExistsError(path)
    files=[(HERE/name,name) for name in CODE]
    files += [(E0_PATH,'parent.pt'),(checkpoint,'stair.pt'),(HERE/'DETECTOR.json','DETECTOR.json')]
    if (HERE/'E0_CALIBRATION.json').is_file():files.append((HERE/'E0_CALIBRATION.json','E0_CALIBRATION.json'))
    identities=json.loads((PITCH/'PLAN.json').read_text(encoding='utf-8'))['asset_identity']
    expected={f'plant/assets/{name}':row['sha256'] for name,row in identities['actual_training_assets'].items()}
    expected['plant/mjcf/scene.xml']=identities['local_mjcf_sha256']
    for name,digest in expected.items():
        if sha256(PLANT/Path(name).relative_to('plant'))!=digest:raise ValueError(f'Plant SHA: {name}')
    if sha256(E0_PATH)!=E0_SHA:raise ValueError('SELECTED_E0 changed')
    inputs=dict(expected,**{name:sha256(src) for src,name in files})
    put(folder/'INPUTS.json',inputs)
    with tarfile.open(path,'w:gz',compresslevel=2) as tar:
        for src,dst in [(DEPS,'dependencies'),(PITCH/'support','support'),(PLANT,'plant'),
                        (LOCAL/'MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120/e0_env.py','support/mod4v3_ppo_v1/e0_env.py'),
                        (folder/'INPUTS.json','INPUTS.json'),*files]:
            tar.add(src,arcname=dst,filter=lambda item:None if '__pycache__' in item.name or item.name.endswith('.pyc') else item)
    return path

def collect(ssh,tag,job):
    remote=REMOTE/tag
    folder=HERE/'evidence'/tag
    folder.mkdir(parents=True,exist_ok=True)
    with ssh.open_sftp() as sftp:
        for suffix in ('_EXIT.json','_REMOTE_LAUNCH.json','.log'):
            try:sftp.get(str(remote/(job+suffix)),str(folder/(job+suffix)))
            except FileNotFoundError:pass
        (folder/job).mkdir(exist_ok=True)
        try:items=sftp.listdir_attr(str(remote/job))
        except FileNotFoundError:return
        for item in items:
            name=item.filename
            if name.endswith(('.json','.pt','.txt','.npz')):
                tmp=folder/job/(name+'.download')
                sftp.get(str(remote/job/name),str(tmp))
                tmp.replace(folder/job/name)
    latest=json.loads((folder/job/'LATEST.json').read_text()) if (folder/job/'LATEST.json').exists() else {}
    brief={k:latest[k] for k in ('steps','ppo_updates','optimizer_steps','elapsed_s','target_dr','active_dr','completed_by_course') if k in latest}
    print(json.dumps(dict(tag=tag,job=job,latest=brief,closed=(folder/job/'SAFE_CLOSED.json').exists()),indent=2))

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('inventory','probe','train','status','collect','stop'))
    p.add_argument('--tag',default='fsm_r1')
    p.add_argument('--checkpoint',type=Path,default=HERE/'weights/stair_bc_r1.pt')
    p.add_argument('--seconds',type=int,default=900)
    p.add_argument('--lr',type=float,default=5.e-5)
    p.add_argument('--dr-exposure-schedule',action='store_true')
    p.add_argument('--job',choices=('probe','train'),default='probe')
    args=p.parse_args()
    if not args.tag.replace('_','').isalnum():p.error('Invalid tag')
    folder=HERE/'evidence'/args.tag
    remote=REMOTE/args.tag
    with connect('host72') as ssh:
        if args.action=='inventory':
            text=execute(ssh,'nvidia-smi --query-gpu=index,uuid,name,memory.used,utilization.gpu --format=csv,noheader,nounits')
            put(HERE/'evidence/GPU_INVENTORY.json',dict(utc=datetime.now(timezone.utc).isoformat(),rows=text))
            print(text);return
        if args.action=='probe':
            bundle=pack(args.tag,args.checkpoint)
            execute(ssh,shlex.join(['mkdir','-p',str(REMOTE)]))
            execute(ssh,shlex.join(['mkdir',str(remote)]))
            with ssh.open_sftp() as sftp:
                sftp.put(str(bundle),str(remote/bundle.name))
                with sftp.open(str(remote/'guard.py'),'w') as out:out.write(GUARD)
            execute(ssh,f'cd {shlex.quote(str(remote))} && tar -xzf inputs.tar.gz',timeout=120)
        if args.action in ('probe','train'):
            job=args.action
            if args.action=='train':
                inputs=json.loads((folder/'INPUTS.json').read_text())
                differences=[name for name in CODE if sha256(HERE/name)!=inputs[name]]
                if differences:
                    put(folder/'LOCAL_WORKING_COPY_DIFFERENCES.json',dict(files=differences,
                        training_uses='immutable uploaded/prechecked snapshot',
                        final_player_equivalence_pending=True))
                collect(ssh,args.tag,'probe')
                if not json.loads((folder/'probe/PROBE.json').read_text())['passed']:
                    raise RuntimeError('Probe not passed')
            script='''import json,subprocess,sys;from pathlib import Path
root,job,budget,python,lr,dr_schedule=sys.argv[1:]
log=Path(root)/(job+'_guard.log')
with log.open('xb',buffering=0) as out:
 p=subprocess.Popen([sys.executable,str(Path(root)/'guard.py'),root,job,budget,python,lr,dr_schedule],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps(dict(guard_pid=p.pid,root=root,job=job,budget_seconds=int(budget))))
'''
            receipt=remote_python(ssh,PYTHON,script,[remote,job,0 if job=='probe' else args.seconds,PYTHON,args.lr,
                int(args.dr_exposure_schedule)])
            put(folder/(job+'_LAUNCH.json'),json.loads(receipt))
            print(receipt)
        elif args.action=='collect':collect(ssh,args.tag,args.job)
        elif args.action=='status':
            script='''import json,sys;from pathlib import Path
r=Path(sys.argv[1]);job=sys.argv[2]
for name in (job+'_REMOTE_LAUNCH.json',job+'_EXIT.json',job+'/LATEST.json',job+'/PROBE.json',job+'/ERROR.txt'):
 p=r/name
 if p.exists():print(name,p.read_text()[-6500:])
p=r/(job+'.log')
if p.exists():print('LOG_TAIL',p.read_text(errors='replace')[-3500:])
'''
            print(remote_python(ssh,PYTHON,script,[remote,args.job]))
        elif args.action=='stop':
            execute(ssh,shlex.join(['touch',str(remote/args.job/'REQUEST_STOP')]))

if __name__=='__main__':main()
