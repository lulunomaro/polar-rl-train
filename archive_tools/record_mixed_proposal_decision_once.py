"""Archive human choice to continue the approved plan, no training action."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
P=Path(__file__).resolve().parents[1];E=P/'history/evidence/MOD4_E1_MIXED20K_FEASIBILITY_20261009'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True,encoding='utf8').strip()
ID='mixed20k-proposal-not-adopted-approved-staged-plan-continued';tag='trial-'+time.strftime('%Y%m%d')+'-'+ID
assert not git('tag','--list',tag),'Already recorded; do not repeat'
m=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
assert m['status']=='ACTIVE' and m['rrule']=='FREQ=HOURLY;INTERVAL=2' and '按照原计划走吧' in m['prompt'][:150]
assert '\ufffd' not in m['prompt']
f=E/'HUMAN_DECISION_PLAN_CONTINUED.json';assert not f.exists()
v=dict(epoch=time.time(),human_request='按照原计划走吧',mixed_allocation_proposal_adopted=False,mixed_allocation_proposal_ever_deployed=False,
 current_existing_gentle_mix_unchanged=True,continue_approved_staged_plan=True,RM_curriculum_revision003_preserved=True,
 monitor_status=m['status'],monitor_rrule=m['rrule'],monitor_prompt_sha256=hashlib.sha256(m['prompt'].encode('utf8')).hexdigest(),
 master_sha256_unchanged='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',
 production_runtime_GPU_PPO_canonical_writes=0,new_budget_seconds=0,not_physical_or_training_failure=True)
f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
files=[(E/n).relative_to(P).as_posix() for n in ['HUMAN_DECISION_PLAN_CONTINUED.md','HUMAN_DECISION_PLAN_CONTINUED.json']]+['archive_tools/record_mixed_proposal_decision_once.py']
cmd=[sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Record human choice to keep approved staged training and leave mixed20k proposal unadopted','--kind','rejected',
 '--note-file',str(E/'HUMAN_DECISION_PLAN_CONTINUED.md'),'--files',*files,'--validation','Human directive preserved; proposal never deployed; monitor2h ACTIVE and UTF8 verified; previous RM revision retained; no training/runtime/GPU/PPO/canonical operation','--push']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if r.returncode:
 (E/'HUMAN_DECISION_RECORD_FAILED.json').write_text(json.dumps(dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,do_not_repeat_record=True),ensure_ascii=False,indent=2),encoding='utf8')
 raise RuntimeError('Archive failed; inspect existing objects before retry')
tag,head=r.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
print(json.dumps(dict(tag=tag,commit=head,remote_main_tag_peeled_verified=True,push_pending=False,approved_plan_continued=True,mixed_proposal_adopted=False,new_budget_seconds=0),ensure_ascii=True))
