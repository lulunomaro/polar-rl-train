from pathlib import Path,PurePosixPath
import hashlib,json,shutil,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;N=T/'H1_STEP270_E3_PAIR_V1_20261021';R=T/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
root=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['roots']['h1']
idx=read(N/'current_pair_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')
rows=idx['index'];assert idx['controls']==318 and len(rows)==14
dest=T/'relocated_forensic_originals/H1step270_pairV1_closed_control318';assert not dest.exists();dest.mkdir(parents=True)
total=sum(x['bytes'] for x in rows);assert shutil.disk_usage(T).free>total+8*1024**3
put('PAIR_V1_H1_CLOSED_CONTROL_RAW_RELOCATION_STARTED_ACTUAL.json',dict(epoch=time.time(),source_root=root,destination=str(dest),files=rows,total_bytes=total,reason='closed failed H1 query forensic preservation and authorized 210 storage release; not Git copying'))
c=None;saved=[]
try:
 c=d.t.connect()
 check=d.code(c,d.t.PY,"from pathlib import Path;import json,os,psutil,shutil;B=Path(v['root']);e=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'];assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));print(json.dumps(dict(all_own_H1_out=True,free_before=shutil.disk_usage(B).free)))",dict(root=root),timeout=30)
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for row in rows:
   p=dest/PurePosixPath(row['path']).name;part=p.with_suffix('.npz.partial');sf.get(row['path'],str(part))
   assert part.stat().st_size==row['bytes']
   h=hashlib.sha256()
   with part.open('rb') as f:
    for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
   assert h.hexdigest()==row['SHA'];part.replace(p);saved.append(dict(row,local_path=str(p),complete_SHA_verified=True))
   put('PAIR_V1_CONTROL_RAW_FILE_'+str(len(saved)).zfill(2)+'_RELOCATED_ACTUAL.json',saved[-1])
 finally:sf.close()
 result=d.code(c,d.t.PY,"""from pathlib import Path
import hashlib,json,os,psutil,shutil,time
B=Path(v['root']);assert json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
before=shutil.disk_usage(B).free;verified=[]
for row in v['files']:
 p=Path(row['path']);assert p.resolve().is_relative_to((B/'job0/production/control_prefix_raw').resolve()) and p.suffix=='.npz' and p.name.startswith('control_prefix_') and not p.is_symlink() and p.stat().st_size==row['bytes'] and row['complete_SHA_verified']
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 assert h.hexdigest()==row['SHA'];verified.append(p)
for p in verified:p.unlink()
print(json.dumps(dict(epoch=time.time(),removed_only_twohost_fullSHA_verified_closed_NPZ_duplicates=len(verified),free_before=before,free_after=shutil.disk_usage(B).free,unique_forensic_contents_preserved_at_verified_local_paths=True,no_model_FINAL_source_text_error_or_budget_changed=True)))
""",dict(root=root,files=saved),timeout=240)
 put('PAIR_V1_H1_CLOSED_CONTROL318_FORENSICS_RELOCATED_SPACE_RELEASED_ACTUAL.json',dict(epoch=time.time(),files=saved,source_check=check,actual=result,total_bytes=total,local_free_after=shutil.disk_usage(T).free))
 print(json.dumps(dict(relocated=len(saved),bytes=total,space=result)))
except BaseException:
 put('PAIR_V1_H1_RAW_RELOCATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),saved_files=saved,no_replay_once=True));raise
finally:
 if c:c.close()
