from slope_io import *
import traceback
ROOT402=NEW
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'

def main():
 save('SNAPSHOT_FULL_RECEIPTS_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='SLOPE5-SNAPSHOT-LITERAL-REPAIR-01',old402_immutable=True,new_native_small_replay=False))
 n,w=connect_both()
 try:
  save('SNAPSHOT_FULL_RECEIPTS_OLD_AUTHORITY.json',boundary(n))
  proof=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,fcntl
D=Path(ROOT402);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
st=j(D/'reports/E1_STATE.json');att=j(D/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
exits=[]
for loc in (st['owner'],st['child'],j(D/'reports/E1_GUARDIAN_STARTED.json')):
 p=Path('/proc')/str(loc['pid']);a=None
 if p.exists():
  f=(p/'stat').read_text().split(') ',1)[1].split();a=dict(state=f[0],start_ticks=int(f[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 exits.append(dict(locator=loc,actual=a))
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
segments=[x for x in l['completed_segments'] if x['pid'] in (2578240,2578663)];assert len(segments)==2
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
small=j(D/'reports/slope_discard128_PASSED.json');assert small['actual_updates']==2 and small['actual_environment_steps']==6144 and small['discarded_preflight']
native={}
for name in ('SLOPE_SDK10.json','SLOPE_NATIVE20K.json'):
 p=D/name;r=j(D/'reports'/(p.stem+'_PASSED.json'));assert r['passed'] and r['no_PPO'] and r['path']==str(p) and r['sha256']==h(p);native[name]=dict(r,bytes=p.stat().st_size)
log=next(D.glob('slope_discard20k_*.log'));assert 'FileNotFoundError' in log.read_text() and 'slope5_command_migration_environment_view.py' in log.read_text()
assert 'Learning iteration' not in log.read_text()
run=next((D/'discard_logs').glob('*_slope_discard20k_*'));assert not (run/'run_manifest.json').exists() and not list(run.glob('model_*.pt'))
startup={p.name:j(p) for p in run.glob('*STARTUP_VERIFIED.json')};assert len(startup)==8 and "SENSOR_RESUME_STARTUP_VERIFIED.json" in startup
f=j(D/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==402 and all(h(D/name)==sha for name,sha in f['sha256'].items())
print(json.dumps(dict(epoch=time.time(),actual_old_parent_child_guardian_exited=exits,old_attention=att,failed_before_PPO_updates=True,source_freeze=f,original_unique_settled_segments=segments,remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds'],canonical_SHA=h(B),native=dict(results=native),small=small,actual_full_CUDA_startup=startup,original_log=dict(path=str(log),bytes=log.stat().st_size,sha256=h(log)),two_real_OS_locks_free=True)))
'''.replace('ROOT402',repr(ROOT402)).replace('BUDGET',repr(B)))
  save('SNAPSHOT_FULL_RECEIPTS_402_FAILURE_ACTUAL.json',proof)
  with n.open_sftp() as f:
   raw=f.open(proof['original_log']['path']).read();assert H(raw)==proof['original_log']['sha256'];p=D/'actual_remote/snapshot_rejection402.log';assert not p.exists();p.write_bytes(raw)
  copied=linux_json(n,r'''from pathlib import Path
import json,hashlib,shutil
old=Path(ROOT402);new=Path(ROOTNEW);B=Path(BUDGET);before=B.read_bytes();f=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert not new.exists()
new.mkdir();(new/'reports').mkdir()
for name,sha in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==sha;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','SLOPE134_COMPLETE_ACTUAL_REVIEW.json','SLOPE_FOUR_CASE_TEMPLATES.json','SLOPE_TARGET_FULLSTATE_CPU_PASSED.json'):
 shutil.copy2(old/'reports'/name,new/'reports'/name)
assert B.read_bytes()==before
print(json.dumps(dict(old402_all_source_bytes_preserved=True,no_GPU_or_budget_transaction=True)))
'''.replace('ROOT402',repr(ROOT402)).replace('ROOTNEW',repr(NEW)).replace('BUDGET',repr(B)))
  save('SNAPSHOT_FULL_RECEIPTS_402_COPIED.json',copied)
  hashes=dict(proof['source_freeze']['sha256'])
  with n.open_sftp() as f:
   for p in sorted((D/'snapshot_reviewed_payload').rglob('*')):
    if not p.is_file():continue
    name=p.relative_to(D/'snapshot_reviewed_payload').as_posix();assert name not in hashes;raw=p.read_bytes();compile(raw,str(p),'exec');put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   freeze=dict(proof['source_freeze'],candidate_root=NEW,sha256=hashes,snapshot_list_literal_repair_only=True,old402_source_immutable=True)
   assert len(hashes)==404
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('SNAPSHOT_FULL_RECEIPTS_SOURCE_FREEZE.json',freeze)
   for name,row in (('REUSED_SLOPE_SMALL128.json',proof['small']),('REUSED_SLOPE_NATIVE.json',proof['native']),('OLD402_SNAPSHOT_REJECTION_ACTUAL.json',proof)):
    put(f,NEW+'/reports/'+name,json.dumps(row,indent=2).encode())
  code=r'''from pathlib import Path
import sys,json,torch,ast,hashlib,time
D=Path(ROOTNEW);old=Path(ROOT402);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
worker=D/'isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py';prior=old/'isaac/mod4/train_slope5_full_resume_ppo.py'
assert worker.read_text()==prior.read_text().replace('slope5_command_migration_environment_view.py','slope5_command_migration.py')
tree=ast.parse(worker.read_text());checked=[]
for node in ast.walk(tree):
 if isinstance(node,ast.For) and isinstance(node.target,ast.Name) and node.target.id=='name' and any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='copy2' for x in ast.walk(node)):
  for x in ast.walk(node.iter):
   if isinstance(x,ast.Constant) and isinstance(x.value,str):
    name=x.value
    if name in ('robot.usd','import_contract.json','robot_cfg.py'):continue
    assert (D/'isaac/mod4'/name).is_file(),name;checked.append(name)
assert 'slope5_command_migration.py' in checked and 'slope5_command_migration_environment_view.py' not in checked
import supervise_slope5_snapshot_reviewed_once as own
own.verify();own.wait_existing();source=own.source();info=own.prior.inherited.fullsave(source);assert info['finite_tensors']==102
assert not torch.cuda.is_initialized()
proof=dict(epoch=time.time(),passed=True,source_sha256=own.s.q.base.sha(source),source_count=404,snapshot_members_checked=len(checked),snapshot_literal_only_change=True,old402_source_exact_preserved=True,new_root_unique_entry_verified=True,SDK_native_small_exact_reused=True,full_CPU_schema_passed=info,no_CUDA_or_PPO_or_budget_action=True,new_big_fresh_formal_pending=True)
(D/'reports/SLOPE_SNAPSHOT_TARGET_CPU_PASSED.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''.replace('ROOTNEW',repr(NEW)).replace('ROOT402',repr(ROOT402))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('SNAPSHOT_FULL_RECEIPTS_CPU_REJECTED.json',dict(returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')));raise RuntimeError('Unique repair CPU admission rejected')
  save('SNAPSHOT_FULL_RECEIPTS_TARGET_CPU_PASSED.json',json.loads(raw))
  save('SNAPSHOT_FULL_RECEIPTS_STAGED_VERIFIED.json',dict(epoch=time.time(),root=NEW,source_count=404,old_failure_unique_cost_retained=True,no_native_small_replay=True))
  print(json.dumps(dict(root=NEW,source_count=404,CPU_passed=True,no_GPU_launch=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_FULL_RECEIPTS_STAGE_ERROR.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
