"""Resume existing validated phase3 record after Windows32767 argv bound, no new ID/tag."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parent;repo=Path(r'F:\RMPOLAR-RL\repo-lqr');record=repo/'history/experiments/20261102-mod4v1-full32-e0-restore-realppo-phase3.json';v=json.loads(record.read_text(encoding='utf-8'))
def git(*args):return subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
assert git('branch','--show-current')=='mod4v1-experts-fulldr-rm70' and not git('diff','--cached','--name-only') and not git('tag','--list',v['tag'])
for rel,expected in v['source_and_evidence_sha256'].items():assert hashlib.sha256((repo/rel).read_bytes()).hexdigest()==expected,rel
# Both directory paths are exactly the already-produced record/selected-source root.
git('add','--',record.relative_to(repo).as_posix(),'history/experiments/mod4v1_fulldr_phase3_sources')
staged=set(git('diff','--cached','--name-only').splitlines());expected=set(v['source_and_evidence_sha256'])|{record.relative_to(repo).as_posix()};assert staged==expected,(staged-expected,expected-staged)
git('commit','-m',v['title']+'\n\nExperiment: '+v['tag']+'\nValidation: '+v['validation']);git('tag','-a',v['tag'],'-m',v['title']+'\n\n'+v['repair_or_experiment_note'])
report={'kind':'GIT_PHASE3_EXISTING_RECORD_ARGV_RECOVERY','original_error':'record_experiment.py git add selected individual paths exceeded Windows command-line bound [WinError206]; record/sourcechecks succeeded beforegitadd; no commit/tag atfailure','fix':'Stage exacttwo alreadyvalidated record/source-directory paths, assertstagedset equals originalrecord hashes, same commit/title/uniqueannotatedtrial; no rerunrecord/experiment/canonical','source_entries':len(expected),'commit':git('rev-parse','HEAD'),'tag':v['tag'],'status':git('status','--porcelain'),'phase4_pending_report':True}
p=R/'reports/GIT_PHASE3_WIN206_EXISTING_RECORD_RECOVERY.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
