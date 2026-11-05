"""Archive only this read-only D0 fact check; no asset, model, SDK or old-trial replay."""
from pathlib import Path
import sys,json,hashlib,subprocess,time
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v1_d0_scut_mechanism_comparison_20261105');dest=repo/rel

def G(*args):
 p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists();G('merge-base','--is-ancestor','cdf3d2ba9d0065119b61e90f0677584ff404d2f5','HEAD')
facts=json.loads((D/'D0_SCUT_MECHANISM_COMPARISON_V1.json').read_bytes());assert facts['repair_asset_runtime_or_training_executed']is False and facts['Registry_models_budget_modified']is False and facts['source_identity']['physics_runtime_tested']is False and facts['MOD4_both_sides']['hip_rad']==[-.5,.5]and facts['SCUT_both_sides']['front1_joint_active_degree']==['-inf','inf']
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
from capture_history import redact
dest.mkdir(parents=True);files=[];index=[]
for name in('D0_SCUT_MECHANISM_COMPARISON_V1.md','D0_SCUT_MECHANISM_COMPARISON_V1.json','prepare_comparison_archive_once.py',Path(__file__).name):
 p=D/name;raw=p.read_bytes();text,count=redact(raw.decode('utf8'));data=text.encode('utf8');target=dest/name;target.write_bytes(data);rp=target.relative_to(repo).as_posix();files.append(rp);index.append(dict(source=str(p),original_bytes=len(raw),original_SHA256=hashlib.sha256(raw).hexdigest(),archive=rp,archive_bytes=len(data),archive_SHA256=hashlib.sha256(data).hexdigest(),redactions=count))
(dest/'INDEX.json').write_text(json.dumps(dict(rows=index,all_new_fact_reports_included=True,original_assets_known_identity_references_only=True,assets_or_PT_or_raw_opened_for_Git=False,repair_or_training_executed=False),indent=2),encoding='utf8');files.append((rel/'INDEX.json').as_posix())
trial='mod4v1-d0-scut-mechanism-comparison';note=dest/'D0_SCUT_MECHANISM_COMPARISON_V1.md';sys.argv=['record_experiment.py','--id',trial,'--title','SCUT continuous leg axes versus MOD4 active hard envelope and stop-contact filtering; read-only D0 comparison','--kind','diagnostic','--note-file',str(note),'--validation','actual-static-SCUT-root-and-linked-physics-payload-identity;four-active-leg-axes-author-infinite-passive-and-slider-finite;MOD4-active-and-follower-finite-range-topology-not-extraDOF;both-six-ball-excluded-tree-not-disabled;actualMOD4-stop-mesh-noCollisionAPI-and-threebody-pairfiltered;CAD145-fixed-to-thigh-not-world;operating-vs-mechanical-and-gas-force-stroke-separated;runtime-default-target-projection-not-live-override-claim;no-asset-runtime-PT-training-SDK-GPU-budget-or-main-modification;original-recorder-validation-redaction-hashes;feature-only-atomic-tag-remoteverification','--files',*files]
record_experiment.main();head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,new_reports_and_source_entries=len(index),original_recorder_validation_redaction_hashes_retained=True,assets_models_raw_or_old_once_replayed_for_Git=False,repair_or_training_started=False,main_push_or_reset=False),indent=2))
