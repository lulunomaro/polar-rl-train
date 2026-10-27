"""NEW source-only gas units/coordinate calibration audit, no simulation.

Read whitelist is existing small JSON and Python. It does not read/stat/hash
PT/raw/NPZ/USD/mesh or compile/load a physical model. Old fixtures not rerun.
"""
from pathlib import Path
import ast,csv,datetime,hashlib,json,math,sys,traceback
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));L=HERE.parents[1];T=L.parent;W=T.parent
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1';R=B/'job0/runtime/isaac/mod4'
from gas_eye_length_and_nominal_force_candidate_v1 import from_import_contract,constant400_nominal_quasistatic_candidate,linear400_anchor_candidate,norm,dot,sub,mul
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)
def source_row(p):
 p=Path(p);assert p.suffix in ('.json','.py');raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
checks=[]
def check(name,condition):assert condition,name;checks.append(name)
put('ENTRY_CONSUMED_SOURCE_ONLY_ACTUAL.json',dict(epoch=datetime.datetime.now().astimezone().isoformat(),new_purpose='human400N_L200_stroke60_existing_R5_gas_source_audit',no_models_no_nativequery_no_SDK_no_physics=True))
try:
 C=B/'job0/assets/import_contract.json';c=json.loads(C.read_bytes())
 paths=[C,R/'mod4_task.py',R/'skills_isaac.py',R/'spring_pressure_component.py',R/'spring_pressure_index_runtime.py',R/'spring_nominal_sdk_readback.py',R/'gas_damping_factor.py',R/'gas_damping_sdk_adapter.py',B/'source/own_usd_closed_chain_ik_v1.py',B/'source/supermimic_reference_adapter_v1.py',W/'polar-rl-train/sources/remote/incoming/rm2025_fixed/tools/export_usd.py',W/'polar-rl-train/sources/remote/incoming/rm2025_mod4/model_parameters.json',W/'polar-rl-train/sources/remote/incoming/rm2025_mod4/PLANT_PROVENANCE.json',W/'polar-rl-train/sources/remote/incoming/rm2025_fixed/model_parameters.json',W/'polar-rl-train/sources/remote/incoming/rm2025_fixed/PLANT_PROVENANCE.json',W/'polar-rl-train/sources/remote/incoming/rm2025_fixed/kinematics_reference.py']
 lineage=[source_row(p) for p in paths]
 put('SOURCE_INPUT_SHA_LINEAGE_ACTUAL.json',dict(inputs=lineage,R5_asset_contract_is_authority_for_this_audit=True,no_USD_mesh_PT_NPZ_or_model_compilation=True,older_parameter_files_are_history_not_R5_values=True))
 task=(R/'mod4_task.py').read_text('utf8');skills=(R/'skills_isaac.py').read_text('utf8');readback=(R/'spring_nominal_sdk_readback.py').read_text('utf8');export=(paths[10]).read_text('utf8')
 check('actual_exporter_slide_axis_X_and_force_drive',"obj.CreateAxisAttr('X')" in export and "drive.CreateTypeAttr('force')" in export)
 check('actual_runtime_implicit_spring_N_m_and_damping_Ns_m_fields',"gas[n][\"stiffness_n_m\"]" in task and "gas[n][\"damping_n_s_m\"]" in task)
 check('actual_preload_event_sets_joint_position_target_not_hole_distance','robot.set_joint_position_target(tgt.unsqueeze(0).repeat(env.num_envs, 1), joint_ids=ids)' in skills)
 check('actual_readback_formula_only_approximate_not_drive_measurement','elastic=k*(target-q);viscous=d*(target_qd-qd);estimated_total=elastic+viscous+ff' in readback and 'SDK_implicit_effort_is_approximate_not_separate_PhysX_drive_force=True' in readback)
 results={};samples=[];candidates={}
 for side in ('left','right'):
  m=from_import_contract(c,side);lo,hi=m.original_q_limits_m;L0=m.length_m(0);axisprojection=dot(m.d,m.u)/dot(m.u,m.u);transverse=norm(sub(m.d,mul(m.u,axisprojection)))
  check(side+'_nominal_units_and_virtual_target',m.original_stiffness_N_per_m==3500 and m.original_damping_Ns_per_m==3 and m.original_target_q_m>.2)
  check(side+'_extension_coordinate_monotone',all(m.dlength_dq(q)>.999999 for q in (lo,0,hi)))
  check(side+'_mapping_inverse_at140_and200',all(abs(m.length_m(m.q_for_length_m(L))-L)<1e-12 for L in (.14,.2)))
  q140=m.q_for_length_m(.14);q200=m.q_for_length_m(.2);lengths=[m.length_m(lo),m.length_m(hi)]
  check(side+'_human60mm_matches60mm_coordinate_on_same_axis',abs((q200-q140)-.06)<1e-12)
  # This is source-coordinate math precision, not a new physical health gate.
  nominal=[m.old_quasistatic_joint_effort_N(hi),m.old_quasistatic_joint_effort_N(lo)]
  results[side]=dict(pin_inner_anchor_m=c['joints'][side+'_gas_pin']['local_pos1'],slide_joint=c['joints'][side+'_gas_slide'],gas_end_anchor_barrel_m=c['closures'][side+'_gas_closure']['anchor0_m'],
   formula='L(q)=norm(d+u*q); positiveq=extension; d=T0*inverse(T1)*gas_end - pin_inner_anchor; u=T0_rotation[:,X]',d_m=m.d,u_unit=m.u,neutral_hole_center_length_m=L0,coaxial_transverse_residual_m=transverse,approximate_scalar_formula=f'L(q)≈{L0:.15g}+q [m]',
   old_target_joint_q_m=m.original_target_q_m,old_target_virtual_hole_center_length_m=m.length_m(m.original_target_q_m),old_target_is_not_hardware_eye_length=True,
   old_limits_q_m=[lo,hi],old_limits_eye_length_m=lengths,old_coordinate_travel_m=hi-lo,
   human140_to200_required_q_m=[q140,q200],human_hardware_60mm_inferred_compressed_endpoint_not_measured=True,
   source_limit_below_human_extended_cap_q_m=hi-q200,source_limit_above_human_compressed_floor_q_m=lo-q140,
   overlap_of_existing_joint_limits_and_human_stroke_q_m=[max(lo,q140),min(hi,q200)],
   overlap_eye_length_m=[m.length_m(max(lo,q140)),m.length_m(min(hi,q200))],
   original_nominal_quasistatic_force_at_q0_N=m.old_quasistatic_joint_effort_N(0),
   original_nominal_quasistatic_force_range_over_original_limits_N=nominal,
   original_D5_factor_range=[.9,1.1],original_D5_stiffness_range_N_m=[3150.,3850.],original_D6_damping_range_Ns_m=[2.7,3.3],
   original_D5_force_envelope_at_zero_velocity_N=[.9*nominal[0],1.1*nominal[1]],
   original_force_at_human_extended200_N=m.old_quasistatic_joint_effort_N(q200),original_force_at_inferred_compressed140_N=m.old_quasistatic_joint_effort_N(q140))
  candidate=linear400_anchor_candidate(m);candidates[side]=dict(constant_quasistatic_nominal=constant400_nominal_quasistatic_candidate(m,q200),linear_engineering_slope_anchor=candidate)
  for label,q in [('old_qmin',lo),('old_neutral',0),('old_qmax',hi)]+[(str(round(L*1000))+'mm_eye',m.q_for_length_m(L)) for L in (.14,.15,.17,.18,.2)]:
   samples.append(dict(side=side,label=label,q_m=q,eye_length_m=m.length_m(q),within_old_joint_limits=lo<=q<=hi,within_human140_200_mm=.14-1e-12<=m.length_m(q)<=.2+1e-12,old_nominal_elastic_N=m.old_quasistatic_joint_effort_N(q),old_D5_min_N=.9*m.old_quasistatic_joint_effort_N(q),old_D5_max_N=1.1*m.old_quasistatic_joint_effort_N(q),constant_nominal_axial_N=400.,linear400_at200_engineering_k3500_N=3500*(candidate['proposed_virtual_target_q_m']-q)))
 check('left_right_mapping_symmetric',abs(results['left']['neutral_hole_center_length_m']-results['right']['neutral_hole_center_length_m'])<1e-12)
 check('source_700N_nominal_at200_has_no400N_offset_explanation',all(abs(v['original_force_at_human_extended200_N']-700)<.001 for v in results.values()))
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
 oldparams=json.loads(paths[11].read_bytes());deprecated=json.loads(paths[13].read_bytes())
 result=dict(passed=True,scope='source_only_units_geometry_and_quasistatic_law_audit_not_actual_force_measurement',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_R5=c['source_mjcf_sha256'],per_side=results,
  current_units=dict(q='m',qd='m/s',stiffness='N/m',damping='N*s/m',prismatic_effort='N',old_implicit_force_cap_N=2000.,armature=0.002,old_virtual_target_is_joint_coordinate=True),
  source_formula='estimated_joint_effort=clip(k_episode*(q_target-q)+c_episode*(qd_target-qd)+feedforward,-2000,2000); target_qd=0 per authored drive, preload event writes position only',
  gas_force_is_not_chassis_vertical_force_and_not_proven_cause_of_training_failure=True,
  model_parameters_history=dict(rm2025_mod4_original=oldparams['gas_spring'],deprecated_rm2025_fixed_not_selected=deprecated['gas_spring'],active_R5_values_come_only_from_exact_R5_contract_and_runtime=True),
  deterministic_source_findings=dict(old_nominal_is_700N_at200_not400=True,old_coordinate_limits_not_exact140_to200=True,virtual_target220mm_is_not_hole_length_bug_by_itself=True,old_R5_hardware_alignment_not_established=True),
  existing_R5_results_preserved_as_parent_report=dict(formal_native_bytes_each=256224393,h1_takeoff3755_recovery_slot_takeoff748=True,both_cross_landing_recovery_all_zero=True,original_closed_balance_snapshot=569553.363275528,no_claim_new_measurement=True),
  no_Luna_OpenRouter_or_image_tool=True,no_model_raw_asset_actor_physics_GPU_remote_or_runtime_edit=True,checks=len(checks),check_names=checks)
 put('EXISTING_R5_GAS_UNITS_EYE_MAPPING_AND_FORCE_AUDIT_ACTUAL.json',result)
 put('400N_NOMINAL_ONLY_ISOLATED_CANDIDATES_NOT_ADMITTED.json',dict(hardware_calibrated=False,deployed=False,new_runtime_or_task_written=False,candidates=candidates,
  recommendation='A constant400N axial quasistatic surrogate is immediately dimensionally meaningful; or explicitly assume400N@200mm and retain3500N/m only as an unmeasured engineering sensitivity slope. Neither identifies purchased-spring compression/damping/friction law.',
  pending=['Diameter variant D18/d8 versus D21/22/d10 not identified','Actual gas label force measurement position/F1 convention not supplied','Force versus stroke/progressivity, extension-compression hysteresis, seal friction, damping/temperature unknown','Human200/60 implies140 minimum, not bench measurement of end stops','Any new constraint range must respect existing closed chain and CAD limits; do not blindly expand lower q or reuse old weights as hardware-aligned','Separate root-approved new source/SDK/physical admission needed before deploying a candidate'],
  not_required_to_continue_already_declared_old_config_frozen_diagnostic=True))
 with (HERE/'SOURCE_ONLY_EYE_LENGTH_FORCE_SAMPLES_ACTUAL.csv').open('x',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=list(samples[0]));writer.writeheader();writer.writerows(samples)
 print(json.dumps(dict(passed=True,checks=len(checks),left=results['left'],linear400_candidate=candidates['left']['linear_engineering_slope_anchor']),indent=2))
except BaseException:
 put('ORIGINAL_SOURCE_AUDIT_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),completed_checks=checks,original_files_untouched=True,no_runtime_or_model_query=True));raise
