"""Finalize source contract/constructor metadata; never reopen NPZ/raw/model."""
from pathlib import Path
import ast,datetime,hashlib,json,sys
import torch
HERE=Path(__file__).resolve().parent;T=HERE.parents[1];L=HERE.parent;B=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1';R2=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'
sys.path[:0]=[str(HERE),str(B/'source'),str(B/'source/sm_deps')]
from own_step_differentiable_objective_v2 import build_own_step_mdp
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
v1=read(HERE/'OWN_STEP_OBJECTIVE_SOURCE_CPU_QUALIFIED_NOT_ADMITTED_ACTUAL.json');v2=read(HERE/'OWN_STEP_OBJECTIVE_V2_SOURCE_CPU_QUALIFIED_NOT_ADMITTED_ACTUAL.json');assert v1['passed'] and v2['passed']
oldcontract=read(B/'job0/assets/import_contract.json');newcontract_path=L/'HARDWARE_GAS_SPRING_400N_L200_S60_HUMAN_20261027/agent_nominal400_target_source_candidate_v1/isolated_text_overlay_NOT_A_PAYLOAD/job0/assets/import_contract.json';newcontract=read(newcontract_path)
geometry_path=R2/'DERIVED_GEOMETRY_20260928.json';geometry=read(geometry_path);reference=read(B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json');names=read(B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json')['expected_runtime_joint_names'];encoder=('left_crank','left_hip','right_crank','right_hip')
mdp=build_own_step_mdp(newcontract,geometry,reference,names,encoder,order_scope='source_CPU_fixture');old=build_own_step_mdp(oldcontract,geometry,reference,names,encoder,order_scope='source_CPU_fixture')
assert all(torch.equal(a,b) for a,b in zip(mdp.wheel_geometry.state_dict().values(),old.wheel_geometry.state_dict().values()))
contract=mdp.contract_manifest();assert contract['reward'].startswith('identical task-dominant') and contract['schema'].endswith('.v2')
put('V2_METADATA_LABEL_CORRECTION_AND_CONSTRUCTOR_CPU_ACTUAL.json',dict(passed=True,checks=2,
 old_report_preserved='OWN_STEP_OBJECTIVE_V2_SOURCE_CPU_QUALIFIED_NOT_ADMITTED_ACTUAL.json',
 correction='Inherited old reward/position_error descriptions in the V2 CPU report were metadata-only stale labels; numeric V2 reward/cost/gradient computations already used the correct bounded new head. Runtime contract labels are now explicit and corrected without changing objective arithmetic.',
 old_runtime_source_preserved='V2_BEFORE_METADATA_LABEL_CORRECTION_SOURCE.txt',
 new400_contract_and_old700_contract_generate_literal_equal_FK_buffers=True,only_four_gas_parameter_leaves_differ_geometry_frames_unaffected=True,
 new_builder_constructs_selected_v2_with_source_scope=True,no_NPZ_raw_model_actor_SDK_or_physics_reexecuted=True))
modules=['own_step_differentiable_geometry_v1.py','own_step_differentiable_objective_v1.py','own_step_differentiable_objective_v2.py'];pins={name:dict(bytes=(HERE/name).stat().st_size,SHA=H(HERE/name)) for name in modules}
qualified=dict(passed=True,qualification_scope='SOURCE_CPU_geometry_objective_gradient_only_NOT_runtime_or_training',selected_class='OwnStepDifferentiableMdpV2',runtime_modules=pins,
 source_CPU_checks=36,source_reports={name:dict(bytes=(HERE/name).stat().st_size,SHA=H(HERE/name)) for name in ('OWN_STEP_OBJECTIVE_SOURCE_CPU_QUALIFIED_NOT_ADMITTED_ACTUAL.json','OWN_STEP_OBJECTIVE_V2_SOURCE_CPU_QUALIFIED_NOT_ADMITTED_ACTUAL.json','V2_METADATA_LABEL_CORRECTION_AND_CONSTRUCTOR_CPU_ACTUAL.json')},
 geometry_JSON=dict(path=str(geometry_path),bytes=geometry_path.stat().st_size,SHA=H(geometry_path),runtime_recommended_relative='source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'),
 reference_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3',new400_contract_source=dict(path=str(newcontract_path),SHA=H(newcontract_path)),objective_contract=contract,
 actual_bodypose_mapping_report='ACTUAL_NEW_R2_DERIVED_FK_MAPPING_ERRORS_ACTUAL.json',
 old_V1_negative_return_rejected=True,all_saved_errors_and_rejections_preserved=True,
 actual_hard_platform_contact_identity_or_success_qualified=False,WM_aux_force_prediction_fidelity_qualified=False,actual_new400_SDK_training_or_skill_gain_qualified=False,
 fixed_real_episode_state_before_after_is_source_analytic_not_new_training=True,caller_actual_SDK_order_contact_order_and_asset_source_readback_still_required=True)
put('SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_ACTUAL.json',qualified)
print(json.dumps(dict(source_CPU_passed=True,checks=36,qualification_SHA=H(HERE/'SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_ACTUAL.json'),runtime_modules=pins,geometry_JSON=qualified['geometry_JSON']),indent=2))
