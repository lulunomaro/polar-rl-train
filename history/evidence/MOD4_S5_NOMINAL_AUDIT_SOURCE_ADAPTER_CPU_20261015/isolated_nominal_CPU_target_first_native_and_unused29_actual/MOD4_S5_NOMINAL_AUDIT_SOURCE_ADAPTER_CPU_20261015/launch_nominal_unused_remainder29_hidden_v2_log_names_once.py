"""One finite coordinator with explicitly redirected handles and hidden window."""
from pathlib import Path
import ast,hashlib,json,subprocess,time
D=Path(__file__).resolve().parent;R=D/'reports';PY='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert json.loads((R/'NOMINAL_COMPLETE_ABC_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU']
 for p in D.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
 p=R/'NOMINAL_ABC_REMAINDER29_ROOT_DISPATCH_INTENT.json';assert not p.exists();script=D/'run_nominal_ABC_unused_remainder29_after_reader_fix_once.py'
 p.write_text(json.dumps(dict(epoch=time.time(),script=str(script),scriptSHA=H(script),fixed_new_native11_full18_only=True,retained_native1_not_replayed=True,unknown_outcome_actualCIM_no_retry=True),indent=2),encoding='utf8')
 with (R/'REMAINDER29_STDOUT.log').open('xb') as out,(R/'REMAINDER29_STDERR.log').open('xb') as err:
  child=subprocess.Popen([PY,'-X','utf8',str(script),'--execute-root-remainder29-unused-only'],cwd=D,stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
 cmd='$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(child.pid)+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'
 ci=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,encoding='utf8',check=True);v=json.loads(ci.stdout);assert v['ProcessId']==child.pid and script.name in v['CommandLine']
 p=R/'NOMINAL_ABC_REMAINDER29_ROOT_DISPATCH_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),actual_CIM=v,scriptSHA=H(script),new_remainder29_exclusive_transport_owner_started=True,other_root_agents_must_not_connect210_249_while_actual_creationargv_alive=True,no_PPO_budget_oldcase_replay=True),indent=2),encoding='utf8');print(json.dumps(dict(actual_CIM=v,started_remainder29=True)))
if __name__=='__main__':main()
