"""Build a new continuation only after the prior guard failed before any write."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
v=json.loads((R/'ENVIRONMENT_VIEW_STAGE_GUARD_DIAGNOSIS.json').read_bytes())
assert not v['new_root_exists'] and not any(x['text'] for x in v['discard_files'])
old=(D/'stage_environment_view_once.py').read_text()
needle='logs=old/\'discard_logs\';error=list(logs.glob(\'curb_discard20k_*.error.txt\'));assert len(error)==1 and "has no attribute \'num_envs\'" in error[0].read_text()'
assert old.count(needle)==1
new=old.replace(needle,"logs=old/'discard_logs';error=list(old.glob('curb_discard20k_*.log'));assert len(error)==1 and \"has no attribute 'num_envs'\" in error[0].read_text();assert not list(logs.glob('curb_discard20k_*.error.txt'))")
new=new.replace("ns={}\nexec(compile", "ns={'torch':torch}\nexec(compile")
assert new.count("ns={'torch':torch}")==1
for a,b in [('ENVIRONMENT_VIEW_STAGE_STARTED','ENVIRONMENT_VIEW_LOG_RECEIPT_STAGE_STARTED'),('ENVIRONMENT_VIEW_STAGE_ERROR','ENVIRONMENT_VIEW_LOG_RECEIPT_STAGE_ERROR'),('CURB-ENVVIEW-384-INDEPENDENT-STAGE-01','CURB-ENVVIEW-384-LOG-RECEIPT-STAGE-CONTINUATION-01')]:new=new.replace(a,b)
compile(new,'stage_environment_view_log_receipt_once.py','exec')
p=D/'stage_environment_view_log_receipt_once.py';assert not p.exists();p.write_bytes(new.encode())
p=R/'LOG_RECEIPT_STAGE_CONTINUATION_REVIEW.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),prior_guard_rejected_before_new_root_write=True,prior_guard_and_errors_preserved=True,actual_worker_log_used_instead_of_missing_future_error_file=True,actual_PID_and_unique_failed_segment_still_required=True,only_unexecuted_copy_and_CPU_admission_continued=True,installed_manager_property_annotations_torch_available=True),indent=2))
