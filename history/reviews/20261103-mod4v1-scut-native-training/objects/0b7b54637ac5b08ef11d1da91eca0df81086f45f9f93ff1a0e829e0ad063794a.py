"""Reuse the original serial launch/return controller for the repaired E0 window."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,time,traceback

N=Path(__file__).resolve().parent;A=N/'env20000_repair_e0_1h_20261104';R=A/'reports'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
read=lambda p:json.loads(Path(p).read_bytes())
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(name,value):
    with(R/name).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2)

def launch():
    old=read(N/'env20000_1h/action_clip_eval1/reports/FULL_RETURNED.json')['files']
    assert old['RELEASE.json']['all_own_waited']and old['RELEASE.json']['locks_released']
    m=load('repaired_original_serial',N/'run.py');m.N=A;m.R=R
    m.launch()

def bind():
    assert not(R/'POSTROUND_BIND_ONCE.json').exists()
    facts=read(R/'FIRST_ACTUAL_RETURNED.json')['files']
    assert facts['production/FIRST_UPDATED.json']['actual_onpolicy_samples']==480000
    put('POSTROUND_BIND_ONCE.json',dict(epoch=time.time(),sole_receiver=True,owner_controls_save_exit_eval=True))
    with(R/'POSTROUND_STDOUT.log').open('xb')as out,(R/'POSTROUND_STDERR.log').open('xb')as err:
        p=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'collect','--root',str(A)],cwd=N,
            stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    cmd='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(p.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    q=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',cmd],capture_output=True,text=True,encoding='utf8',check=True)
    put('POSTROUND_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(q.stdout),sole_receiver=True))
    print(json.dumps(dict(bound=True,PID=p.pid)))

def recover_bind():
    """Replace only the collector that refused the old default root locally."""
    assert(R/'POSTROUND_BIND_ONCE.json').exists()
    assert not(R/'POSTROUND_ONCE.json').exists()
    assert not(R/'POSTROUND_RECOVERY_BIND_ONCE.json').exists()
    assert 'POSTROUND_ONCE.json' in (R/'POSTROUND_STDERR.log').read_text(encoding='utf-8')
    local=load('recovered_receiver_local_gate',N/'run.py')
    assert not any(row['ProcessId']!=os.getpid()for row in local.local_rows()),'Another controller active'
    put('POSTROUND_RECOVERY_BIND_ONCE.json',dict(epoch=time.time(),sole_receiver=True,
        reason='Original collector omitted --root and refused old alreadyconsumed POSTROUND_ONCE before network',
        failed_bind_preserved=True,network_or_production_replay=False))
    with(R/'POSTROUND_RECOVERY_STDOUT.log').open('xb')as out,(R/'POSTROUND_RECOVERY_STDERR.log').open('xb')as err:
        p=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'collect','--root',str(A)],cwd=N,
            stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(p.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    result=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,encoding='utf-8',check=True)
    put('POSTROUND_RECOVERY_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(result.stdout),sole_receiver=True))
    print(json.dumps(dict(bound=True,PID=p.pid,recovered_local_receiver=True)))

def collect():
    assert not(R/'POSTROUND_ONCE.json').exists()
    go=read(R/'FIRST_ACTUAL_RETURNED.json')['files']['GO_PRODUCTION.json'];job=read(A/'PLAN.json')['remote_root']
    put('POSTROUND_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),sameprocess_finite_receiver=True))
    while time.time()<go['save_deadline']+45:time.sleep(min(10,go['save_deadline']+45-time.time()))
    receiver=load('repaired_original_postround',N/'postround.py');receiver.A=A;receiver.R=R;receiver.m.R=R
    receiver.put=put
    start=time.time()
    while any(row['ProcessId']!=os.getpid()for row in receiver.m.local_rows()):
        if time.time()-start>10800:raise RuntimeError('Local serial controller still active')
        time.sleep(10)
    receiver.receive(job,'REPAIRED_E0_POSTROUND_RETURN')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['launch','bind','collect','recover_bind'])
    p.add_argument('--root',type=Path);a=p.parse_args()
    if a.root is not None:
        A=a.root.resolve();assert A.is_relative_to(N)and(A/'PLAN.json').is_file()
        R=A/'reports'
    try:globals()[a.mode]()
    except BaseException:
        put('CONTROL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
