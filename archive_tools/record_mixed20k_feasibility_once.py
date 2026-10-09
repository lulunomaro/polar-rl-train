"""Archive a read-only mixed-terrain feasibility opinion; never deploy training."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
REPO=Path(__file__).resolve().parents[1];W=REPO.parent;E=REPO/'history/evidence/MOD4_E1_MIXED20K_FEASIBILITY_20261009'
def git(*a):return subprocess.check_output(['git','-C',str(REPO),*a],text=True,encoding='utf8').strip()
ID='e1-total20k-mixed-terrain-feasibility-and-efficiency-reviewed';tag='trial-'+time.strftime('%Y%m%d')+'-'+ID
assert not git('tag','--list',tag),'Already recorded; do not repeat'
v=json.loads((W/'MOD4_E1_GRADUATION_ESTIMATE_20261009/reports/E1_ETA_ACTUAL.json').read_text(encoding='utf8'))
p=W/'MOD4_D9_COMBINATION_PREPARE_20261009/reports/e1_verified_source_bytes/rough_recipe.py'
h=hashlib.sha256(p.read_bytes()).hexdigest();assert v['own_run']['manifest']['source_map']['isaac/mod4/e1_rough_recipe.py']==h
paths=['rough_recipe.py','rough_intro_runtime.py','rough_intro_reset.py'];references={}
for n in paths:
 q=p.parent/n;references[n]=dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),role='previously_verified_shared_source_configuration; runtime deployment not changed')
proof=dict(read_only_feasibility=True,human_request='Can total20000 environments mix multiple terrains and improve efficiency? Give an opinion.',
 actual_recipe_byte_SHA_verified=True,source_refs=references,actual_observation_report='history/evidence/MOD4_E1_GRADUATION_ESTIMATE_20261009/E1_ETA_ACTUAL.json',
 illustrative_allocation=[14000,4000,2000],allocation_not_deployed=True,no_measured_mixed_distribution_speedup=True,
 primary_sources=['https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.terrains.html','https://isaac-sim.github.io/IsaacLab/main/source/how-to/simulation_performance.html'],
 local_source_lookup_missing_313_isaac_directory=True,fallback_verified_shared_recipe=True,production_runtime_GPU_PPO_canonical_writes=0,new_budget_seconds=0)
q=E/'EVIDENCE.json';assert not q.exists();q.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
files=[(E/n).relative_to(REPO).as_posix() for n in ['REPORT.md','EVIDENCE.json']]+['archive_tools/record_mixed20k_feasibility_once.py']
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review total20k mixed-terrain feasibility and distinguish throughput from learning efficiency','--kind','diagnostic',
 '--note-file',str(E/'REPORT.md'),'--files',*files,'--validation','Existing mixed gentle recipe byte SHA matches own manifest; official terrain/performance API read; illustrative allocation sums20000; no mixed A/B run or production change; saved report and evidence included','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (E/'RECORD_FAILED.json').write_text(json.dumps(dict(stdout=p.stdout,stderr=p.stderr,returncode=p.returncode,do_not_repeat_record=True),ensure_ascii=False,indent=2),encoding='utf8')
 raise RuntimeError('Archive failed; inspect existing objects before retry')
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
print(json.dumps(dict(tag=tag,commit=head,remote_main_tag_peeled_verified=True,push_pending=False,opinion_only_not_deployed=True,new_budget_seconds=0),ensure_ascii=True))
