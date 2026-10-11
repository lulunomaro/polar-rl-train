from slope_io import *
import traceback
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
def main():
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import json,sys,time,hashlib,torch,fcntl
D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=D/'reports/e1_SLOPE5_independent_observation_PASSED.json'
if not p.exists():print(json.dumps(dict(epoch=time.time(),pending=True,reason='own formal PASSED not generated yet',no_CUDA_or_GPU_or_budget_action=True)));raise SystemExit(0)
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_slope5_snapshot_reviewed_once as own
row=j(p);source=Path(row['checkpoint']['path']);ck=own.fullsave(source);run=Path(row['run']);m=j(run/'run_manifest.json');rec=j(run/'latest_complete.json');freeze=j(run/'rolling_source_freeze.json')
assert row['source_sha256']==own.prior.SOURCE_SHA and ck['sha256']==row['checkpoint']['sha256'] and ck['finite_tensors']==102
assert row['source_count']==404 and row['own_PID_bound_receipt']==rec and rec['pid']==row['unique_completed_segment'][0]['pid']
assert len(row['unique_completed_segment'])==1 and not row['discarded_preflight'] and source.is_relative_to(D/'learning_logs')
assert m['source_map']==j(D/'reports/SOURCE_FREEZE.json')['sha256'] and all(h(run/'src_snapshot'/n)==sha for n,sha in m['src_sha256'].items())
assert own.prior.learning_health_pass(row['health']) and not torch.cuda.is_initialized()
st=j(D/'reports/E1_STATE.json');ready=(D/'reports/E1_REVIEW_READY.json').exists();exits=[]
for loc in (st['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=rec['pid'],start_ticks=row['unique_completed_segment'][0].get('start_ticks',0))):
 actual=own.identity(loc['pid']);exits.append(dict(locator=loc,actual=actual))
l=j(B);segments=[x for x in l['completed_segments'] if x['pid']==rec['pid']];assert segments==row['unique_completed_segment'] and l['authorized_training_seconds']==828000
locks=[]
for name in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 try:
  with name.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  locks.append(dict(path=str(name),free=True))
 except BlockingIOError:locks.append(dict(path=str(name),free=False))
print(json.dumps(dict(epoch=time.time(),pending=False,formal_CPU_fullsource_verified=True,checkpoint=ck,own_PID_receipt=rec,source_count=404,actual_snapshot_count=len(m['src_sha256']),manifest=m,rolling_freeze=freeze,formal_PASSED=row,actual_phase=st['phase'],ready=ready,actual_parent_guardian_child=exits,two_real_OS_locks=locks,canonical=dict(sha256=h(B),active=l['active_segment'],remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds']),unique_original_segment_verified=True,no_CUDA_or_GPU_or_budget_action=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(B))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('SNAPSHOT_OWN_CPU_REJECTED_'+str(time.time_ns())+'.json',dict(returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')));raise RuntimeError('Own actual CPU receipt review rejected')
  row=json.loads(raw);p=save('SNAPSHOT_OWN_FORMAL_CPU_'+str(time.time_ns())+'.json',row)
  print(json.dumps(dict(report=str(p),pending=row['pending'],checkpoint=row.get('checkpoint'),snapshot_count=row.get('actual_snapshot_count'),phase=row.get('actual_phase'),canonical=row.get('canonical'))))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_OWN_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_signal_or_relaunch=True));raise
