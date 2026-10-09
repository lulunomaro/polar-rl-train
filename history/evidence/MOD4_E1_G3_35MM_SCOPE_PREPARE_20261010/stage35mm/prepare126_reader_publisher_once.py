"""Prepare unique126 delivery and readers; retain original125 publisher and rejection."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'PREPARE126_STARTED.json').exists()
(R/'PREPARE126_STARTED.json').write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-35MM-126-DELIVERY-PREPARE-04')).encode())
s=(D/'publish35mm_scope_once.py').read_text(encoding='utf8')
a=s.index("   C=W/'MOD4_E1_G2_MATCHED_CONTINUE_20261010'");b=s.index('\n finally:',a)
s=s[:a]+"  print(json.dumps(dict(job_id=JID,package_SHA=pkg['sha256'],worker_actual=own,actual_boundary=boundary,new_behavior_pending=True,no_learning=True,new_budget_seconds=0)))"+s[b:]
s=s.replace('125-e1-g3-35mm-source32058-fullroute-flat','126-e1-g3-35mm-source32058-manifest-reviewed-fullroute-flat').replace('E1_ARTIFACT_SOURCE_REVIEW','E1_G3_PACKAGE_REVIEW').replace('eval_worker_e1_artifact_source_review.py','eval_worker_e1_g3_package_review.py')
s=s.replace("(W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010/eval_worker_e1_g3_package_review.py')","(D/'eval_worker_e1_g3_package_review.py')")
s=s.replace("R/'PREPARED.json'","R/'REPAIRED_PREPARED.json'").replace("'PUBLISH_STARTED.json'","'PUBLISH126_STARTED.json'").replace("'PUBLISHED.json'","'REPAIRED_PUBLISHED.json'").replace("'PUBLISH_ERROR.json'","'PUBLISH126_ERROR.json'").replace('E1-G3-35MM-FROZEN-PUBLISH-01','E1-G3-35MM-REPAIRED-FROZEN-PUBLISH-04')
s=s.replace('worker_not_modified_or_restarted=True','new_worker_own_admission_verified=True,original125_and_old_worker_rejection_retained=True')
ast.parse(s);(D/'publish35mm_manifest_reviewed126_once.py').write_bytes(s.encode())
for source,target in [('collect35mm_actual.py','collect35mm126_actual.py'),('review35mm_actual.py','review35mm126_actual.py')]:
 s=(D/source).read_text(encoding='utf8').replace('E1_ARTIFACT_SOURCE_REVIEW','E1_G3_PACKAGE_REVIEW').replace('eval_worker_e1_artifact_source_review.py','eval_worker_e1_g3_package_review.py').replace("R/'PUBLISHED.json'","R/'REPAIRED_PUBLISHED.json'").replace("R/'PREPARED.json'","R/'REPAIRED_PREPARED.json'").replace('G3_125','G3_126').replace('new125','new126').replace('E1-G3-35MM-ACTUAL-COLLECT-01','E1-G3-35MM-126-ACTUAL-COLLECT-04').replace('E1-G3-35MM-ACTUAL-REVIEW-01','E1-G3-35MM-126-ACTUAL-REVIEW-04').replace('E1-G3-35MM-CPU-READER-01','E1-G3-35MM-126-CPU-READER-04')
 ast.parse(s);(D/target).write_bytes(s.encode())
print(json.dumps(dict(new126_delivery_and_readers_prepared=True,original125_not_replayed=True)))
