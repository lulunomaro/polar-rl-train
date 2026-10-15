"""Launch one finite owner hidden; refuse duplicate or unknown previous outcome."""
from pathlib import Path
import ast,hashlib,json,subprocess,time
D=Path(__file__).resolve().parent;R=D/'reports'
PY='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert json.loads((R/'FIRST_GATE_RETENTION_PAIR_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU']
    p=R/'FIRST_GATE_RETENTION_FIXED_NINE_ROOT_DISPATCH_INTENT.json';assert not p.exists()
    for source in D.glob('*.py'):ast.parse(source.read_text(encoding='utf8'),filename=str(source))
    script=D/'run_first_gate_retention_fixed_nine_case_batch_once.py'
    p.write_text(json.dumps(dict(epoch=time.time(),script=str(script),script_SHA=H(script),fixed_native3_full6=True,
        unknown_launch_outcome_requires_actualCIM_no_retry=True),indent=2),encoding='utf8')
    command="$ErrorActionPreference='Stop';$s='"+str(script)+"';$p=Start-Process -FilePath '"+PY+"' -ArgumentList @('-X','utf8',('\"'+$s+'\"'),'--execute-root-fixed-nine-new-cases') -WorkingDirectory '"+str(D)+"' -RedirectStandardOutput '"+str(R/'FINITE_NINE_STDOUT.log')+"' -RedirectStandardError '"+str(R/'FINITE_NINE_STDERR.log')+"' -WindowStyle Hidden -PassThru; $a=Get-CimInstance Win32_Process -Filter ('ProcessId = '+$p.Id);$a|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress"
    launch=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,encoding='utf8',check=True)
    actual=json.loads(launch.stdout);assert actual['ProcessId'] and script.name in actual['CommandLine']
    value=dict(epoch=time.time(),actual_CIM=actual,script_SHA=H(script),new_finite9_owner_started=True,
        root_and_other_agents_must_not_connect210_249_while_this_creation_argv_alive=True,
        no_new_PPO_budget_monitor_or_oldcase_replay=True)
    q=R/'FIRST_GATE_RETENTION_FIXED_NINE_ROOT_DISPATCH_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(value))

if __name__=='__main__':main()
