"""Archive one actual closeout/newscope deployment. Explicit files, no binary artifacts."""
from pathlib import Path
import json,time,subprocess,shutil,sys,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train';F=D.parent/'MOD4_D5_FULL_CONTRACT_20261008'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=R/'D6_FULL_CONTRACT_GIT_RECORDED.json';assert not receipt.exists()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b';assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==MASTER
assert read(R/'D5_CLOSEOUT_D6_FORMAL_REVIEW.json')['D6_actual_formal']['current']['PPO_log_updates']>0
folder=REPO/'history/evidence/MOD4_D5_CLOSEOUT_D6_GAS_FULL_DEPLOYMENT_20261009';assert not folder.exists();folder.mkdir(parents=True);files=[]
def cp(p,name):
 target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);assert sha(p)==sha(target);files.append(target.relative_to(REPO).as_posix())
for p in (D/'isaac/mod4').glob('*.py'):cp(p,'implementation/isaac/mod4/'+p.name)
for p in D.glob('*.py'):cp(p,'implementation/'+p.name)
for n in ('SOURCE_FREEZE.json','D6_FULL_TARGET_CPU_PASSED.json','STAGED_D6_FULL_CONTRACT.json','D6_LAUNCHED.json','D6_INSTALL_BOUNDARY.json','D6_NATIVE20K_PASSED.json','D6_COMPLETE_PPO_PREFLIGHT_PASSED.json','D6_CURRENT_ACTUAL.json','SELECTED_D5_BEHAVIOR_SOURCE.json','D6_CLOSEDLOOP_PACKAGE_PUBLISHED.json','D6_FROZEN_BEHAVIOR_PACKAGES.json','D5_CLOSEOUT_D6_FORMAL_REVIEW.json','D5_CLOSEOUT_D6_FORMAL_REPORT.md','D5_FULL_RETENTION_PUBLISHED.json','NOMINAL_SCOPE_REVIEW_WORKER_ADMITTED.json','D6_EVALUATOR_POST_PUBLICATION_ACTUAL.json','NOMINAL_SCOPE_PACKAGE_PUBLISHED.json','NOMINAL_PACKAGE_INDEPENDENT_CPU_REVIEW.json','NOMINAL_PUBLICATION_LAUNCHED.json','NEXT_D7_COM_PD_WORK_ORDER.json','D7_FROZEN_SOURCE_READ_ONLY.json'):cp(R/n,'reports/'+n)
cp(F/'reports/D5_BLOCKS_ACTUAL_VERIFIED.json','D5_reports/D5_BLOCKS_ACTUAL_VERIFIED.json');cp(F/'reports/D5_MODEL30649_MATCHED_REVIEW.json','D5_reports/D5_LATER_MATCHED_SCOPE_REVIEW.json')
cp(R/'D5_CLOSEOUT_D6_FORMAL_REPORT.md','EXPERIMENT_NOTE.md');files.append('history/plans/MOD4_S2_D6_GAS_DAMPING_IMPLEMENTATION.json')
args=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','d5-saved-closeout-d6-gas-full-ppo-parallel-stable-deployed','--title','D5 saved closeout, D6 gas damping full PPO and parallel stable training deployed','--kind','deployment','--note-file',str(folder/'EXPERIMENT_NOTE.md'),'--files',*files,'--validation','D5 three own CPU89/source255 full saves,276960 exact callbacks and three uniquely settled segments; isolated265 source/predecessor255 exact; priorCPU13+10/SDK reused; native20k576 callbacks and two fullPPO6144/1920000 steps discarded uniquely charged; actual CUDA gas/full optimizer streams restore and own formal CPU90/source/snapshot/PID proof; frozen three correct dispatchers, evaluator real exit-lock-task safe repair; nominal AST exact and SDK conditional publication pending, not graduation','--push']
p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'D6_GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),indent=2));raise RuntimeError(p.stdout+'\n'+p.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag);remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
v=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,master_SHA_unchanged=MASTER,new_budget_seconds=0,evidence_folder=str(folder),weights_large_raw_USD_only_SHA_indexed=True)
receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
