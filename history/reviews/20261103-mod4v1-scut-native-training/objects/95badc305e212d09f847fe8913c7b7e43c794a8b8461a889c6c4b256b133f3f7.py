"""One bounded same-final target-limit diagnostic, using original locks/transport."""
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

N = Path(__file__).resolve().parent
G = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
A = N/'env20000_published_recipe_1h_20261104/attempt02'
D = A/'target_limit_eval1'
R = D/'reports'
read = lambda p: json.loads(Path(p).read_bytes())
sha = lambda value: hashlib.sha256(value).hexdigest()


def put(path, value):
    with Path(path).open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


OWNER = '''from pathlib import Path
import fcntl,hashlib,importlib.util,json,os,subprocess,time,traceback
r=Path(__file__).resolve().parent;plan=json.loads((r/'PLAN.json').read_bytes());j=Path(plan['closed_root'])
s=importlib.util.spec_from_file_location('closed_mod4_original_owner',j/'owner.py');o=importlib.util.module_from_spec(s);s.loader.exec_module(o)
locks=[];worker=None;error=None
try:
 for path in [*o.b.LOCKS,o.C.parent.parent/('three_expert_v2_'+plan['GPU_UUID']+'.lock'),o.C.parent.parent/'finite_environment_validation.lock']:
  stream=path.open('rb+');locks.append(stream);fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert json.loads(o.C.read_bytes())['active_segment']is None
 release=json.loads((j/'OWNER_EXIT.json').read_bytes());assert release['all_own_waited']and release['original_cost_settled']and release['original_leases_released']
 resource=o.resource(plan['GPU_UUID']);o.put(r/'GPU_ADMISSION.json',resource)
 for row in json.loads((r/'INSTALL_MANIFEST.json').read_bytes()):
  value=(r/row['relative']).read_bytes();assert len(value)==row['bytes']and hashlib.sha256(value).hexdigest()==row['SHA']
 registry=plan['source_registry'];value=Path(registry['path']).read_bytes();assert len(value)==registry['bytes']and hashlib.sha256(value).hexdigest()==registry['SHA']
 o.put(r/'SOURCE_REGISTRY.json',dict(**registry,verified=True))
 task=json.loads((j/'TASK.json').read_bytes());env=o.environment(plan['GPU_UUID']);env['MOD4_SCUT_SOURCE_PATHS']=registry['path']
 overlays=[str(r/'overlay')]+task.get('module_overlays',[task['module_overlay']])
 code="import sys,runpy;sys.path.insert(0,"+repr(task['package_root'])+");import mod4v1_scut;mod4v1_scut.__path__[:0]="+repr(overlays)+";runpy.run_module('mod4v1_scut.evaluate',run_name='__main__')"
 c=plan['checkpoint'];args=['--assets',task['assets'],'--runtime',task['runtime'],'--runtime-manifest',task['runtime_manifest'],'--guard',task['guard'],'--profile',task['profile'],'--job-root',str(r/'evaluation'),'--checkpoint',c['path'],'--checkpoint-SHA',c['SHA'],'--repair-target-limits']
 for path in task['support']:args+=['--support',path]
 with(r/'WORKER.log').open('xb')as log:
  worker=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B','-c',code,*args],env=env,cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(f.fileno()for f in locks))
 o.put(r/'WORKER_IDENTITY.json',o.b.ident(worker.pid));rc=worker.wait()
 o.put(r/'WORKER_WAITED.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 result=r/'evaluation/RESULT.json'
 if rc or(r/'evaluation/ERROR.json').exists()or not result.exists()or not json.loads(result.read_bytes())['passed_execution']:
  raise RuntimeError('Target-limit diagnostic failed or omitted complete result: '+str(rc))
except BaseException:
 error=traceback.format_exc();o.put(r/'ERROR.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 for stream in reversed(locks):fcntl.flock(stream,fcntl.LOCK_UN);stream.close()
 o.put(r/'RELEASE.json',dict(epoch=time.time(),error=error,all_own_waited=worker is None or worker.poll()is not None,locks_released=True,optimizer_operations=0,ledger_writes=0))
'''


