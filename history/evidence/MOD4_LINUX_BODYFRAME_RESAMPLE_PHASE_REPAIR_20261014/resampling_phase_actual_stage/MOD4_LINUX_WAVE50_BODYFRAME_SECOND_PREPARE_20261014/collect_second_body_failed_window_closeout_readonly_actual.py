"""Keep original failure and every saved input; no scope PASS or ledger rewrite."""
from pathlib import Path
import json,sys,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));import transport_second_body_root_owned as t
CODE=r'''
from pathlib import Path
import json,psutil,fcntl,time,hashlib
R=Path(CONTEXT['root']);A=R/'formal3600/attempt';E=json.loads((A/'EXIT_RECEIPT.json').read_bytes());err=json.loads((R/'PIPELINE_ORIGINAL_ERROR.json').read_bytes());parent=json.loads((R/'PARENT_IDENTITY.json').read_bytes())
ids=[]
for row in (parent,E['child']):
 try:
  p=psutil.Process(row['pid']);actual=dict(pid=p.pid,created=p.create_time(),argv=p.cmdline(),same_identity=p.create_time()==row['created']);assert not actual['same_identity'];ids.append(actual)
 except psutil.NoSuchProcess:ids.append(dict(pid=row['pid'],actual_absent=True))
assert (R/'GUARDIAN_EXIT.json').exists()
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');d=json.loads(B.read_bytes());assert d['active_segment'] is None
segments=[v for v in d['completed_segments'] if v['kind']==E['canonical_unique_segment']];assert len(segments)==1
locks=[]
for path in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_free=True))
files=[]
def add(p,relative=None):
 if p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  files.append(dict(path=str(p),relative=relative or p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest()))
for p in R.glob('*.json'):add(p)
add(R/'pipeline_parent.log');add(R/'guardian.log');add(R/'formal3600/BODYFRAME_TARGET_ACTUAL_MANIFEST.json');add(R/'formal3600/BODYFRAME_SOURCE_FREEZE.json')
for p in A.glob('*'):add(p)
ptr=list((A/'learning_logs').glob('*/latest_complete.json'));assert len(ptr)==1;latest=json.loads(ptr[0].read_bytes());ck=Path(latest['checkpoint']);add(ck)
for p in ck.parent.glob('*.json'):add(p)
for p in ck.parent.glob('retention_prefix_*.npz'):add(p)
for p in ck.parent.glob('*BODYFRAME*.pt'):add(p)
print(json.dumps(dict(epoch=time.time(),root=str(R),original_parent_exit=E,original_parent_error=err,original_worker_returncode=E['returncode'],parent_failed_not_PASS=True,actual_parent_guardian_child_out=True,actual_identities=ids,locks=locks,canonical_idle=True,canonical_remaining=d['remaining_training_seconds'],canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),unique_completed_segment=segments[0],latest_complete=latest,files=files,no_GPU_PPO_signal_or_budgetwrite=True)))
'''
def main():
 c=None;sf=None;stamp=str(time.time_ns())
 try:
  c=t.connect();v,receipt=t.run(c,CODE,dict(root=t.ROOT),'SECOND_BODY_FAILED_WINDOW_REMOTE_ACTUAL',180);dest=D/('failed_window_actual_'+stamp);dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(60);rows=[]
  for row in v['files']:
   p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
   h=hashlib.sha256()
   with p.open('rb') as f:
    for b in iter(lambda:f.read(1048576),b''):h.update(b)
   assert p.stat().st_size==row['bytes'] and h.hexdigest()==row['sha256'];rows.append(dict(**row,local_path=str(p),two_host_byteSHA_exact=True))
  out=R/('SECOND_BODY_FAILED_WINDOW_ALL_INPUTS_TWOHOST_ACTUAL_'+stamp+'.json');out.write_text(json.dumps(dict(epoch=time.time(),actual=v,collected=rows,all_two_host_byteSHA_exact=True,original_false_preserved=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),files=len(rows),bytes=sum(x['bytes'] for x in rows),original_exit=v['original_worker_returncode'],unique_parent_seconds=v['unique_completed_segment']['ended_epoch']-v['unique_completed_segment']['started_epoch'],original_failed_not_PASS=True,locks_actual_free=True)))
 except BaseException:
  p=R/('SECOND_BODY_FAILED_WINDOW_COLLECTION_ORIGINAL_ERROR_'+stamp+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),readonly=True,no_retry=True),indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
