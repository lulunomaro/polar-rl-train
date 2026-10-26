"""Constrained actual-demo retarget V2 using saved canonical pose/contact data only.

Preserves rejected V1. No source NPZ reread, actor, optimizer, dynamics or network.
Common limb excursion attenuation is explicit; L/R recorded height asymmetry is
kept, then own root Z is reconstructed from the recorded wheel-height path.
"""
from pathlib import Path
import hashlib,json,time,traceback
import numpy as np

from supermimic_reference_adapter_v1 import TaskspaceDemo,quat_to_mat,retarget_taskspace
from own_usd_closed_chain_ik_v1 import OwnUsdKinematics

HERE=Path(__file__).resolve().parent;J=HERE.parent;T=J.parent
PREVIOUS=HERE/"ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900"


def put(path,value):
    with Path(path).open("x",encoding="utf8") as stream:json.dump(value,stream,ensure_ascii=False,indent=2)


def main():
    trial="ACTUAL_FUDAN_CONSTRAINED_RETARGET_V2_"+str(time.time_ns());out=HERE/trial;out.mkdir(exist_ok=False)
    source_dir=out/"source_snapshot";source_dir.mkdir();source=[]
    for name in (Path(__file__).name,"supermimic_reference_adapter_v1.py","own_usd_closed_chain_ik_v1.py","reference_schema_v1.json"):
        data=(HERE/name).read_bytes();(source_dir/name).write_bytes(data)
        source.append(dict(path=str(source_dir/name),bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
    canonical=PREVIOUS/"upstream_actual_default_dt_standing_jump_CANONICAL_TASKSPACE_DEMO.json"
    config=dict(crop_start_source_s=1.,crop_end_source_s=3.6,target_control_dt_s=.01,
                common_limb_excursion_attenuation=.1,max_ik_iterations=40,
                source_wheel_radius_m=.06,own_onset_age_control=100,source_onset_sim_s=1.5)
    put(out/"STARTUP_CONTRACT.json",dict(trial_id=trial,source=source,configuration=config,
        canonical_input=dict(path=str(canonical),SHA256=hashlib.sha256(canonical.read_bytes()).hexdigest()),
        prior_rejected_trial_preserved=str(PREVIOUS),new_source_NPZ_reads=0,
        scope="actual demonstration retarget static kinematics, not own dynamics or skill acceptance",
        source_checkpoint_SHA="not_loaded_reference_provenance_only",git_archive_state="pending_root_stage_archive"))
    try:
        demo=TaskspaceDemo.from_dict(json.loads(canonical.read_text(encoding="utf8")))
        assets=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets"
        kin=OwnUsdKinematics.from_sources(assets/"robot.usd",T/"full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json",assets/"import_contract.json")
        task=retarget_taskspace(demo,kin.wheel_local(np.zeros(30)),[0,0,kin.source_metadata["nominal_spawn_height_m"]],
            target_control_dt_s=.01,start_s=1.,end_s=3.6,limb_excursion_attenuation=.1)
        task=kin.preserve_recorded_wheel_height_asymmetry(demo,task,source_wheel_radius_m=.06)
        seed=np.zeros(30);q=[];results=[];start=time.time()
        with (out/"OWN_STATIC_IK_ALL_FRAME_RESULTS.jsonl").open("x",encoding="utf8") as stream:
            for i,target in enumerate(task.wheel_local_m):
                fit=kin.solve(target,seed,max_iterations=40);seed=fit.joint_pos30.copy();q.append(seed);results.append(fit)
                stream.write(json.dumps(dict(trial_id=trial+f":frame{i:04d}",frame=i,time_s=float(task.time_s[i]),
                    target_wheel_local_m=target.tolist(),**fit.summary()))+"\n");stream.flush()
                if i%60==0:print(json.dumps(dict(frame=i,total=len(task.time_s),status=fit.status,wall_s=time.time()-start)),flush=True)
        q=np.stack(q);all_fit=all(row.status=="STATIC_KINEMATIC_FIT" for row in results)
        task,height=kin.reconstruct_root_height_from_recorded_wheel_path(demo,task,q,source_wheel_radius_m=.06)
        put(out/"OWN_RECONSTRUCTED_HEIGHT_APPROXIMATION.json",height)
        put(out/"CONSTRAINED_TASKSPACE_TARGETS.json",dict(metadata=task.metadata,time_s=task.time_s.tolist(),
            root_position_m=task.root_position_m.tolist(),root_quaternion_wxyz=task.root_quaternion_wxyz.tolist(),
            wheel_local_m=task.wheel_local_m.tolist(),wheel_contact=task.wheel_contact.tolist(),contact_phase=list(task.contact_phase)))
        # Small static skeleton coordinates are enough for a no-engine PNG/GIF.
        selected=[0,50,71,85,100,114,140,200,260];draw=[]
        r=quat_to_mat(task.root_quaternion_wxyz)
        for i in selected:
            poses=kin.forward(q[i]);world={name:(r[i]@poses[name][:3,3]+task.root_position_m[i]).tolist() for name in kin.body_names}
            anchors=[dict(name=row["name"],parent=row["parent"],child=row["child"],
                          parent_point=(r[i]@(poses[row["parent"]]@row["T0"])[:3,3]+task.root_position_m[i]).tolist(),
                          child_point=(r[i]@(poses[row["child"]]@row["T1"])[:3,3]+task.root_position_m[i]).tolist()) for row in kin.closures]
            draw.append(dict(frame=i,reference_time_s=float(task.time_s[i]),source_time_s=float(task.time_s[i]+1),
                             own_age_control=float((task.time_s[i]-.5)/.01+100),body_world_m=world,closures=anchors,
                             joint_pos30=q[i].tolist(),status=results[i].status))
        put(out/"STATIC_KINEMATIC_DRAW_DATA.json",dict(frames=draw,body_names=list(kin.body_names),
            tree_edges=[[row["parent"],row["child"]] for row in kin.joints],
            own_wheel_radius_m=kin.source_metadata["actual_own_wheel_collision_radius_m"],
            source_canonical_path=str(canonical),own_height_approximation=height,
            not_own_dynamics_or_skill_success=True))
        native=None
        if all_fit:
            reference=kin.to_native_reference(task,q,results,source_jump_validation=demo.source["source_jump_validation"])
            reference=reference.align_control_clock(native_frame_anchor=100,reference_time_anchor_s=.5)
            path=out/"H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73.json";put(path,reference.as_dict())
            native=dict(path=str(path),bytes=path.stat().st_size,SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        schema="mod4.supermimic.native_reference.v1",sdk_joint_order_verified=False,
                        source_jump_trigger_sim_s=1.5,own_jump_onset_age_control=100,own_jump_onset_s=1.,
                        initial_hold_until_own_age_control=50,then_interpolate=True)
        report=dict(trial_id=trial,status="STATIC_ALL_FRAMES_FIT_NATIVE_PARTIAL_REFERENCE_EXPORTED" if native else "PENDING_NATIVE_REFERENCE_NOT_EXPORTED",
            configuration=config,source_canonical_path=str(canonical),source_original_NPZ_SHA256=demo.source["artifact_sha256"],
            prior_rejected_trial=str(PREVIOUS),prior_result_retained="111_of_201_direct_frames_fit_90_fail_no_native_export",
            frames=len(results),fit_frames=sum(x.status=="STATIC_KINEMATIC_FIT" for x in results),
            failed_frames=[i for i,x in enumerate(results) if x.status!="STATIC_KINEMATIC_FIT"],
            closure_error_max_m=max(x.closure_error_max_m for x in results),wheel_fit_error_max_m=max(x.wheel_error_max_m for x in results),
            own_vs_recorded_scaled_wheel_bottom_error_max_m=height["maximum_abs_wheel_bottom_reference_error_m"],
            root_height_range_m=[float(task.root_position_m[:,2].min()),float(task.root_position_m[:,2].max())],
            source_shape_common_excursion_distortion="0.1 amplitude after prior rest-length normalization; 0.9 removed, explicit own-limit retarget",
            lateral_wheel_height_asymmetry="recorded difference retained separately before own IK",
            root_height="from_recorded_ground_relative_wheel_height_displacement_plus_own_collision_FK_not_invented_step",
            own_collision_and_motor_dynamics="pending_not_tested",source_contact_is_not_actual_own_contact=True,
            own_H1_step270_forward_arrival_topcontact_recovery="not_demonstrated",physical_V8_commands_success_WM_sources="unchanged",
            native_runtime_loss_and_fullsave_GO="pending_root_protocol",native_reference=native,wall_s=time.time()-start,
            git_archive_state="pending_root_stage_archive")
        put(out/"ACTUAL_CONSTRAINED_RETARGET_CPU_RESULT.json",report)
        print(json.dumps(dict(out=str(out),status=report["status"],fit_frames=report["fit_frames"],frames=len(results),native=native)),flush=True)
    except BaseException:
        put(out/"ACTUAL_CONSTRAINED_RETARGET_ORIGINAL_ERROR.json",dict(trial_id=trial,error=traceback.format_exc(),
            all_partial_files_preserved=True,git_archive_state="pending_root_stage_archive"));raise


if __name__=="__main__":main()
