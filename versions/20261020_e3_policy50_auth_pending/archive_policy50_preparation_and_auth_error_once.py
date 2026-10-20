"""Record this actual partial stage once; never re-run this helper or re-tag it."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';G=W/'polar-rl-train'
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
ID='e3-policy50-clock-preparation-auth-pending'
DEST=G/'versions/20261020_e3_policy50_auth_pending'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')=='d739f4f0692489e5add8989ed10606c38489ad9b'
 assert not git('diff','--cached','--name-only') and not DEST.exists()
 tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines();assert len(tags)==1412
 put(R/'POLICY50_PREARCHIVE_ORIGINAL_TAG_OBJECTS_ACTUAL.json',dict(epoch=time.time(),base_HEAD=git('rev-parse','HEAD'),old_tag_objects_and_peeled=tags,old_tag_count=len(tags),new_stage_ID=ID,new_trial_not_new_training=True))
 files=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md') and p.stat().st_size<50_000_000
  text=p.read_text('utf8');archived,n=redact(text);raw=p.read_bytes();dest=DEST/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(archived,encoding='utf8')
  files.append(dict(path=str(p),bytes=len(raw),SHA=H(raw),archive=dest.relative_to(G).as_posix(),archive_bytes=dest.stat().st_size,archive_SHA=H(dest.read_bytes()),redaction_count=n,mode='redacted' if archived!=text else 'full_text'))
 put(DEST/'COMPLETE_STAGE_TEXT_MANIFEST.json',dict(epoch=time.time(),entries=files,no_weights_raw_or_credentials=True,all_original_errors_retained=True,actual_50Hz_GO=False,authentication_pending=True))
 selected=[p.relative_to(G).as_posix() for p in sorted(DEST.rglob('*')) if p.is_file()]
 cmd=[sys.executable,'-B','-X','utf8',str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','E3 50Hz clock components prepared; SSH key load failed and remote switch remains pending','--kind','diagnostic','--note-file',str(DEST/'STAGE_NOTE.md'),'--validation','Four CPU component groups passed; exact existing-monitor prompt readback; no authenticated remote command, no 50Hz GO/PPO, no canonical writes','--files',*selected,'--push']
 p=subprocess.run(cmd,text=True,capture_output=True,timeout=180);print(p.stdout,flush=True)
 if p.returncode:print(p.stderr,flush=True);raise RuntimeError('Record or push failed; inspect existing objects and do not re-record')
 head=git('rev-parse','HEAD');tag='trial-20261020-'+ID
 assert git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines()==sorted(tags+[git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/'+tag)])
 remote=dict(line.split()[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines())
 assert remote['refs/heads/main']==head
 for line in tags:
  parts=line.split();ref,obj=parts[:2];assert remote[ref]==obj
  if len(parts)==3:assert remote[ref+'^{}']==parts[2]
 assert remote['refs/tags/'+tag]==git('rev-parse',tag) and remote['refs/tags/'+tag+'^{}']==head
 print(json.dumps(dict(remote_main=head,unique_stage_tag=tag,tag_object=remote['refs/tags/'+tag],total_tags=1413,all1412_old_tag_objects_and_peels_unchanged=True,archived_text_files=len(files),actual_50Hz_GO=False,authentication_pending=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('POLICY50_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_record_or_helper=True));raise
