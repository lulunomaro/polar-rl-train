"""Prepare independent actual-reset reader; preserve old failing reader and results."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
old=D/'review_entry139_schema_actual.py';new=D/'review_entry139_final_reset_schema_actual.py';assert not new.exists()
text=old.read_text(encoding='utf8');assert 'from review_curb132_actual import audit' in text
text=text.replace('from review_curb132_actual import audit','from entry139_final_reset_recipe_review import audit',1).replace('CURB139_SCHEMA_REVIEW','CURB139_FINAL_RESET_SCHEMA_REVIEW');ast.parse(text);new.write_text(text,encoding='utf8')
error=max(R.glob('CURB139_SCHEMA_REVIEW_ERROR_[0-9]*.json'));p=R/'ENTRY139_FINAL_RESET_READER_ADMITTED.json';assert not p.exists()
p.write_text(json.dumps(dict(epoch=time.time(),trial_id='ENTRY139-FINAL-RESET-RECEIPT-READER-01',old_source=str(old),old_source_SHA=H(old.read_bytes()),old_error=str(error),old_result_false_not_overwritten=True,new_source=str(new),new_source_SHA=H(new.read_bytes()),actual_final_step_declared_route_truncation_env69=True,actual_sensor_all_channels_requested_age0_observed_age0_sample1500_warmup_false=True,old_feedback_delay_reset_apply_source_byteSHA_bound=True,all_unreset_rows_original_strict_checks=True,all_ground_contact_COMlink_hardware_force_integral_tolerances_unchanged=True,no_GPU_eval_replay_or_budget_mutation=True),indent=2),encoding='utf8')
print(json.dumps(dict(new_reader=str(new),original_error_preserved=str(error),reader_only=True)))
