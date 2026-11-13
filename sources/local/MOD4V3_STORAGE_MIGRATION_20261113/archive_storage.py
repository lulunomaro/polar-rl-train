from pathlib import Path
import sys,json,hashlib,tempfile,subprocess,time
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';ID='mod4-windows-training-storage-migration-01';TAG='trial-20261113-'+ID;SYNC_ID=ID+'-sync';SYNC_TAG='trial-20261113-'+SYNC_ID
BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):return subprocess.check_output([*BASE,*args],text=True,encoding='utf8').strip()
def refs(*tags):
 names=['refs/heads/main','refs/heads/mod4v1-experts-fulldr-rm70']
 for t in tags:names += ['refs/tags/'+t,'refs/tags/'+t+'^{}']
 return {line.split()[1]:line.split()[0] for line in git('ls-remote','origin',*names).splitlines()}
assert git('branch','--show-current')=='mod4v1-experts-fulldr-rm70';before=refs();main=before['refs/heads/main']
files=[p for p in sorted(T.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in {'GIT_STORAGE_RECEIPT.json','ARCHIVE_STORAGE.log'} and p.suffix!='.pyc']+[R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md']
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git
def scoped(*args):
 if args[0]=='add':
  names=[v for v in args[1:] if v!='--']
  with tempfile.NamedTemporaryFile(mode='wb',prefix='storage-paths-',dir=R.parent/'tmp',delete=False) as f:
   for name in names:f.write(name.encode('utf8')+b'\0')
   spec=Path(f.name)
  try:return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
  finally:spec.unlink()
 if args[0]=='tag' and '-m' in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',prefix='storage-tag-',dir=R.parent/'tmp',delete=False) as f:f.write(args[i+1]);note=Path(f.name)
  try:return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args[:i],'-F',str(note),*args[i+2:])
  finally:note.unlink()
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=scoped
sys.argv=['record_experiment.py','--id',ID,'--title','Move210 training data to Windows volume and prune verified archived duplicates','--kind','repair','--note-file',str(T/'README.md'),'--validation','130878 files SHA256 verified,41 links preserved,old paths kept,persistent NTFS mount;114 old PT proved published ordinary Git blobs,two closed-job caches removed;current25m35/78/6/17Adam/full replay state loads;proxy7897/TLS;main preserved','--files',*[p.relative_to(R).as_posix() for p in files]]
rec.main();commit=git('rev-parse','HEAD');git('push','--atomic','origin','HEAD','refs/tags/'+TAG);remote=refs(TAG);assert remote['refs/tags/'+TAG+'^{}']==commit and remote['refs/heads/mod4v1-experts-fulldr-rm70']==commit and remote['refs/heads/main']==main
checks=[]
for p in [E/'VERIFIED_FILES.jsonl',E/'CLEANUP_COMPLETE.json',E/'VERIFIED_GIT_MODELS.json']:
 rel=p.relative_to(R).as_posix();raw=subprocess.check_output([*BASE,'show',commit+':'+rel]);assert hashlib.sha256(raw).digest()==hashlib.sha256(p.read_bytes()).digest();checks.append(dict(path=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
receipt=E/'GIT_STORAGE_RECEIPT.json';receipt.write_text(json.dumps(dict(epoch=time.time(),payload_commit=commit,payload_tag=TAG,remote_refs=remote,main_before=main,main_after=remote['refs/heads/main'],proxy='http://127.0.0.1:7897',TLS_verify=True,verified_raw_records=checks),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sys.argv=['record_experiment.py','--id',SYNC_ID,'--title','Record verified210 Windows training-data migration archive','--kind','repair','--note-file',str(receipt),'--validation','Branch/tag/peeled and raw checksum/removal manifests verified;proxy7897/TLS;main unchanged','--files',receipt.relative_to(R).as_posix(),'--push'];rec.main();sync=git('rev-parse','HEAD');remote=refs(TAG,SYNC_TAG);assert remote['refs/tags/'+TAG+'^{}']==commit and remote['refs/tags/'+SYNC_TAG+'^{}']==sync and remote['refs/heads/mod4v1-experts-fulldr-rm70']==sync and remote['refs/heads/main']==main
print(json.dumps(dict(status='STORAGE_ARCHIVE_COMPLETE',payload_commit=commit,sync_commit=sync,remote_refs=remote),ensure_ascii=False),flush=True)
