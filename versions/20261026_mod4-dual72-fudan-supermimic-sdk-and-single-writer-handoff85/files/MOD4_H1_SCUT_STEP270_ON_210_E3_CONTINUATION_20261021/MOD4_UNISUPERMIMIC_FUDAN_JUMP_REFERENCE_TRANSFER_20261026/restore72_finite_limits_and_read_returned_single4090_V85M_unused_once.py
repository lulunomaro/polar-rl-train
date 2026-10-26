from pathlib import Path
import importlib.util,json,socket,sys,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026';R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
RESTORE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,time
B=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026');C=B/'TRAINING_BUDGET_10H.json';held=[]
try:
 for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
  f=(B/name).open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held.append(f)
 before=C.read_bytes();c=json.loads(before);assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['active_segment'] is None and c['budget_mode']=='temporary_unlimited_until_single4090_returns'
 assert c['charged_training_seconds']==1672743.1759386063 and c['remaining_training_seconds']==595256.8240613937 and c['completed_segments']==[] and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
 assert not (B/'BUDGET_LIMITS_RESTORED_ACTUAL.json').exists()
 c.update(budget_mode='finite_original_limits_restored_after_single4090_return',active_spending_cap_seconds=2268000,remaining_is_tracking_not_launch_limit=False,temporary_unlimited_ended_epoch=time.time(),finite_minimum_remaining_seconds=86412.86069250107)
 raw=(json.dumps(c,ensure_ascii=False,indent=2)+'\n').encode('utf8');tmp=C.with_suffix('.json.partial')
 with tmp.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 tmp.replace(C)
 result=dict(epoch=time.time(),approved=True,passed=True,limits_restored=True,authority_generation=c['authority_generation'],single4090_returned=True,budget_mode=c['budget_mode'],minimum_remaining_seconds=86412.86069250107,canonical_path=str(C),before_SHA=hashlib.sha256(before).hexdigest(),after_SHA=hashlib.sha256(raw).hexdigest(),human_return_verbatim='单4090主机已经上线，我拓展了快600g空间可以用',original_human_override_expiry='单主机回来后再加限制',actual_temporary_unlimited_GPU_cost_seconds=0.,remaining=595256.8240613937,charged=1672743.1759386063,old210_Linux_authority_stays_retired=True,no_owner_GO_or_model_action=True)
 p=B/'BUDGET_LIMITS_RESTORED_ACTUAL.json'
 with p.open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps(result))
finally:
 for f in reversed(held):f.close()
'''
READ="from pathlib import Path;import json,shutil,subprocess,time;B=Path('/mnt/mod4_linux_durable_20261013');print(json.dumps(dict(epoch=time.time(),original_Linux_pin_and_password_authenticated=True,durable_exists=B.is_dir(),durable_free=shutil.disk_usage(B).free if B.is_dir() else None,durable_total=shutil.disk_usage(B).total if B.is_dir() else None,mount=subprocess.check_output(['findmnt','-n','-o','UUID,FSTYPE,OPTIONS','--target',str(B)],text=True).strip() if B.is_dir() else None,GPU_UUID_freeMiB_utilization=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True),no_original_Linux_ledger_write_or_owner_launch=True)))"
def main():
 put('SINGLE_RETURN_FINITE_RESTORE_AND_RESOURCE_STARTED_ACTUAL.json',dict(epoch=time.time(),human_verbatim='单4090主机已经上线，我拓展了快600g空间可以用',new_authority_stays72=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d
 ms=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');mem=importlib.util.module_from_spec(ms);ms.loader.exec_module(mem);secret=mem.recover();c=None;result={}
 try:
  c=d.connect72(secret);secret=None;result['finite_restore72']=d.code(c,d.PY72,RESTORE,{},timeout=45);c.close();c=None;put('SINGLE_RETURN72_FINITE_LIMITS_RESTORED_RETURNED_ACTUAL.json',result['finite_restore72'])
  for label,host,port in [('forwarded','10.24.5.27',4090),('original_direct','10.24.4.210',22)]:
   try:
    with socket.create_connection((host,port),timeout=4):pass
    if label=='forwarded':c=d.t.connect()
    else:
     import paramiko
     sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
     password,_=recover('RM_SSH_PASSWORD');assert password;c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy())
     try:c.connect(host,port=port,username='egde',password=password,look_for_keys=False,allow_agent=False,timeout=12,banner_timeout=12,auth_timeout=12)
     finally:password=None
    result[label]=d.code(c,d.t.PY,READ,{},timeout=45);c.close();c=None;break
   except BaseException:
    result[label]=dict(epoch=time.time(),original_identity_connection_failed=True,error=traceback.format_exc(),no_accept_new_key_or_old_writer=True)
   finally:
    if c:c.close();c=None
  put('SINGLE_RETURN_PINNED_RESOURCE_AND_CURRENT72_LIMITS_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,result=result,no_GPU_or_new_owner_or_old_account_write=True));print(json.dumps(result))
 except BaseException:
  put('SINGLE_RETURN_FINITE_RESTORE_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial=result,no_same_once_retry_or_reactivate_old_writer=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
