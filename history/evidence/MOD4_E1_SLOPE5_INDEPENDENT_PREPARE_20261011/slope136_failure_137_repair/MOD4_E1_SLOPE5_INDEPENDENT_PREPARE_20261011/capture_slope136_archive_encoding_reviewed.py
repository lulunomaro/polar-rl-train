"""Complete the interrupted capture without changing original nonUTF8 console logs."""
from archive_slope_scope_stage_once import *

def capture(dest):
 # The first archive stopped before record_experiment on one mixed-console-encoding log.
 assert dest.exists();known=known_refs();entries=[];files=[]
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 for scope in (PRE,D):
  for p in sorted(scope.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h)
   if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip','.partial') or len(raw)>50_000_000:
    row.update(capture='actual_large_original_index_only',original_retained=True);entries.append(row);continue
   assert p.suffix.lower() in ('.py','.md','.json','.txt','.log','.toml'),p
   if h in known:
    ref=known[h];row.update(capture='existing_same_SHA_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256']);entries.append(row);continue
   encoding='utf8'
   try:text=raw.decode('utf8')
   except UnicodeDecodeError:
    assert p.suffix.lower() in ('.log','.txt'),p
    # Byte-preserving latin1 view lets the credential redactor inspect ASCII keys.
    # Unredacted legacy console bytes remain exact, rather than converting a guessed encoding.
    text=raw.decode('latin1');encoding='original_nonUTF8_console_bytes_latin1_redaction_view_only'
   clean,n=redact(text);captured=raw if n==0 else clean.encode('utf8')
   out=dest/scope.name/p.relative_to(scope);out.parent.mkdir(parents=True,exist_ok=True)
   if out.exists():assert out.read_bytes()==captured
   else:out.write_bytes(captured)
   gp=out.relative_to(REPO).as_posix();files.append(gp)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',redactions=n,source_encoding=encoding,
    Git_path=gp,archived_bytes=len(captured),archived_sha256=H(captured),original_retained=True)
   entries.append(row);known[h]=row
 ip=dest/'REPORT_CAPTURE_INDEX.json';assert not ip.exists();ip.write_bytes(json.dumps(dict(epoch=time.time(),entries=entries,
  original_mixed_encoding_console_bytes_preserved=True,original_capture_rejection_retained=True,
  all_current_saved_reports_source_reader_errors_workorders_captured=True,credentials_excluded=True,
  large_originals_indices_only=True,later_reports_need_supplement=True),ensure_ascii=False,indent=2).encode());files.append(ip.relative_to(REPO).as_posix())
 return entries,files
