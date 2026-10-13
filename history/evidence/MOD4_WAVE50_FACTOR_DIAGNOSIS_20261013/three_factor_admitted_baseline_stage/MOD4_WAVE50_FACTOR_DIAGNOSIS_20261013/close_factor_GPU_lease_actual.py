from pathlib import Path
import sys,json,time,hashlib,psutil,msvcrt,numpy as np
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
case=sys.argv[1];leasepath=D/'leases'/(case+'.json');lease=json.loads(leasepath.read_bytes())
A=D/'geometry_pose/attempts'/case;O=A/'output'
dispatch=json.loads((A/'DISPATCH_RECEIPT.json').read_bytes());end=json.loads((A/'PARENT_EXIT_RECEIPT.json').read_bytes())
assert end['no_PPO'] and not end['canonical_budget_written']
actual_exits=[]
for label,pid,created in [('child',dispatch['child_pid'],dispatch['child_creation']),('parent',dispatch['parent_pid'],dispatch['parent_creation'])]:
 try:
  p=psutil.Process(pid);assert p.create_time()!=created,f'{label} same actual process still active'
  actual_exits.append(dict(label=label,pid=pid,original_creation=created,reused_pid=True,current_creation=p.create_time()))
 except psutil.NoSuchProcess:actual_exits.append(dict(label=label,pid=pid,original_creation=created,actual_absent=True))
lock=Path(lease['shared_native_lock'])
with lock.open('r+b') as f:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
complete=O/'COMPLETE_ACTUAL.json';error=O/'ORIGINAL_ERROR.json'
proof=None
if complete.exists():
 c=json.loads(complete.read_bytes());assert c['no_PPO'] and c['passed_data_contract'] and c['case_id']==case and c['checkpoint_sha256']==lease['checkpoint_sha256']
 assert c['steps']==lease['case_parameters']['steps'] and c['callbacks']==c['steps']*4 and end['exit_code']==0
 raw=O/'route_raw.npz'
 with np.load(raw,allow_pickle=False) as z:
  fields={k:list(z[k].shape) for k in z.files}
  for k in z.files:
   if z[k].dtype.kind in 'fc':assert np.isfinite(z[k]).all(),k
 proof=dict(path=str(complete),sha256=H(complete),raw_path=str(raw),raw_bytes=raw.stat().st_size,raw_sha256=H(raw),fields=fields,passed_data_contract=True,not_qualification=True)
else:assert error.exists() or end['exit_code']!=0,'Neither actual complete nor retained failed exit'
q=D/'leases'/(case+'_CLOSED_ACTUAL.json');assert not q.exists()
r=dict(epoch=time.time(),case_id=case,lease_sha256=H(leasepath),actual_process_exit=actual_exits,native_shared_lock_actual_free=True,parent_exit_receipt_sha256=H(A/'PARENT_EXIT_RECEIPT.json'),parent_load_run_save_exit_seconds=end['unique_actual_parent_load_run_save_exit_seconds'],original_exit_code=end['exit_code'],natural_app_close_receipt_present=(O/'EXIT_NATURAL.json').exists(),original_error_present=error.exists(),complete=proof,no_PPO=True,no_budget_transaction=True,original_missing_or_false_receipts_unchanged=True)
q.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in r.items() if k!='complete'},ensure_ascii=False))
