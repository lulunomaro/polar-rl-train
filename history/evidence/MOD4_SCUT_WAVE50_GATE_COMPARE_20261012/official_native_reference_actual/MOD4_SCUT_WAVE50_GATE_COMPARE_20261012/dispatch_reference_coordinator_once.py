"""Launch only the new human-requested coordinator; it waits for an actually idle slot."""
from scut_wave_io import *

def main():
    assert json.loads((R/'TARGET_CPU_ADMITTED.json').read_bytes())['passed'] and not (R/'REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').exists()
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,subprocess,time,os,hashlib,base64
D=Path(ROOT_TOKEN);p=D/'reference_coordinator_once.py';assert not (D/'REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').exists() and not (D/'REFERENCE_COORDINATOR_STARTED.json').exists()
argv=[PY_TOKEN,'-X','utf8',str(p)];env=dict(os.environ);env.update(PYTHONUTF8='1',PYTHONUNBUFFERED='1')
with (D/'coordinator.log').open('xb') as f:child=subprocess.Popen(argv,cwd=D,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
code="$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(child.pid)+"';$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}}|ConvertTo-Json -Compress"
r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert r.returncode==0;r=json.loads(r.stdout);assert r['ProcessId']==child.pid and str(p).replace('/','\\') in r['CommandLine'].replace('/','\\')
v=dict(epoch=time.time(),coordinator=r,argv=argv,coordinator_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),human_requested_frozen_reference_only=True,actual_coordinator_dispatch=True,actual_probe_pending_owned_slot_and_reversible_idle_worker_borrow=True,no_4090_training_or_budget_authority=True)
q=D/'REFERENCE_DISPATCH_ACTUAL_RECEIPT.json';q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(REMOTE)).replace('PY_TOKEN',repr(PY)))
        save('REFERENCE_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(dict(dispatched=True,coordinator=v['coordinator'],probe_not_claimed_from_coordinator=True)))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_REFERENCE_DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_once_or_GPU_replay=True));raise
