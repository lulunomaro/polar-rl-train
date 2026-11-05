"""Archive only this read-only D0 fact check; no asset, model, SDK or old-trial replay."""
from pathlib import Path
import sys,json,hashlib,subprocess,time
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v1_d0_joint_limit_origin_facts_20261105');dest=repo/rel

def G(*args):
 p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists();G('merge-base','--is-ancestor','8ab03d34e9111aab9b7baa412b0bcc61ed6f24f6','HEAD')
facts=json.loads((D/'D0_LIMIT_ORIGIN_FACTCHECK_V1.json').read_bytes());assert facts['fix_executed']is False and facts['asset_or_runtime_or_checkpoint_or_Registry_modified']is False and facts['training_dynamics_SDK_GUI_GPU_started']is False and facts['v1_production']['joint_limits_changed_by_enhancement']is False
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
from capture_history import redact
dest.mkdir(parents=True);files=[];index=[]
for name in('D0_LIMIT_ORIGIN_FACTCHECK_V1.md','D0_LIMIT_ORIGIN_FACTCHECK_V1.json',Path(__file__).name):
 p=D/name;raw=p.read_bytes();text,count=redact(raw.decode('utf8'));data=text.encode('utf8');target=dest/name;target.write_bytes(data);rp=target.relative_to(repo).as_posix();files.append(rp);index.append(dict(source=str(p),original_bytes=len(raw),original_SHA256=hashlib.sha256(raw).hexdigest(),archive=rp,archive_bytes=len(data),archive_SHA256=hashlib.sha256(data).hexdigest(),redactions=count))
(dest/'INDEX.json').write_text(json.dumps(dict(rows=index,all_new_fact_reports_included=True,original_assets_known_identity_references_only=True,assets_or_PT_or_raw_opened_for_Git=False,repair_or_training_executed=False),indent=2),encoding='utf8');files.append((rel/'INDEX.json').as_posix())
trial='mod4v1-d0-joint-limits-origin-facts';note=dest/'D0_LIMIT_ORIGIN_FACTCHECK_V1.md';sys.argv=['record_experiment.py','--id',trial,'--title','MOD4v1 D0 joint limits origin: inherited operating bounds and gas upper wrapper narrowing; no asset edits','--kind','diagnostic','--note-file',str(note),'--validation','source-build-receipt-and-original-unchanged-static-check-recovered;baseline-wrapper-explicit-gas-upper-override-and-current-USD-MJCF-finite-limits-readonly;conditional-kinematics-screenshot-match-rightgas-upper8.1539mm;old-vs-current-MJCF-separated;early-operating-envelope-vs-one-sided-CAD-stop-and-50um-margin-separated;exactUI-and-hard-stop-qualification-gaps-honest;no-assets-checkpoints-Registry-training-SDK-GPU-or-budget-edits;original-recorder-validation-redaction-hashes;feature-only-mainreadonly','--files',*files]
record_experiment.main();head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,new_reports_and_source_entries=len(index),original_recorder_validation_redaction_hashes_retained=True,assets_models_raw_or_old_once_replayed_for_Git=False,repair_or_training_started=False,main_push_or_reset=False),indent=2))
