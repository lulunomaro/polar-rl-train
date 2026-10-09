"""Retain125 pre-GPU manifest rejection; independently validate new package and authority."""
from pathlib import Path
import ast,hashlib,json,time,zipfile,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
BAD='clk2500-closure-episode-d3-125-e1-g3-35mm-source32058-fullroute-flat'
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 save('MANIFEST_REPAIR_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-PACKAGE-MANIFEST-REPAIR-02',original125_retained=True))
 actual=json.loads(sorted(R.glob('G3_125_COLLECTED_*.json'))[-1].read_bytes());assert actual['processes']==[] and 'AssertionError: runtime/isaac/mod4/frozen_history_flat.py' in actual['current_attention']['error']
 prepared=json.loads((R/'PREPARED.json').read_bytes());first=Path(prepared['package']['path']);assert H(first.read_bytes())==prepared['package']['sha256']
 with zipfile.ZipFile(first) as z:members={n:z.read(n) for n in z.namelist()}
 original=json.loads(members['SOURCE_MANIFEST.json']);bad={n:dict(expected=h,actual=H(members[n])) for n,h in original['files'].items() if H(members[n])!=h};assert set(bad)=={'runtime/isaac/mod4/frozen_history_flat.py'}
 # Explicit approved geometry/dispatcher byte changes were independently CPU-reviewed.
 changes=['runtime/isaac/mod4/frozen_history_flat.py','runtime/isaac/mod4/g3_cad_profile.json','runtime/isaac/mod4/g3_cad_wave_geometry.py']
 revised=json.loads(json.dumps(original));revised['previous20mm_SOURCE_MANIFEST_sha256']=H(members['SOURCE_MANIFEST.json']);revised['protocol']='approved_E1_G3_derived35mm_complete_wave_route_behavior_v1';revised['G3_peak_to_trough_m']=.035
 revised['retained125_failure']='Frozen dispatcher changed for approved35mm scope, but its immutable file map still referred to20mm dispatcher; rejection before GPU/PhysX/PPO.'
 revised['only_next35mm_geometry_dispatcher_and_explicit_manifest_changed']=True
 for n in changes:revised['files'][n]=H(members[n])
 revised['new_or_changed_G3_members']={n:H(members[n]) for n in changes};members['SOURCE_MANIFEST.json']=json.dumps(revised,indent=2).encode()
 assert all(H(members[n])==h for n,h in revised['files'].items()) and len(revised['files'])==len(original['files'])+2
 for n,h in original['files'].items():
  if n not in changes:assert revised['files'][n]==h
 pkg=D/'artifacts/e1-g3-derived35mm-complete-route-manifest-reviewed-v2-frozen.zip'
 with zipfile.ZipFile(pkg,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for n,b in members.items():z.writestr(n,b)
 with zipfile.ZipFile(pkg) as z:assert all(H(z.read(n))==h for n,h in revised['files'].items())
 save('PACKAGE_REJECTION_REVIEW.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-PACKAGE-MANIFEST-REJECTION-01',original125_job_id=BAD,original_package=prepared['package'],manifest_mismatch=bad,new_geometry_and_dispatcher_reviewed_by_CPU_source_hash=True,original_attention=actual['current_attention'],actual_old_worker_and_children_exited=True,no_GPU_PhysX_PPO_or_skill_result=True,original125_not_passed_or_retried=True,only_new_126_scope_uses_reviewed_package=True,new_budget_seconds=0))
 repaired=dict(prepared);repaired.update(epoch=time.time(),trial_id='E1-G3-35MM-MANIFEST-REPAIRED-PREPARE-02',package=dict(path=str(pkg.resolve()),bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes())),changed_or_added_members=changes+['SOURCE_MANIFEST.json'],actual_all_immutable_package_file_maps_verified=True,original125_package_and_rejection_retained=True)
 save('REPAIRED_PREPARED.json',repaired)
 old=W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010'
 s=(old/'eval_worker_e1_artifact_source_review.py').read_text(encoding='utf8').replace('E1_ARTIFACT_SOURCE_REVIEW','E1_G3_PACKAGE_REVIEW')
 s=s.replace('PAUSED_SHALLOW_JOBS=',"RETIRED=RETIRED+("+repr(BAD)+",)\nPAUSED_SHALLOW_JOBS=")
 ast.parse(s);(D/'eval_worker_e1_g3_package_review.py').write_text(s,encoding='utf8')
 save('G3_WORKER_EXPECTED.json',dict(epoch=time.time(),old_artifact_source_sha256=H((old/'eval_worker_e1_artifact_source_review.py').read_bytes()),new_source_sha256=H(s.encode()),only_namespace_and_exact125_before_GPU_rejection_exclusion_changed=True,restricted_bridge_shared_GPU_lock_base_guard_JSON_retry_unchanged=True))
 s=(old/'admit_e1_artifact_source_review_once.py').read_text(encoding='utf8')
 start=s.index(" expected=read(D/'E1_ARTIFACT_WORKER_EXPECTED.json')");end=s.index(' actual=ps(',start)
 block=""" expected=read(D/'E1_G3_WORKER_EXPECTED.json')
 assert hashlib.sha256((D/'eval_worker_e1_artifact_source_review.py').read_bytes()).hexdigest()==expected['old_artifact_source_sha256']
 assert hashlib.sha256((D/'eval_worker_e1_g3_package_review.py').read_bytes()).hexdigest()==expected['new_source_sha256']
 fault=read(D/'E1_ARTIFACT_SOURCE_REVIEW_WORKER_ATTENTION.json');assert 'AssertionError: runtime/isaac/mod4/frozen_history_flat.py' in fault['error']
 jid='clk2500-closure-episode-d3-125-e1-g3-35mm-source32058-fullroute-flat';folder=D/'jobs'/jid
 manifest=read(folder/'manifest.json');assert manifest['no_learning'] and not manifest['canonical_write_authority']
 assert not (folder/'result.json').exists() and not (folder/'probe.json').exists()
 runtime=D/'runtimes'/manifest['artifacts']['runtime']['sha256'];assert not (runtime/'PACKAGE_READY.json').exists()
 original=read(runtime/'SOURCE_MANIFEST.json');actual_sha=hashlib.sha256((runtime/'runtime/isaac/mod4/frozen_history_flat.py').read_bytes()).hexdigest();assert actual_sha!=original['files']['runtime/isaac/mod4/frozen_history_flat.py']
 failed=dict(phase='immutable_package_map_rejected_before_GPU',job_id=jid,original_manifest=manifest,original_attention=fault,original_dispatcher_SHA=actual_sha,expected_dispatcher_SHA=original['files']['runtime/isaac/mod4/frozen_history_flat.py'])
"""
 s=s[:start]+block+s[end:]
 s=s.replace('E1_ARTIFACT_SOURCE_REVIEW_WORKER_ADMISSION','E1_G3_PACKAGE_REVIEW_WORKER_ADMISSION').replace('admit_e1_artifact_source_review_once.py','admit_e1_g3_package_review_once.py')
 s=s.replace("old='MOD4_AsyncFrozenEvaluation_v15_e1_full_route_review'","old='MOD4_AsyncFrozenEvaluation_v15_e1_artifact_source_review'")
 s=s.replace('OLD_FULL_ROUTE_TASK_BEFORE_ARTIFACT_SOURCE.xml','OLD_ARTIFACT_TASK_BEFORE_G3_PACKAGE.xml').replace('exclusion_of121_is_transport_rejection_before_GPU_not_pass=True','exclusion_of125_is_package_rejection_before_GPU_not_pass=True')
 s=s.replace("$name='MOD4_AsyncFrozenEvaluation_v15_e1_artifact_source_review'","$name='MOD4_AsyncFrozenEvaluation_v15_e1_g3_package_review'").replace("\\eval_worker_e1_artifact_source_review.py'","\\eval_worker_e1_g3_package_review.py'")
 s=s.replace('E1_ARTIFACT_SOURCE_REVIEW_WORKER_STARTED','E1_G3_PACKAGE_REVIEW_WORKER_STARTED').replace('E1_ARTIFACT_SOURCE_REVIEW_WORKER_ATTENTION','E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION').replace("fault=read(D/'E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json')","fault=read(D/'E1_ARTIFACT_SOURCE_REVIEW_WORKER_ATTENTION.json')")
 s=s.replace('E1_ARTIFACT_SOURCE_REVIEW_TASK.xml','E1_G3_PACKAGE_REVIEW_TASK.xml').replace('E1_ARTIFACT_SOURCE_REVIEW_WORKER_ADMITTED','E1_G3_PACKAGE_REVIEW_WORKER_ADMITTED')
 s=s.replace('Retain failed119 proxy dtype proof and neverrun candidate; new frozen complete-wave route review; original bridge/lock; no trainer/budget authority.','Retain125 immutable file map rejection before GPU; new frozen35mm reviewed package; original guard/bridge/lock; no trainer or budget authority.')
 ast.parse(s);(D/'admit_e1_g3_package_review_once.py').write_text(s,encoding='utf8')
 s=(old/'deploy_artifact_worker_once.py').read_text(encoding='utf8').replace('ARTIFACT_WORKER_DEPLOY','G3_PACKAGE_WORKER_DEPLOY').replace('eval_worker_e1_artifact_source_review.py','eval_worker_e1_g3_package_review.py').replace('admit_e1_artifact_source_review_once.py','admit_e1_g3_package_review_once.py')
 s=s.replace('ARTIFACT_WORKER_EXPECTED.json','G3_WORKER_EXPECTED.json').replace('E1_ARTIFACT_WORKER_EXPECTED.json','E1_G3_WORKER_EXPECTED.json').replace('E1_ARTIFACT_SOURCE_REVIEW_WORKER_','E1_G3_PACKAGE_REVIEW_WORKER_').replace('OLD_FULL_ROUTE_TASK_BEFORE_ARTIFACT_SOURCE.xml','OLD_ARTIFACT_TASK_BEFORE_G3_PACKAGE.xml').replace('E1_ARTIFACT_SOURCE_REVIEW_TASK.xml','E1_G3_PACKAGE_REVIEW_TASK.xml')
 ast.parse(s);(D/'deploy_g3_package_worker_once.py').write_text(s,encoding='utf8')
 print(json.dumps(dict(repaired_package_SHA=repaired['package']['sha256'],all_package_file_maps_verified=True,original125_rejection_retained=True,no_learning_or_budget_change=True)))
if __name__=='__main__':
 try:main()
 except Exception:
  save('MANIFEST_REPAIR_ERROR.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-PACKAGE-MANIFEST-REPAIR-02',error=traceback.format_exc(),no_production_change=True));raise