def prepare():
    facts = read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']
    assert facts['OWNER_EXIT.json']['all_own_waited'] and facts['OWNER_EXIT.json']['original_leases_released']
    assert facts['evaluation/RESULT.json']['strict'] == 0
    D.mkdir(); R.mkdir()
    plan = read(A/'PLAN.json')
    registry = next(x for x in read(N/'env20000_1h/INDEX_SOURCE_FROZEN.json')['files'] if x['relative'] == 'SOURCE_PATHS.json')
    value = dict(kind='SAME_FINAL_CONTRACT_TARGET_LIMIT_DIAGNOSTIC',
        closed_root=plan['remote_root'], remote_root=plan['remote_root']+'/'+D.name,
        checkpoint=facts['production/FINAL.json']['checkpoint'], GPU_UUID=plan['GPU_UUID'],
        source_registry=dict(path=plan['remote_root'].split('/env20000_published_recipe_')[0]+'/env20000_1h/SOURCE_PATHS.json',bytes=registry['bytes'],SHA=registry['SHA']),
        profile='trained_stair', num_envs=80, controls_max=400, seed=9137,
        repair='SCUT processed position clamp mapped to four MOD4 motor intervals before original D4 queue; same CAD difference',
        optimizer_operations=0, ledger_writes=0, source_checkpoint_unchanged=True,
        new_training_window=False, strict_reserve=plan['original_strictreserve'])
    put(D/'PLAN.json', value)
    (D/'owner_eval.py').write_text(OWNER, encoding='utf8', newline='\n'); ast.parse(OWNER)
    files=[]
    for name in ('config.py','target_limits.py','sdk.py','train.py','checkpoint.py','evaluate.py'):
        path=G/'project/isaac/mod4v1_scut'/name
        data=path.read_bytes(); ast.parse(data)
        files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(data),SHA=sha(data)))
    for name in ('owner_eval.py','PLAN.json'):
        path=D/name; data=path.read_bytes()
        files.append(dict(path=str(path),relative=name,bytes=len(data),SHA=sha(data)))
    put(D/'INDEX.json',dict(files=files,shared_index=str(A/'INDEX_SOURCE_FROZEN.json'),
        shared_index_SHA=sha((A/'INDEX_SOURCE_FROZEN.json').read_bytes()),source_only=True,
        whole_tree_model_asset_copy=False))
    print(json.dumps(dict(prepared=str(D),files=len(files),native=False)))


def prepare_first_axis():
    previous=read(R/'FULL_RETURNED.json')['files']
    assert previous['RELEASE.json']['all_own_waited']and previous['RELEASE.json']['locks_released']
    assert previous['evaluation/RESULT.json']['strict']==0
    assert read(R/'ACTUAL_TARGET_LIMIT_NATIVE_REVIEW.json')['actual_all_motor_intervals_passed']
    plan=read(D/'PLAN.json')
    plan.update(kind='SAME_FINAL_FIRST_AXIS_REINITIALIZATION_DIAGNOSTIC',
        repair_first_axis=True,source_revision=2,
        repair='Existing nativeverified target limits plus explicit first output row/bias0 and STD1; other actor/critic source intact',
        prior_result=str(R/'ACTUAL_TARGET_LIMIT_NATIVE_REVIEW.json'))
    put(D/'PLAN_FIRST_AXIS.json',plan)
    wrapper=OWNER
    replacements=[("r/'PLAN.json'","r/'PLAN_FIRST_AXIS.json'"),
        ("r/'INSTALL_MANIFEST.json'","r/'INSTALL_MANIFEST_FIRST_AXIS.json'"),
        ("r/'overlay'","r/'overlay_first_axis'"),("r/'evaluation'","r/'evaluation_first_axis'"),
        ("r/'WORKER.log'","r/'WORKER_FIRST_AXIS.log'"),
        ("r/'WORKER_IDENTITY.json'","r/'WORKER_IDENTITY_FIRST_AXIS.json'"),
        ("r/'WORKER_WAITED.json'","r/'WORKER_WAITED_FIRST_AXIS.json'"),
        ("r/'ERROR.json'","r/'ERROR_FIRST_AXIS.json'"),
        ("r/'RELEASE.json'","r/'RELEASE_FIRST_AXIS.json'"),
        ("r/'GPU_ADMISSION.json'","r/'GPU_ADMISSION_FIRST_AXIS.json'"),
        ("r/'SOURCE_REGISTRY.json'","r/'SOURCE_REGISTRY_FIRST_AXIS.json'"),
        ("r/'evaluation/RESULT.json'","r/'evaluation_first_axis/RESULT.json'"),
        ("r/'evaluation/ERROR.json'","r/'evaluation_first_axis/ERROR.json'"),
        ("'--repair-target-limits']","'--repair-target-limits','--repair-first-axis']")]
    for old,new in replacements:
        assert wrapper.count(old)==1,(old,wrapper.count(old))
        wrapper=wrapper.replace(old,new)
    ast.parse(wrapper)
    (D/'owner_first_axis.py').write_text(wrapper,encoding='utf8',newline='\n')
    files=[]
    for name in ('config.py','target_limits.py','sdk.py','train.py','checkpoint.py','evaluate.py','finetune.py'):
        path=G/'project/isaac/mod4v1_scut'/name;value=path.read_bytes();ast.parse(value)
        files.append(dict(path=str(path),relative='overlay_first_axis/'+name,bytes=len(value),SHA=sha(value)))
    for name in ('owner_first_axis.py','PLAN_FIRST_AXIS.json'):
        path=D/name;value=path.read_bytes()
        files.append(dict(path=str(path),relative=name,bytes=len(value),SHA=sha(value)))
    put(D/'INDEX_FIRST_AXIS.json',dict(files=files,previous_index_SHA=sha((D/'INDEX.json').read_bytes()),
        same_diagnostic_namespace=True,whole_tree_model_asset_copy=False))
    print(json.dumps(dict(prepared=True,source_revision=2,files=len(files),native=False)))


