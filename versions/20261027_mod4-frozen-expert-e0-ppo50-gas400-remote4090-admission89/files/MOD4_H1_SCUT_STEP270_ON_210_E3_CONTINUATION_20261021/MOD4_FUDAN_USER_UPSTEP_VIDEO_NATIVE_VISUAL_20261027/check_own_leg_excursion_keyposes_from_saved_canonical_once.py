"""Bounded own-geometry retarget investigation; no reference deployment/physics."""
from pathlib import Path
import sys,json,time,traceback,hashlib
import numpy as np
V=Path(__file__).resolve().parent;T=V.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
O=L/'real_Fudan_video_phase_retarget_reachability_candidate_v1'
J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'
S=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027'
def main():
 O.mkdir();start=time.time()
 intent=dict(epoch=start,purpose='User rejects90percent limb attenuation; test whether stronger original leg excursions fit own400N geometry at four representative saved standing-jump poses',real_video_gives_phase_evidence_not_3D_joints=True,no_new_reference_export_or_deployment=True,no_checkpoint_original_NPZ_actor_GPU_or_physics=True)
 with (O/'INTENT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(intent,f,indent=2)
 sys.path[:0]=[str(J/'agent_reference_retarget_cpu'),str(L/'agent_MOD4_step_reference_conversion_candidate_v1')]
 from supermimic_reference_adapter_v1 import TaskspaceDemo,quat_to_mat,retarget_taskspace
 from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
 from mod4_step_reference_conversion_v1 import build_recorded_kinematics
 canonical=J/'agent_reference_retarget_cpu/ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/upstream_actual_default_dt_standing_jump_CANONICAL_TASKSPACE_DEMO.json'
 demo=TaskspaceDemo.from_dict(json.loads(canonical.read_bytes()))
 N=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027';B=N/'payloads/h1'
 geometry=json.loads((S/'actual210/seed_20260928/ACTUAL_RENDER_GEOMETRY.json').read_bytes())
 contract=json.loads((B/'job0/assets/import_contract.json').read_bytes())
 kin=build_recorded_kinematics(contract,geometry,OwnUsdKinematics,transform,quat_to_mat)
 old=json.loads((B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json').read_bytes())
 oldq=np.asarray(old['packed73'])[:,13:43];ages=np.asarray(old['ages']);order=[old['joint_names'].index(n) for n in kin.joint_names]
 times=[1.50,1.65,1.86,2.00];rows=[];results=[]
 for amplitude in (1.,.5,.25,.1):
  task=retarget_taskspace(demo,kin.wheel_local(np.zeros(30)),[0,0,kin.source_metadata['nominal_spawn_height_m']],target_control_dt_s=.01,start_s=1.,end_s=3.6,limb_excursion_attenuation=amplitude)
  task=kin.preserve_recorded_wheel_height_asymmetry(demo,task,source_wheel_radius_m=.06)
  for source_t in times:
   i=int(np.argmin(abs(task.time_s-(source_t-1.))));age=int(round((source_t-.5)*100));j=int(np.argmin(abs(ages-age)))
   fit=kin.solve(task.wheel_local_m[i],oldq[j][order],max_iterations=60)
   rows.append(dict(amplitude=amplitude,source_saved_standing_jump_t_s=source_t,own_old_clock_age=age,target_wheel_local_m=task.wheel_local_m[i].tolist(),**fit.summary()))
   results.append((amplitude,source_t,fit.joint_pos30.copy(),task.wheel_local_m[i].copy()))
   print(json.dumps(dict(amplitude=amplitude,source_t=source_t,status=fit.status,wheel_error_m=fit.wheel_error_max_m,wall_s=time.time()-start)),flush=True)
 artifact=O/'KEYPOSE_RESULTS_ONLY.json'
 report=dict(epoch=time.time(),source_canonical_path=str(canonical),source_canonical_SHA=hashlib.sha256(canonical.read_bytes()).hexdigest(),own400_contract_SHA=hashlib.sha256((B/'job0/assets/import_contract.json').read_bytes()).hexdigest(),poses_tested=16,rows=rows,
   maximum_amplitude_fit_at_all_four_keyposes=max([a for a in (1.,.5,.25,.1) if all(r['status']=='STATIC_KINEMATIC_FIT' for r in rows if r['amplitude']==a)],default=None),
   only_four_keyposes_not_fullclip_or_motion_derivatives=True,not_dynamic_torque_impulse_collision_or_success_proof=True,
   no_new_reference_exported=True,source_standing_jump_not_real_video_step=True,
   real_video_used_for_phase_semantics_only=True,original_saved_data_and_current9223_unchanged=True,wall_s=time.time()-start)
 with artifact.open('x',encoding='utf8') as f:json.dump(report,f,indent=2,allow_nan=False)
 print(json.dumps(dict(output=str(artifact),maximum_amplitude_fit_at_all_four_keyposes=report['maximum_amplitude_fit_at_all_four_keyposes'],not_deployed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  O.mkdir(exist_ok=True)
  with (O/('ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_retry=True),f,indent=2)
  raise
