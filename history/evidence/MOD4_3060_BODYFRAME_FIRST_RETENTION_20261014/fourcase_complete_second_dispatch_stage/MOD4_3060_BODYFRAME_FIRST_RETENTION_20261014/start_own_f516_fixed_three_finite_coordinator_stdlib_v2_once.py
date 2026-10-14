"""Root gives this finite coordinator sole 249 transport ownership until its actual exit."""
from pathlib import Path
import json,os,subprocess,sys,time,hashlib,base64
from datetime import datetime
D=Path(__file__).resolve().parent;R=D/'reports';SCRIPT=D/'run_bodyframe_retention_fixed_three_candidate_batch_once.py'
def main():
 target=json.loads((R/'BODYFRAME_FIRST_RETENTION_TARGET_SOURCE_UPLOAD_CPU_ACTUAL.json').read_bytes())
 assert target['source_whole20k_195_107_99_CPU_verified'] and target['source_owned_body_state_independently_validated'] and target['no_GPU_no_PPO_no_budgetwrite']
 assert target['source_SHA']=='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
 receipt=R/'BODYFRAME_FIRST_RETENTION_FINITE_BATCH_ROOT_DISPATCH_ACTUAL.json';assert not receipt.exists() and not (R/'BODYFRAME_FIRST_RETENTION_FIXED_THREE_STARTED_ACTUAL.json').exists()
 def cim(code):
  text="[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false);"+code
  raw=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(text.encode('utf-16-le')).decode()],capture_output=True,check=True).stdout
  return json.loads(raw.decode('utf-8-sig'))
 current=cim("$p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match 'python' -and $_.CommandLine -match 'run_.*retention.*(batch|fixed_three)'});ConvertTo-Json -InputObject $p -Depth 4 -Compress")
 assert not current,('Another finite coordinator already owns transport',current)
 compile(SCRIPT.read_text(encoding='utf8'),str(SCRIPT),'exec')
 argv=[sys.executable,'-X','utf8',str(SCRIPT),'--execute-root-fixed-three-cases']
 with (D/'finite_fixed_three.stdout.log').open('xb') as out,(D/'finite_fixed_three.stderr.log').open('xb') as err:
  child=subprocess.Popen(argv,cwd=D,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
 identity=cim("$p=Get-CimInstance Win32_Process -Filter \"ProcessId="+str(child.pid)+"\";if($null -eq $p){throw 'New coordinator already exited; inspect reports before any new action'};[PSCustomObject]@{pid=$p.ProcessId;creation_iso=$p.CreationDate.ToUniversalTime().ToString('o');actual_command_line=$p.CommandLine}|ConvertTo-Json -Compress")
 value=dict(epoch=time.time(),pid=child.pid,creation=datetime.fromisoformat(identity['creation_iso'].replace('Z','+00:00')).timestamp(),actual_CIM=identity,argv=argv,script_SHA=hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),sole_transport_owner_210_and249_until_actual_exit=True,coordinator_uses249_only=True,root_and_agents_must_not_connect_210_or249_while_actual_owner_alive=True,fixed_three_new_candidate_case_ids=[f'retention_bodyframe_first_f516_{k}_1500_v8' for k in ('flat','spin','world')],reused_native120_no_GPU_replay=True,new_source_SHA=target['source_SHA'],baseline_e3_complete_same_initial_pair_required=True,no_PPO_no_budgetwrite=True,no_retry_no_signal_no_qualification=True)
 with receipt.open('x',encoding='utf8') as out:json.dump(value,out,indent=2)
 print(json.dumps(value))
if __name__=='__main__':main()
