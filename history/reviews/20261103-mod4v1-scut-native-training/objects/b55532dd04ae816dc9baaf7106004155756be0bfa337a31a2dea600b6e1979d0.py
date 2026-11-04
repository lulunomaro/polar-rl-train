"""Single serial control for the authorized two-hour SCUT/MOD4v1 task.

Uses the prior transport only; none of the H1 experiment entry points are called.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import hashlib

N = Path(__file__).resolve().parent
R = N / 'reports'
REPO = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
PRIOR = N.parent / 'h1_target_limit_cont_20261103/run.py'
PATTERN = r'MOD4_H1|RMPOLAR|watch|run_once_after_resume|E1.*collect|prepare_archive|single_gpu|collect_nine|collect_generic|collect_actual|stage_new|dispatch|retention|postround|standing|mod4v1_scut|mod4v1-scut|(?<![A-Za-z])PAIR[0-9_]*(?![A-Za-z])'


def put(name, value):
    with (R/name).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def local_rows():
    query = "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); $OutputEncoding = [Console]::OutputEncoding; Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|powershell|pwsh|ssh|cmd' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4"
    p = subprocess.run(['pwsh.exe','-NoProfile','-NonInteractive','-Command',query],
                       capture_output=True,text=True,encoding='utf-8',check=True)
    if p.stderr.strip(): raise RuntimeError(p.stderr)
    rows = json.loads(p.stdout) if p.stdout.strip() else []
    if isinstance(rows,dict): rows=[rows]
    byid={r['ProcessId']:r for r in rows}
    ancestors=set(); pid=os.getpid()
    while pid in byid and pid not in ancestors:
        ancestors.add(pid);pid=byid[pid]['ParentProcessId']
    selected=[]
    for row in rows:
        cmd=row.get('CommandLine') or ''
        if not re.search(PATTERN,cmd,re.I):continue
        if cmd.endswith(r'C:\Users\lulu\.cc-switch\catalog-maxfix\watcher.py'):continue
        # This exact observed E3 process only runs a local CPU MuJoCo viewer.
        # Its RMPOLAR path does not make it a remote controller or ledger writer.
        viewer = Path('F:/RMPOLAR-RL/mod4v1_e3_mujoco_view_20261104/view_current_e3_v2.py')
        if (row['ProcessId'] in (48084,4760)
                and str(row.get('CreationDate','')).startswith('2026-11-04T10:14:50.')
                and (row.get('ExecutablePath')or'').lower().endswith('pythonw.exe')
                and cmd.replace('\\','/').endswith('-B -X utf8 '+str(viewer).replace('\\','/'))
                and hashlib.sha256(viewer.read_bytes()).hexdigest() == '0b3467d7d5e54b322d3500fc13726a2c788c189b17fb20c60c1f445eefc3c3e7'):
            continue
        replay = Path('F:/RMPOLAR-RL/mod4v1_e3_stowed_startup_20261104/view_startup_replay.py')
        if (row['ProcessId'] in (49288,25156)
                and str(row.get('CreationDate','')).startswith('2026-11-04T11:18:08.')
                and (row.get('ExecutablePath')or'').lower().endswith('pythonw.exe')
                and cmd.replace('\\','/').endswith('-B '+str(replay).replace('\\','/'))
                and hashlib.sha256(replay.read_bytes()).hexdigest() == '5db111a4b8efd17f44e0bc4a48e1507045926f967c2e088fdc3fe38c14787def'):
            continue
        teleop = Path('F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/teleop_lqr_mujoco_v2.py')
        if (row['ProcessId']==3608
                and str(row.get('CreationDate',''))=='2026-11-04T16:21:45.322513+08:00'
                and (row.get('ExecutablePath')or'').replace('\\','/').lower()=='c:/users/lulu/appdata/local/programs/python/python314/pythonw.exe'
                and cmd.replace('\\','/').endswith('-B "'+str(teleop).replace('\\','/')+'"')
                and hashlib.sha256(teleop.read_bytes()).hexdigest()=='246fdac4cb8199b4a10dc553ca4fb6ed9f1884636ec6b07acbcfe2686041a56f'):
            continue
        fps = Path('F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/RM_FPS_PLAYER_V1/player.py')
        if (row['ProcessId']==48896
                and str(row.get('CreationDate',''))=='2026-11-04T17:14:26.364359+08:00'
                and (row.get('ExecutablePath')or'').replace('\\','/').lower()=='c:/users/lulu/appdata/local/programs/python/python314/pythonw.exe'
                and cmd.replace('\\','/').endswith('-B -X utf8 '+str(fps).replace('\\','/')+' --scene flat')
                and hashlib.sha256(fps.read_bytes()).hexdigest()=='6ace6a06aa73797fd5661616c10e2bd9b0cfdb6bcd2eb870e970c0377b5ba731'):
            continue
        if (row['ProcessId']==51820 and row['ParentProcessId']==36120
                and str(row.get('CreationDate',''))=='2026-11-04T20:52:04.522469+08:00'
                and (row.get('ExecutablePath')or'').replace('\\','/').lower()=='c:/users/lulu/appdata/local/programs/python/python314/pythonw.exe'
                and cmd.replace('\\','/').endswith('-B -X utf8 '+str(fps).replace('\\','/')+' --scene latest_rm --controller c2_fps')
                and hashlib.sha256(fps.read_bytes()).hexdigest()=='7ec0270a08590e3d3a46a0beb06cf225534d99a047391812efec6cc694fa82af'):
            # Exact local MuJoCo/GLFW/Tk controller; no remote or ledger client.
            continue
        scut_replay = Path(__file__).resolve().parent/'view_scut_actual_replay.py'
        if (row['ProcessId']==35988
                and str(row.get('CreationDate',''))=='2026-11-04T17:35:35.282382+08:00'
                and (row.get('ExecutablePath')or'').replace('\\','/').lower()=='c:/users/lulu/appdata/local/programs/python/python314/pythonw.exe'
                and cmd.replace('\\','/').endswith('-B -X utf8 '+str(scut_replay).replace('\\','/'))
                and hashlib.sha256(scut_replay.read_bytes()).hexdigest()=='5ff56762718baf51d198a49984bcfd1e186655049008b7b22647e30df804ac52'):
            continue
        if row['ProcessId'] in ancestors and row['ProcessId']!=os.getpid():continue
        if row['ParentProcessId']==os.getpid():continue
        selected.append(row)
    return selected


@contextmanager
def connection(label):
    spec=importlib.util.spec_from_file_location('scut_original_transport_only',PRIOR)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.R=R;module.local_rows=local_rows
    module.put=lambda name,value,root=None: put(name,value)
    with module.connection(label) as pair:
        yield pair


ADMIT = '''from pathlib import Path
import json,time,fcntl,psutil
base=Path('/home/lc01/Zonglin Li/zonglin2')
C=base/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
c=json.loads(C.read_bytes());active=c['active_segment']
peer=base/'tasks/MOD4_STANDING200_RLBPTT_V16_1793702292525110700'
docs={}
for rel in ['OWNER_STARTED.json','OWNER_EXIT.json','TRAIN_CLOSED.json','EVAL_WAITED.json']:
 p=peer/rel
 docs[rel]=json.loads(p.read_bytes()) if p.is_file() else None
identity=None
if psutil.pid_exists(1538723):
 p=psutil.Process(1538723)
 identity=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
locks={}
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',base/'state/finite_environment_validation.lock']:
 try:
  with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  locks[str(p)]=True
 except BlockingIOError:locks[str(p)]=False
paths={}
for rel in ['tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/runtime/isaac/mod4',
 'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/lib',
 'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/sm_deps',
 'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/assets',
 'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/original_run_manifest.json',
 'tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/E0/production/model_final_complete.pt']:
 p=base/rel;paths[str(p)]=dict(exists=p.exists(),isdir=p.is_dir(),bytes=p.stat().st_size if p.is_file() else None)
print(json.dumps(dict(epoch=time.time(),canonical_active=active,remaining=c['remaining_training_seconds'],
 generation=c['authority_generation'],strictreserve=86412.86069250107,locks=locks,peer=docs,peer_exact_current=identity,
 paths=paths,PT_reads=0,SDK_imports=0,physics=0,GPU_scans=0,canonical_writes=0)))'''


def admit():
    assert not (R/'RESOURCE_ADMISSION_ONCE.json').exists()
    # Fresh local gate occurs inside connection before any network operation.
    with connection('RESOURCE_ADMISSION') as (client,deploy):
        put('RESOURCE_ADMISSION_ONCE.json',dict(epoch=time.time(),purpose='fresh original canonical exact-peer and lock admission',new_training_seconds=7200,exit_headroom_seconds=300))
        value=deploy.code(client,deploy.PY72,ADMIT,{},timeout=45)
        put('RESOURCE_ADMISSION_ACTUAL.json',value)
    print(json.dumps(value,ensure_ascii=False,indent=2))


def metadata():
    code = '''from pathlib import Path
import json,time
b=Path('/home/lc01/Zonglin Li/zonglin2');s=b/'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400'
c=json.loads((b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes())
assert c['active_segment'] is None,'Canonical busy; metadata only'
names=['runtime/isaac/mod4/train_mod4v1_e0.py','runtime/isaac/mod4/launcher_mod4v1_e0.py','runtime/isaac/mod4/mod4v1_fresh_dr_guard.py','runtime/isaac/mod4/pose_cache_runtime_adapter_v4.py','sm_deps/pose_cache_runtime_adapter_v4.py','source/pose_cache_runtime_adapter_v4.py','control/single_writer72_authority_V85M_source.py','runtime/isaac/mod4/mod4_task.py']
print(json.dumps(dict(epoch=time.time(),active=None,files={name:dict(exists=(s/name).exists(),bytes=(s/name).stat().st_size if (s/name).is_file() else None) for name in names},PT_reads=0,physics=0)))'''
    with connection('NATIVE_STAGE_METADATA01') as (client,d):
        value=d.code(client,d.PY72,code,{},timeout=40)
        put('NATIVE_STAGE_METADATA01.json',value)
    print(json.dumps(value,indent=2))


def launch():
    index=json.loads((N/'INDEX_SOURCE_FROZEN.json').read_bytes())
    plan=json.loads((N/'PLAN.json').read_bytes());job=plan['remote_root']
    assert not (R/'LAUNCH_ONCE.json').exists()
    for row in index['files']:
        raw=Path(row['path']).read_bytes()
        assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'],row['path']
    with connection('LAUNCH02') as (client,d):
        check='''from pathlib import Path
import json,time,hashlib
b=Path('/home/lc01/Zonglin Li/zonglin2');c=json.loads((b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes())
assert c['active_segment'] is None,'Canonical active; no new namespace or GO'
shared=b/'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400'
names=['runtime/isaac/mod4/train_mod4v1_e0.py','runtime/isaac/mod4/launcher_mod4v1_e0.py','runtime/isaac/mod4/mod4_task.py','runtime/isaac/mod4/mod4v1_fresh_dr_guard.py','source/pose_cache_runtime_adapter_v4.py','control/three_slot_common_v1.py','control/single_writer72_authority_V85M_source.py','original_run_manifest.json']
rows=[]
for name in names:
 p=shared/name;raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
job=Path(v['job']);job.mkdir(exist_ok=False)
print(json.dumps(dict(epoch=time.time(),active=None,shared_text=rows,job_created=str(job),PT_reads=0,physics=0)))'''
        actual=d.code(client,d.PY72,check,dict(job=job),timeout=40)
        put('STAGE_SHARED_ACTUAL.json',actual)
        put('LAUNCH_ONCE.json',dict(epoch=time.time(),remote=job,index_SHA=hashlib.sha256((N/'INDEX_SOURCE_FROZEN.json').read_bytes()).hexdigest()))
        sf=client.open_sftp()
        try:
            def upload(relative,raw):
                path=job+'/'+relative;parts=relative.split('/')[:-1];cursor=job
                for part in parts:
                    cursor+='/'+part
                    try:sf.mkdir(cursor)
                    except OSError:sf.stat(cursor)
                with sf.file(path,'wx')as f:f.write(raw);f.flush()
            for row in index['files']:upload(row['relative'],Path(row['path']).read_bytes())
            manifest=dict(files=[{k:row[k]for k in ('relative','bytes','SHA')}for row in index['files']],
                shared_text=actual['shared_text']+index.get('shared_text',[]))
            data=json.dumps(manifest,indent=2).encode();upload('INSTALL_MANIFEST.json',data)
            put('INSTALL_MANIFEST_LOCAL.json',manifest)
        finally:sf.close()
        start='''from pathlib import Path
import json,subprocess,time,psutil
j=Path(v['job'])
with (j/'OWNER.log').open('xb') as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(j/'owner.py')],cwd=j,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 q=psutil.Process(p.pid)
 print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd())))'''
        owner=d.code(client,d.PY72,start,dict(job=job),timeout=30);put('OWNER_LAUNCH.json',owner)
        print(json.dumps(dict(owner=owner,remote=job),ensure_ascii=False),flush=True)
        # Sole finite FIRST observation, no second SSH/controller.
        put('FIRST_ONCE.json',dict(epoch=time.time(),owner=owner,maxwait=900))
        for attempt in range(45):
            code='''from pathlib import Path
import json,time,psutil
j=Path(v['job']);out={}
for rel in ['GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','OWNER_CURRENT.json','WORKER_IDENTITY.json','OWNER_EXIT.json','OWNER_ERROR.json','production/FINETUNE_INITIALIZATION.json','production/FULL_STATE_RESTORE.json','production/STARTUP.json','production/FIRST_UPDATED.json','production/ERROR.json','production/FINAL.json','TRAIN_CLOSED.json']:
 p=j/rel
 if p.exists():
  try:out[rel]=json.loads(p.read_bytes())
  except json.JSONDecodeError:pass
for rel in ['OWNER.log','WORKER.log']:
 p=j/rel
 if p.exists():
  with p.open('rb')as f:f.seek(max(0,p.stat().st_size-12000));out[rel]=f.read().decode('utf-8','replace')
if 'production/FIRST_UPDATED.json'in out:
 import hashlib
 p=j/'WORKER.log';raw=p.read_bytes()
 out['WORKER_COMPLETE.log']=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'))
print(json.dumps(dict(epoch=time.time(),files=out)))'''
            value=d.code(client,d.PY72,code,dict(job=job),timeout=30)
            if 'production/FIRST_UPDATED.json'in value['files']or 'OWNER_EXIT.json'in value['files']:
                put('FIRST_ACTUAL_RETURNED.json',value)
                print(json.dumps(value,ensure_ascii=False,indent=2),flush=True);break
            if attempt%3==0:
                print(json.dumps(dict(wait=attempt,epoch=value['epoch'],files=list(value['files']),tail=value['files'].get('WORKER.log','')[-500:])),flush=True)
            time.sleep(20)
        else:
            put('FIRST_PENDING_OR_ERROR.json',value)
            print(json.dumps(dict(pending=True,remote=job,files=list(value['files']))),flush=True)


def ray_source():
    code='''from pathlib import Path
import json
p=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/sensors/ray_caster/ray_caster.py')
print(json.dumps(dict(path=str(p),text=p.read_text(),physics=0,PT_reads=0)))'''
    with connection('ACTUAL_RAY_SOURCE01') as (client,d):
        value=d.code(client,d.PY72,code,{},timeout=40)
        put('ACTUAL_RAY_SOURCE01.json',value)
    lines=value['text'].splitlines()
    for i,line in enumerate(lines):
        if any(s in line for s in ['meshes','mesh_prim_paths','raycast_mesh','warp_mesh']):
            print(str(i+1)+': '+line)


def ray_backend():
    code='''from pathlib import Path
import json
root=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source')
files=list(root.rglob('ray_caster.py'))+list(root.rglob('base_ray_caster.py'))
print(json.dumps(dict(files={str(p):p.read_text() for p in files},PT_reads=0,physics=0)))'''
    with connection('ACTUAL_RAY_BACKEND01') as (client,d):
        value=d.code(client,d.PY72,code,{},timeout=40)
        put('ACTUAL_RAY_BACKEND01.json',value)
    for name,text in value['files'].items():
        print(name)
        for i,line in enumerate(text.splitlines()):
            if any(s in line for s in ['meshes','mesh_prim_paths','raycast_mesh','warp_mesh']):print(str(i+1)+': '+line)


def reset_source():
    code='''from pathlib import Path
import json,hashlib
s=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400')
names=['runtime/isaac/mod4/scut_flat_rescue.py','runtime/isaac/mod4/mod4v1_e0_asset_compat.py','MOD4V1_ASSET_DIFF.json']
print(json.dumps(dict(files={name:dict(text=(s/name).read_text(),bytes=(s/name).stat().st_size,SHA=hashlib.sha256((s/name).read_bytes()).hexdigest())for name in names},PT_reads=0,physics=0)))'''
    with connection('ACTUAL_RESET_SOURCE01') as (client,d):
        value=d.code(client,d.PY72,code,{},timeout=40)
        put('ACTUAL_RESET_SOURCE01.json',value)
    for name,row in value['files'].items():
        print(name)
        print(row['text'][:18000] if name.endswith('.py') else row['SHA'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['admit','metadata','launch','ray_source','ray_backend','reset_source']);args=parser.parse_args()
    globals()[args.mode]()
