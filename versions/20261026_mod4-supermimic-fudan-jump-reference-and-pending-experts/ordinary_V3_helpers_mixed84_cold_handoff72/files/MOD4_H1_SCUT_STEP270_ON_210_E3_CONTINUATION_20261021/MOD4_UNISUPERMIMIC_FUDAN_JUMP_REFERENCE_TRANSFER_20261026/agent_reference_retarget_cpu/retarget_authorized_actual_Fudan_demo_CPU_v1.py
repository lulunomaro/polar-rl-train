"""Read root-authorized NEW captures once; preserve source validation and static fits.

No policy/model content, actor, optimizer, RNG, dynamics, GPU, remote/network or Git.
Every invocation is a new independent CPU trial folder; all errors/fits are kept.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys,time,traceback
import numpy as np

from supermimic_reference_adapter_v1 import (
    FUDAN_COMMIT,angular_velocity_world,derivative,import_new_fudan_capture,
    quat_to_mat,retarget_taskspace,
)
from own_usd_closed_chain_ik_v1 import OwnUsdKinematics

HERE=Path(__file__).resolve().parent;J=HERE.parent;T=J.parent


def put(path,value):
    with Path(path).open("x",encoding="utf8") as stream:json.dump(value,stream,ensure_ascii=False,indent=2)


def segments(mask,times):
    result=[];start=None;dt=float(np.median(np.diff(times)))
    for i,yes in enumerate(np.r_[mask,False]):
        if yes and start is None:start=i
        if not yes and start is not None:
            result.append(dict(start_row=start,end_row=i-1,start_s=float(times[start]),
                               end_s=float(times[i-1]),observed_duration_s=float(times[i-1]-times[start]+dt),rows=i-start))
            start=None
    return result


def analyze_source(demo):
    t=demo.time_s;r=quat_to_mat(demo.chassis_quaternion_wxyz)
    v=derivative(demo.chassis_position_m,t);w=angular_velocity_world(demo.chassis_quaternion_wxyz,t)
    tilt=np.degrees(np.arccos(np.clip(r[:,2,2],-1,1)))
    pre=(t>=1.)&(t<1.4);jump=(t>=1.5)&(t<=2.1)
    both=demo.wheel_contact.all(-1);air=~demo.wheel_contact.any(-1)
    baseline=float(np.median(demo.wheel_bottom_world_z_m[pre].min(-1)))
    flights=segments(air,t);supports=segments(both,t)
    jump_flights=[s for s in flights if s["end_s"]>=1.5 and s["start_s"]<=2.1]
    primary=max(jump_flights,key=lambda x:x["observed_duration_s"]) if jump_flights else None
    touchdown=None;hold=None
    if primary is not None:
        after=np.flatnonzero(both&(t>primary["end_s"]))
        if len(after):
            i=int(after[0]);touchdown=float(t[i]);window=(t>=touchdown)&(t<touchdown+.5)
            hold=dict(start_s=touchdown,requested_window_s=.5,available_observed_rows=int(window.sum()),
                      both_contact_fraction=float(both[window].mean()),tilt_max_deg=float(tilt[window].max()),
                      linear_speed_max_m_s=float(np.linalg.norm(v[window],axis=-1).max()),
                      linear_speed_p95_m_s=float(np.quantile(np.linalg.norm(v[window],axis=-1),.95)),
                      angular_speed_max_rad_s=float(np.linalg.norm(w[window],axis=-1).max()),
                      not_our_callback_stable_recovery_acceptance=True)
    clearance=demo.wheel_bottom_world_z_m.min(-1)-baseline
    observed_jump=bool(primary is not None and primary["observed_duration_s"]>.1 and clearance[jump].max()>.05)
    result=dict(source=demo.source,clock=demo.clock,rows=len(t),
                sample_dt_min_s=float(np.diff(t).min()),sample_dt_max_s=float(np.diff(t).max()),
                sample_dt_median_s=float(np.median(np.diff(t))),
                initial_supported_bottom_world_z_m=baseline,
                source_starts_on_original_surface_not_our_ground_or_step=True,
                pre_window=dict(start_s=1.,end_s=1.4,both_contact_fraction=float(both[pre].mean()),
                                tilt_max_deg=float(tilt[pre].max()),linear_speed_max_m_s=float(np.linalg.norm(v[pre],axis=-1).max())),
                observed_jump_candidate=observed_jump,source_jump_validation="observed_jump_validated" if observed_jump else "pending_or_no_observed_jump",
                source_jump_evidence_rule="contact_absence_over_0.1s_overlaps_original_1.5_to_2.1s_trigger_and_bothwheel_relative_clearance_exceeds_0.05m; this labels_source_jump_only",
                primary_jump_flight=primary,all_both_air_segments=flights,all_both_support_segments=supports,
                first_returned_both_support_s=touchdown,first_returned_support_half_second_diagnostics=hold,
                minimum_two_wheel_relative_clearance_peak_m=float(clearance.max()),
                root_displacement_world_m=(demo.chassis_position_m[-1]-demo.chassis_position_m[0]).tolist(),
                jump_tilt_max_deg=float(tilt[jump].max()),
                post3s=dict(both_contact_fraction=float(both[t>=3].mean()),tilt_max_deg=float(tilt[t>=3].max()),
                            speed_p95_m_s=float(np.quantile(np.linalg.norm(v[t>=3],axis=-1),.95)),
                            angular_speed_p95_rad_s=float(np.quantile(np.linalg.norm(w[t>=3],axis=-1),.95))),
                source_landing_stability="diagnostics_only_no_frozen_or_own_270mm_recovery_certification",
                own_H1_step270_coverage=False,source_highest_peak_is_not_selection_rule=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument("--crop-start",type=float,default=1.);p.add_argument("--crop-end",type=float,default=3.)
    p.add_argument("--max-ik-iterations",type=int,default=40);args=p.parse_args()
    trial="ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_"+str(time.time_ns());out=HERE/trial;out.mkdir(exist_ok=False)
    src=out/"source_snapshot";src.mkdir()
    source=[]
    for filename in (Path(__file__).name,"supermimic_reference_adapter_v1.py","own_usd_closed_chain_ik_v1.py","reference_schema_v1.json"):
        data=(HERE/filename).read_bytes();(src/filename).write_bytes(data)
        source.append(dict(path=str(src/filename),bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
    put(out/"STARTUP_CONTRACT.json",dict(trial_id=trial,epoch=time.time(),configuration=vars(args),source=source,
        checkpoint_SHA="no_checkpoint_loaded_or_needed_for_reference_CPU_work",physics_changed=False,
        no_foreign_policy_execution_no_old_raw_read_no_optimizer_no_GPU_no_network_no_Git=True,
        actual_reference_artifacts_explicitly_authorized_by_root=True,git_archive_state="pending_root_stage_archive"))
    try:
        producer_path=J/"reports/FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_FINITE_RETURNED_ACTUAL.json"
        summary_path=J/"actual_72_reference_text/reference_capture/BOUNDED_FUDAN_JUMP_REFERENCE_CASES_CPU_ACTUAL.json"
        producer=json.loads(producer_path.read_text(encoding="utf8"));summaries=json.loads(summary_path.read_text(encoding="utf8"))
        artifacts={Path(row["local_path"]).parent.name:row for row in producer["small_artifacts"]}
        xml=J/"source/mujoco/assert_now/infantry_binglian_yuntai/infantry_V2/meshes/mjmodel.xml"
        demos={};analyses={}
        for case in summaries["cases"]:
            name=case["case"]["name"];artifact=artifacts[name]
            receipt=dict(new_capture_explicitly_authorized=True,two_host_sha_verified=artifact["twohost_complete_SHA"],
                         source_commit=FUDAN_COMMIT,artifact_path=artifact["local_path"],artifact_sha256=artifact["SHA"],
                         source_jump_validation="pending_source_pose_contact_review",producer_report=str(producer_path))
            demo=import_new_fudan_capture(artifact["local_path"],xml,receipt,case)
            analysis=analyze_source(demo);demo.source["source_jump_validation"]=analysis["source_jump_validation"]
            demos[name]=demo;analyses[name]=analysis
            put(out/(name+"_CANONICAL_TASKSPACE_DEMO.json"),demo.as_dict())
            put(out/(name+"_SOURCE_POSE_CONTACT_VALIDATION.json"),analysis)
        name="upstream_actual_default_dt_standing_jump";demo=demos[name]
        assets=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets"
        kin=OwnUsdKinematics.from_sources(assets/"robot.usd",T/"full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json",assets/"import_contract.json")
        task=retarget_taskspace(demo,kin.wheel_local(np.zeros(30)),[0,0,kin.source_metadata["nominal_spawn_height_m"]],
                               target_control_dt_s=.01,start_s=args.crop_start,end_s=args.crop_end)
        put(out/"PRIMARY_TASKSPACE_TARGETS_BEFORE_IK.json",dict(metadata=task.metadata,time_s=task.time_s.tolist(),
            root_position_m=task.root_position_m.tolist(),root_quaternion_wxyz=task.root_quaternion_wxyz.tolist(),
            wheel_local_m=task.wheel_local_m.tolist(),wheel_contact=task.wheel_contact.tolist(),contact_phase=list(task.contact_phase)))
        q=[];results=[];seed=np.zeros(30);start=time.time()
        with (out/"OWN_STATIC_IK_ALL_FRAME_RESULTS.jsonl").open("x",encoding="utf8") as stream:
            for i,target in enumerate(task.wheel_local_m):
                fit=kin.solve(target,seed,max_iterations=args.max_ik_iterations);seed=fit.joint_pos30.copy();q.append(seed);results.append(fit)
                row=dict(trial_id=trial+f":frame{i:04d}",frame=i,time_s=float(task.time_s[i]),target_wheel_local_m=target.tolist(),**fit.summary())
                stream.write(json.dumps(row)+"\n");stream.flush()
                if i%40==0:print(json.dumps(dict(frame=i,total=len(task.time_s),status=fit.status,wall_s=time.time()-start)),flush=True)
        all_fit=all(r.status=="STATIC_KINEMATIC_FIT" for r in results);native=None;native_error=None
        if all_fit:
            try:
                reference=kin.to_native_reference(task,np.stack(q),results,source_jump_validation=analyses[name]["source_jump_validation"])
                path=out/"H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73.json";put(path,reference.as_dict())
                native=dict(path=str(path),bytes=path.stat().st_size,SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            schema="mod4.supermimic.native_reference.v1",full_task_coverage=False,sdk_joint_order_and_phase_anchor_pending=True)
            except BaseException:
                native_error=traceback.format_exc();put(out/"NATIVE_EXPORT_ORIGINAL_ERROR.json",dict(error=native_error))
        report=dict(trial_id=trial,status="STATIC_ALL_FRAMES_FIT_NATIVE_PARTIAL_REFERENCE_EXPORTED" if native else "PENDING_NATIVE_REFERENCE_NOT_EXPORTED",
            original_source_case=name,source_artifact=artifacts[name],source_validation=analyses[name],
            selection="actual_original_2ms_case_with_returned_support_not_highest_peak_5ms_case",
            crop_source_s=[args.crop_start,args.crop_end],target_control_dt_s=.01,frames=len(results),
            fit_frames=sum(r.status=="STATIC_KINEMATIC_FIT" for r in results),failed_frames=[i for i,r in enumerate(results) if r.status!="STATIC_KINEMATIC_FIT"],
            closure_error_max_m=max(r.closure_error_max_m for r in results),wheel_fit_error_max_m=max(r.wheel_error_max_m for r in results),
            all_original_frame_errors_preserved=True,ik_wall_s=time.time()-start,native_reference=native,native_export_error=native_error,
            actual_SDK_joint_order="pending_runtime_named_reorder",reference_phase_anchor="pending_explicit_native_H1_alignment",
            own_collision_and_motor_dynamics="pending_no_plant_sampling_performed",native_runtime_loss_GO="pending_not_authorized_by_CPU_report",
            H1_270mm_dualwheel_cross_topcontact_recovery="not_demonstrated",other_skill_groups="registry_only_pending_demonstrations",
            physical_V8_reward_commands_success_and_WM_real_transition_sources="unchanged",
            git_archive_state="pending_root_stage_archive")
        put(out/"ACTUAL_REFERENCE_RETARGET_CPU_RESULT.json",report)
        print(json.dumps(dict(out=str(out),status=report["status"],frames=len(results),fit_frames=report["fit_frames"],native=native)),flush=True)
    except BaseException:
        put(out/"ACTUAL_REFERENCE_RETARGET_ORIGINAL_ERROR.json",dict(trial_id=trial,error=traceback.format_exc(),
            original_sources_and_partial_results_preserved=True,git_archive_state="pending_root_stage_archive"));raise


if __name__=="__main__":main()
