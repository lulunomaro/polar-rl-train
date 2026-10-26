"""Freeze helper source/lineage/attempts for root's ordinary Git supplement. No Git."""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent;T=HERE.parent.parent
PAYLOAD=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/e2"
SOURCE=PAYLOAD/"job0/runtime/isaac/mod4"


def item(path):
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def put(path,value):
    with path.open("x",encoding="utf8") as f:json.dump(value,f,ensure_ascii=False,indent=2)


def main():
    stamp=str(time.time_ns());lineage_dir=HERE/("ORIGINAL_E2_SOURCE_LINEAGE_"+stamp);lineage_dir.mkdir(exist_ok=False)
    names=("e2_directional_spin_runtime_v1.py","spin_translation_math.py","e2_h1_flat_environment_v1.py",
           "e2_command_checkpoint_v1.py","contact_capture.py","mod4_env.py","mod4_task.py","scut_flat_rescue.py",
           "world_drift_reward.py","world_drift_isaac.py","physics_clock.py","chassis_pd_training_env.py","train_E2_full_resume_v1.py")
    source=[]
    for name in names:
        path=SOURCE/name;raw=path.read_bytes();archived=lineage_dir/(name+".original_source_bytes.txt")
        with archived.open("xb") as f:f.write(raw)
        source.append(dict(**item(path),preserved_path=str(archived)))
    env_path=SOURCE/"env.json";env=json.loads(env_path.read_text(encoding="utf8"))
    allowed=("RM_SPIN_STAGE","RM_SPIN_MAX_RAD_S","RM_PURE_SPIN_FRACTION","RM_MOVING_SPIN_FRACTION",
      "RM_SPIN_TRANSITION_WITHIN_PURE","RM_SPIN_WORLD_PROGRESS_M_S","RM_SPIN_BODY_SPEED_LIMIT_M_S","RM_WORLD_DRIFT_PROFILE",
      "RM_PHYSICS_DT_S","RM_NOMINAL_HEIGHT","RM_CONTACT_INTEGRATED","RM_CONTACT_EAGER5MS","RM_MOD4_TERRAIN")
    delivery_path=PAYLOAD/"job0/runtime/train/deploy/contract_rm2025_later.json"
    delivery=json.loads(delivery_path.read_text(encoding="utf8"))
    historical_path=PAYLOAD/"job0/TASK.json";historical=json.loads(historical_path.read_text(encoding="utf8"))
    cpu_report=HERE/"E2_NATIVE_SOURCE_CPU_1793008998304094700/E2_NATIVE_SOURCE_CPU_RESULT.json"
    first_report=HERE/"E2_NATIVE_SOURCE_CPU_1793008909524345900/E2_NATIVE_SOURCE_CPU_RESULT.json"
    candidate=[item(HERE/name) for name in ("e2_native_supermimic_candidate_v1.py","e2_source_readonly_adapter_v1.py","test_e2_native_source_cpu_v1.py","e2_reference_schema_v1.json")]
    manifest=dict(schema="mod4.e2.source_CPU_admission_bundle.v1",status="SOURCE_CPU_READY_RUNTIME_AND_GO_PENDING",
      source_kind="E2_WORLD_MOVING_SIGNED4",qualified_complete83B_source_from_root=dict(updates=90,Adam=857460,
        SHA256="72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f",model_not_opened_or_hashed=True),
      historical_payload_TASK=dict(**item(historical_path),source_SHA=historical["source_SHA"],
        source_updates=historical.get("source_owned_completed_updates"),not_later_complete83B_identity=True),
      original_source=source,source_env=dict(**item(env_path),only_allowlisted_nonsecret_fields_preserved={k:env[k] for k in allowed if k in env}),
      delivery_contract=dict(**item(delivery_path),fields={k:delivery[k] for k in ("policy_hz","leg_action_scale","wheel_action_scale","leg_kp","leg_kd","wheel_kd")}),
      candidate_source=candidate,passed_CPU_report=item(cpu_report),original_failed_CPU_report=item(first_report),
      source_and_native_counts=dict(original_PPO_actor175_critic98=True,native_context93=True,native_obs175_history10=True,native_critic_base170_with_goal243=True,
        equal_obs_count_is_coincidence_no_weight_compatibility=True),
      reference="declared_command_kinematic_hypothesis_not_measured_demonstration",
      preGO_pending=["actual qualified complete checkpoint/full private-state writer lineage",
        "actual SDK joint names, current delay queues/processed target fields and pre-reset ingress callback timing",
        "actual public phase/resampling clock contract at50Hz and source physics2.5msx8",
        "bounded plan-book capacity/replay lifetime and cross-device live-book synchronization",
        "complete native learner/reference-book/bridge save and failed-partial protocol",
        "own dynamic feasibility and explicit original-writer Task_GO within existing budget"],
      original_physical_command_action_clip_PD_delay_DR_rewards_success="unchanged",
      H1_Fudan_and_mixed84_frozen_files="not_modified",E0_W35_and_current_qualified_experts="retained",
      no_actual_models_checkpoints_raw_NPZ_actor_optimizer_RNG_GPU_plant_remote_or_budget_writer=True,
      numerical_guards="existing native_float32_160kquery_2mm_perenv_reset_reused_no_extra_global_gate",
      source_frozen_after_this_handoff=True,git_archive_state="pending_root_ordinary_supplement_not_claimed_recorded")
    manifest_path=HERE/("E2_SOURCE_CPU_ADMISSION_MANIFEST_"+stamp+".json");put(manifest_path,manifest)
    files=[]
    for path in sorted(HERE.rglob("*")):
        if path.is_file():
            row=item(path);row["relative_path"]=str(path.relative_to(HERE));row["archive"]= "index_only_regenerable_bytecode" if path.suffix==".pyc" else "include_source_report_or_small_artifact"
            files.append(row)
    index=HERE/("E2_COMPLETE_ARCHIVE_INDEX_"+stamp+".json")
    put(index,dict(schema="mod4.e2.complete_helper_archive_index.v1",files=files,admission_manifest=item(manifest_path),
        preserve_all_failed_and_success_reports=True,index_itself_must_be_in_root_supplement=True,
        no_Git_or_external_state_action_by_helper=True,git_archive_state="pending_root_ordinary_supplement"))
    print(json.dumps(dict(admission_manifest=item(manifest_path),archive_index=item(index),candidate_source=candidate,
        passed_CPU_report=item(cpu_report),files=len(files),source_frozen=True)))


if __name__=="__main__":main()
