"""Reuse the existing finite controller after exact original peer release."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import inspect
import json
import os
import subprocess
import time
import traceback
N=Path(__file__).resolve().parent
D=N/'env20000_target_axis_repair_1h_20261104/scut_stairs_eval1'
R=D/'reports'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
def put(name,value):
    with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2)
def controller():
    spec=importlib.util.spec_from_file_location('scut_existing_finite_diagnostic',N/'target_limits_control.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=D;m.R=R
    source=inspect.getsource(m.run)
    needle="ready=c['active_segment']is None and e['all_own_waited']and e['original_cost_settled']and e['original_leases_released']"
    wait=json.loads((D/'RESOURCE_WAIT.json').read_bytes())
    additional="""
fixed_peer=Path(%r)
peer_started=json.loads((fixed_peer/'OWNER_STARTED.json').read_bytes())
assert peer_started['identity']['pid']==%r and peer_started['identity']['creation']==%r
exit_path=fixed_peer/'OWNER_EXIT.json'
peer_exit=json.loads(exit_path.read_bytes()) if exit_path.exists() else None
ready=ready and bool(peer_exit and peer_exit['all_own_waited'] and peer_exit['original_cost_settled'] and peer_exit['original_leases_released'])
""" % (wait['peer_root'],wait['peer_owner']['pid'],wait['peer_owner']['creation'])
    assert source.count(needle)==1
    source=source.replace(needle,needle+additional)
    source=source.replace("D/'INDEX.json'", "D/'INDEX_REV2.json'")
    scope=dict(vars(m));exec(compile(source,str(Path(__file__)),'exec'),scope)
    scope['run'](True)
def timer():
    assert not(R/'RESOURCE_TIMER_ONCE.json').exists()
    put('RESOURCE_TIMER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),local_only_until_due=True))
    due=json.loads((D/'RESOURCE_WAIT.json').read_bytes())['not_before_epoch']
    while time.time()<due:time.sleep(min(10,due-time.time()))
    controller()
    put('RESOURCE_TIMER_COMPLETED.json',dict(epoch=time.time(),PID=os.getpid()))
def bind():
    assert not(R/'RESOURCE_TIMER_BIND_ONCE.json').exists()
    put('RESOURCE_TIMER_BIND_ONCE.json',dict(epoch=time.time(),sole_timer=True))
    with(R/'RESOURCE_TIMER_STDOUT.log').open('xb')as out,(R/'RESOURCE_TIMER_STDERR.log').open('xb')as err:
        p=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'timer'],cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(p.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    q=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put('RESOURCE_TIMER_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(q.stdout)))
    print(json.dumps(dict(PID=p.pid,sole_timer=True,not_before_epoch=json.loads((D/'RESOURCE_WAIT.json').read_bytes())['not_before_epoch'])))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['timer','bind']);a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        put('LOCAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
