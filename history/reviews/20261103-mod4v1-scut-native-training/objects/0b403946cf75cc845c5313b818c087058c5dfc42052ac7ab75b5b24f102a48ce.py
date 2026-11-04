"""Prepare the human-approved new hour and use the original serial admission."""
from pathlib import Path
import argparse
import ast
import importlib.util
import json
import os
import subprocess
import time
import traceback
import hashlib

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_scut_stairs_1h_20261104'
A=P/'attempt06'
R=A/'reports'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda raw:hashlib.sha256(raw).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)


def prepare():
    B=P/'attempt05';old=read(B/'PLAN.json')
    f=read(B/'reports/FIRST_ACTUAL_RETURNED.json')['files']
    assert all(f['OWNER_EXIT.json'][k]for k in('all_own_waited','original_cost_settled','original_leases_released'))
    assert not f.get('production/FIRST_UPDATED.json')and f['TRAIN_CLOSED.json']['passed_execution']is False
    prepared=read(P/'reports/NEXT_FILTER_FIX_PREPARED.json')
    for row in prepared['files']:
        raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes']and H(raw)==row['SHA']
    A.mkdir();R.mkdir()
    authorization=dict(epoch=time.time(),human_answer='允许重新训练一小时',
        original_question='是否允许修复版继续使用同一原canonical余额，重新开一个20,000环境的一小时训练窗？',
        num_envs=20000,train_seconds=3600,exit_headroom_seconds=300,
        existing_canonical_balance_only=True,budget_grant_or_refund=False,
        original_failed_window_unchanged=True,actor_output_STD_reset=False)
    put(R/'HUMAN_NEW_HOUR_AUTHORIZATION.json',authorization)
    remote=read(P/'PLAN.json')['remote_root']+'/attempt06'
    plan=dict(old)
    for key in('original_window_run_id','original_save_deadline','original_nominal_end_epoch','original_window_extended'):
        plan.pop(key,None)
    plan.update(run_id='MOD4V1_SCUT_STAIRS_EXPLICIT_FILTER_20000ENV_1H_'+str(time.time_ns()),
        remote_root=remote,module_overlay=remote+'/overlay',
        module_overlays=[remote+'/overlay']+old['module_overlays'],
        train_seconds=3600,max_parent_seconds=3900,
        human_latest='允许重新训练一小时',human_authorization=authorization,
        repair='Explicit singleton paths for ten global collision chunks; original20k actor layout, source recipe/reward/PPO/physics preserved',
        boundary_reset='PinnedV14 globalterrain boundarytimeout; training140cols absx49.5/absy634.5; eval14cols absx49.5/absy67.5',
        prior_failure=str(B/'reports/ACTUAL_FILTER_FAILURE_FINAL_REVIEW.json'),
        newly_authorized_window=True,old_absolute_window_not_extended=True,
        new_budget_or_refund=False,pending_actual_resource_selection=True)
    put(A/'PLAN.json',plan)
    # This is a newly authorized hour. The original owner starts its absolute
    # 3600s window only after canonical, locks and measured resources admit it.
    (A/'owner.py').write_bytes((P/'owner.py').read_bytes())
    (A/'entry.py').write_bytes((B/'entry.py').read_bytes())
    files=[]
    for name in('stairs.py','sdk.py'):
        path=G/'project/isaac/mod4v1_scut'/name;raw=path.read_bytes();ast.parse(raw)
        files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
    shared=list(read(B/'INDEX_SOURCE_FROZEN.json')['shared_text'])
    for row in read(B/'INDEX_SOURCE_FROZEN.json')['files']:
        if row['relative'].startswith('overlay/'):
            shared.append(dict(path=old['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
    put(A/'SOURCE_ONLY_PREPARED.json',dict(epoch=time.time(),files=files,shared_text=shared,
        source_only=True,whole_tree_model_asset_copy=False,source_checkpoint=plan['source_checkpoint'],
        authorization=str(R/'HUMAN_NEW_HOUR_AUTHORIZATION.json'),native_started=False))
    put(R/'LOCAL_PREPARE_READER_ERRORS.json',dict(epoch=time.time(),errors=[
        dict(operation='Search standing peer CURRENT_STATE.json/latest_status.json',
             error='Those two guessed paths do not exist; rg found actual CURRENT_WORK_ORDER.json',
             resolution='Read exact existing CURRENT_WORK_ORDER.json; no remote or production operations')]))
    print(json.dumps(dict(prepared=str(A),num_envs=20000,train_seconds=3600,source_modules=2,GO=False)))


def inventory():
    peer=read(Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/CURRENT_WORK_ORDER.json'))
    put(R/'EXACT_PEER_LOCAL_CONTEXT.json',dict(epoch=time.time(),remote_job=peer['remote_job'],
        owner=peer['original_owner'],GO=peer['GO'],status=peer['status'],read_only_other_chat=True))
    m=load('scut_explicit_filter_fourcard',N/'check_four_gpu.py');m.R=R
    m.READ=m.READ.replace('MOD4_STANDING200_SCUT_RECIPE_V20_FLAT_1793718811682640300',Path(peer['remote_job']).name)
    m.READ=m.READ.replace('1549188',str(peer['original_owner']['pid']))
    m.READ=m.READ.replace('1793718880.82',str(peer['original_owner']['creation']))
    m.main()


def freeze(resource):
    assert not(A/'INDEX_SOURCE_FROZEN.json').exists()
    assert not(R/'LAUNCH_ONCE.json').exists()
    assert resource['ready']and resource['canonical_active']is None
    assert time.time()-resource['epoch']<120
    plan=read(A/'PLAN.json');plan['GPU_UUID']=resource['GPU_UUID']
    plan.pop('pending_actual_resource_selection',None)
    (A/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
    prepared=read(A/'SOURCE_ONLY_PREPARED.json');files=list(prepared['files'])
    for row in files:
        raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes']and H(raw)==row['SHA']
    for name in('PLAN.json','owner.py','entry.py'):
        path=A/name;raw=path.read_bytes()
        if path.suffix=='.py':ast.parse(raw)
        files.append(dict(path=str(path),relative=name,bytes=len(raw),SHA=H(raw)))
    put(A/'INDEX_SOURCE_FROZEN.json',dict(epoch=time.time(),files=files,shared_text=prepared['shared_text'],
        overlay_resolution_order=plan['module_overlays'],source_only=True,
        whole_tree_model_asset_copy=False,same_original_canonical=True,new_budget_or_refund=False,
        new_hour_human_authorization=str(R/'HUMAN_NEW_HOUR_AUTHORIZATION.json')))


def bind():
    assert not(R/'RESOURCE_TIMER_BIND_ONCE.json').exists()
    inv=read(R/'FOUR_GPU_HUMAN_REQUEST_ACTUAL.json')
    actual=inv['hosts']['72']['actual'];peer=read(R/'EXACT_PEER_LOCAL_CONTEXT.json')
    assert inv['all_clients_closed']and inv['SESSION_restored']
    ident=actual['exact_peer']['OWNER_STARTED.json']['identity']
    assert ident['pid']==peer['owner']['pid']and ident['creation']==peer['owner']['creation']
    assert actual['canonical']['active']['owner_parent_pid']==ident['pid']
    assert actual['exact_peer_alive']and actual['exact_peer']['OWNER_EXIT.json']is None
    wait=dict(epoch=time.time(),peer_root=peer['remote_job'],peer_identity=ident,
        peer_GO=peer['GO'],wait_until=peer['GO']['nominal_end_epoch']+60,
        preferred_GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
        reason='ExactV28 peer holds original canonical and authority/finite locks; GPU1 empty does not permit bypass',
        new_hour_begins_only_after_actual_admission=True,max_resource_wait_seconds=900)
    m=load('scut_filter06_bind_local',N/'run.py');rows=m.local_rows()
    assert not any(row['ProcessId']!=os.getpid()for row in rows),'Other local controller active'
    put(A/'RESOURCE_WAIT_FROZEN.json',wait)
    raw=Path(__file__).read_bytes()
    put(A/'RESOURCE_TIMER_SOURCE_FROZEN.json',dict(path=str(Path(__file__)),bytes=len(raw),SHA=H(raw),
        prepared_SHA=H((A/'SOURCE_ONLY_PREPARED.json').read_bytes()),
        wait_SHA=H((A/'RESOURCE_WAIT_FROZEN.json').read_bytes()),local_rows=rows))
    put(R/'RESOURCE_TIMER_BIND_ONCE.json',dict(epoch=time.time(),sole_local_controller=True))
    with(R/'RESOURCE_TIMER_STDOUT.log').open('xb')as out,(R/'RESOURCE_TIMER_STDERR.log').open('xb')as err:
        process=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe',
            '-B','-X','utf8',str(Path(__file__)),'timer'],cwd=N,stdin=subprocess.DEVNULL,
            stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(process.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    result=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put(R/'RESOURCE_TIMER_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(result.stdout)))
    print(json.dumps(dict(bound=True,PID=process.pid,wait_until=wait['wait_until'],new_hour_not_started=True)))


def timer():
    assert not(R/'RESOURCE_TIMER_ONCE.json').exists()
    source=read(A/'RESOURCE_TIMER_SOURCE_FROZEN.json')
    assert H(Path(__file__).read_bytes())==source['SHA']
    assert H((A/'SOURCE_ONLY_PREPARED.json').read_bytes())==source['prepared_SHA']
    assert H((A/'RESOURCE_WAIT_FROZEN.json').read_bytes())==source['wait_SHA']
    wait=read(A/'RESOURCE_WAIT_FROZEN.json')
    put(R/'RESOURCE_TIMER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),local_wait=True))
    while time.time()<wait['wait_until']:time.sleep(min(10,wait['wait_until']-time.time()))
    m=load('scut_filter06_pending_serial',N/'run.py');m.R=R
    local_start=time.time()
    while any(row['ProcessId']!=os.getpid()for row in m.local_rows()):
        if time.time()-local_start>10800:raise RuntimeError('Original local controller did not release within3h')
        time.sleep(10)
    code='''from pathlib import Path
import json,time,fcntl,subprocess,shutil,psutil
b=Path('/home/lc01/Zonglin Li/zonglin2');C=b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
c=json.loads(C.read_bytes());peer=Path(v['peer_root']);s=json.loads((peer/'OWNER_STARTED.json').read_bytes())['identity'];p=peer/'OWNER_EXIT.json';e=json.loads(p.read_bytes())if p.is_file()else None
same=s['pid']==v['peer_identity']['pid']and s['creation']==v['peer_identity']['creation']
released=same and e is not None and all(e[k]for k in('all_own_waited','original_cost_settled','original_leases_released'))
locks={};ready=released and c['active_segment']is None
if ready:
 for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock',C.parent.parent/('three_expert_v2_'+v['preferred_GPU_UUID']+'.lock')]:
  try:
   with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   locks[str(p)]=True
  except BlockingIOError:locks[str(p)]=False
 ready=all(locks.values())
resource=None
if ready:
 uuid=v['preferred_GPU_UUID'];line=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip()for x in line.split(',')]
 apps=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).strip()
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(Path(v['remote_parent'])).free
 ready=a[0]==uuid and a[1]=='NVIDIA GeForce RTX 4090'and int(a[2])>15669 and(not apps or(int(a[3])<=4096 and int(a[4])<=30))and ram>64*1024**3 and disk>50*1024**3
 resource=dict(line=line,compute_apps=apps,ram=ram,disk=disk)
print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],remaining=c['remaining_training_seconds'],peer_identity_matches=same,peer_exit=e,locks=locks,GPU_UUID=v['preferred_GPU_UUID'],resource=resource,PT_reads=0,physics=0,canonical_writes=0)))'''
    wait['remote_parent']=read(A/'PLAN.json')['remote_root'].rsplit('/',1)[0]
    value=None
    with m.connection('FILTER06_PENDING_RESOURCE')as(client,d):
        for tick in range(31):
            value=d.code(client,d.PY72,code,wait,timeout=40)
            if value['ready']:break
            if value['canonical_active']and value['canonical_active']['owner_run_id']!=wait['peer_GO']['run_id']:
                break
            if tick<30:time.sleep(30)
        if not value['ready']:
            put(R/'RESOURCE_STILL_BLOCKED.json',value)
            return
        put(R/'RESOURCE_READY_ACTUAL.json',value)
    freeze(value)
    controller=load('scut_filter06_owned_launch',N/'repaired_training_control.py')
    controller.A=A;controller.R=R;controller.launch()
    facts=read(R/'FIRST_ACTUAL_RETURNED.json')['files']if(R/'FIRST_ACTUAL_RETURNED.json').exists()else{}
    first=facts.get('production/FIRST_UPDATED.json')
    errors=[x for x in facts.get('WORKER.log','').splitlines()if '[Error]'in x or 'cooking failure'in x or 'foundLostAggregatePairsCapacity'in x or 'OutOfMemoryError'in x]
    if first and not errors and 'production/ERROR.json'not in facts:
        assert first['full_save']and first['actual_onpolicy_samples']==480000
        assert first['gradient']['actor_norm']>0 and first['gradient']['critic_norm']>0
        controller.bind()
    put(R/'RESOURCE_TIMER_COMPLETED.json',dict(epoch=time.time(),LAUNCH_consumed=(R/'LAUNCH_ONCE.json').exists(),
        actual_FIRST=first,actual_native_errors=errors,postround_bound=(R/'POSTROUND_BIND_ONCE.json').exists(),
        FIRST_not_skill=True,source_checkpoint=read(A/'PLAN.json')['source_checkpoint']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','inventory','bind','timer'])
    args=parser.parse_args()
    try:globals()[args.mode]()
    except BaseException:
        if R.exists():put(R/('CONTROL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),mode=args.mode,PID=os.getpid(),error=traceback.format_exc()))
        raise
