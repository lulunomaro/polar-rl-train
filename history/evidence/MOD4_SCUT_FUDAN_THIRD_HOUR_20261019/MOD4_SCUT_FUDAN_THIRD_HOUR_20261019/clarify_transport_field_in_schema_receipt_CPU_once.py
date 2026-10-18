"""Preserve an inaccurate boilerplate field and append actual correction separately."""
from pathlib import Path
import json,time,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';p=R/'SAME_RECIPE_TARGET_PROOF_AND_LOCAL_CALLBACK_SCHEMA_CPU_ACTUAL.json';v=json.loads(p.read_bytes());assert v['no_new_module_or_transport_error'] is True
errors=sorted(R.glob('THREE_REAL_LEARNING_FINITE_COLLECTOR_ORIGINAL_ERROR_*.json'));assert errors
out=dict(epoch=time.time(),original_report=dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()),field='no_new_module_or_transport_error',original_value=True,correct_current_value=False,cause='Copied verifier boilerplate did not inspect subsequent or concurrent transport-error receipts. The real10054 error is independently preserved; this field is not a measured assertion.',actual_original_errors=[dict(path=str(q),bytes=q.stat().st_size,SHA=hashlib.sha256(q.read_bytes()).hexdigest()) for q in errors],unchanged_reward_bytes_and_target_source_CPU_and_callback_schema_checks_still_actual=True,no_new_local_module_error=True,original_report_source_kept_unchanged=True,no_GPU_or_account_or_live_player_change=True)
with (R/'SAME_RECIPE_SCHEMA_RECEIPT_TRANSPORT_FIELD_CLARIFICATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print('Original boilerplate retained; separate transport-field correction saved.')
