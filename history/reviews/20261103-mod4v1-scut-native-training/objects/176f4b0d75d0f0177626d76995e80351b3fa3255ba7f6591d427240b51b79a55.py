"""Finite original E0 inference on the current SCUT task; no training or ledger writes.

Reuse the existing serial diagnostic transport/ownwait implementation. Only the
explicit source and returned observation-comparison report differ.
"""
from pathlib import Path
import argparse, ast, hashlib, importlib.util, inspect, json, os, subprocess, time, traceback

N=Path(__file__).resolve().parent
A=N/'env20000_repair_e0_1h_20261104'
D=A/'e0_source_diagnostic';R=D/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()

def put(p,value):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2)

def shared():
    s=importlib.util.spec_from_file_location('existing_finite_evaluation',N/'action_clip_eval.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    return m

def prepare():
    closed=read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']
    assert closed['OWNER_EXIT.json']['all_own_waited']and closed['OWNER_EXIT.json']['original_leases_released']
    p=read(A/'PLAN.json');identity=closed['OWNER_STARTED.json']['identity']
    D.mkdir();R.mkdir()
    plan=dict(kind='ORIGINAL_E0_SAME_SCUT_TASK_INPUT_DIAGNOSTIC',closed_root=p['remote_root'],
        remote_root=p['remote_root']+'/e0_source_diagnostic',checkpoint=p['source_checkpoint'],
        GPU_UUID=p['GPU_UUID'],peer_root=p['remote_root'],peer_identity=identity,
        num_envs=80,controls_max=400,seed=9137,optimizer_operations=0,ledger_writes=0,
        no_new_training_window=True,source_checkpoint_unchanged=True,
        purpose='Compare original E0 and adapted observations/actions at identical physical endpoints; adapted actions drive the actual task')
    wrapper=shared().WRAPPER
    assert wrapper.count("'--repair-unclipped-v2'")==1
    wrapper=wrapper.replace("'--repair-unclipped-v2'","'--e0-source-diagnostic'")
    ast.parse(wrapper);owner=D/'owner_eval.py';owner.write_text(wrapper,encoding='utf8',newline='\n')
    put(D/'PLAN.json',plan)
    files=[]
    for path,relative in [(G/'project/isaac/mod4v1_scut/evaluate.py','overlay/evaluate.py'),(owner,'owner_eval.py'),(D/'PLAN.json','PLAN.json')]:
        raw=path.read_bytes()
        if path.suffix=='.py':ast.parse(raw)
        files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=H(raw)))
    put(D/'INDEX_SOURCE_FROZEN.json',dict(files=files,prior_overlay=p['module_overlay'],shared_package=p['package_root'],
        new_tree_or_model_copy=False,training_updates=0))
    print(json.dumps(dict(prepared=str(D),files=len(files),native_pending=True)))

def run():
    m=shared();m.D=D;m.R=R
    code=inspect.getsource(m.run)
    for before,after in [('PLAN_REV3.json','PLAN_NATIVE_REV2.json'),('SOURCE_FROZEN_REV3.json','INDEX_NATIVE_REV2.json'),
        ('ACTION_CLIP_NATIVE01','E0_SOURCE_NATIVE02'),('ORIGINAL_ADMISSION_READ.json','ORIGINAL_ADMISSION_READ02.json'),
        ("'evaluation/CONTROL_CURVES.json','evaluation/ERROR.json'","'evaluation/CONTROL_CURVES.json','evaluation/E0_INPUT_COMPARISON.json','evaluation/ERROR.json'")]:
        assert code.count(before)==1
        code=code.replace(before,after)
    exec(compile(code,str(N/'action_clip_eval.py'),'exec'),m.__dict__)
    m.run(False)

