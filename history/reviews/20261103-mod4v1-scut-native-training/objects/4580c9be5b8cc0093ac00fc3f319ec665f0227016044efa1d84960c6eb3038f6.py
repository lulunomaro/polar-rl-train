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

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run','resource_context','revise','bind','timer']);a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        if R.exists():put(R/('ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
        raise
