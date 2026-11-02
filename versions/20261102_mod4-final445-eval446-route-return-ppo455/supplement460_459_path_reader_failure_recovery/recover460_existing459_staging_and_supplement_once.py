"""Finish existing459 staged record without rerunning record; preserve quoted-path assertion failure."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
ID='mod4-final445-eval446-route-return-ppo455';TAG='trial-20261102-'+ID
V=G/('versions/20261102_'+ID)/'record459_actual446_video_curves455FIRST';SUP=V.parent/'supplement460_459_path_reader_failure_recovery'
def rawgit(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,check=True).stdout
def git(*args):return rawgit(*args).decode('utf8').strip()
def read(p):return json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def refs(s):return{r.split()[1]:r.split()[0]for r in s.splitlines()}
once=R/'RECOVER460_EXISTING459_ONCE_CONSUMED.json';assert not once.exists()
original=read(R/'RECORD459_ONCE_CONSUMED_BEFORE_GIT.json');recordpath=G/'history/experiments'/('20261102-'+ID+'.json');record=read(recordpath)
assert not git('tag','--list',TAG)and git('rev-parse','HEAD')=='f30410178844fbd6d122922f218831b1ac095821'
expected={p.relative_to(G).as_posix()for p in V.rglob('*')if p.is_file()}|{recordpath.relative_to(G).as_posix()}
staged={v.decode('utf8')for v in rawgit('diff','--cached','--name-only','-z').split(b'\0')if v}
assert staged==expected
for p,sha in record['source_and_evidence_sha256'].items():assert hashlib.sha256((G/p).read_bytes()).hexdigest()==sha
errors=sorted(R.glob('RECORD459_ORIGINAL_ERROR_*.json'));assert len(errors)==1 and 'AssertionError'in read(errors[0])['error']
put(once,dict(epoch=time.time(),existing_record=recordpath.relative_to(G).as_posix(),existing_staged_files=len(staged),
    cause='git diff--name-only quotes Chinese paths by default; same128 paths verified exact using NUL-delimited UTF8. No content missing; firstrecord did not commit/tag.',
    originalerror=str(errors[0]),no_record_replay=True,no_tag_overwrite=True,no_model_or_physics=True))
git('commit','-m',record['title']+'\n\nExperiment: '+TAG+'\nValidation: '+record['validation'])
phasehead=git('rev-parse','HEAD');assert not git('tag','--list',TAG)
message=R/'RECOVER460_EXISTING459_TAG_MESSAGE.txt'
with message.open('x',encoding='utf8')as f:f.write(record['title']+'\n\n'+record['repair_or_experiment_note'])
git('tag','-a',TAG,'-F',str(message))
obj=git('rev-parse','refs/tags/'+TAG);assert git('rev-parse','refs/tags/'+TAG+'^{}')==phasehead
git('push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+TAG)
remote=refs(git('ls-remote','--tags','origin'));assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==phasehead
assert all(remote.get(k)==v for k,v in original['oldrefs'].items())
assert git('ls-remote','origin','refs/heads/main').split()[0]==phasehead
put(R/'RECOVER460_EXISTING459_COMMIT_TAG_PUSH_RECEIPT.json',dict(epoch=time.time(),passed=True,phaseHEAD=phasehead,tagobject=obj,tagpeel=phasehead,remote_main=phasehead,oldrefsprotected=True,
    original459failurepreserved=True,record_not_replayed=True,tag_created_once=True))
SUP.mkdir();sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
targets=[*errors,once,message,R/'RECOVER460_EXISTING459_COMMIT_TAG_PUSH_RECEIPT.json',Path(__file__)]
rows=[]
for p in targets:
    data=p.read_bytes();safe,count=redact(data.decode('utf8'));arch=data if count==0 else safe.encode('utf8');out=SUP/p.name;out.write_bytes(arch)
    rows.append(dict(path=str(p),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),Git_path=out.relative_to(G).as_posix(),archive_SHA=hashlib.sha256(arch).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
put(SUP/'CAPTURE_INDEX_SUPPLEMENT460.json',dict(epoch=time.time(),phase=ID,files=rows,phaseHEAD=phasehead,tagobject=obj,tagpeel=phasehead,ordinary_supplement_no_newtag=True))
git('add','--',SUP.relative_to(G).as_posix());git('commit','-m','Preserve459 quoted-path reader failure and exact staged recovery receipt')
head=git('rev-parse','HEAD');git('push','origin','HEAD:refs/heads/main')
remote=refs(git('ls-remote','--tags','origin'));local=refs(git('show-ref','--tags','-d'))
assert all(remote.get(k)==v and local.get(k)==v for k,v in original['oldrefs'].items())
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==phasehead
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,main=head,remote_main=head,phase_commit=phasehead,tag=TAG,tagobject=obj,peel=phasehead,oldrefsprotected=True,lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad',clean=True,full_raw_failure_archived=True,no_record_replay=True)),flush=True)
