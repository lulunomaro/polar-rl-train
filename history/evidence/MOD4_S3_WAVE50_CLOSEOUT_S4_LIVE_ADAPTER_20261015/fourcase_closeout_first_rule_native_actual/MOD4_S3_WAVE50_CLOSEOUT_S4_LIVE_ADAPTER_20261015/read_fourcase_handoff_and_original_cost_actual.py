"""One sequential CPU-only actual boundary/accounting read; no launch or budget write."""
from pathlib import Path
import json, sys, time, hashlib, traceback, subprocess
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports'
D=W/'MOD4_LINUX_BODYFRAME_RESAMPLE_PHASE_REPAIR_20261014'
def main():
 out=R/'FOURCASE_FINITE_ACTUAL_HANDOFF_AND_ORIGINAL_COST_READONLY.json';assert not out.exists()
 cim=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId=62028 OR ProcessId=13556' | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True)
 assert not cim.stdout.strip(),'Finite owner may still own transport; inspect actual identity before connecting'
 complete=json.loads((D/'reports/PHASE_FINAL_FOURCASE_FINITE_COMPLETE_ACTUAL.json').read_bytes());assert complete['all_four_cases_complete']
 sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'));import transport_249_bodyframe_current_terminal_role_v3 as t
 t.ROOT='D:/MOD4_async_eval/MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015'
 c=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert guard['shared_OS_lock_free'] and guard['oldworker_and_GPUchild_absence']
 finally:t.close(c)
 sys.path.insert(0,str(D));import transport_phase_repair_root_owned as l
 code=r'''
from pathlib import Path
import json,time,hashlib,fcntl
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');raw=B.read_bytes();b=json.loads(raw)
assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['active_segment'] is None
assert sum(x['extension_id']=='USER_ADD100H_20261011_7TH' for x in b['budget_extensions'])==1
locks=[]
for path in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_fcntl_free=True))
assert B.read_bytes()==raw
print(json.dumps(dict(epoch=time.time(),canonical_path=str(B),canonical_byte_SHA=hashlib.sha256(raw).hexdigest(),canonical_snapshot_evidence_only=b,locks=locks,no_GPU_or_canonical_write=True)))
'''
 c=None
 try:
  c=l.connect();budget,receipt=l.run(c,code,{},'FOURCASE_POSTEXIT_CANONICAL_READONLY')
 finally:l.close(c)
 result=dict(epoch=time.time(),local_root_and_child_actual_CIM_absent=True,prior_finite_script_and_all_GPU_cases_consumed_no_replay=True,root_reclaims_sole210249_sequential_transport=True,actual_3060_slot=guard,actual_original_budget=budget,original_budget_transport_receipt=str(receipt),complete_fourcase_report_SHA=hashlib.sha256((D/'reports/PHASE_FINAL_FOURCASE_FINITE_COMPLETE_ACTUAL.json').read_bytes()).hexdigest(),S4_native_root_unused_snapshot=guard['new_root_unused'],no_new_GPU_PPO_or_budgetwrite=True)
 out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),actual_all_prior_owners_absent=True,slot_free=True,canonical_idle=True,remaining=budget['canonical_snapshot_evidence_only']['remaining_training_seconds'],GPU_not_started=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('HANDOFF_COST_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_retry_no_GPU_no_budgetwrite=True),indent=2),encoding='utf8');raise
