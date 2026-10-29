"""Small actual CPU-report readback only; no checkpoint/model/statistics action."""
from pathlib import Path
import json,hashlib,time
N=Path(__file__).resolve().parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=R/'NEW114_ACTUAL_SOURCE_SDK_FULLSTATE_CPU_RETURNED_ACTUAL.json';j=read(p)
assert j['passed'] and j['actual_CPU_waited_EXIT0'] and j['proof']['actual_waited'] and j['proof']['returncode']==0 and not j['errors']
v=j['value'];norm=v['WM114_actual_installed_input_norm_readback'];reward=v['reward111_actual_installed_readback'];assert norm['passed'] and reward['passed']
assert v['all_native_modules_norms_threeoptimizers_strict_restore_CPU_passed'] and v['initial_loads']==dict(selected111source=1,normal86=1)
spec=read(R/'NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json')
assert v['payload_manifest_SHA']==spec['manifest_SHA'] and v['source_progress']==spec['source_progress']
out=dict(schema='mod4.native114.one_actual_CPU_bound_spec.pending_controller.v1',epoch=time.time(),actual_target_CPU_passed=True,actual_source_CPU_returned_report=str(p),actual_source_CPU_returned_report_SHA=H(p),actual_CPU_report_SHA=j['proof']['report_SHA'],actual_waited_proof_SHA=j['proof_SHA'],actual_target_job_root=j['actual_job_root'],payload=spec['payload'],manifest_SHA=spec['manifest_SHA'],source_contract_SHA=spec['source_contract_SHA'],task=spec['task'],source=spec['source'],source_progress=spec['source_progress'],GPU_UUID=spec['GPU_UUID'],logical_slot='h1',physical_seed=27,native_learning_seed=27,
 actual_inherited_WM_input_normalizer=norm['actual_loaded_normalizer_slots_1_3'],analytic_max_raw_shift=[.01,.005],analytic_max_normalized_shift_using_actual_inherited_std=[a/b for a,b in zip([.01,.005],norm['actual_loaded_normalizer_slots_1_3']['std'])],normalizer_buffers_literal_unchanged=norm['normalizer_buffers_literal_unchanged'],actual_bank133_at_yaw0_raw_delta=norm['actual_measurement_max_raw_shift'],actual_bank133_at_yaw0_normalized_delta=norm['actual_measurement_max_normalized_shift'],source_synthetic_opposite_heading_separated=True,
 actual_reward111_own_FK_readback=reward,all_native_WM_Pi_Critic_norms_threeopts_and_frozen_RSL832460_fullfinite_literal=True,initial_model_loads_this_new_admission=dict(native111=1,necessary_normal86=1),no_WM_Pi_Critic_forward_in_CPU=True,no_source_model_environment_RNG_or_replay_restored=True,
 ready_for_new_controller_source_seal_only=True,new_owner_registered=False,new_GO=False,new_fee=False,new_GPU_learning=False,actual_GPU_source_and_loaded_input_readback_before_first_control_still_required=True,
 next='Prepare genuine one-H1 or separately admitted mixed single72writer controller/TaskGO using original owner/common/forward; freeze first/normal900/initialformal reviewer sources before launch. No placeholder/hotadd/secondwriter. Fresh light resource/account/locks before anyGO. Preserve human reward-before-use and current111 reward/true270/20s. Do not call this universal reward correctness or successful stair skill.')
with (R/'NATIVE114_ACTUAL_CPU_BOUND_ONE_H1_SPEC_PENDING_CONTROLLER_SEAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(dict(actual_target_CPU_passed=True,loaded_norm_std=norm['actual_loaded_normalizer_slots_1_3']['std'],analytic_bound_normalized_shift=out['analytic_max_normalized_shift_using_actual_inherited_std'],new_GPU_learning=False)))
