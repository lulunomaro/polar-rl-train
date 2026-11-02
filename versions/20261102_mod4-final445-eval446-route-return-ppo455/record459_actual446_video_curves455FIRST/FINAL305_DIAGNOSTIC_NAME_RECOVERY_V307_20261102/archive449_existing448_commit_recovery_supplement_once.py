"""Record original448 commit failure and same-staging completion, without rerecording/retagging."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
V=G/'versions/20261102_mod4-final433-eval437-saturation-ppo445/supplement449_existing448_commit_recovery'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)

assert not V.exists()and not(R/'SUPPLEMENT449_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert not git('status','--porcelain')and git('branch','--show-current')=='main'
assert git('rev-parse','HEAD')=='49319b0e662beaf48afb25094ba780ebfb319be7'
refs=lambda text:{r.split()[1]:r.split()[0]for r in text.splitlines()}
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in old.items())
tag='trial-20261102-mod4-final433-eval437-saturation-ppo445'
assert old['refs/tags/'+tag]=='d4a60f4a47b341f46693802d3e7e13021b753612'
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
put(R/'SUPPLEMENT449_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),ordinary=True,record448_done=True,
    original_tagobject=old['refs/tags/'+tag],original_peel=old['refs/tags/'+tag+'^{}'],no_record_replay=True,no_retag=True,
    original448_commit128_reason='Unknown: original record wrapper did not print captured stderr',
    sameexistingstaging_retrycommit_success=True,record448_remotemain_tag_peel_verified=True,
    modelreads=0,physics=0,newSSH=0,pushretry='Existingobjects only'))
sources=[Path(__file__),R/'RECORD448_ORIGINAL_COMMIT128_AND_EXISTING_STAGING_RECOVERY.json',
         R/'RECORD448_EXISTING_ANNOTATED_TAG_BODY.txt',R/'SUPPLEMENT449_ONCE_CONSUMED_BEFORE_GIT.json']
V.mkdir(parents=True);(V/'.gitattributes').write_text('* -text\n',encoding='utf8')
index=[]
for path in sources:
    target=V/path.name;target.write_bytes(path.read_bytes())
    index.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),Git_path=target.relative_to(G).as_posix(),archiveSHA=H(target)))
put(V/'CAPTURE_INDEX_SUPPLEMENT449.json',dict(epoch=time.time(),files=index,record448tagobject=old['refs/tags/'+tag],
    record448peel=old['refs/tags/'+tag+'^{}'],alloldtags_protected=True,no_modelreads_or_physics=True))
git('add','--',V.relative_to(G).as_posix())
git('commit','-m','Preserve record448 initial commit refusal and existing-staging completion')
head=git('rev-parse','HEAD');git('push','origin','HEAD:refs/heads/main')
after=refs(git('ls-remote','--tags','origin'));local=refs(git('show-ref','--tags','-d'))
assert all(after.get(k)==v and local.get(k)==v for k,v in old.items())
assert all(after.get(k)==v for k,v in remote.items())
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,remote_main=head,record448tagobject=old['refs/tags/'+tag],
    record448peel=old['refs/tags/'+tag+'^{}'],alloldtagsprotected=True,lqr=lqr,clean=True,
    archived_original_commit128_and_recovery=True,no_more_savedpostGitreport=True)),flush=True)
