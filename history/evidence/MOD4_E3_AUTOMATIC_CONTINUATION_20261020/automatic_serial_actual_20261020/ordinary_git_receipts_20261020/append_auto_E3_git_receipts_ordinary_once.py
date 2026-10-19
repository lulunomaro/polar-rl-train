"""Append all post-record source/reports/app receipts to the same series; no new record or tag."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';ROOT=REPO/'history/evidence'/B.name/'automatic_serial_actual_20261020';DEST=ROOT/'ordinary_git_receipts_20261020';BASE='db7559366b40369b6cd016db807876af14e59698';H=lambda x:hashlib.sha256(x).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(REPO),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(old.splitlines())==1412;prior={}
 for p in [ROOT/'REPORT_CAPTURE_INDEX.json',ROOT/'archive_resume_same_unique_trial/RESUME_REPORT_CAPTURE_INDEX.json']:
  for row in json.loads(p.read_bytes())['entries']:
   if row.get('source_SHA'):prior[(row['source_path'],row['source_SHA'])]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir();files=[];entries=[];extensions={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.bat','.ps1','.xml','.mjcf','.cfg','.h','.cpp','.c','.ini'}
 for f in sorted(B.rglob('*')):
  if not f.is_file() or '__pycache__' in f.parts or f.suffix.lower() not in extensions:continue
  raw=f.read_bytes();sha=H(raw)
  if (str(f),sha) in prior:continue
  try:text=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:text=raw.decode('latin1');enc='latin1'
  clean,count=redact(text);data=clean.encode(enc) if count else raw;assert len(data)<50_000_000;q=DEST/f.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);rel=q.relative_to(REPO).as_posix();files.append(rel);entries.append(dict(source_path=str(f),source_SHA=sha,bytes=len(raw),Git_path=rel,archived_SHA=H(data),redactions=count,original_retained=True,capture='complete_exact_bytes' if count==0 else 'complete_credential_redacted'))
 q=DEST/'ORDINARY_SUPPLEMENT_CAPTURE_INDEX.json';q.write_text(json.dumps(dict(epoch=time.time(),kind='ordinary_append_same_auto_E3_stage',entries=entries,old_unique=BASE,existing_tags_unchanged=True,no_record_or_new_tag_or_training_or_ledger_or_SSH=True,deferred=[]),indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix());git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode('utf8') for x in files)+b'\0');git('commit','-m','Append automatic E3 serial stage remote receipts and consumed-monitor readback');git('push','origin','HEAD:main');head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags')==old
 for line in old.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 for row in entries:
  p=subprocess.run(['git','-C',str(REPO),'show',head+':'+row['Git_path']],capture_output=True,check=True);assert H(p.stdout)==row['archived_SHA']
 assert not git('status','--porcelain');print(json.dumps(dict(status='ORDINARY_REMOTE_VERIFIED',commit=head,unique_stage=BASE,total_tags=1412,all1412_tag_objects_and_peels_unchanged=True,text_entries=len(entries),all_committed_new_blobs_verified=True,deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('AUTO_E3_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True),f,indent=2)
  raise
