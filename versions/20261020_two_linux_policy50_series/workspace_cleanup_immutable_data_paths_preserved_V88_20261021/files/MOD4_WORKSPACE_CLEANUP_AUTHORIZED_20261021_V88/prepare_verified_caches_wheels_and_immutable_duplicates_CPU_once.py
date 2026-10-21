"""Inventory only. Hashes serve authorized storage identity checks, never Git."""
from pathlib import Path
import collections,datetime,hashlib,json,os,stat,time,traceback
B=Path(__file__).resolve().parent;W=B.parent.resolve();R=B/'reports';H=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def row(p):
 s=p.stat(follow_symlinks=False);assert p.resolve().is_relative_to(W) and stat.S_ISREG(s.st_mode) and not (getattr(s,'st_file_attributes',0)&1024);return dict(path=str(p.resolve()),bytes=s.st_size,mtime_ns=s.st_mtime_ns,inode=s.st_ino,nlink=s.st_nlink)
def put(n,v):(R/n).open('x',encoding='utf8').write(json.dumps(v,ensure_ascii=False,indent=2))
try:
 put('CLEANUP_V88_IDENTITY_INVENTORY_STARTED.json',dict(epoch=time.time(),authorization='[REDACTED]',no_delete=True))
 inv=json.loads((R/'WORKSPACE_SIZE_AND_REGENERABLE_CACHE_INVENTORY_ACTUAL.json').read_bytes());caches=[]
 for x in inv['safe_regenerable_python_cache_files']:
  p=Path(x['path'])
  if p.exists():
   a=row(p)
   if (a['bytes'],a['mtime_ns'],a['inode'])==(x['bytes'],x['mtime_ns'],x['inode']):caches.append(a)
 wh=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr/TESTED_MINIMAL_NATIVE311_WHEELHOUSE_20261013';m=json.loads((wh/'ACTUAL_WHEELHOUSE_MANIFEST.json').read_bytes());wheels=[];wheel_kept=[]
 for x in m['selected']:
  p=Path(x['destination']);source=Path(x['source'])
  if not p.exists():continue
  assert p.parent.resolve()==wh.resolve() and p.suffix=='.whl';a=row(p)
  if not source.is_file() or source.stat().st_size!=x['bytes']:wheel_kept.append(dict(path=str(p),reason='original installer cache unavailable; retained'));continue
  # The external pip original is read only, never removed by workspace cleanup.
  if H(source)!=x['sha256'] or H(p)!=x['sha256']:wheel_kept.append(dict(path=str(p),reason='identity mismatch; retained'));continue
  wheels.append(dict(**a,SHA=x['sha256'],retained_original_path=str(source.resolve()),retained_original_bytes=source.stat().st_size,source_manifest=str(wh/'ACTUAL_WHEELHOUSE_MANIFEST.json'),reason='obsolete Windows311 offline installer copy; original exact pip cache retained'))
 protected={'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021','MOD4_CURRENT_EXPERT_GRADUATION_JUMP_FROZEN_20261021','MOD4_BUDGET_ADD100H_EIGHTH_20261021','MOD4_TWO_LINUX_POLICY50_COHORT_51_20261021','MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021','MOD4_TWO_LINUX_POLICY50_COHORT_53_20261021','MOD4_LATEST_HYBRID_MOE_PACKAGE_20261020','MOD4_LOCAL_LATEST_MOE_WASD_20261018','MOD4_LOCAL_MOE_LATEST_CLOSED_UPDATE_20261019','MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019'}
 cutoff=datetime.datetime(2026,10,21,tzinfo=datetime.timezone(datetime.timedelta(hours=8))).timestamp();groups=collections.defaultdict(list);stack=[p for p in W.iterdir() if p.is_dir() and p.name.startswith('MOD4_') and p.name not in protected and p!=B]
 while stack:
  d=stack.pop()
  with os.scandir(d) as it:
   for e in it:
    p=Path(e.path);st=e.stat(follow_symlinks=False)
    if getattr(st,'st_file_attributes',0)&1024:continue
    if e.is_dir(follow_symlinks=False):
     if e.name not in ('.git','__pycache__','node_modules','.venv'):stack.append(p)
    elif e.is_file(follow_symlinks=False) and p.suffix.lower() in ('.pt','.pth','.npz') and st.st_size>=1024**2 and st.st_mtime<cutoff:groups[st.st_size].append(p)
 duplicates=[];hashed=0;bytes_hashed=0
 for size,files in groups.items():
  if len(files)<2:continue
  same=collections.defaultdict(list)
  for p in files:
   a=row(p);digest=H(p);hashed+=1;bytes_hashed+=size;after=row(p);assert a==after;same[digest].append(a)
  for digest,rs in same.items():
   if len(rs)<2:continue
   def victim(x):
    p=Path(x['path']);parts=[v.lower() for v in p.parts]
    return any('payload' in v or v=='source_snapshot' for v in parts) or p.parent.name.lower()=='source' or p.name.lower()=='source.pt'
   keep=sorted(rs,key=lambda x:(victim(x),len(Path(x['path']).parts),x['path']))[0]
   targets=[x for x in rs if x is not keep and victim(x) and x['inode']!=keep['inode'] and x['nlink']==1]
   if targets:duplicates.append(dict(SHA=digest,bytes=size,retained=keep,targets=targets,all_paths_and_bytes_retained_by_hardlink=True,original_mtime_metadata_recorded=True))
 # Verify native NTFS hardlink support inside this explicit workspace before selection.
 p=B/'V88_HARDLINK_PREFLIGHT_SOURCE.tmp';q=B/'V88_HARDLINK_PREFLIGHT_LINK.tmp';assert not p.exists() and not q.exists();p.write_bytes(b'MOD4 immutable-data-only cleanup preflight\n');os.link(p,q);assert H(p)==H(q) and p.stat().st_ino==q.stat().st_ino and p.stat().st_nlink==2;q.unlink();p.unlink()
 out=dict(epoch=time.time(),workspace=str(W),passed_identity_inventory=True,no_delete_yet=True,regenerable_python_cache_files=caches,cache_bytes=sum(x['bytes'] for x in caches),obsolete_wheel_copies_with_exact_retained_original=wheels,wheel_bytes=sum(x['bytes'] for x in wheels),wheel_copies_retained=wheel_kept,immutable_binary_duplicate_groups=duplicates,duplicate_bytes_eliminable=sum(x['bytes']*len(x['targets']) for x in duplicates),hardlink_native_preflight_passed=True,hashing_purpose='necessary byte equality for user-authorized storage cleanup, not Git',hash_files=hashed,hash_bytes=bytes_hashed,protected_stage_roots=sorted(protected),no_FINAL_or_unique_model_raw_source_report_log_or_Git_object_delete=True,Python_environment_and_player_preserved=True,no_permission_or_reparse_bypass=True)
 put('CLEANUP_V88_VERIFIED_EXACT_TARGETS_CPU_ACTUAL.json',out);print(json.dumps(dict(passed=True,caches=len(caches),cache_bytes=out['cache_bytes'],obsolete_wheel_copies=len(wheels),wheel_bytes=out['wheel_bytes'],duplicate_groups=len(duplicates),duplicate_targets=sum(len(x['targets']) for x in duplicates),duplicate_bytes=out['duplicate_bytes_eliminable'],wheel_kept=len(wheel_kept))))
except BaseException:put('CLEANUP_V88_INVENTORY_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_deletion=True));raise
