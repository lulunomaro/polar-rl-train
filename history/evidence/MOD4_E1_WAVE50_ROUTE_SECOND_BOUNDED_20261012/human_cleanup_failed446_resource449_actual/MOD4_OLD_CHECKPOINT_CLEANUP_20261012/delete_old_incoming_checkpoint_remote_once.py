from pathlib import Path
import os,json,time,hashlib,stat,re,shutil
B=Path('/home/egde/rl_candidates').resolve();P=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/HUMAN_OBSOLETE_INCOMING_CHECKPOINT_CLEANUP_PLAN_STAGED_20261012.json');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(P)=='c7c28347ab1bd97e84e42d9d33792c38ba92c336b7776c0594c16fe71d56fb18';plan=json.loads(P.read_bytes());allowed=Path(plan['only_allowed_directory']).resolve()
assert allowed==B/'MOD4_native_floor_continue10h_20260930/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac'
R=B/'MOD4_MOE_PLAN_EXECUTION_20261007/reports';journal=R/'HUMAN_OLD_CHECKPOINT_DELETE_JOURNAL_20261012.jsonl';receipt=R/'HUMAN_OLD_CHECKPOINT_DELETE_ACTUAL_20261012.json';assert not journal.exists() and not receipt.exists()
for name,sha in plan['protected_SHA'].items():assert h(Path(name))==sha
budget=Path(next(k for k in plan['protected_SHA'] if k.endswith('TRAINING_BUDGET_10H.json')));assert json.loads(budget.read_bytes())['active_segment'] is None
refs=set();exclude={P,R/'HUMAN_OLD_CHECKPOINT_ROWS_STAGED_20261012.json'};pattern=re.compile(rb'model_[0-9]+[.]pt')
for root,dirs,names in os.walk(B,followlinks=False):
 dirs[:]=[x for x in dirs if x not in ('__pycache__','.git') and not Path(root,x).is_symlink()]
 for name in names:
  p=Path(root,name)
  if p in exclude or p.is_symlink() or p.suffix.lower() not in ('.json','.md','.py','.txt'):continue
  with p.open('rb') as f:
   tail=b''
   for block in iter(lambda:f.read(1048576),b''):
    data=tail+block;refs.update(x.decode() for x in pattern.findall(data));tail=data[-128:]
active=[];opened=set()
for root in Path('/proc').glob('[0-9]*'):
 try:
  argv=[x.decode(errors='replace') for x in (root/'cmdline').read_bytes().split(b'\x00') if x];cwd=(root/'cwd').resolve()
  ownroots=[Path(a) for a in argv if a.startswith(str(B)+'/')]
  if cwd.is_relative_to(B) and cwd!=B:ownroots.append(cwd)
  if any((B/q.relative_to(B).parts[0])==B/'MOD4_native_floor_continue10h_20260930' for q in ownroots):active.append(dict(pid=int(root.name),argv=argv,cwd=str(cwd)))
  for fd in (root/'fd').iterdir():
   try:opened.add(str(fd.resolve()))
   except OSError:pass
 except (OSError,ValueError):pass
assert not active,('A process owns the canonical source root; no deletion',active)
for row in plan['rows']:
 p=Path(row['path']);s=p.stat();assert p.resolve()==p and p.is_relative_to(allowed) and not p.is_symlink() and stat.S_ISREG(s.st_mode) and s.st_nlink==1
 assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(row['device'],row['inode'],row['bytes'],row['mtime_ns'],row['ctime_ns'])
 assert p.name not in refs and str(p) not in opened and int(p.stem[6:])%1000!=0 and h(p)==row['sha256']
 siblings=sorted(p.parent.glob('model_[0-9]*.pt'),key=lambda x:int(x.stem[6:]));assert p!=siblings[0] and p not in siblings[-3:]
before=shutil.disk_usage(B).free;deleted=[]
with journal.open('x') as log:
 for row in plan['rows']:
  p=Path(row['path']);s=p.stat();assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(row['device'],row['inode'],row['bytes'],row['mtime_ns'],row['ctime_ns'])
  log.write(json.dumps(dict(epoch=time.time(),action='intent_exact_unlink',path=str(p),bytes=row['bytes'],sha256=row['sha256']))+'\n');log.flush();os.fsync(log.fileno())
  p.unlink();assert not p.exists();out=dict(epoch=time.time(),path=str(p),bytes=row['bytes'],allocated_bytes=row['allocated_bytes'],sha256=row['sha256'],deleted=True,human_authorized_obsolete_checkpoint_only=True,original_binary_no_longer_retained=True)
  log.write(json.dumps(dict(action='deleted',**out))+'\n');log.flush();os.fsync(log.fileno());deleted.append(out)
for name,sha in plan['protected_SHA'].items():assert h(Path(name))==sha
v=dict(epoch=time.time(),passed=True,authorization='远古一些废旧检查点可以清理',exact_plan_path=str(P),exact_plan_sha256='c7c28347ab1bd97e84e42d9d33792c38ba92c336b7776c0594c16fe71d56fb18',deleted=deleted,deleted_files=len(deleted),deleted_bytes=sum(x['bytes'] for x in deleted),planned_reclaimed_allocated_bytes=sum(x['allocated_bytes'] for x in deleted),durable_free_before=before,durable_free_after=shutil.disk_usage(B).free,only_allowed_directory=str(allowed),first_last3_every1000_and_referenced_models_retained=True,no_source_report_raw_env_cache_or_current_expert_checkpoint_deleted=True,protected_SHA=plan['protected_SHA'],protected_checkpoints_and_canonical_bytes_exact=True,no_GPU_PPO_or_budget_transaction=True,journal_path=str(journal),journal_sha256=h(journal))
receipt.write_text(json.dumps(v,ensure_ascii=False,indent=2));print(json.dumps(dict(receipt_path=str(receipt),receipt_sha256=h(receipt),deleted_files=v['deleted_files'],deleted_bytes=v['deleted_bytes'],free_before=before,free_after=v['durable_free_after'])))