def first_axis(recover=False):
    """Reuse bounded controller with separate once/results in the same namespace."""
    import inspect
    global R
    prior=R; R=D/'reports_first_axis';R.mkdir(exist_ok=True)
    text=inspect.getsource(run)
    for old,new in [("D/'PLAN.json'","D/'PLAN_FIRST_AXIS.json'"),("D/'INDEX.json'","D/'INDEX_FIRST_AXIS.json'"),
        ('TARGET_LIMIT_NATIVE01','FIRST_AXIS_NATIVE01'),
        ("p.mkdir(exist_ok=False);(p/'overlay').mkdir()","assert p.is_dir();(p/'overlay_first_axis').mkdir()"),
        ("'/INSTALL_MANIFEST.json'","'/INSTALL_MANIFEST_FIRST_AXIS.json'"),
        ("r/'OWNER.log'","r/'OWNER_FIRST_AXIS.log'"),("r/'owner_eval.py'","r/'owner_first_axis.py'"),
        ("'WORKER.log','OWNER.log'","'WORKER_FIRST_AXIS.log','OWNER_FIRST_AXIS.log'"),
        ("D/'evaluation'","D/'evaluation_first_axis'")]:
        assert old in text,old
        text=text.replace(old,new)
    old=" p=r/name\n if p.is_file():files[name]=json.loads(p.read_bytes())"
    new=""" actual=name.replace('evaluation/','evaluation_first_axis/')
 if '/' not in name:actual=name.replace('.json','_FIRST_AXIS.json')
 p=r/actual
 if p.is_file():files[name]=json.loads(p.read_bytes())"""
    assert text.count(old)==1
    text=text.replace(old,new)
    scope=dict(globals());exec(compile(text,str(Path(__file__)),'exec'),scope);scope['run'](recover)


