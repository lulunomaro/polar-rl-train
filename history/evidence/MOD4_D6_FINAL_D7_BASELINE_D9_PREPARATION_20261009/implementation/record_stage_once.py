"""Archive one actual stage scope/preparation, binary and large raw only SHA indexed."""
from pathlib import Path
import json,time,subprocess,shutil,sys,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train';read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=R/'D6_FINAL_D7_BASELINE_D9_GIT_RECORDED.json';assert not receipt.exists()
v=read(R/'D6_FINAL_D7_BASELINE_D9_PREPARATION_REVIEW.json');assert v['master_SHA_unchanged']==sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')
folder=REPO/'history/evidence/MOD4_D6_FINAL_D7_BASELINE_D9_PREPARATION_20261009';assert not folder.exists();folder.mkdir(parents=True);files=[]
def cp(p,name):
 target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);assert sha(p)==sha(target);files.append(target.relative_to(REPO).as_posix())
a=v['D7_actual_formal'];cur=a['current'];start=cur['chassis_PD_startup'];pub=v['D9_publication_actual']
compact=dict(epoch=v['epoch'],master_SHA_unchanged=v['master_SHA_unchanged'],D6_final=v['D6_final_model32950_actual_paired_review'],D7_baseline=v['D7_baseline_actual_scope'],D7_candidate_pending=True,D7_actual_owner=a['actual_owner'],D7_actual_guardian=a['actual_guardian'],D7_actual_child=a['actual_child'],own_run=cur['run'],own_checkpoint=cur['checkpoint'],own_receipt=cur['receipt'],snapshot_count=cur['snapshot_count'],startup={k:x for k,x in start.items() if k!='actual_chassis_PD_audit'},live_health=cur['live_health'],live_health_not_final=True,publisher=pub['actual_publisher'],publisher_phase=pub['reports']['REVIEW_STATE.json'],nominal_SDK=pub['reports']['D9_NOMINAL_ACTUAL_SDK_REVIEW.json'],new_PPO_learning_canonical_transactions=0,remaining_seconds_snapshot=a['actual_tail_adjusted_remaining_seconds'],RM_annotation_ref=v['RM_terrain_annotation_ref'],large_source_evidence_SHA={str(p.relative_to(D.parent)):sha(p) for p in (R/'D6_FINAL_D7_BASELINE_D9_PREPARATION_REVIEW.json',D.parent/'MOD4_D6_FULL_CONTRACT_20261009/reports/D6_ACTUAL_BASELINE_SCOPE_REVIEW.json',D.parent/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_ACTUAL_BASELINE_SCOPE_REVIEW.json',R/'nominal_sdk/probe.json',R/'nominal_sdk/result.json')})
(R/'D6_FINAL_D7_BASELINE_D9_COMPACT.json').write_text(json.dumps(compact,indent=2),encoding='utf8')
for p in D.glob('*.py'):cp(p,'implementation/'+p.name)
for name in ('D6_FINAL_D7_BASELINE_D9_COMPACT.json','D6_FINAL_D7_BASELINE_D9_PREPARATION_REPORT.md','D9_ACTUAL_COMBINATION_ASSIGNMENT_AUDIT.json','D9_NOMINAL_INTERFACE_PUBLISHED.json','D9_NOMINAL_ACTUAL_SDK_REVIEW.json','D9_PUBLICATION_LAUNCHED.json','D9_RESET_REVIEW_LAUNCHED.json','D9_FIRST_PUBLICATION_ATTENTION.json','REVIEW_STARTED.json','REVIEW_STATE.json'):
 cp(R/name,'reports/'+name)
cp(R/'D6_FINAL_D7_BASELINE_D9_PREPARATION_REPORT.md','EXPERIMENT_NOTE.md')
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','d6-final-retention-d7-baseline-and-d9-nominal-combination-prepared','--title','D6 final retention D7 actual COM-PD baseline and D9 nominal development publication prepared','--kind','deployment','--note-file',str(folder/'EXPERIMENT_NOTE.md'),'--files',*files,'--validation','D6 final three same-platform fullpaired cases and JSON bridge byteSHA; D7 baseline actual complete COM-PD/old-group readbacks and full signed circles; active ownCPU94/source277/44snapshots/PID receipt; nominal lifecycle whiteASTexact actual10env300control noD0draw eachaction1200callback; distinct CPU selected-reset reader actualprocess waiting explicit ownpaired source before15new+3exactreuse cases; oldreadererror retained; productionGPU/PPO/canonical0; masterSHA and RM annotations preserved','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),indent=2),encoding='utf8');raise RuntimeError(p.stdout+'\n'+p.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag);remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
g=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,master_SHA_unchanged=v['master_SHA_unchanged'],new_budget_seconds=0,weights_large_raw_USD_only_SHA_indexed=True)
receipt.write_text(json.dumps(g,indent=2),encoding='utf8');print(json.dumps(g))
