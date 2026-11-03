"""One H1 attitude-reward run: launch, one FIRST, then serial close/eval.

Only changed sources are deployed. Frozen455 dependencies are referenced by
absolute path and SHA. All network calls retain the original transport/owner.
"""
from pathlib import Path, PurePosixPath
from contextlib import contextmanager
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import runpy
import secrets
import subprocess
import sys
import time
import traceback
import types
import zipfile

N=Path(__file__).resolve().parent;R=N/'reports';V=N/'evaluation'
PATHS=json.loads((N/'RUN_PATHS.json').read_bytes())
S=Path(PATHS['scope']);T=Path(PATHS['task_root']);OLD=Path(PATHS['prior_root']);G=Path(PATHS['repo'])
W=Path('C:/Users/lulu/Desktop/claude/mjcf')
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
PATTERN='MOD4_H1|RMPOLAR|watch|run_once_after_resume|E1.*collect|prepare_archive|single_gpu|collect_nine|collect_generic|collect_actual|PAIR|stage_new|dispatch|retention|postround|h1_attitude|h1_wheel_height|h1_reward_tail|h1_wheel_planar|h1_attitude_tight|h1_target_limit|h1_target_limit_cont|run476'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
raw=lambda v:json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False).encode()


def put(name,value,root=R):
    with (root/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec)
    sys.modules[name]=value;spec.loader.exec_module(value);return value


def local_rows():
    query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+PATTERN+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
    response=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    assert not response.stderr.strip(),response.stderr
    rows=json.loads(response.stdout)if response.stdout.strip()else[]
    return rows if isinstance(rows,list)else[rows]


