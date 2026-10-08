"""Record one real D4 closeout and D5 fullscope deployment, excluding large artifacts."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
receipt=R/'D5_FULL_CONTRACT_GIT_RECORDED.json';assert not receipt.exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==MASTER
actual=read(R/'D5_FORMAL_OWN_SOURCE_VERIFIED.json');assert actual['PPO_iteration_log_count']>0 and actual['source_count']==255
folder=REPO/'history/evidence/MOD4_D5_FULL_CONTRACT_20261008';assert not folder.exists();folder.mkdir(parents=True)
files=[]
def copy(p,name):
 dest=folder/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert sha(p)==sha(dest)
 files.append(dest.relative_to(REPO).as_posix())
for p in sorted(D.glob('*.py')):copy(p,'implementation/'+p.name)
for p in sorted((D/'isaac/mod4').glob('*.py')):copy(p,'implementation/isaac/mod4/'+p.name)
for name in ('SOURCE_FREEZE.json','SOURCE_FREEZE_FIRST_PATH_REJECTED.json','STAGED_D5_FULL_CONTRACT.json','LOCAL_FULL_CONTRACT_BUILT.json',
 'SPRING_CHECKPOINT_CPU_PASSED.json','SPRING_PRESSURE_CPU_PASSED.json','SPRING_PRESSURE_ADAPTER_CPU_PASSED.json',
 'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json','SELECTED_D4_BEHAVIOR_SOURCE.json','D5_LAUNCHED.json',
 'D5_CURRENT_ACTUAL.json','D5_FORMAL_OWN_SOURCE_VERIFIED.json','D5_FROZEN_BEHAVIOR_PACKAGES.json','D5_CLOSEDLOOP_PACKAGE_PUBLISHED.json',
 'D5_STAGE_PATH_FIRST_ERROR.json','D5_PACKAGE_FIRST_PATH_ERROR.json','D5_PACKAGE_ALIAS_READER_ERROR.json','D5_FORMAL_FIRST_READER_ERRORS.json',
 'D4_CLOSEOUT_D5_FORMAL_REVIEW.json','D4_CLOSEOUT_D5_FORMAL_REPORT.md','MOD4_D4_CHECKPOINT_INDEX.json','NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json'):
 copy(R/name,'reports/'+name)
W=D.parent/'MOD4_D4_WORLD_DISPATCH_REVIEW_20261008';F=D.parent/'MOD4_D4_FULL_CONTRACT_20261008'
for name in ('collect_later_d4_scope.py','review_later_d4_scope.py'):copy(W/name,'D4_review/'+name)
for name in ('LATER_D4_SCOPE_FILES.json','D4_LATER_BLOCKS_MATCHED_REVIEW.json'):copy(W/'reports'/name,'D4_review/'+name)
copy(F/'reports/D4_BLOCKS_ACTUAL_VERIFIED.json','D4_review/D4_BLOCKS_ACTUAL_VERIFIED.json')
copy(D.parent/'MOD4_D5_SPRING_LAW_PREPARE_20261008/reports/PRESSURE_WORKER_CURRENT_ACTUAL.json','reports/PRESSURE_WORKER_CURRENT_ACTUAL.json')
for name in ('MOD4_S2_D5_SPRING_STIFFNESS_PRESSURE.json','MOD4_S2_D5_SPRING_STIFFNESS_PRESSURE.md'):files.append('history/plans/'+name)
note=folder/'EXPERIMENT_NOTE.md';note.write_text((R/'D4_CLOSEOUT_D5_FORMAL_REPORT.md').read_text(encoding='utf8'),encoding='utf8');files.append(note.relative_to(REPO).as_posix())
ident='d4-model29690-matched-sixhour-closeout-and-d5-full-ppo-stable-training'
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ident,'--title',
  'Complete D4 window, select behavior-reviewed29690 and deploy full D5 stiffness-pressure learning','--kind','deployment',
 '--note-file',str(note),'--files',*files,'--validation',
 'D4 own243-source/CPU88/24snapshots; matched trueworld64/64; D5 native20k and128x2/20kx4 completePPO discarded; actual formalCPU89/255source/31snapshots; CUDA full-state startup; samecanonical; immutable trueD5 package','--push']
run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if run.returncode:
 (R/'D5_GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=run.stdout,stderr=run.stderr,returncode=run.returncode,do_not_repeat_record=True),indent=2),encoding='utf8')
 raise RuntimeError(run.stdout+'\n'+run.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=run.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
v=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,
 evidence_folder=str(folder),master_plan_SHA_unchanged=MASTER,new_budget_seconds=0,weights_raw_USD_indexed_only=True)
receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