def revise():
    assert not(R/'LAUNCH_ONCE.json').exists()
    peer=read(R/'RESOURCE_EXACT_CURRENT_PEER.json')
    plan=read(D/'PLAN.json')
    plan.update(peer_root=peer['peer_root'],peer_identity=peer['peer']['OWNER_STARTED.json']['identity'],
        peer_original_go=peer['peer']['GO_PRODUCTION.json'],
        wait_until=peer['peer']['GO_PRODUCTION.json']['nominal_end_epoch']+900,
        prior_original_release=read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']['OWNER_EXIT.json'])
    put(D/'PLAN_NATIVE_REV2.json',plan)
    index=read(D/'INDEX_SOURCE_FROZEN.json')
    for row in index['files']:
        if row['relative']=='PLAN.json':row['path']=str(D/'PLAN_NATIVE_REV2.json')
        raw=Path(row['path']).read_bytes();row.update(bytes=len(raw),SHA=H(raw))
    put(D/'INDEX_NATIVE_REV2.json',index)
    print(json.dumps(dict(revised=True,peer=plan['peer_root'],wait_until=plan['wait_until'])))

def timer():
    assert not(R/'RESOURCE_TIMER_ONCE.json').exists()
    put(R/'RESOURCE_TIMER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),local_wait_only=True))
    deadline=read(D/'PLAN_NATIVE_REV2.json')['wait_until']
    while time.time()<deadline:time.sleep(min(10,deadline-time.time()))
    # run.py checks fresh broad local controller identities before any SSH.
    run()
    put(R/'RESOURCE_TIMER_COMPLETED.json',dict(epoch=time.time(),native_launched=(R/'LAUNCH_ONCE.json').exists(),
        full_returned=(R/'FULL_RETURNED.json').exists()))

def bind():
    assert not(R/'RESOURCE_TIMER_BIND_ONCE.json').exists()
    s=importlib.util.spec_from_file_location('source_timer_local_only',N/'run.py')
    local=importlib.util.module_from_spec(s);s.loader.exec_module(local)
    rows=local.local_rows()
    assert not any(row['ProcessId']!=os.getpid()for row in rows),'Other local controller active'
    source=Path(__file__).read_bytes()
    put(D/'RESOURCE_TIMER_SOURCE_FROZEN.json',dict(path=str(Path(__file__)),bytes=len(source),SHA=H(source),
        native_index_SHA=H((D/'INDEX_NATIVE_REV2.json').read_bytes()),fresh_local_rows=rows,local_timer_only=True))
    put(R/'RESOURCE_TIMER_BIND_ONCE.json',dict(epoch=time.time(),sole_local_waiter=True))
    with(R/'RESOURCE_TIMER_STDOUT.log').open('xb')as out,(R/'RESOURCE_TIMER_STDERR.log').open('xb')as err:
        p=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(Path(__file__)),'timer'],
            cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(p.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    q=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put(R/'RESOURCE_TIMER_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(q.stdout)))
    print(json.dumps(dict(bound=True,PID=p.pid)))

def resource_context():
    """Finite exact current-owner metadata only; no SDK, GPU or PT access."""
    s=importlib.util.spec_from_file_location('source_diagnostic_serial',N/'run.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.R=R
    with m.connection('E0_SOURCE_PEER_CONTEXT')as(client,d):
        code="""from pathlib import Path
import json,time,psutil
b=Path('/home/lc01/Zonglin Li/zonglin2');c=json.loads((b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];docs={};identity=None;root=None
if a is not None:
 root=b/'tasks'/a['owner_run_id']
 for name in ['OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_EXIT.json','GO_PRODUCTION.json']:
  p=root/name
  docs[name]=json.loads(p.read_bytes())if p.exists()else None
 try:
  p=psutil.Process(a['owner_parent_pid']);identity=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),canonical_active=a,peer_root=str(root)if root else None,peer=docs,exact_identity=identity,modelreads=0,physics=0,GPUscan=0)))"""
        value=d.code(client,d.PY72,code,{},timeout=40)
        put(R/'RESOURCE_EXACT_CURRENT_PEER.json',value)
        print(json.dumps(value))

def prepare_repair():
    """Append an isolated control revision inside the same diagnostic root."""
    returned=read(R/'FULL_RETURNED.json')
    assert returned['files']['RELEASE.json']['all_own_waited']and returned['files']['RELEASE.json']['locks_released']
    assert 'evaluation/ERROR.json'in returned['files']and 'evaluation/RESULT.json'not in returned['files']
    plan=read(D/'PLAN_NATIVE_REV2.json')
    # The already frozen successful production entry explicitly binds this
    # shared registry. Its run root deliberately does not contain a copy.
    entry=ast.parse((A/'entry.py').read_bytes())
    binding=next(ast.literal_eval(n.value)for n in ast.walk(entry)if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Subscript)and isinstance(t.value,ast.Attribute)
            and t.value.attr=='environ'and isinstance(t.slice,ast.Constant)
            and t.slice.value=='MOD4_SCUT_SOURCE_PATHS'for t in n.targets))
    expected=next(x for x in read(N/'env20000_1h/INDEX_SOURCE_FROZEN.json')['files']if x['relative']=='SOURCE_PATHS.json')
    plan.update(source_paths=dict(path=binding,bytes=expected['bytes'],SHA=expected['SHA']),
        control_revision=3,prior_failure=str(R/'FULL_RETURNED.json'),
        diagnostic_only=True,model_reads_in_failed_attempt=0,physics_steps_in_failed_attempt=0)
    put(D/'PLAN_NATIVE_REV3.json',plan)
    wrapper=(D/'owner_eval.py').read_text(encoding='utf8')
    replacements=[("r/'PLAN.json'","r/'PLAN_NATIVE_REV3.json'"),
        ("r/'INSTALL_MANIFEST.json'","r/'INSTALL_MANIFEST03.json'"),
        ("r/'overlay'","r/'overlay03'"),("r/'evaluation'","r/'evaluation03'"),
        ("r/'WORKER.log'","r/'WORKER03.log'"),("r/'WORKER_IDENTITY.json'","r/'WORKER_IDENTITY03.json'"),
        ("r/'WORKER_WAITED.json'","r/'WORKER_WAITED03.json'"),
        ("r/'ORIGINAL_ERROR.json'","r/'ORIGINAL_ERROR03.json'"),("r/'RELEASE.json'","r/'RELEASE03.json'"),
        ("env['MOD4_SCUT_SOURCE_PATHS']=str(j/'SOURCE_PATHS.json')","env['MOD4_SCUT_SOURCE_PATHS']=plan['source_paths']['path']")]
    for before,after in replacements:
        assert wrapper.count(before)==1,(before,wrapper.count(before))
        wrapper=wrapper.replace(before,after)
    before=" env=o.environment(plan['GPU_UUID']);env['MOD4_SCUT_SOURCE_PATHS']=plan['source_paths']['path']"
    after=""" source_registry=plan['source_paths'];source_raw=Path(source_registry['path']).read_bytes()
 assert len(source_raw)==source_registry['bytes']and hashlib.sha256(source_raw).hexdigest()==source_registry['SHA']
 o.put(r/'SOURCE_REGISTRY_RESOLVED03.json',dict(**source_registry,passed=True,checkpoint_reads=0,physics_steps=0))
 env=o.environment(plan['GPU_UUID']);env['MOD4_SCUT_SOURCE_PATHS']=source_registry['path']"""
    assert wrapper.count(before)==1
    wrapper=wrapper.replace(before,after)
    before=" if rc:raise RuntimeError('Actual diagnostic worker failed: '+str(rc))"
    after=""" if rc or (r/'evaluation03/ERROR.json').exists()or not(r/'evaluation03/RESULT.json').exists():
  raise RuntimeError('Actual diagnostic worker failed or omitted complete result: '+str(rc))"""
    assert wrapper.count(before)==1
    wrapper=wrapper.replace(before,after);ast.parse(wrapper)
    owner=D/'owner_eval03.py';owner.write_text(wrapper,encoding='utf8',newline='\n')
    files=[]
    for p,relative in [(G/'project/isaac/mod4v1_scut/evaluate.py','overlay03/evaluate.py'),
                       (owner,'owner_eval03.py'),(D/'PLAN_NATIVE_REV3.json','PLAN_NATIVE_REV3.json')]:
        raw=p.read_bytes()
        if p.suffix=='.py':ast.parse(raw)
        files.append(dict(path=str(p),relative=relative,bytes=len(raw),SHA=H(raw)))
    put(D/'INDEX_NATIVE_REV3.json',dict(files=files,shared_source_registry=plan['source_paths'],
        previous_index_SHA=H((D/'INDEX_NATIVE_REV2.json').read_bytes()),
        same_diagnostic_namespace=True,full_tree_model_asset_copy=False))
    (R/'attempt03').mkdir()
    print(json.dumps(dict(repaired_plan=str(D/'PLAN_NATIVE_REV3.json'),registry=plan['source_paths'],native_started=False)))

def run_repair():
    m=shared();m.D=D;m.R=R/'attempt03'
    code=inspect.getsource(m.run)
    for before,after in [('PLAN_REV3.json','PLAN_NATIVE_REV3.json'),('SOURCE_FROZEN_REV3.json','INDEX_NATIVE_REV3.json'),
        ('ACTION_CLIP_NATIVE01','E0_SOURCE_NATIVE03'),("r/'OWNER.log'","r/'OWNER03.log'"),
        ("r/'owner_eval.py'","r/'owner_eval03.py'"),("'/INSTALL_MANIFEST.json'","'/INSTALL_MANIFEST03.json'"),
        ("(D/'evaluation')","(D/'evaluation03')"),
        ("'evaluation/CONTROL_CURVES.json','evaluation/ERROR.json'","'evaluation/CONTROL_CURVES.json','evaluation/E0_INPUT_COMPARISON.json','SOURCE_REGISTRY_RESOLVED03.json','evaluation/ERROR.json'")]:
        assert code.count(before)>=1,(before,code.count(before))
        code=code.replace(before,after)
    before="p.mkdir(exist_ok=False);(p/'overlay').mkdir()"
    assert code.count(before)==1
    code=code.replace(before,"assert p.is_dir();(p/'overlay03').mkdir()")
    before=" p=r/name\n if p.is_file():f[name]=json.loads(p.read_bytes())"
    after=""" actual=name.replace('evaluation/','evaluation03/')
 actual={'WORKER_WAITED.json':'WORKER_WAITED03.json','ORIGINAL_ERROR.json':'ORIGINAL_ERROR03.json','RELEASE.json':'RELEASE03.json'}.get(actual,actual)
 p=r/actual
 if p.is_file():f[name]=json.loads(p.read_bytes())"""
    assert code.count(before)==1
    code=code.replace(before,after)
    before="p=r/'WORKER.log'"
    assert code.count(before)==1
    code=code.replace(before,"p=r/'WORKER03.log'")
    if (D/'RESOURCE_WAIT03_FROZEN.json').exists():
        before="plan=read(D/'PLAN_NATIVE_REV3.json');index=read(D/'INDEX_NATIVE_REV3.json')"
        assert code.count(before)==1
        code=code.replace(before,before+";plan['resource_wait']=read(D/'RESOURCE_WAIT03_FROZEN.json')")
        before="print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],peer_exit=e,peer_identity_matches=same,GPUscan=0,modelreads=0,physics=0)))"
        after="""wait=v.get('resource_wait');wait_release=None
if wait:
 w=Path(wait['peer_root']);ws=json.loads((w/'OWNER_STARTED.json').read_bytes())['identity'];wp=w/'OWNER_EXIT.json';we=json.loads(wp.read_bytes())if wp.exists()else None
 wait_release=dict(identity_matches=ws['pid']==wait['peer_identity']['pid']and ws['creation']==wait['peer_identity']['creation'],exit=we)
 ready=ready and wait_release['identity_matches']and we is not None and we['all_own_waited']and we['original_cost_settled']and we['original_leases_released']
print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],peer_exit=e,peer_identity_matches=same,exact_wait_peer=wait_release,GPUscan=0,modelreads=0,physics=0)))"""
        assert code.count(before)==1
        code=code.replace(before,after)
    exec(compile(code,str(N/'action_clip_eval.py'),'exec'),m.__dict__)
    m.run(False)

def repair_resource_context():
    s=importlib.util.spec_from_file_location('repair_diagnostic_serial',N/'run.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.R=R/'attempt03'
    with m.connection('E0_SOURCE_REPAIR_PEER')as(client,d):
        code="""from pathlib import Path
import json,time,psutil,hashlib
b=Path('/home/lc01/Zonglin Li/zonglin2');c=json.loads((b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());active=c['active_segment'];docs={};identity=None;root=None
if active is not None:
 root=b/'tasks'/active['owner_run_id']
 for name in ['OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_EXIT.json','GO_PRODUCTION.json']:
  p=root/name;docs[name]=json.loads(p.read_bytes())if p.exists()else None
 try:
  p=psutil.Process(active['owner_parent_pid']);identity=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:pass
registry=v['source_paths'];p=Path(registry['path']);raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert len(raw)==registry['bytes']and sha==registry['SHA']
paths=json.loads(raw);source_present={key:Path(value).is_file()for key,value in paths.items()}
print(json.dumps(dict(epoch=time.time(),canonical_active=active,peer_root=str(root)if root else None,peer=docs,exact_identity=identity,source_registry=dict(**registry,actual_SHA=sha,files_exist=source_present),PT_reads=0,physics=0,GPUscan=0)))"""
        value=d.code(client,d.PY72,code,read(D/'PLAN_NATIVE_REV3.json'),timeout=40)
        put(R/'attempt03/RESOURCE_EXACT_CURRENT_PEER.json',value)
        print(json.dumps(value))

def repair_bind():
    target=R/'attempt03'
    assert not(target/'RESOURCE_TIMER_BIND_ONCE.json').exists()
    peer=read(target/'RESOURCE_EXACT_CURRENT_PEER.json')
    go=peer['peer']['GO_PRODUCTION.json']
    wait=dict(peer_root=peer['peer_root'],peer_identity=peer['peer']['OWNER_STARTED.json']['identity'],
        peer_original_go=go,wait_until=go['nominal_end_epoch']+900,source_registry_actual=peer['source_registry'])
    put(D/'RESOURCE_WAIT03_FROZEN.json',wait)
    s=importlib.util.spec_from_file_location('repair_wait_local_only',N/'run.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    rows=m.local_rows();assert not any(x['ProcessId']!=os.getpid()for x in rows),'Other local controller active'
    raw=Path(__file__).read_bytes()
    put(D/'RESOURCE_TIMER03_SOURCE_FROZEN.json',dict(path=str(Path(__file__)),bytes=len(raw),SHA=H(raw),
        native_index_SHA=H((D/'INDEX_NATIVE_REV3.json').read_bytes()),resource_wait_SHA=H((D/'RESOURCE_WAIT03_FROZEN.json').read_bytes()),local_rows=rows))
    put(target/'RESOURCE_TIMER_BIND_ONCE.json',dict(epoch=time.time(),sole_local_waiter=True))
    with(target/'RESOURCE_TIMER_STDOUT.log').open('xb')as out,(target/'RESOURCE_TIMER_STDERR.log').open('xb')as err:
        p=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(Path(__file__)),'repair_timer'],
            cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(p.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    q=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put(target/'RESOURCE_TIMER_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(q.stdout)))
    print(json.dumps(dict(bound=True,PID=p.pid,wait_until=wait['wait_until'])))

def repair_timer():
    target=R/'attempt03'
    assert not(target/'RESOURCE_TIMER_ONCE.json').exists()
    put(target/'RESOURCE_TIMER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),localwait=True))
    deadline=read(D/'RESOURCE_WAIT03_FROZEN.json')['wait_until']
    while time.time()<deadline:time.sleep(min(10,deadline-time.time()))
    run_repair()
    put(target/'RESOURCE_TIMER_COMPLETED.json',dict(epoch=time.time(),launch_consumed=(target/'LAUNCH_ONCE.json').exists(),
        full_returned=(target/'FULL_RETURNED.json').exists()))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run','resource_context','revise','bind','timer','prepare_repair','run_repair','repair_resource_context','repair_bind','repair_timer']);a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        if R.exists():put(R/('ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
        raise