def gate(label):
    rows=local_rows();own=[r for r in rows if r['ProcessId']==os.getpid()];others=[r for r in rows if r['ProcessId']!=os.getpid()]
    put(label+'_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows,serialFREE=not others))
    assert len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower()
    assert not others,'Another known controller active; no network/once consumption'


def wait_local():
    started=time.time()
    while any(r['ProcessId']!=os.getpid()for r in local_rows()):
        assert time.time()-started<10800,'Other local controller not released in3h'
        time.sleep(10)


def transport_module():
    relative='H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py'
    path=T/relative
    if path.exists():return module('h1_original_transport',path)
    with (S/'history/h1_closed_stages_through_20261031.index.jsonl').open(encoding='utf8')as f:
        row=next(json.loads(line)for line in f if json.loads(line)['relative_path']==relative)
    with zipfile.ZipFile(S/'history/h1_closed_stages_through_20261031.zip')as archive:data=archive.read('objects/'+row['SHA256'])
    assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['SHA256']
    value=types.ModuleType('h1_original_transport');value.__file__=str(path)
    exec(compile(data,str(path),'exec'),value.__dict__)
    value.W=W
    return value


@contextmanager
def connection(label):
    gate(label)
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as deploy
    transport=previous=client=secret=None
    try:
        transport,previous=transport_module().install()
        secret=module('h1_same_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
        client=deploy.connect72(secret);secret=None
        yield client,deploy
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put(label+'_SSH_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))


def stage(sf,path,data):
    current=''
    for part in str(PurePosixPath(path).parent).split('/'):
        if not part:continue
        current+='/'+part
        try:sf.mkdir(current)
        except OSError:sf.stat(current)
    with sf.file(path,'wx')as stream:stream.write(data);stream.flush()


def protocol():return module('h1_protocol476',N/'source/teacher_task476.py')


def verify_index(expected=None):
    index=N/'INDEX_SOURCE_FROZEN.json'
    if expected is not None:assert H(index)==expected
    for row in read(index)['files']:
        path=Path(row['path']);assert path.stat().st_size==row['bytes']and H(path)==row['SHA'],str(path)


def snapshot(client,deploy,task):
    # Reuse the existing finite text snapshot, changing labels only.
    tree=ast.parse((OLD/'launch455_actual_residual_RL_once.py').read_text('utf8'))
    text=next(ast.literal_eval(node.value)for node in tree.body if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SNAPSHOT'for t in node.targets))
    text=text.replace('455','476')
    return deploy.code(client,deploy.PY72,text,dict(job=task['job_root'],owner=task['owner_root']),timeout=60)


def launch(expected):
    assert not(R/'LAUNCH_ONCE.json').exists()
    verify_index(expected);task=read(N/'TASK476_FROZEN.json');p=protocol();p.validate_task(task)
    fixture=read(R/'CPU476_LAUNCH_LANDING_RETURN_FULL_RESTORE_ADMISSION.json');assert fixture['passed']and fixture['production_optimizer_steps']==0
    assert fixture['source_offsets']==[56937,13997,75210]and fixture['learnerSHA']==H(N/'source/actual_transition_learner476.py')
    remote=module('h1_remote_shared',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py')
    light=module('h1_resource_shared',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_additions.py')
    with connection('LAUNCH')as(client,d):
        put('LAUNCH_ONCE.json',dict(epoch=time.time(),task=task,source_model_reads_parent=0))
        put('AUTHORITY_BEFORE_DEPLOY.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
        J=task['job_root'];C=task['owner_root']
        create="from pathlib import Path\nimport json\np=Path(v['job']);assert p.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p.mkdir(parents=True,exist_ok=False);print(json.dumps(dict(passed=True,new_run=str(p),model_reads=0)))"
        put('NEW_RUN_ACTUAL.json',d.code(client,d.PY72,create,dict(job=J),timeout=30))
        resource=d.code(client,d.PY72,light.RESOURCE,dict(job=J,GPU_UUID=task['GPU_UUID']),timeout=45);put('RESOURCE_ACTUAL.json',resource);assert resource['passed']
        shared=read(N/'SHARED_SOURCE_REFERENCES.json')['files'];files=[dict(path=row['path'],bytes=row['bytes'],SHA=row['SHA'])for row in shared]
        uploads={}
        for path in sorted((N/'source').glob('*.py')):
            dest=J+'/source/'+path.name;data=path.read_bytes();uploads[dest]=data;files.append(dict(path=dest,bytes=len(data),SHA=hashlib.sha256(data).hexdigest()))
        taskbytes=raw(task);uploads[J+'/TASK476.json']=taskbytes;files.append(dict(path=J+'/TASK476.json',bytes=len(taskbytes),SHA=hashlib.sha256(taskbytes).hexdigest()))
        manifest=dict(kind='H1_SHARED_SOURCE_OVERLAY476',files=files);manifestbytes=raw(manifest);manifestsha=hashlib.sha256(manifestbytes).hexdigest()
        spec=dict(task,key='jump_72',role='node',execution_backend='target72',private_lock=resource['private_lock'],python=d.PY72,worker_script='source/worker476.py',manifest_file='MANIFEST476.json',manifest_SHA=manifestsha,allowed_source_roots=[J,str(PurePosixPath(task['shared_source_root']).parent),str(PurePosixPath(task['attitude_source_root']).parent),str(PurePosixPath(task['height_source_root']).parent),str(PurePosixPath(task['mapping_source_root']).parent),str(PurePosixPath(task['planar_source_root']).parent),str(PurePosixPath(task['tight_source_root']).parent),str(PurePosixPath(task['target_source_root']).parent)])
        ready=dict(passed=True,kind=p.READY_KIND,manifest_SHA=manifestsha,source_SHA=task['source_SHA'],source_CPU_report_SHA=task['source_CPU_report_SHA'],actual_source_migration_and_H32_CPU_passed=True,admission_optimizer_steps=0,fresh_CNone_CIM_resources_actual=True,actual_resource_admission_SHA=H(R/'RESOURCE_ACTUAL.json'),actual_live_gradient_required_before_first_step=True,CPU_report_scope='Fullfinal474 restore; same474reward retained; existing targetlimit tests reused; live actual128 gradients/native24 required')
        row=dict(phase='ready',manifest_SHA=manifestsha,original_error=False,closed_source_CPU=dict(value=ready,SHA=p.ready_value_SHA(ready)));assert p.valid_ready(row,spec)
        schedule=dict(run_id=task['run_id'],scheduling_authority='human_requested_available_experts',owner_root=C,experts={'jump_72':spec},deferred_experts=[]);p.validate_schedule(schedule)
        uploads.update({J+'/MANIFEST476.json':manifestbytes,J+'/FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json':raw(ready),C+'/SCHEDULE_PUBLIC.json':raw(schedule)})
        for path in (N/'control').glob('*.py'):uploads[C+'/'+path.name]=path.read_bytes()
        sf=client.open_sftp();sf.get_channel().settimeout(120)
        try:
            for path,data in uploads.items():stage(sf,path,data)
        finally:sf.close()
        allfiles=files+[dict(path=path,bytes=len(data),SHA=hashlib.sha256(data).hexdigest())for path,data in uploads.items()if path not in {r['path']for r in files}]
        verify="from pathlib import Path\nimport json,hashlib\nfor r in v['files']:\n p=Path(r['path']);b=p.read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['SHA'],str(p)\nprint(json.dumps(dict(passed=True,files=len(v['files']),shared_sources_referenced=True,model_reads=0)))"
        put('DEPLOY_POSTCOPY_ACTUAL.json',d.code(client,d.PY72,verify,dict(files=allfiles),timeout=90))
        put('DEPLOY_MANIFEST_SCHEDULE.json',dict(epoch=time.time(),spec=spec,schedule=schedule,manifest=manifest,ready=ready,uploads=[dict(path=p,bytes=len(b),SHA=hashlib.sha256(b).hexdigest())for p,b in uploads.items()]))
        put('AUTHORITY_BEFORE_OWNER.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
        token=secrets.token_hex(32);private_spec=dict(spec,token=token)
        cfg=dict(role='owner',run_id=task['run_id'],token=token,scheduling_authority='human_requested_available_experts',experts={'jump_72':private_spec},deferred_experts=[])
        owner=d.code(client,d.PY72,remote.SPAWN,dict(root=C,module='model2050_240_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd='/home/lc01/Zonglin Li/zonglin2'),timeout=30)
        put('OWNER_LAUNCH_ACTUAL.json',dict(run_id=task['run_id'],owner=owner,specs={'jump_72':spec}))
        node=d.code(client,d.PY72,remote.SPAWN,dict(root=C,module='model2050_240_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private_spec,expected_control_cwd='/home/lc01/Zonglin Li/zonglin2'),timeout=30)
        put('NODE_LAUNCH_ACTUAL.json',node)
        put('INITIAL_SNAPSHOT.json',snapshot(client,d,task))
        print(json.dumps(dict(dispatched=True,owner=owner,node=node,run_id=task['run_id'],GO_or_learning_not_yet_claimed=True)),flush=True)


def first():
    assert not(R/'FIRST_ONCE.json').exists()
    task=read(N/'TASK476_FROZEN.json')
    with connection('FIRST')as(client,d):
        put('FIRST_ONCE.json',dict(epoch=time.time(),one_snapshot=True))
        wait="from pathlib import Path\nimport json,time\nB=Path(v['job']);end=time.time()+850\nwhile time.time()<end and not(B/'production/FIRST_ACTUAL_TEACHER_DEPTH_STUDENT476_UPDATE.json').exists()and not(B/'control476/NODE_TERMINAL_ACTUAL.json').exists():time.sleep(2)\nprint(json.dumps(dict(waited=True,first=(B/'production/FIRST_ACTUAL_TEACHER_DEPTH_STUDENT476_UPDATE.json').exists())))"
        put('FIRST_FINITE_WAIT.json',d.code(client,d.PY72,wait,dict(job=task['job_root']),timeout=900))
        value=snapshot(client,d,task);put('FIRST_SNAPSHOT.json',value)
    files={Path(r['path']).name:json.loads(r['UTF8'])for r in value['full_selected_UTF8']}
    assert not any(key in files for key in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
    protocol().validate_first(files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT476_UPDATE.json'],task,files['GO_PRODUCTION.json'])
    put('LIVE_BINDING.json',dict(passed=True,current=files['OWNER_CURRENT.json'],files=files,canonical_None=False,owner=read(R/'OWNER_LAUNCH_ACTUAL.json')['owner']))
    print(json.dumps(dict(passed=True,go=files['GO_PRODUCTION.json'],first=files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT476_UPDATE.json'],latest=files.get('LATEST_PROGRESS.json'))),flush=True)


def cpu_final():
    # Execute the established full final reader with new source offsets/labels.
    assert not(R/'CPU476_NEW_FINAL_CONSUMED.json').exists()
    text=(OLD/'review455_new_final_full_CPU_once.py').read_text('utf8')
    text=text.replace('455','476').replace('36159','75210').replace('56634','56937').replace('13694','13997')
    text=text.replace("from tracking_task476 import", "from teacher_task476 import")
    text=text.replace("sys.path.insert(0,str(N));", "sys.path.insert(0,str(N/'source'));")
    text=text.replace('and s[\'actual_reward_unchanged\']', "and not s['actual_reward_unchanged']")
    # Preserve execution in the CPU runtime; this script is the only decoder.
    prepared=N/'review_final_cpu.py'
    assert prepared.read_text('utf8')==text,'Frozen CPU reader must match selected source offsets'
    result=subprocess.run([CPU,'-B','-X','utf8',str(prepared)],cwd=N,capture_output=True,text=True,encoding='utf8')
    put('CPU_FINAL_PROCESS.json',dict(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
    assert result.returncode==0,result.stderr
    return read(R/'ROOT476_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')


def close_original():
    assert not(R/'NORMAL_ONCE.json').exists()
    task=read(N/'TASK476_FROZEN.json');binding=read(R/'LIVE_BINDING.json');go=binding['current']['go']
    assert go['jump_72']['nominal_end_epoch']-time.time()<=900
    # The same finite collector is used without copying its source tree.
    text=(OLD/'normal455/collect455_fullclose_transfer_once.py').read_text('utf8')
    tree=ast.parse(text)
    code=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='COLLECT_NODE'for t in n.targets))
    code=code.replace('455','476').replace('36159','75210')
    code=code.replace('import sys;sys.path.insert(0,str(C));from report_classification312 import classify_error_reports',"import sys;classifier=Path(v['spec']['shared_control_root'])/'report_classification312.py';assert hashlib.sha256(classifier.read_bytes()).hexdigest()=='50223444323c1898af61b34821f486d9b6e524425ef5cef191dce87c7d69e78f';sys.path[:0]=[str(C),str(classifier.parent)];from report_classification312 import classify_error_reports")
    spec=read(R/'OWNER_LAUNCH_ACTUAL.json')['specs']['jump_72']
    with connection('NORMAL')as(client,d):
        put('NORMAL_ONCE.json',dict(epoch=time.time(),original_go=go,owner=binding['owner']))
        owner_code="""from pathlib import Path
import json,time,fcntl,psutil
O=Path(v['owner']['root']);go=v['go'];assert max(g['nominal_end_epoch']for g in go.values())-time.time()<=900
identity=json.loads((O/'OWNER_IDENTITY.json').read_bytes());assert identity['pid']==v['owner']['pid']and identity['creation']==v['owner']['creation']
end=time.time()+850
while time.time()<end and not(O/'OWNER_EXIT_ACTUAL.json').exists():time.sleep(2)
final=json.loads((O/'COHORT_FINAL.json').read_bytes());exit=json.loads((O/'OWNER_EXIT_ACTUAL.json').read_bytes())
assert final['original_cost_settled']and exit['original_cost_settled']and final['go']==go
def running(x):
 try:p=psutil.Process(x['pid']);return p.create_time()==x['creation']and p.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
while time.time()<end and running(v['owner']):time.sleep(.5)
assert not running(v['owner'])
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(P.read_bytes());assert c['active_segment']is None
segments=[s for s in c['completed_segments']if s.get('owner_parent_pid')==v['owner']['pid']];assert len(segments)==1
s=segments[0];fees={k:s['experts'][k]['charged_seconds']for k in go};assert abs(sum(fees.values())-s['charged_expert_seconds'])<1e-5
assert all(final['rows'][k]['terminal_all_own_children_waited']and s['experts'][k]['duration_bound_passed']for k in go)
for name in('native_floor_supervisor.lock','autonomy_controller.lock'):
 with(P.parent/name).open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[]
for p in sorted(O.iterdir()):
 if p.is_file()and p.suffix in('.json','.log'):
  raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),UTF8=raw.decode('utf8','replace')))
print(json.dumps(dict(passed=True,canonical_None=True,shared_locks_free=True,cohort_final=final,owner_exit=exit,original_one_owner_segment=s,raw_fee_sum_once=sum(fees.values()),closing_balance_snapshot=c['remaining_training_seconds'],full_UTF8=texts)))"""
        owner=d.code(client,d.PY72,owner_code,dict(owner=binding['owner'],go=go),timeout=900);put('OWNER_CLOSED_ACTUAL.json',owner)
        role=d.code(client,d.PY72,code,dict(spec=spec),timeout=210);put('NODE_CLOSED_FULLTEXT_ACTUAL.json',role)
        formals={}
        if role['qualified_formal']:
            formal=role['formal'];dest=N/'current_closed476_models/jump_72/formal/model_final.pt';dest.parent.mkdir(parents=True,exist_ok=False)
            sf=client.open_sftp()
            try:sf.get(formal['path'],str(dest))
            finally:sf.close()
            assert dest.stat().st_size==formal['bytes']and H(dest)==formal['SHA']
            formals['jump_72']=dict(path=str(dest),source=formal['path'],bytes=formal['bytes'],SHA=formal['SHA'],transfers=1,two_host_SHA_equal=True)
        put('ROOT476_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json',dict(passed_collection=True,run_id=task['run_id'],owner_closed=owner,roles={'jump_72':role},formals=formals,skill_not_inferred=True))
    assert formals,'No qualified complete final; preserve original failure'


def evaluate(final):
    assert not(R/'EVAL_ONCE.json').exists()
    task=read(N/'TASK476_FROZEN.json');complete=read(R/'ROOT476_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    e=read(V/'TASK477_PENDING.json');e.update(model_path=complete['roles']['jump_72']['formal']['path'],model_SHA=final['SHA'],model_bytes=final['bytes'],expected_Pi_updates=final['Pi'],source_full_CPU_receipt_SHA=H(R/'ROOT476_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),pending_actual_final_identity=False)
    put('TASK477_FROZEN.json',e,V)
    remotejob=task['job_root']+'/independent477'
    files=[];uploads={}
    for path in [*sorted((V/'source').glob('*.py')),V/'contract477.py',V/'target477_parent.py']:
        relative=path.relative_to(V).as_posix();uploads[relative]=path.read_bytes()
    uploads['TASK477.json']=raw(e)
    for rel,data in uploads.items():files.append(dict(relative=rel,bytes=len(data),SHA=hashlib.sha256(data).hexdigest()))
    wait_local()
    with connection('EVAL')as(client,d):
        put('EVAL_ONCE.json',dict(epoch=time.time(),task=e,job=remotejob,optimizer_steps=0))
        sf=client.open_sftp()
        try:
            for relative,data in uploads.items():stage(sf,remotejob+'/'+relative,data)
            stage(sf,remotejob+'/PACKAGE477_SOURCE_AND_TASK.json',raw(dict(files=files)))
        finally:sf.close()
        code="""from pathlib import Path
import contextlib,io,json,runpy,sys,time,traceback,hashlib
B=Path(v['job']);capture=io.StringIO();error=None
try:
 sys.argv=[str(B/'target477_parent.py'),'--task',str(B/'TASK477.json')]
 with contextlib.redirect_stdout(capture):runpy.run_path(sys.argv[0],run_name='__main__')
except BaseException:error=traceback.format_exc()
texts=[]
for root in(B,B/'actual_capture'):
 for p in sorted(root.glob('*')):
  if p.is_file()and p.suffix in('.json','.log'):
   b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
p=B/'actual_capture/RESULT477.json'
print(json.dumps(dict(epoch=time.time(),job=str(B),wrapper_error=error,full_UTF8=texts,parent_stdout=capture.getvalue(),result=json.loads(p.read_bytes())if p.is_file()else None)))"""
        value=d.code(client,d.PY72,code,dict(job=remotejob),timeout=1800);put('ROOT477_EVALUATION_FULL_RETURNED.json',value,V/'reports')
        assert not value['wrapper_error']and value['result']and value['result']['passed']
        (V/'replay').mkdir(exist_ok=False);rows=[];sf=client.open_sftp()
        try:
            for row in value['result']['replay']:
                path=V/'replay'/Path(row['path']).name;sf.get(row['path'],str(path));assert path.stat().st_size==row['bytes']and H(path)==row['SHA'];rows.append(dict(row,local_path=str(path),transfers=1,two_host_SHA_equal=True))
        finally:sf.close()
        put('ROOT477_SELECTED_REPLAY_TRANSFERS.json',dict(passed=True,model_SHA=e['model_SHA'],cases=rows),V/'reports')
    return value['result']


def postround():
    assert not(R/'POSTROUND_ONCE.json').exists()
    binding=read(R/'LIVE_BINDING.json');go=binding['current']['go']['jump_72']
    put('POSTROUND_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),sameprocesscollector=True))
    while time.time()<go['nominal_end_epoch']-898:time.sleep(min(10,max(.01,go['nominal_end_epoch']-898-time.time())))
    wait_local();close_original();final=cpu_final();assert final['passed']
    wait_local();result=evaluate(final)
    render=subprocess.run([CONTROL,'-B','-X','utf8',str(N/'render_saved_evaluation.py')],cwd=N,capture_output=True,text=True,encoding='utf8')
    put('RENDER_PROCESS.json',dict(returncode=render.returncode,stdout=render.stdout,stderr=render.stderr))
    assert render.returncode==0,render.stderr
    put('POSTROUND_RL_DECISION.json',dict(epoch=time.time(),status='EVALUATED_PENDING_NATIVE_REVIEW',final=final,strict=result['strict_successes'],terminations=result['terminations'],evalroot=str(V),next='Render recorded477 poses and inspectnative route/clearance/topmanifold; actively repair byactualevidence'))


def bind():
    assert not(R/'POSTROUND_BIND_ONCE.json').exists()and read(R/'LIVE_BINDING.json')['passed']
    put('POSTROUND_BIND_ONCE.json',dict(epoch=time.time(),no_network=True))
    with(R/'POSTROUND_STDOUT.log').open('xb')as out,(R/'POSTROUND_STDERR.log').open('xb')as err:
        process=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'postround'],cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    put('POSTROUND_LAUNCH.json',dict(epoch=time.time(),PID=process.pid,script=str(Path(__file__)),sameprocesscollector=True))
    print(json.dumps(dict(bound=True,PID=process.pid)))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['launch','first','bind','postround']);parser.add_argument('--index-SHA');args=parser.parse_args()
    if args.action=='launch':launch(args.index_SHA)
    elif args.action=='first':first()
    elif args.action=='bind':bind()
    else:postround()


if __name__=='__main__':
    try:main()
    except BaseException:
        put('CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),argv=sys.argv,error=traceback.format_exc(),no_automatic_replay=True));raise
