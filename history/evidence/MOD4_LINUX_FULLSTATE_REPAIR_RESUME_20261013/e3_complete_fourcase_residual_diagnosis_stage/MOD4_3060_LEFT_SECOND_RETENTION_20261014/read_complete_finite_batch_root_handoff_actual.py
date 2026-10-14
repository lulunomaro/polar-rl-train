"""Root-only one current shared-slot read after actual local coordinator exit."""
from pathlib import Path
import json,sys,time,subprocess
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
def main():
 completed=json.loads((R/'SECOND_RETENTION_FIXED_THREE_COMPLETE_ACTUAL.json').read_bytes());assert completed['all_three_new_candidates_complete'] and len(completed['results'])==3
 p=subprocess.run(['powershell','-NoProfile','-Command',"$x=Get-CimInstance Win32_Process -Filter 'ProcessId=12420';[PSCustomObject]@{present=($null -ne $x);creation=if($x){$x.CreationDate.ToString('o')}else{$null};argv=if($x){$x.CommandLine}else{$null}}|ConvertTo-Json -Compress"],capture_output=True,text=True,encoding='utf8',check=True)
 local=json.loads(p.stdout);assert not local['present'],'Do not connect while actual finite transport owner remains active'
 sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'));import transport_249_only as t;t.ROOT='D:/MOD4_async_eval/MOD4_3060_LEFT_SECOND_RETENTION_20261014'
 c=t.connect()
 try:guard=t.py(c,t.guard_code())
 finally:t.close(c)
 out=R/'SECOND_RETENTION_COMPLETE_ACTUAL_ROOT_TRANSPORT_HANDOFF.json';assert not out.exists()
 result=dict(epoch=time.time(),actual_local_coordinator_absent=local,all_three_current_cases_already_actual_complete=True,current_actual_shared_slot_guard=guard,root_reclaimed_sole_sequential210_249_transport=True,all_oldcases_and_finite_once_stay_consumed=True,no_GPU_PPO_signal_or_budgetaction=True)
 out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),handoff_actual=True,guard=guard)))
if __name__=='__main__':main()
