"""Add truthful ascent-only height/vZ supervision to the saved actual own reference.
Preserve all raw V2 states; elevated landing is a separate OWN task term.
"""
from pathlib import Path
import hashlib,json,time,traceback
import numpy as np
from supermimic_reference_adapter_v1 import NativeReference,with_partial_step270_phase_contract

HERE=Path(__file__).resolve().parent
V2=HERE/"ACTUAL_FUDAN_CONSTRAINED_RETARGET_V2_1793005471832546700"
CANONICAL=HERE/"ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/upstream_actual_default_dt_standing_jump_CANONICAL_TASKSPACE_DEMO.json"


def put(path,data):
    with Path(path).open("x",encoding="utf8") as stream:json.dump(data,stream,ensure_ascii=False,indent=2)


def main():
    trial="ACTUAL_PARTIAL_STEP270_PHASE_V3_"+str(time.time_ns());out=HERE/trial;out.mkdir(exist_ok=False)
    try:
        snapshot=out/"source_snapshot";snapshot.mkdir();sources=[]
        for name in (Path(__file__).name,"supermimic_reference_adapter_v1.py","own_usd_closed_chain_ik_v1.py","test_reference_contract_cpu_v1.py","reference_schema_v1.json"):
            data=(HERE/name).read_bytes();(snapshot/name).write_bytes(data)
            sources.append(dict(path=str(snapshot/name),bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
        previous=V2/"H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73.json"
        ref=NativeReference.from_dict(json.loads(previous.read_text(encoding="utf8")))
        demo=json.loads(CANONICAL.read_text(encoding="utf8"));t=np.asarray(demo["time_s"]);bottom=np.asarray(demo["wheel_bottom_world_z_m"])
        window=np.flatnonzero((t>=1.5)&(t<=2.1));apex=int(window[np.argmax(bottom[window].min(-1))])
        source_apex=float(t[apex]);cutoff=source_apex-float(ref.metadata["source_clock"]["crop_start_source_s"])
        ref=with_partial_step270_phase_contract(ref,measured_ascent_end_reference_time_s=cutoff,
            own_step_edge_x_m=.35,own_platform_height_m=.27,
            own_nominal_chassis_height_m=ref.metadata["own_geometry"]["nominal_spawn_height_m"],
            own_support_region_transition_m=ref.metadata["own_geometry"]["actual_own_wheel_collision_radius_m"])
        ref.metadata["partial_phase_source_evidence"]=dict(source_canonical_path=str(CANONICAL),source_apex_row=apex,
            source_sim_apex_time_s=source_apex,reference_apex_time_s=cutoff,
            own_apex_age_control=(cutoff-float(ref.metadata["native_frame_zero_reference_time_s"]))/ref.metadata["target_control_dt_s"],
            original_source_NPZ_SHA256=demo["source"]["artifact_sha256"],
            source_flat_return_preserved_as_raw_evidence_but_excluded_from_elevated_landing_supervision=True)
        path=out/"H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json";put(path,ref.as_dict())
        report=dict(trial_id=trial,status="PARTIAL_PHASE_CONTRACT_DECLARED_CPU_LOSS_PROOF_PENDING",
            native_reference=dict(path=str(path),bytes=path.stat().st_size,SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),schema="mod4.supermimic.native_reference.v1"),
            previous_raw_kinematic_artifact=dict(path=str(previous),SHA256=hashlib.sha256(previous.read_bytes()).hexdigest(),preserved=True),
            source=sources,phase_contract=ref.metadata["partial_phase_contract"],phase_evidence=ref.metadata["partial_phase_source_evidence"],
            all261_raw_states_unchanged=True,raw_state_shape=list(ref.states.shape),sdk_joint_order_verified=False,
            source_height_vz_after_apex="masked_in_goals_and_imagination_loss",
            own_task_landing="nominal_own_height_plus_actual0.270m_after_source_ascent_in_own_step_region_not_foreign_evidence",
            physical_V8_commands_success_and_WM_sources="unchanged",runtime_loss_fullsave_GO="pending_root_protocol",
            dynamic_collision_motor_and_skill_acceptance="pending",git_archive_state="pending_root_stage_archive")
        put(out/"ACTUAL_PARTIAL_PHASE_CONTRACT_V3_RESULT.json",report)
        print(json.dumps(dict(out=str(out),native=report["native_reference"],cutoff_reference_s=cutoff,source_apex_sim_s=source_apex)))
    except BaseException:
        put(out/"PARTIAL_PHASE_CONTRACT_ORIGINAL_ERROR.json",dict(error=traceback.format_exc(),git_archive_state="pending_root_stage_archive"));raise


if __name__=="__main__":main()
