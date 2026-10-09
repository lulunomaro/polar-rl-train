from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';G=W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads(sorted(R.glob('ACTUAL_COLLECTED_*.json'))[-1].read_bytes());assert 'Source outside artifact allowlist' in v['current_attention']['error'] and v['processes']==[]
m=json.loads((R/'MANIFEST_TEMPLATE.json').read_bytes());sel=json.loads((R/'SELECTED_E1_NEXT_GEOMETRY_BEHAVIOR_SOURCE.json').read_bytes());assert m['artifacts']['checkpoint']['sha256']==sel['source']['sha256']
bad='clk2500-closure-episode-d3-121-e1-g2-20mm-source32053-fullroute-flat'
s=(G/'eval_worker_e1_full_route_review.py').read_text(encoding='utf8').replace('E1_FULL_ROUTE_REVIEW','E1_ARTIFACT_SOURCE_REVIEW')
s=s.replace('PAUSED_SHALLOW_JOBS=',"RETIRED=RETIRED+("+repr(bad)+",)\nPAUSED_SHALLOW_JOBS=");ast.parse(s);(D/'eval_worker_e1_artifact_source_review.py').write_text(s,encoding='utf8')
expected=dict(epoch=time.time(),new_source_sha256=H((D/'eval_worker_e1_artifact_source_review.py').read_bytes()),old_fullroute_source_sha256=H((G/'eval_worker_e1_full_route_review.py').read_bytes()),only_namespace_and_exact121_rejection_exclusion_changed=True,original_guard_unchanged=True)
(R/'ARTIFACT_WORKER_EXPECTED.json').write_text(json.dumps(expected,indent=2),encoding='utf8')
s=(G/'admit_e1_full_route_review_once.py').read_text(encoding='utf8')
start=s.index(" assert hashlib.sha256((D/'eval_worker_e1_curriculum_interface_review.py')");end=s.index(' actual=ps(',start)
block=""" expected=read(D/'E1_ARTIFACT_WORKER_EXPECTED.json')
 assert hashlib.sha256((D/'eval_worker_e1_full_route_review.py').read_bytes()).hexdigest()==expected['old_fullroute_source_sha256']
 assert hashlib.sha256((D/'eval_worker_e1_artifact_source_review.py').read_bytes()).hexdigest()==expected['new_source_sha256']
 fault=read(D/'E1_FULL_ROUTE_REVIEW_WORKER_ATTENTION.json');assert 'Source outside artifact allowlist' in fault['error']
 jid='clk2500-closure-episode-d3-121-e1-g2-20mm-source32053-fullroute-flat';folder=D/'jobs'/jid
 manifest=read(folder/'manifest.json');assert '/learning_logs/' in manifest['artifacts']['checkpoint']['path']
 assert not (folder/'result.json').exists() and not (folder/'probe.json').exists()
 failed=dict(phase='artifact_transport_rejected_before_GPU',job_id=jid,original_manifest=manifest,original_attention=fault)
"""
s=s[:start]+block+s[end:]
s=s.replace('E1_FULL_ROUTE_REVIEW_WORKER_ADMISSION','E1_ARTIFACT_SOURCE_REVIEW_WORKER_ADMISSION').replace('admit_e1_full_route_review_once.py','admit_e1_artifact_source_review_once.py')
s=s.replace("old='MOD4_AsyncFrozenEvaluation_v15_e1_curriculum_interface_review'","old='MOD4_AsyncFrozenEvaluation_v15_e1_full_route_review'")
s=s.replace('OLD_E1_CURRICULUM_TASK_BEFORE_FULL_ROUTE.xml','OLD_FULL_ROUTE_TASK_BEFORE_ARTIFACT_SOURCE.xml').replace("exclusion_of119_is_failure_and_neverrun_not_pass=True","exclusion_of121_is_transport_rejection_before_GPU_not_pass=True")
s=s.replace("$name='MOD4_AsyncFrozenEvaluation_v15_e1_full_route_review'","$name='MOD4_AsyncFrozenEvaluation_v15_e1_artifact_source_review'").replace("\\eval_worker_e1_full_route_review.py'","\\eval_worker_e1_artifact_source_review.py'")
s=s.replace('E1_FULL_ROUTE_REVIEW_WORKER_STARTED','E1_ARTIFACT_SOURCE_REVIEW_WORKER_STARTED').replace('E1_FULL_ROUTE_REVIEW_WORKER_ATTENTION','E1_ARTIFACT_SOURCE_REVIEW_WORKER_ATTENTION')
# The previous worker attention is the rejection evidence; do not replace this reference.
s=s.replace("fault=read(D/'E1_ARTIFACT_SOURCE_REVIEW_WORKER_ATTENTION.json')","fault=read(D/'E1_FULL_ROUTE_REVIEW_WORKER_ATTENTION.json')")
s=s.replace('E1_FULL_ROUTE_REVIEW_TASK.xml','E1_ARTIFACT_SOURCE_REVIEW_TASK.xml').replace('E1_FULL_ROUTE_REVIEW_WORKER_ADMITTED','E1_ARTIFACT_SOURCE_REVIEW_WORKER_ADMITTED')
ast.parse(s);(D/'admit_e1_artifact_source_review_once.py').write_text(s,encoding='utf8')
s=(G/'deploy_route_worker_once.py').read_text(encoding='utf8').replace('ROUTE_WORKER_DEPLOY','ARTIFACT_WORKER_DEPLOY').replace('eval_worker_e1_full_route_review.py','eval_worker_e1_artifact_source_review.py').replace('admit_e1_full_route_review_once.py','admit_e1_artifact_source_review_once.py').replace('ROUTE_WORKER_CPU_PREPARED.json','ARTIFACT_WORKER_EXPECTED.json').replace('E1_FULL_ROUTE_WORKER_EXPECTED.json','E1_ARTIFACT_WORKER_EXPECTED.json').replace('E1_FULL_ROUTE_REVIEW_WORKER_','E1_ARTIFACT_SOURCE_REVIEW_WORKER_').replace('OLD_E1_CURRICULUM_TASK_BEFORE_FULL_ROUTE.xml','OLD_FULL_ROUTE_TASK_BEFORE_ARTIFACT_SOURCE.xml').replace('E1_FULL_ROUTE_REVIEW_TASK.xml','E1_ARTIFACT_SOURCE_REVIEW_TASK.xml')
ast.parse(s);(D/'deploy_artifact_worker_once.py').write_text(s,encoding='utf8')
s=(D/'publish20mm_once.py').read_text(encoding='utf8').replace('PUBLISH_STARTED','REPAIRED_PUBLISH_STARTED').replace('PUBLISH_ERROR','REPAIRED_PUBLISH_ERROR').replace("R/'PUBLISHED.json'","R/'REPAIRED_PUBLISHED.json'").replace('FROZEN-PUBLISH-01','ALLOWLIST-PUBLISH-02').replace('d3-121-','d3-122-').replace('E1_FULL_ROUTE_REVIEW_WORKER','E1_ARTIFACT_SOURCE_REVIEW_WORKER').replace('eval_worker_e1_full_route_review.py','eval_worker_e1_artifact_source_review.py')
s=s.replace("(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010/eval_worker_e1_artifact_source_review.py').read_bytes()","(D/'eval_worker_e1_artifact_source_review.py').read_bytes()")
s=s.replace("m['artifacts']['checkpoint']=source;raw=", "assert m['artifacts']['checkpoint']['sha256']==source['sha256'];assert H(nf.open(m['artifacts']['checkpoint']['path']).read())==source['sha256'];raw=")
s=s.replace("nf.put(pkg['path'],remote+'.partial');assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)","assert H(nf.open(remote).read())==pkg['sha256'] # reuse already published exact runtime, no upload repeat")
ast.parse(s);(D/'publish20mm_allowlist_reviewed_once.py').write_text(s,encoding='utf8')
(R/'ALLOWLIST_REJECTION_REVIEW.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-ARTIFACT-ALLOWLIST-REPAIR-02',original121_manifest_attention_and_partial_files_retained=True,actual_old_worker_and_children_gone=v['processes']==[],rejected_before_GPU_no_learning=True,reason='Original trained checkpoint path outside unchanged restricted bridge allowlist; existing byte-SHA-identical artifact checkpoint is allowed.',old_allowlist_not_widened=True,existing_frozen_checkpoint_copy=m['artifacts']['checkpoint'],new122_not_replay121=True,no_4090_GPU_PPO_or_canonical_mutation=True),indent=2),encoding='utf8')
