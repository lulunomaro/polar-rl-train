"""One finite diagnostic transport after actual failed21 closure, never a production source."""
from pathlib import Path
import importlib.util,hashlib,json,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';N=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,time
q=v['q'];root=Path(q['roots']['h1']);owner=Path(q['owner_root'])
assert not any(p.pid!=os.getpid() and any(a.startswith((str(root)+'/',str(owner)+'/')) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
c=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');ledger=json.loads(c.read_bytes());assert ledger['active_segment'] is None
locks=[]
for p in (c.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(q['specs']['h1']['private_lock'])):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
row=json.loads((root/'job0/production/failed_prefix_complete.json').read_bytes());assert row['failed_partial_prefix'] and row['updates']==72
p=Path(row['path']);assert p.parent==root/'job0/production' and p.name=='own_failed_valid_prefix.pt' and not p.is_symlink()
s=p.stat();assert s.st_size==row['bytes']
print(json.dumps(dict(epoch=time.time(),failed_diagnostic_prefix=row,stat=dict(bytes=s.st_size,inode=s.st_ino,mtime_ns=s.st_mtime_ns),all_own_out=True,canonical_none=True,original_locks_free=locks,durable_free_bytes=shutil.disk_usage(root).free,no_budget_write=True)))
'''
RESOURCE=r'''
from pathlib import Path
import json,psutil,shutil,subprocess,time
s=v['spec'];base=Path('/home/lc01/Zonglin Li/zonglin2')
rows=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
n=sum(s['GPU_UUID'] in x for x in rows.splitlines())
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x)
ram=psutil.virtual_memory().available;free=shutil.disk_usage(base).free;gpu=int(line.split(',')[-1])
print(json.dumps(dict(epoch=time.time(),RAM_available_bytes=ram,RAM8_passed=ram>8*1024**3,durable_free_bytes=free,disk25_passed=free>25*1024**3,expected_GPU_UUID=s['GPU_UUID'],GPU_free_MiB=gpu,GPU7000_passed=gpu>7000,expected_GPU_empty=n==0,allocation_count_on_expected_GPU=n,unknown_peer_identity_not_queried=True,no_mutation_or_GO=True)))
'''
def main():
 closed=json.loads((N/'reports/H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closed['actual_finite_transport_returned'] and closed['original_canonical_cost_settled'] and not closed['complete_models']['h1']
 q=json.loads((N/'reports/H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
 put('V110_FAILED21_DIAGNOSTIC_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),no_GO_or_account_write=True))
 c=d.t.connect()
 try:
  a=d.code(c,d.t.PY,READ,dict(q=q),timeout=60);row=a['failed_diagnostic_prefix'];dest=N/'failed_H1_diagnostic_models'/Path(row['path']).name;dest.parent.mkdir(exist_ok=True);assert not dest.exists()
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   before=sf.stat(row['path']);part=dest.with_suffix('.pt.partial');sf.get(row['path'],str(part));after=sf.stat(row['path'])
   assert before.st_size==after.st_size==row['bytes'] and before.st_mtime==after.st_mtime
   assert part.stat().st_size==row['bytes'] and hashlib.sha256(part.read_bytes()).hexdigest()==row['SHA'];part.replace(dest)
  finally:sf.close()
 finally:c.close()
 put('V110_FAILED21_DIAGNOSTIC_PREFIX_TWOHOST_SHA_AND_ALL_OUT_ACTUAL.json',dict(a,local_prefix=dict(row,local_path=str(dest),twohost_complete_SHA=True),not_qualified_production_source=True,actual210_transport_returned=True))
 eq=json.loads((T/'H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022/reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes())
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover()
 try:c=d.connect72(secret)
 finally:secret=None
 try:r=d.code(c,d.PY72,RESOURCE,dict(spec=eq['specs']['recovery']),timeout=45)
 finally:c.close()
 put('V110_AFTER_FAILED21_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json',r)
 print(json.dumps(dict(diagnostic_prefix_twohost_SHA=True,not_production_source=True,E3_resource=r,all_finite_transport_returned=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('V110_DIAGNOSTIC_TRANSPORT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rerun_or_refund=True));raise
