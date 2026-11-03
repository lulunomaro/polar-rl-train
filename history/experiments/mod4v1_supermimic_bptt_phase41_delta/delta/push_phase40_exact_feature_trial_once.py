"""Push only this feature and one annotated trial; inspect main read-only."""
from pathlib import Path
import argparse,json,re,subprocess,time
R=Path(__file__).resolve().parent;repo=R.parent/'repo-lqr';out=R/'reports/PHASE40_FEATURE_AND_ANNOTATED_TRIAL_REMOTE_VERIFY_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE40_FEATURE_TAG_PUSH_STARTED_ONCE.json';p=argparse.ArgumentParser();p.add_argument('--expected-head',required=True);a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.expected_head)and not out.exists()and not marker.exists();branch='mod4v1-experts-fulldr-rm70';tag='trial-20261104-mod4v1-supermimic-phase1-b4-cpu-good-static-stage-phase40'
def g(*x):return subprocess.run(['git','-C',str(repo),*x],check=True,capture_output=True,text=True,encoding='utf8').stdout.strip()
assert g('branch','--show-current')==branch and g('rev-parse','HEAD')==a.expected_head and not g('status','--porcelain');assert g('cat-file','-t','refs/tags/'+tag)=='tag'and g('rev-parse','refs/tags/'+tag+'^{}')==a.expected_head;obj=g('rev-parse','refs/tags/'+tag)
with marker.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),feature=branch,head=a.expected_head,tag=tag,tag_object=obj,push_refs_only=[branch,tag],main_operation='READ_ONLY_LS_REMOTE'),f,indent=2)
push=subprocess.run(['git','-C',str(repo),'push','--atomic','origin','HEAD:refs/heads/'+branch,'refs/tags/'+tag+':refs/tags/'+tag],capture_output=True,text=True,encoding='utf8');assert push.returncode==0,push.stderr
remote={ref:sha for sha,ref in(x.split()for x in g('ls-remote','origin','refs/heads/'+branch,'refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/'+branch]==a.expected_head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==a.expected_head and not g('status','--porcelain')
v=dict(kind='EXACT_FEATURE_ANNOTATED_TRIAL_ATOMIC_PUSH_REMOTE_VERIFIED_PHASE40',epoch=time.time(),feature=branch,commit=a.expected_head,tag=tag,tag_object=obj,remote=remote,main_readonly_independently_advancing=True,main_push_or_reset=False,working_tree_clean=True,push_stdout=push.stdout,push_stderr=push.stderr,model_raw_native_CPU_C_or_resource_operations=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
