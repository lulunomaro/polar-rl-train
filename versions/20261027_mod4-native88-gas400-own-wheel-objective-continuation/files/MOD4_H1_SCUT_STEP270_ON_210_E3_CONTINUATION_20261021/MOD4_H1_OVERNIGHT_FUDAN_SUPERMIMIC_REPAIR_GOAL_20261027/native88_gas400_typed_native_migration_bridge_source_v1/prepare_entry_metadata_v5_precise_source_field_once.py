"""Preserve V4's ambiguous substring failure; use complete GPU report anchor."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
with (HERE/'V4_ORIGINAL_METADATA_GENERATOR_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(error='AssertionError: source_SHA=BOOTSTRAP_SHA,',cause='Substring also matched bootstrap_task_source_SHA; exact count was2, not1',original_entry='prepare_entry_metadata_v4_after_parent_objective_evidence_once.py',no_runtime_or_models=True,old_source_preserved=True),f,indent=2)
text=(HERE/'native_own_fudan88_gas400_training.py').read_text('utf8')
changes=[("actual_source_policy_bootstrap=bootstrap,source_SHA=BOOTSTRAP_SHA,","actual_source_frozen_RSL_witness=bootstrap,source_SHA=task['source_SHA'],frozen_RSL_bootstrap_SHA=BOOTSTRAP_SHA,"),("NATIVE87_ACTUAL_GPU_PRECONTROL_ADMISSION.json","NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json"),("native_actual_method='own_MOD4_converted_Fudan_jump_native_v3'","native_actual_method='own_MOD4_native88_nominal400_changed_plant'"),("initial_native_source=window.source,gas400_parameter_source_contract_SHA=window.parameter_contract_SHA,","initial_native_source=window.source,gas400_parameter_source_contract_SHA=window.parameter_contract_SHA,\n        own_step_objective_qualification_SHA=task['own_step_objective_qualification_SHA'],")]
for old,new in changes:
 assert text.count(old)==1,old;text=text.replace(old,new)
with (HERE/'native_own_fudan88_gas400_training_v2.py').open('x',encoding='utf8',newline='') as f:f.write(text)
