"""One actual stage/SDK/evaluator repair archive; no binary checkpoints or raw probes."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train';F=D.parent/'MOD4_D5_FULL_CONTRACT_20261008'
receipt=R/'D5_BLOCK1_D6_ATOMIC_GIT_RECORDED.json';assert not receipt.exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b';assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==MASTER
assert read(R/'ATOMIC_RETRY_WORKER_CURRENT_ACTUAL.json')['current_attention'] is None
assert read(R/'D6_NOMINAL_ACTUAL_JOINT_SDK_REVIEW.json')['SDK_read_only_parameter_scope_accepted']
folder=REPO/'history/evidence/MOD4_D5_STAGE_D6_READBACK_ATOMIC_REPAIR_20261008';assert not folder.exists();folder.mkdir(parents=True)
files=[]
def copy(path,name):
 dest=folder/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest);assert sha(path)==sha(dest);files.append(dest.relative_to(REPO).as_posix())
for p in sorted(D.glob('*.py')):copy(p,'implementation/'+p.name)
for name in ('D6_NOMINAL_SOURCE_SUMMARY.json','GAS_DAMPING_CPU_PASSED.json','GAS_DAMPING_CPU_STAGED.json','D6_NOMINAL_JOINT_SDK_PUBLISHED.json',
 'D6_NOMINAL_JOINT_SDK_CURRENT.json','D6_NOMINAL_ACTUAL_JOINT_SDK_REVIEW.json','D6_KERNEL_READER_FIRST_PATH_ERROR.json','D6_REVIEW_FIRST_SCHEMA_ERROR.json',
 'EVALUATOR_ATOMIC_WRITE_ACTUAL_FAULT.json','ATOMIC_RETRY_CPU_PASSED.json','ATOMIC_RETRY_WORKER_ADMITTED.json','ATOMIC_RETRY_WORKER_CURRENT_ACTUAL.json',
 'NATIVE_WINDOWS_RECEIPT_SHARING_PASSED.json','D5_BLOCK1_D6_SOURCE_AND_EVALUATOR_REPAIR_REVIEW.json','D5_BLOCK1_D6_SOURCE_AND_EVALUATOR_REPAIR_REPORT.md','NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json'):
 copy(R/name,'reports/'+name)
for name in ('collect_d5_scope.py','review_d5_scope.py','read_verified_d5_blocks.py'):copy(F/name,'D5_readers/'+name)
for name in ('D5_BLOCKS_ACTUAL_VERIFIED.json','D5_COMPLETED_SCOPE_FILES.json','D5_ACTUAL_BASELINE_SCOPE_REVIEW.json'):copy(F/'reports'/name,'D5_reports/'+name)
note=folder/'EXPERIMENT_NOTE.md';copy(R/'D5_BLOCK1_D6_SOURCE_AND_EVALUATOR_REPAIR_REPORT.md','EXPERIMENT_NOTE.md')
ident='d5-model30649-stage-d6-joint-readback-and-eval-atomic-repaired'
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ident,'--title',
 'D5 first2h and fullstate continuation, D6 actual joint readback and evaluator sharing retry repair','--kind','repair','--note-file',str(note),
 '--files',*files,'--validation','OwnCPU89/source255/31snapshots and960updates verified; pairedD5 baseline and candidateflat; actualD6 read-only1200callbacks and9CPU; Windows sharing fault injection/native retry; old eval exited and new single-GPU demand worker verified; no4090 runtime or budget mutation','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'D5_D6_ATOMIC_GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=p.stdout,stderr=p.stderr,returncode=p.returncode,do_not_repeat_record=True),indent=2),encoding='utf8');raise RuntimeError(p.stdout+'\n'+p.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
v=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,master_SHA_unchanged=MASTER,new_budget_seconds=0,evidence_folder=str(folder),weights_large_raw_USD_only_SHA_indexed=True)
receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
