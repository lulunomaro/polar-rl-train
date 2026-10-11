"""Append saved poststage receipts/prepared readers only; never replay a trial."""
from second50_io import *
import subprocess
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name

def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only')
 previous=gitio.refs();covered=set()
 for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes()).get('entries',[]):
   if 'sha256' not in row:continue # Legacy other-project shape is not reused as coverage.
   if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
   covered.add(row['sha256'])
 pending=[]
 for folder in (D,PRIOR):
  for p in sorted(folder.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   raw=p.read_bytes();sha=H(raw)
   if sha not in covered:pending.append((folder,p,raw,sha))
 if not pending:print(json.dumps(dict(no_new_saved_evidence=True,no_trial_or_commit_created=True)));return
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 dest=BASE/('saved_report_supplement_'+str(time.time_ns()));dest.mkdir(parents=True);rows=[];files=[]
 for folder,p,raw,sha in pending:
  row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:txt=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(txt);data=clean.encode('utf8') if count else raw;out=dest/folder.name/p.relative_to(folder);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
  rows.append(row)
 p=dest/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_saved_report_supplement=True,no_training_evaluation_budget_record_tag_or_automation_replay=True,large_originals_retained=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
 gitio.g('commit','-m','Append Wave50 second386 Git receipt and future direct146 reader evidence');head=gitio.g('rev-parse','HEAD');gitio.g('push','origin','HEAD')
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
 for name,(obj,peeled) in previous.items():assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 assert not gitio.g('status','--porcelain')
 print(json.dumps(dict(commit=head,remote_main_verified=True,old_tags_preserved=len(previous),saved_delta_sources=len(rows),all_saved_delta_reports_tracked_exact=True,ordinary_supplement=True,no_new_trial_tag=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('SAVED_DELTA_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_original_objects_only_no_commit_tag_replay=True));raise
