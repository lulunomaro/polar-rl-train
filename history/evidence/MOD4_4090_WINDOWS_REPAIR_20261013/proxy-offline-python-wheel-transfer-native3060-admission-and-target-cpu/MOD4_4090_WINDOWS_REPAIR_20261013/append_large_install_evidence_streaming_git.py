from pathlib import Path
import sys,json,time,subprocess,hashlib
from append_windows4090_evidence_git import a,g,R,D

def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def capture_streaming(dest):
 prior=a.prior_index();sys.path.insert(0,str(R/'archive_tools'));from capture_history import redact
 assert not dest.exists();dest.mkdir(parents=True);rows=[];files=[]
 for folder in a.FOLDERS:
  for p in sorted(folder.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   size=p.stat().st_size;large=p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.whl','.dmp') or size>8000000
   if large:
    before=p.stat();sha=sha_file(p);after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'Artifact changed during SHA snapshot'
    row=dict(source_path=str(p.resolve()),bytes=size,sha256=sha)
   else:
    raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
   if sha in prior:
    ref=prior[sha];assert sha_file(R/ref['Git_path'])==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
   elif large:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True,streaming_hash_without_GB_memory_allocation=True)
   else:
    try:txt=raw.decode('utf8');enc='utf8'
    except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1_byte_preserving'
    clean,n=redact(txt);data=clean.encode('utf8') if n else raw;out=dest/folder.name/p.relative_to(folder);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(R).as_posix();files.append(name);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=hashlib.sha256(data).hexdigest(),encoding=enc,redactions=n)
   rows.append(row)
 p=dest/'REPORT_CAPTURE_INDEX.json';p.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_source_reports_rejections_errors_cost_false_and_prepared_unused_captured=True,large_originals_retained_index_only=True,credentials_excluded=True,streaming_large_artifact_hashing=True,later_Git_receipts_require_supplement=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(p.relative_to(R).as_posix());return rows,files

# The imported old helper expects a label; it has already consumed sys.argv[1]
# and executed on import. This module must not import its executable main.
