"""One new immutable frozen terrain scope; all original D0-D7/assets retained."""
from pathlib import Path
import ast,json,hashlib,zipfile,time,copy
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 assert not (R/'G1_BEHAVIOR_PACKAGE_BUILT.json').exists()
 inspection=json.loads((R/'G1_TARGET_INSPECTED.json').read_text())
 reviewed=json.loads((R/'predecessor/E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json').read_text())
 old=json.loads((W/'MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports/E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json').read_text())
 assert reviewed['actual_five_cases_review_complete'] and reviewed['source_sha256']==inspection['source_sha256']==old['row']['checkpoint']['sha256']
 selected=dict(epoch=time.time(),trial_id='E1-RETENTION-REPAIR-SELECT-01',source=dict(path=inspection['source_path'],sha256=inspection['source_sha256'],bytes=inspection['source_bytes']),actual_behavior_review_complete=True,no_unreviewed_latest_source=True,source310_snapshot57_finite96=True,own_PID_bound_receipt=old['row']['own_PID_bound_receipt'],unique_completed_segment=old['row']['unique_completed_segment'],behavior_review=dict(path=str(R/'predecessor/E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json'),sha256=sha((R/'predecessor/E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json').read_bytes())),rollback_reason='Two completed G0 stable blocks worsened inherited skills while terrain remained usable; no third unchanged G0 block.',not_all_skills_graduated=True,E0_kept_frozen=True,no_rejected_70_20_10_quota_scheme=True,first_learning_observation_s=900,permanent_forgetting_cure_not_claimed=True)
 (R/'SELECTED_E1_REPAIR_SOURCE.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
 base=D/'artifacts/s3-e1-actual310-gentle-fullroute-frozen.zip';assert sha(base.read_bytes())=='0c901815cf0024469bc53fd15a090375ad1e7a71563eed054271e60984a18b22'
 with zipfile.ZipFile(base) as z:
  manifest=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in manifest['files']}
 assert all(sha(b)==manifest['files'][n] for n,b in payload.items())
 entry='runtime/isaac/mod4/frozen_history_flat.py';original=payload[entry].decode();new=original.replace('from e1_scene_query_resource import configure_intro','from g1_cad_wave_geometry import configure_g1 as configure_intro').replace("protocol='approved_E1_gentle_route_behavior_v1'","protocol='approved_E1_G1_derived10mm_route_behavior_v1'")
 assert new!=original
 # Only the configuration import and explicit protocol identifier may differ.
 assert new.replace('from g1_cad_wave_geometry import configure_g1 as configure_intro','from e1_scene_query_resource import configure_intro').replace("protocol='approved_E1_G1_derived10mm_route_behavior_v1'","protocol='approved_E1_gentle_route_behavior_v1'")==original
 ast.parse(new);payload[entry]=new.encode()
 for name in ('g1_cad_wave_geometry.py','g1_cad_profile.json'):
  payload['runtime/isaac/mod4/'+name]=(D/'payload/isaac/mod4'/name).read_bytes()
 changed={n:sha(b) for n,b in payload.items() if manifest['files'].get(n)!=sha(b)}
 assert set(changed)=={entry,'runtime/isaac/mod4/g1_cad_wave_geometry.py','runtime/isaac/mod4/g1_cad_profile.json'}
 meta=dict(manifest,files={n:sha(b) for n,b in payload.items()},new_or_changed_members=changed,protocol='approved_E1_G1_derived10mm_route_behavior_v1',geometry_curriculum_revision='MOD4-RM-TERRAIN-CURRICULUM-REVISION-003',G1_peak_to_trough_m=.01,real_RM70mm=False,all_original_D0_D7_and_assets_byteexact_except_geometry_import=True,unchanged_ground_contact_reset_data_tolerances=True,no_learning=True,no_actor_terrain_truth=True,failed_G0_cases_retained=True)
 dest=D/'artifacts/e1-g1-cad-derived10mm-fullroute-frozen.zip';assert not dest.exists()
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in payload.items():z.writestr(n,b)
  z.writestr('SOURCE_MANIFEST.json',json.dumps(meta,indent=2))
 report=dict(epoch=time.time(),trial_id='E1-G1-PACKAGE-01',package=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest.read_bytes())),baseline_package_sha256=sha(base.read_bytes()),changed_members=changed,manifest=meta,only_three_members_changed=True,actual_G1_closedloop_behavior_pending=True,no_GPU_PPO_queue_canonical_write=True)
 (R/'G1_BEHAVIOR_PACKAGE_BUILT.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='manifest'}))
if __name__=='__main__':main()
