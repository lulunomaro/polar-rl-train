"""Push only the existing feature and exact Phase36 annotated trial atomically.
Read-only main observation; never changes main, commits or experiment artifacts.
"""
from pathlib import Path
import subprocess,json,sys,time
R=Path(__file__).resolve().parent;REPO=R.parent/'repo-lqr';out=R/'reports/PHASE36_FEATURE_AND_ANNOTATED_TRIAL_REMOTE_VERIFY_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE36_EXACT_FEATURE_TRIAL_PUSH_STARTED_ONCE.json';assert not out.exists()and not marker.exists()
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
branch='mod4v1-experts-fulldr-rm70';head='99a85ed22f96d156c501fd9c590f54b0163af490';tag='trial-20261104-mod4v1-supermimic-phase1-qualified-capture-good-source-publication-phase36'
def G(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
assert G('branch','--show-current')==branch and G('rev-parse','HEAD')==head and not G('status','--porcelain');assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head;obj=G('rev-parse','refs/tags/'+tag)
with marker.open('x',encoding='utf-8')as f:json.dump(dict(epoch=time.time(),feature=branch,HEAD=head,annotated_trial=tag,tag_object=obj,main_push_reset_or_new_commit=False),f,indent=2)
p=subprocess.run(['git','-C',str(REPO),'push','--atomic','origin','refs/heads/'+branch+':refs/heads/'+branch,'refs/tags/'+tag+':refs/tags/'+tag],capture_output=True,text=True,encoding='utf-8');v=dict(kind='PHASE36_EXACT_FEATURE_AND_ANNOTATED_TRIAL_REMOTE_VERIFY_V1',epoch=time.time(),branch=branch,local_HEAD=head,tag=tag,annotated_tag_object=obj,push_returncode=p.returncode,push_stdout=redact(p.stdout)[0],push_stderr=redact(p.stderr)[0],main_pushed_reset_or_modified=False,model_raw_native_C_or_checkpoint_operations=0)
if p.returncode==0:
 rows=G('ls-remote','origin','refs/heads/'+branch,'refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main');remote={line.split()[1]:line.split()[0]for line in rows.splitlines()};v.update(remote_refs=remote,remote_feature_exact=remote.get('refs/heads/'+branch)==head,remote_annotated_tag_exact=remote.get('refs/tags/'+tag)==obj,remote_peeled_trial_exact=remote.get('refs/tags/'+tag+'^{}')==head,read_only_observed_remote_main=remote.get('refs/heads/main'),local_clean=not G('status','--porcelain'));v['verified']=all(v[k]for k in('remote_feature_exact','remote_annotated_tag_exact','remote_peeled_trial_exact','local_clean'))
else:v['verified']=False
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2));assert p.returncode==0 and v['verified']
