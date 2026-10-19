"""One finite read-only current-resource and account-host preflight for new authorization."""
from pathlib import Path
import base64,getpass,hashlib,importlib.util,json,os,paramiko,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True);sys.path.insert(0,str(W/'MOD4_AVAILABLE_E2_E3_HOUR18_20261019'));import deploy_available_E2_E3_original_writer_V2_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import os,json,time,psutil,fcntl,subprocess,shutil
B=Path('/home/lc01/Zonglin Li/zonglin2');node=B/'tasks/E3solo18_2010v25/recovery';owner=B/'tasks/E3solo18_2010v25/owner';new=B/'tasks/E3auto_2010v26';e=json.loads((node/'NODE_EXIT_ACTUAL.json').read_bytes());t=json.loads((node/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];o=json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes());co=json.loads((owner/'COHORT_FINAL.json').read_bytes());assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and t['returncode']==0 and not t['errors'] and t['final']['passed'] and t['final']['final']['SHA']=='2275dbb403b65d4d4a1126a2464611ff018b24f6c9e30d665558f6224aeb552b';assert o['pending_cost_record_complete'] and o['original_cost_settled'] is False and co['pending_cost']['cost']['actual_production_seconds']==3626.8895361423492;assert not new.exists();old=B/'state/MOD4_SINGLE_E3_OFFLINE_COST_PENDING_20261020.json';assert old.is_file();assert not (B/'state/MOD4_E3_AUTO_PENDING_SERIES_20261020.json').exists();own=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(r)+'/') for r in (node,owner) for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
assert not own;locks=[]
for q in [B/'state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',B/'state/finite_environment_validation.lock']:
 free=False
 with q.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
 locks.append(dict(path=str(q),actual_fcntl_free=free))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();gpu=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d' in x);disk=shutil.disk_usage(B);ram=psutil.virtual_memory().available;checks=dict(previous_source_and_owner_actual_out=True,new_series_root_unused=True,old_pending_reservation_retained=True,new_series_reservation_unused=True,E3_GPU_empty=not any('GPU-c27eecbd-6838-7290-1cd2-37e34522213d' in x for x in compute.splitlines()),GPU_free_over7000=int(gpu.split(',')[-1])>7000,RAM_over8GiB=ram>8*1024**3,disk_over25GiB=disk.free>25*1024**3,private_shared_free=all(x['actual_fcntl_free'] for x in locks));print(json.dumps(dict(epoch=time.time(),checks=checks,ready=all(checks.values()),GPU_line=gpu,compute_snapshot=compute,disk=dict(zip(('total','used','free'),disk)),RAM_available=ram,locks=locks,source_final=t['final']['final'],previous_cost=co['pending_cost']['cost'],no_peer_identity_or_GPU_Task_or_canonical_write=True)))
'''
def main():
 put('AUTO_E3_PREFLIGHT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transport=True,human_authority='可以允许自动续训，一直训练都行'));pw=getpass.getpass('72 auto E3 resource preflight (hidden): ');c=None
 try:c=d.a.connect72(pw);pw=None;v=d.a.code(c,d.a.PY,READ,timeout=60);put('AUTO_E3_CURRENT_RESOURCE_PREVIOUS_CLOSED_ACTUAL.json',v)
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=d.a.t.connect();state=d.a.code(c,d.a.t.PY,"from pathlib import Path;import json,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());print(json.dumps(dict(epoch=time.time(),canonical_available=True,active=v['active_segment'],remaining=v['remaining_training_seconds'],authorized=v['authorized_training_seconds'],no_account_write=True)))",timeout=60);account=dict(kind='original_Linux_available_requires_reconciliation_before_new_GO',actual=state)
 except paramiko.BadHostKeyException as ex:
  observed=ex.key.asbytes();known=paramiko.HostKeys(str(Path.home()/'.ssh/known_hosts_mod4_4090_windows_20261013')).lookup('10.24.4.210')['ssh-ed25519'].asbytes();assert observed==known;put('ORIGINAL_LINUX_PIN_REFUSAL_CURRENT_WINDOWS_PIN_MATCH_ACTUAL.json',dict(epoch=time.time(),original_exception=str(ex),observed_matches_existing_separate_Windows_pin=True,no_pin_changed=True))
  sp=importlib.util.spec_from_file_location('known_windows_preflight',W/'MOD4_4090_WINDOWS_REPAIR_20261013/windows4090_native_transport.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);raw=m.powershell(None,"[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false);$o=Get-CimInstance Win32_OperatingSystem;[ordered]@{computer=$env:COMPUTERNAME;caption=$o.Caption;version=$o.Version;no_system_or_account_write=$true}|ConvertTo-Json",timeout=60);account=dict(kind='original_Linux_canonical_offline_Windows_OS_confirmed',actual=json.loads(raw),original_Linux_pin_untouched=True)
 finally:
  if c:d.a.t.close(c)
 out=dict(epoch=time.time(),target72=v,account_host=account,actual_finite_transport_returned=True,no_training_launched_or_budget_written=True);put('AUTO_E3_INITIAL_PREFLIGHT_RETURNED_ACTUAL.json',out);print(json.dumps(dict(E3_ready=v['ready'],GPU=v['GPU_line'],account_host=account['kind'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('AUTO_E3_PREFLIGHT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_GPU_retry_or_pin_change=True));raise
