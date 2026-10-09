from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
loc=json.loads((R/'PLAN_MASTER_LOCATION_READ.json').read_bytes());assert 'MOD4_MOE_MASTER_PLAN.md' in loc['report_plan_files']
assert loc['approval']['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
err=json.loads((R/'POSTWINDOW_METADATA_FINISH_ERROR.json').read_bytes());assert 'FileNotFoundError' in err['error']
s=(D/'finish_postwindow_sync_quote_reviewed_once.py').read_text(encoding='utf8').replace('POSTWINDOW_METADATA_FINISH_STARTED','POSTWINDOW_METADATA_LOCATION_STARTED').replace('POSTWINDOW_METADATA_FINISH_ERROR','POSTWINDOW_METADATA_LOCATION_ERROR').replace('QUOTE-CONTINUATION-03','MASTER-LOCATION-CONTINUATION-04').replace("master=R.parent/'MOD4_MOE_MASTER_PLAN.md'","master=R/'MOD4_MOE_MASTER_PLAN.md'")
ast.parse(s);p=D/'finish_postwindow_sync_master_location_reviewed_once.py';assert not p.exists();p.write_text(s,encoding='utf8')
(R/'SYNC_MASTER_LOCATION_REJECTION_REVIEW.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-POSTWINDOW-MASTER-LOCATION-REVIEW-04',original_missing_master_path_retained=True,actual_master_is_under_reports_not_root=True,previous_failure_before_CAS_current_handoff_write=True,already_uploaded_reports_reused_after_exact_bytes_check=True,no_GPU_PPO_runtime_or_canonical_mutation=True),indent=2),encoding='utf8')
