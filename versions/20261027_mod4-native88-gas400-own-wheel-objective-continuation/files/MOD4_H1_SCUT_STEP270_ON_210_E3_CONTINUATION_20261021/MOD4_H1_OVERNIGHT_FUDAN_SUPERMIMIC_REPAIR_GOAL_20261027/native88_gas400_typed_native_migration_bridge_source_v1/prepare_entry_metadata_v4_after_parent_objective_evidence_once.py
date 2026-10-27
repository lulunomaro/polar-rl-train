"""Keep earlier generated entry as draft; fix metadata labels/source bindings."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE/'native_own_fudan88_gas400_training.py').read_text('utf8')
for old,new in [("source_SHA=BOOTSTRAP_SHA,","source_SHA=task['source_SHA'],frozen_RSL_bootstrap_SHA=BOOTSTRAP_SHA,"),("actual_source_policy_bootstrap=bootstrap","actual_source_frozen_RSL_witness=bootstrap"),("NATIVE87_ACTUAL_GPU_PRECONTROL_ADMISSION.json","NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json"),("native_actual_method='own_MOD4_converted_Fudan_jump_native_v3'","native_actual_method='own_MOD4_native88_nominal400_changed_plant'"),("initial_native_source=window.source,gas400_parameter_source_contract_SHA=window.parameter_contract_SHA,","initial_native_source=window.source,gas400_parameter_source_contract_SHA=window.parameter_contract_SHA,\n        own_step_objective_qualification_SHA=task['own_step_objective_qualification_SHA'],")]:
 assert text.count(old)==1,old;text=text.replace(old,new)
with (HERE/'native_own_fudan88_gas400_training_v2.py').open('x',encoding='utf8',newline='') as f:f.write(text)
