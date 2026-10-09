"""Record one actual isolated optimization result; binaries and large raw only SHA."""
from pathlib import Path
import sys,json,hashlib,time,subprocess,shutil
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
receipt=R/'PERFORMANCE_GIT_RECORDED.json';assert not receipt.exists()
v=json.loads((R/'PERFORMANCE_REVIEW.json').read_text(encoding='utf8'))
assert v['main_training_source_bytes_unchanged'] and not v['production_adopted'] and v['main_training_and_canonical_write_transactions']==0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==v['master_SHA_unchanged']
folder=REPO/'history/evidence/MOD4_D7_RESET_PERFORMANCE_3060_20261009';assert not folder.exists();folder.mkdir(parents=True)
files=[]
def cp(p,name):
 dst=folder/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);assert sha(dst)==sha(p);files.append(dst.relative_to(REPO).as_posix())
for p in D.glob('*.py'):cp(p,'implementation/'+p.name)
for name in ('PERFORMANCE_REVIEW.json','PERFORMANCE_REPORT.md','TARGET_CPU_PASSED.json','ACTUAL_SDK_ACCEPTED.json','SDK_PUBLISHED.json','ROTATION_READER_SDK_PUBLISHED.json','DEVICE_ALIGNED_SDK_PUBLISHED.json','COLLECTION_PACKAGES.json','COLLECTION_PUBLISHED.json'):
 cp(R/name,'reports/'+name)
cp(R/'PERFORMANCE_REPORT.md','EXPERIMENT_NOTE.md')
index={}
for folderraw in R.glob('clk*'):
 for p in folderraw.iterdir():
  if p.is_file():index[str(p.relative_to(D))]=dict(sha256=sha(p),bytes=p.stat().st_size)
(folder/'RAW_SHA_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8');files.append((folder/'RAW_SHA_INDEX.json').relative_to(REPO).as_posix())
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','d7-com-readback-optimized-3060-isolated-performance-reviewed',
    '--title','D7 COM readbacks optimized and actual 3060 isolated reset performance compared', '--kind','evaluation',
    '--note-file',str(folder/'EXPERIMENT_NOTE.md'),'--files',*files,
    '--validation','Target Torch2.10 CPU stale/cache/nonfinite/unselected faults; actual10env300control ABBA COM translation-privateRNG exact and original rotation-inertia contracts; actual paired80env1500control collection stress6000applycallbacks each group/parameters/gain-envelope; JSON bridge byteSHA; main277source untouched actualD7block2 continues; noPPO/canonicaltransaction; failedreader evidence retained; 20k4090 speed not inferred','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),indent=2),encoding='utf8')
 raise RuntimeError(p.stdout+'\n'+p.stderr)
def git(*a):return subprocess.check_output(['git','-C',str(REPO),*a],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
v=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,production_adopted=False,new_budget_seconds=0,master_SHA_unchanged=v['master_SHA_unchanged'])
receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