def run(recover=False):
    if recover:
        assert(R/'CONTROLLER_ONCE.json').exists()
        assert not(R/'LAUNCH_ONCE.json').exists() and not(R/'ADMISSION.json').exists()
        assert read(R/'TARGET_LIMIT_NATIVE01_LOCAL_CIM.json')['serialFREE'] is False
        assert not(R/'PRELAUNCH_RECOVERY_ONCE.json').exists()
    else:
        assert not(R/'CONTROLLER_ONCE.json').exists()
        put(R/'CONTROLLER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),sole_controller=True))
    s=importlib.util.spec_from_file_location('target_limits_original_transport',N/'run.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.R=R
    plan=read(D/'PLAN.json');index=read(D/'INDEX.json')
    for row in index['files']:
        value=Path(row['path']).read_bytes();assert len(value)==row['bytes']and sha(value)==row['SHA']
    label='TARGET_LIMIT_NATIVE01_RECOVERY' if recover else 'TARGET_LIMIT_NATIVE01'
    with m.connection(label)as(client,transport):
        if recover:
            put(R/'PRELAUNCH_RECOVERY_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),
                previous_refusal_before_network=True,old_marker_preserved=True,
                production_launch_replayed=False))
        query='''from pathlib import Path
import json,time
b=Path('/home/lc01/Zonglin Li/zonglin2');c=json.loads((b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());j=Path(v['closed_root'])
s=json.loads((j/'OWNER_STARTED.json').read_bytes());e=json.loads((j/'OWNER_EXIT.json').read_bytes())
ready=c['active_segment']is None and e['all_own_waited']and e['original_cost_settled']and e['original_leases_released']
peer={}
if c['active_segment']:
 root=b/'tasks'/c['active_segment']['owner_run_id']
 for name in ['OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_EXIT.json','GO_PRODUCTION.json']:
  path=root/name;peer[name]=json.loads(path.read_bytes())if path.is_file()else None
 peer['root']=str(root)
print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],remaining=c['remaining_training_seconds'],prior_start=s,prior_exit=e,current_peer=peer,PT_reads=0,physics=0,GPU_scan=0)))'''
        admission=transport.code(client,transport.PY72,query,plan,timeout=40)
        put(R/'ADMISSION.json',admission)
        if not admission['ready']:
            print(json.dumps(dict(resource_busy=True,native=False)));return
        create="from pathlib import Path\nimport json\np=Path(v['remote_root']);p.mkdir(exist_ok=False);(p/'overlay').mkdir();print(json.dumps(dict(created=str(p))))"
        transport.code(client,transport.PY72,create,plan,timeout=40)
        sf=client.open_sftp()
        try:
            for row in index['files']:
                with sf.file(plan['remote_root']+'/'+row['relative'],'wx')as stream:stream.write(Path(row['path']).read_bytes())
            with sf.file(plan['remote_root']+'/INSTALL_MANIFEST.json','wx')as stream:stream.write(json.dumps(index['files']).encode())
        finally:sf.close()
        put(R/'LAUNCH_ONCE.json',dict(epoch=time.time(),plan=plan,index_SHA=sha((D/'INDEX.json').read_bytes())))
        start='''from pathlib import Path
import json,psutil,subprocess,time
r=Path(v['remote_root'])
with(r/'OWNER.log').open('xb')as log:p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(r/'owner_eval.py')],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
q=psutil.Process(p.pid);print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline())))'''
        identity=transport.code(client,transport.PY72,start,plan,timeout=40);put(R/'OWNER_LAUNCH.json',identity)
        for poll in range(60):
            query='''from pathlib import Path
import json,psutil,time
r=Path(v['root']);files={}
for name in ['GPU_ADMISSION.json','SOURCE_REGISTRY.json','WORKER_IDENTITY.json','WORKER_WAITED.json','RELEASE.json','ERROR.json','evaluation/NATIVE_STARTUP.json','evaluation/RESULT.json','evaluation/ALL80.json','evaluation/CONTROL_CURVES.json','evaluation/ERROR.json','evaluation/APP_CLOSE_INTENT.json']:
 p=r/name
 if p.is_file():files[name]=json.loads(p.read_bytes())
for name in ['WORKER.log','OWNER.log']:
 p=r/name
 if p.is_file():
  with p.open('rb')as stream:stream.seek(max(0,p.stat().st_size-10000));files[name]=stream.read().decode('utf8','replace')
alive=False
try:p=psutil.Process(v['pid']);alive=p.create_time()==v['creation']and p.status()!=psutil.STATUS_ZOMBIE
except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=files,exact_owner_alive=alive)))'''
            returned=transport.code(client,transport.PY72,query,dict(root=plan['remote_root'],**identity),timeout=40)
            if 'RELEASE.json'in returned['files']and not returned['exact_owner_alive']:
                put(R/'FULL_RETURNED.json',returned)
                evaluation=returned['files'].get('evaluation/RESULT.json')
                transfers=[]
                if evaluation:
                    (D/'evaluation').mkdir();sf=client.open_sftp()
                    try:
                        for key in ('all80_manifold','actual_poses'):
                            row=evaluation[key];path=D/'evaluation'/Path(row['path']).name
                            sf.get(row['path'],str(path))
                            with path.open('rb')as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
                            assert path.stat().st_size==row['bytes']and digest==row['SHA']
                            transfers.append(dict(row,local_path=str(path),SHA_verified=True))
                    finally:sf.close()
                put(R/'TRANSFERS.json',dict(files=transfers,PT_reads=0,new_physics=0))
                put(R/'COMPLETED.json',dict(epoch=time.time(),execution_passed=bool(evaluation and evaluation['passed_execution']),release=returned['files']['RELEASE.json']))
                print(json.dumps(dict(result=evaluation,release=returned['files']['RELEASE.json'])),flush=True);return
            if poll%6==0:print(json.dumps(dict(poll=poll,files=list(returned['files']))),flush=True)
            time.sleep(10)
        put(R/'FINITE_WAIT_PENDING.json',returned)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run','recover_prelaunch','prepare_first_axis','first_axis','first_axis_recover']);args=p.parse_args()
    try:
        if args.mode=='recover_prelaunch':run(True)
        elif args.mode=='first_axis_recover':first_axis(True)
        else:globals()[args.mode]()
    except BaseException:
        if R.exists():put(R/('LOCAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
        raise
