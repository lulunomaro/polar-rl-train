"""Authorized single200mm jump hour, using the existing owner and collector."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import time
import traceback

N=Path(__file__).resolve().parent
B=N/'env20000_scut_stairs_1h_20261104/attempt08'
Q=N/'jump200_step_eval1_20261104'
A=N/'env20000_jump200_1h_20261104';R=A/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
PEER_REPORT=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/reports/SCUT30_ACTUAL_FIRST1473_V28_FINAL1472_NATIVE_HANDOFF_20261104.json')
read=lambda p:json.loads(Path(p).read_bytes())
sha=lambda b:hashlib.sha256(b).hexdigest()


def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def put(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2)


def prepare():
    assert read(Q/'reports/ACTUAL_JUMP200_BASELINE_NATIVE_REVIEW.json')['all4_actual_images_reviewed']
    assert read(Q/'reports/JUMP200_FULLSTATE_TRANSFER_CPU.json')['passed']
    closed=read(B/'reports/POSTROUND_FULL_RETURNED.json')['files']
    assert closed['OWNER_EXIT.json']['original_leases_released']
    A.mkdir();R.mkdir()
    authorization=dict(epoch=time.time(),human_quote='批准200mm跳台阶训练一小时',
        num_envs=20000,train_seconds=3600,exit_headroom_seconds=300,
        same_original_canonical=True,budget_grant_or_refund=False)
    put(R/'HUMAN_JUMP200_HOUR_AUTHORIZATION.json',authorization)
    plan=read(B/'PLAN.json')
    for key in ('original_save_deadline','original_nominal_end_epoch','stair_branch',
                'course_layout','geometry_adaptation','boundary_reset','pending_actual_resource_selection'):
        plan.pop(key,None)
    remote_base=plan['remote_root'].split('/env20000_scut_stairs_')[0]
    plan.update(run_id='MOD4V1_SCUT_SINGLE200MM_JUMP_20000ENV_1H_'+str(time.time_ns()),
        remote_root=remote_base+'/'+A.name,profile='jump200',num_envs=20000,
        train_seconds=3600,max_parent_seconds=3900,exit_headroom_seconds=300,
        source_checkpoint=closed['production/FINAL.json']['checkpoint'],
        full_state_continuation=True,source_optimizer_loaded=True,
        source_profile='scut_stairs',target_profile='jump200',task_changed=True,
        source_is_jump_expert=False,repair_first_axis=False,resized_learning_continuation=False,
        initialization='Full actor/critic/STD/Adam/LR/iteration/component/RNG/queue transfer, explicit scut_stairs->jump200, then one fresh physical reset',
        human_latest=authorization['human_quote'],human_authorization=authorization,
        newly_authorized_window=True,old_absolute_window_not_extended=True,
        first_flight_required=False,airborne_jump_required=True,fixed_height270_required=False,
        target_step_height_m=.2,full_rough_restored=False,
        position='Single vertical200mm edge x=.8m, flat top to3.5m, positive-x heading±.05rad, root .38m, no initialvelocity',
        repair='Human correction: single200mm jump, source ballistic takeoff rewards/noassist; actual airborne clearance and stablelanding required',
        task_differences=['Single200mm verticalstep replaces mistaken smallstairs',
            'Source optional takeoff helper and explicit push/peak rewards enabled',
            'Realray step event requests takeoff; actual airborne tabletop landing changes speedcommand to0'],
        preserved=['Enhanced asset/contract/fullD0-D7/solver/PD/DC/clip6/targetlimits/CAD/D4',
            'OriginalordinaryPPO/canonical/reserve/fullsave'],
        native_diagnostic_review=str(Q/'reports/ACTUAL_JUMP200_BASELINE_NATIVE_REVIEW.json'),
        previous_final_review=str(B/'reports/ACTUAL_RIGHTANGLE08_FINAL_NATIVE_REVIEW.json'),
        independent_evaluation='Originalowner fullsave/safeclose then native80/400controls8s/seed9137/newDR/400Hz, allposeimages review',
        pending_actual_resource_selection=True)
    overlay=plan['remote_root']+'/overlay'
    plan['module_overlays']=[overlay]+read(B/'PLAN.json')['module_overlays'];plan['module_overlay']=overlay
    put(A/'PLAN.json',plan)
    (A/'owner.py').write_bytes((B/'owner.py').read_bytes())
    entry=(B/'entry.py').read_text(encoding='utf8')
    needle="    if task.get('repair_first_axis'):sys.argv+=['--repair-first-axis']"
    assert entry.count(needle)==1
    entry=entry.replace(needle,"    if task.get('task_changed'):sys.argv+=['--resume-source-profile',task['source_profile']]\n"+needle)
    ast.parse(entry);(A/'entry.py').write_text(entry,encoding='utf8',newline='\n')
    previous=read(B/'INDEX_SOURCE_FROZEN.json');shared=list(previous['shared_text'])
    for row in previous['files']:
        if row['relative'].startswith('overlay/'):
            shared.append(dict(path=read(B/'PLAN.json')['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
    files=[]
    for name in ('config.py','jump200.py','rewards.py','sdk.py','train.py','evaluate.py','checkpoint.py'):
        path=G/'project/isaac/mod4v1_scut'/name;raw=path.read_bytes();ast.parse(raw)
        files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=sha(raw)))
    put(A/'SOURCE_ONLY_PREPARED.json',dict(epoch=time.time(),files=files,shared_text=shared,
        source_only=True,whole_tree_model_asset_copy=False,human_authorization=authorization))
    print(json.dumps(dict(prepared=str(A),changed_modules=len(files),sharedrefs=len(shared),source=plan['source_checkpoint'])))


def inventory():
    target=R/('FOUR_GPU_'+str(time.time_ns()));target.mkdir()
    m=load('jump200_train_four_gpu',N/'check_four_gpu.py');m.R=target;m.main()


def bind():
    assert not(R/'RESOURCE_TIMER_BIND_ONCE.json').exists()
    assert not(A/'INDEX_SOURCE_FROZEN.json').exists() and not(R/'LAUNCH_ONCE.json').exists()
    raw=PEER_REPORT.read_bytes();peer=json.loads(raw)
    go=peer['GO'];identity=peer['original_owner']
    assert go['run_id']==peer['run_id']==Path(peer['remote_job']).name
    assert identity['pid']==1614229 and identity['creation']==1793793094.65
    assert go['learning_started_epoch']==1793793095.372965
    local=load('jump200_timer_bind_local',N/'run.py');rows=local.local_rows()
    others=[row for row in rows if row['ProcessId']!=os.getpid()]
    assert not any('jump200_training_control.py'in(row.get('CommandLine')or'')for row in others),'This task already has a controller'
    wait=dict(epoch=time.time(),peer_root=peer['remote_job'],peer_identity=identity,peer_GO=go,
        peer_report=dict(path=str(PEER_REPORT),bytes=len(raw),SHA=sha(raw)),
        wait_until=go['nominal_end_epoch']+60,max_resource_wait_seconds=900,
        reason='Exact standingV30 holds original canonical and shared authority/finite locks',
        foreign_local_rows_at_bind=others,bind_is_local_only=True,
        new_hour_begins_only_at_actual_GO=True,human_authorization=str(R/'HUMAN_JUMP200_HOUR_AUTHORIZATION.json'))
    put(A/'RESOURCE_WAIT_FROZEN.json',wait)
    source=Path(__file__).read_bytes()
    put(A/'RESOURCE_TIMER_SOURCE_FROZEN.json',dict(path=str(Path(__file__)),bytes=len(source),SHA=sha(source),
        prepared_SHA=sha((A/'SOURCE_ONLY_PREPARED.json').read_bytes()),
        wait_SHA=sha((A/'RESOURCE_WAIT_FROZEN.json').read_bytes()),local_rows=rows))
    put(R/'RESOURCE_TIMER_BIND_ONCE.json',dict(epoch=time.time(),sole_local_controller=True))
    with(R/'RESOURCE_TIMER_STDOUT.log').open('xb')as out,(R/'RESOURCE_TIMER_STDERR.log').open('xb')as err:
        process=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'timer'],cwd=N,
            stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(process.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    result=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put(R/'RESOURCE_TIMER_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(result.stdout)))
    print(json.dumps(dict(bound=True,PID=process.pid,wait_until=wait['wait_until'],new_hour_not_started=True)))


def timer():
    assert not(R/'RESOURCE_TIMER_ONCE.json').exists()
    source=read(A/'RESOURCE_TIMER_SOURCE_FROZEN.json')
    assert sha(Path(__file__).read_bytes())==source['SHA']
    assert sha((A/'SOURCE_ONLY_PREPARED.json').read_bytes())==source['prepared_SHA']
    assert sha((A/'RESOURCE_WAIT_FROZEN.json').read_bytes())==source['wait_SHA']
    wait=read(A/'RESOURCE_WAIT_FROZEN.json')
    put(R/'RESOURCE_TIMER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),local_wait=True))
    while time.time()<wait['wait_until']:time.sleep(min(10,wait['wait_until']-time.time()))
    local=load('jump200_timer_original_transport',N/'run.py');local.R=R
    started=time.time()
    while any(row['ProcessId']!=os.getpid()for row in local.local_rows()):
        if time.time()-started>10800:raise RuntimeError('Original local controller did not release within3h')
        time.sleep(10)
    code='''from pathlib import Path
import json,time,fcntl
b=Path('/home/lc01/Zonglin Li/zonglin2');C=b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
c=json.loads(C.read_bytes());peer=Path(v['peer_root']);s=json.loads((peer/'OWNER_STARTED.json').read_bytes())['identity'];p=peer/'OWNER_EXIT.json';e=json.loads(p.read_bytes())if p.is_file()else None
same=all(s.get(k)==v['peer_identity'].get(k)for k in('pid','creation','exe','argv','root'))
released=same and e is not None and all(e.get(k,False)for k in('all_own_waited','original_cost_settled','original_leases_released'))
locks={};ready=released and c['active_segment']is None
if ready:
 for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock']:
  try:
   with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   locks[str(p)]=True
  except BlockingIOError:locks[str(p)]=False
 ready=all(locks.values())and c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],remaining=c['remaining_training_seconds'],peer_identity_matches=same,peer_exit=e,locks=locks,PT_reads=0,physics=0,canonical_writes=0)))'''
    with local.connection('JUMP200_PENDING_RESOURCE')as(client,d):
        for tick in range(31):
            value=d.code(client,d.PY72,code,wait,timeout=40)
            if value['ready']:break
            if not value['peer_identity_matches']:break
            if value['canonical_active']and value['canonical_active']['owner_run_id']!=wait['peer_GO']['run_id']:break
            if tick<30:time.sleep(30)
        if not value['ready']:
            put(R/'RESOURCE_STILL_BLOCKED.json',value)
            return
        put(R/'RESOURCE_READY_ACTUAL.json',value)
    launch()
    put(R/'RESOURCE_TIMER_COMPLETED.json',dict(epoch=time.time(),
        LAUNCH_consumed=(R/'LAUNCH_ONCE.json').exists(),postround_bound=(R/'POSTROUND_BIND_ONCE.json').exists(),
        FIRST_not_skill=True))


def launch():
    assert not(A/'INDEX_SOURCE_FROZEN.json').exists() and not(R/'LAUNCH_ONCE.json').exists()
    inventories=sorted(R.glob('FOUR_GPU_*/FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'))
    if not inventories or time.time()-read(inventories[-1])['hosts']['72']['actual']['epoch']>120:
        inventory();inventories=sorted(R.glob('FOUR_GPU_*/FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'))
    host=read(inventories[-1])['hosts']['72']['actual'];candidates=[]
    for line in host['gpu']['stdout'].splitlines():
        v=[x.strip()for x in line.split(',')]
        if v[2]!='NVIDIA GeForce RTX 4090':continue
        free,used,util=map(int,v[4:7]);busy=v[1]in host['compute_apps']['stdout']
        if free>15669 and(not busy or(used<=4096 and util<=30)):candidates.append((not busy,free,v[1]))
    assert candidates,'No currently admissible4090 on originalhost'
    assert host['canonical']['active']is None and all(host['locks'].values()),'Original locks/canonical busy; no newnamespace'
    assert host['ram']['available']>64*1024**3 and host['disk']['free']>50*1024**3
    assert host['canonical']['remaining']>86412.86069250107+3900
    plan=read(A/'PLAN.json');plan['GPU_UUID']=max(candidates)[2];plan.pop('pending_actual_resource_selection')
    (A/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
    prepared=read(A/'SOURCE_ONLY_PREPARED.json');files=list(prepared['files'])
    for name in ('PLAN.json','owner.py','entry.py'):
        path=A/name;raw=path.read_bytes();files.append(dict(path=str(path),relative=name,bytes=len(raw),SHA=sha(raw)))
    for row in files:
        raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes']and sha(raw)==row['SHA']
    put(A/'INDEX_SOURCE_FROZEN.json',dict(epoch=time.time(),files=files,shared_text=prepared['shared_text'],
        source_only=True,whole_tree_model_asset_copy=False,source_profile='scut_stairs',target_profile='jump200'))
    controller=load('jump200_original_launch',N/'repaired_training_control.py');controller.A=A;controller.R=R
    controller.launch()
    facts=read(R/'FIRST_ACTUAL_RETURNED.json')['files']
    first=facts.get('production/FIRST_UPDATED.json');full=facts.get('WORKER_COMPLETE.log',{})
    terms=['[error]','traceback (most recent call last)','cooking failure','failed to cook','foundlostaggregatepairscapacity','patch buffer overflow','outofmemoryerror','dropped pair']
    errors=[line for line in full.get('text','').splitlines()if any(t in line.lower()for t in terms)]
    put(R/'FIRST_FULL_LOG_VALIDATION.json',dict(epoch=time.time(),full_log_returned=bool(full),
        errors=errors,FIRST=first,production_error=facts.get('production/ERROR.json')))
    assert first and full and not errors and 'production/ERROR.json'not in facts
    assert first['actual_onpolicy_samples']==480000 and first['rollout_controls']==24 and first['full_save']
    assert first['iteration']==81 and first['gradient']['steps']==20
    assert first['gradient']['actor_norm']>0 and first['gradient']['critic_norm']>0
    restore=facts['production/FULL_STATE_RESTORE.json'];assert restore['source_iteration']==80
    assert restore['optimizer_state_entries']==17 and restore['optimizer_step_min']==restore['optimizer_step_max']==1600
    assert restore['source_profile']=='scut_stairs'and restore['target_profile']=='jump200'
    assert facts['production/STARTUP.json']['course']['step_height_m']==.2
    controller.bind()
    put(R/'FIRST_NATIVE_VALIDATED_AND_COLLECTOR_BOUND.json',dict(epoch=time.time(),FIRST=first,
        full_restore=restore,GO=facts['GO_PRODUCTION.json'],collector=read(R/'POSTROUND_EXACT_CIM.json'),
        FIRST_not_skill=True,complete_log_errors=errors))
    print(json.dumps(dict(valid_FIRST=first,collector=read(R/'POSTROUND_EXACT_CIM.json'),GO=facts['GO_PRODUCTION.json'])))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','inventory','launch','bind','timer']);a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        if R.exists():put(R/('CONTROL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
        raise
