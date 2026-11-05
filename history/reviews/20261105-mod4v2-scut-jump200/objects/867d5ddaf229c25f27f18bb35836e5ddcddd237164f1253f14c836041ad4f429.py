"""Human-directed reward switch: stop after complete update/save, then receive once."""
from pathlib import Path
import importlib.util,json,os,subprocess,time,traceback
from shared_control_access import connection

N=Path(__file__).resolve().parent
A=N/'takeoff_velocity_weight12_final346_1h'
R=A/'reports'
read=lambda p:json.loads(Path(p).read_bytes())

def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False)

def main():
    put('FUDAN_SWITCH_STOP_AND_RECEIVE_ONCE.json',dict(epoch=time.time(),pid=os.getpid(),human='先用复旦的奖励去训跳跃吧，学习压腿跳跃',complete_update_save_close_required=True))
    assert not(R/'POSTROUND_FINITE_READ_ONCE.json').exists()and not(R/'POSTROUND_COMPLETED.json').exists()
    expected=read(R/'POSTROUND_EXACT_CIM.json')['row']
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(expected['ProcessId'])+'" | Select-Object ProcessId,ParentProcessId,@{Name="CreationDate";Expression={$_.CreationDate.ToString("o")}},ExecutablePath,CommandLine | ConvertTo-Json'
    result=subprocess.run(['pwsh','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    actual=json.loads(result.stdout)
    from datetime import datetime
    assert actual['ProcessId']==expected['ProcessId']and actual['ParentProcessId']==expected['ParentProcessId']
    assert datetime.fromisoformat(actual['CreationDate'])==datetime.fromisoformat(expected['CreationDate'])
    assert actual['ExecutablePath']==expected['ExecutablePath']and actual['CommandLine']==expected['CommandLine']
    assert 'takeoff_velocity_weight12_control.py collect --root 'in actual['CommandLine']
    subprocess.run(['pwsh','-NoProfile','-Command','Stop-Process -Id '+str(actual['ProcessId'])+' -ErrorAction Stop'],check=True)
    check=subprocess.run(['pwsh','-NoProfile','-Command','Get-CimInstance Win32_Process -Filter "ProcessId = '+str(actual['ProcessId'])+'" | Select-Object ProcessId | ConvertTo-Json'],capture_output=True,text=True,check=True)
    assert not check.stdout.strip()
    put('FUDAN_SWITCH_LOCAL_SLEEPER_RETIRED.json',dict(epoch=time.time(),exact=actual,only_own_sleeping_local_receiver=True,finite_read_unconsumed=True,other_chat_processes_changed=False))
    plan=read(A/'PLAN.json');first=read(R/'FIRST_ACTUAL_RETURNED.json')['files']
    code=r'''
from pathlib import Path
import json,psutil,time
j=Path(v['root']);go=json.loads((j/'GO_PRODUCTION.json').read_bytes());cur=json.loads((j/'OWNER_CURRENT.json').read_bytes())
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment']
assert go['run_id']==v['run_id'] and a and a['owner_run_id']==v['run_id'] and a['owner_parent_pid']==v['owner_pid']
owner=psutil.Process(v['owner_pid']);assert abs(owner.create_time()-v['owner_creation'])<.02
w=cur['worker'];p=psutil.Process(w['pid']);assert abs(p.create_time()-w['creation'])<.02 and str(j/'entry.py')in p.cmdline()
stop=j/'STOP_AFTER_SAVE.json';request=dict(epoch=time.time(),human='先用复旦的奖励去训跳跃吧，学习压腿跳跃',reason='Human reward-family switch; complete current update then fullsave/safeexit',fullsave_required=True,original_GO=go)
with stop.open('x')as f:json.dump(request,f,indent=2)
print(json.dumps(dict(epoch=time.time(),request=request,owner=dict(pid=owner.pid,creation=owner.create_time(),argv=owner.cmdline()),worker=w,canonical_owner_matched=True,budget_mutations=0)))
'''
    owner=read(R/'OWNER_LAUNCH.json')
    with connection(R,'FUDAN_SWITCH_STOP_REQUEST')as(client,t):
        receipt=t.code(client,t.PY72,code,dict(root=plan['remote_root'],run_id=plan['run_id'],owner_pid=owner['pid'],owner_creation=owner['creation']),timeout=45)
        put('FUDAN_SWITCH_REMOTE_STOP_REQUESTED.json',receipt)
    old=N.parent/'mod4v1_scut_step270_2h_20261103/postround.py'
    spec=importlib.util.spec_from_file_location('fudan_switch_original_receive',old);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.A=A;m.R=R;m.m.R=R;m.put=put;m.m.connection=lambda label:connection(R,label)
    m.receive(plan['remote_root'],'FUDAN_SWITCH_POSTROUND_RETURN')

if __name__=='__main__':
    try:main()
    except BaseException:
        put('FUDAN_SWITCH_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
