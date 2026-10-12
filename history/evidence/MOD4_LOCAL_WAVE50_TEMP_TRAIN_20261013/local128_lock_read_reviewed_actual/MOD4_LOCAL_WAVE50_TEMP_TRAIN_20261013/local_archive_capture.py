from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;REPO=D.parent/'polar-rl-train'
sys.path.insert(0,str(D.parent/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as inherited
H=lambda b:hashlib.sha256(b).hexdigest()
def capture(dest):
 prior=inherited.prior_index();sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 assert not dest.exists();dest.mkdir(parents=True);rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  if p==D/'LOCAL_GPU_EXCLUSIVE.lock':
   rows.append(dict(source_path=str(p.resolve()),bytes=p.stat().st_size,sha256=None,capture='live_owned_OS_lock_metadata_only',reason='actual_msvcrt_byte_lock_prevents_read; no unlock/delete/permission mutation',original_retained=True));continue
  raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True,live_partial_saving_file=p.name.endswith('.saving.pt'))
  else:
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1_byte_preserving'
   clean,n=redact(txt);data=clean.encode('utf8') if n else raw;out=dest/D.name/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=enc,redactions=n)
  rows.append(row)
 p=dest/'REPORT_CAPTURE_INDEX.json';p.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_sources_reports_and_original_failures_captured=True,live_OS_lock_SHA_unknown_disclosed=True,live_output_point_in_time_snapshot_only=True,later_updates_and_Git_receipts_require_supplement=True,large_originals_index_only=True,credentials_excluded=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(p.relative_to(REPO).as_posix());return rows,files
