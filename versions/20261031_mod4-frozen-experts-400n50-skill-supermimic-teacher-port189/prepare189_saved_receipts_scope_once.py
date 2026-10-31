"""Materialize the newly authorized continuation from saved small text only."""
from pathlib import Path
import hashlib
import json
import time

B = Path(__file__).resolve().parent
T = B.parent
W = T.parent
L = T / "MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027"
R = B / "reports"
R.mkdir(exist_ok=True)
marker = R / "PREPARE189_SAVED_TEXT_STARTED.json"
with marker.open("x", encoding="utf8") as file:
    json.dump(dict(epoch=time.time(), purpose="new human background continuation"), file)

evidence = []
def read(path):
    path = Path(path)
    assert path.suffix.lower() in (".json", ".md", ".py")
    raw = path.read_bytes()
    evidence.append(dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest()))
    return json.loads(raw.decode("utf-8-sig")) if path.suffix == ".json" else raw.decode("utf-8-sig")

formal_paths = {
    "E0": T / "MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V2.json",
    "W35": L / "W35_fixed92_NEW_FINAL_whole_CPU_reviewer_v1/W35_FIXED92_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V2.json",
    "E2": T / "MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/reports/E2_93_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json",
    "E3": L / "TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1/reports/E3_97_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json",
}
review_paths = {
    "E0": L / "E0_82_NEW86_EARLY_RESAMPLE_FULL1000_SAVED_TEXT_REVIEW_20261029_V2/HANDOFF_FROZEN_E0V2_FULL1000_SAVED_TEXT_REVIEW.md",
    "W35": L / "W35_UID_CYCLE_V2_FULL800_COMMAND_UID_CYCLE_SAVED_TEXT_REVIEW_20261030_V1/HANDOFF_W35_FULL800_UID_CYCLE_TEXT_REVIEW.md",
    "E2": L / "E2_V5_FINAL_EARLY_COMMAND_SAVED_TEXT_REVIEW_20261029_V1/HANDOFF_FROZEN_E2_V5_SAVED_TEXT_COMPLETE_COMMAND_PROFILE_REVIEW.md",
    "E3": L / "E3_CONCRETE_INSTANCE_OWNER_EFFORT_GAP_PLAN_SOURCE_20261030_V14/HANDOFF_FROZEN_CONCRETE_INSTANCE_OWNER_EFFORT_BOUNDARY_PLAN_NO_RUNTIME_CALLER.md",
}
master = read(W / "polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md")
assert "tol=max(0.03,0.1V)" in master and "±0.2 rad/s" in master
partial = read(L / "FROZEN_EXPERTS_REMAINING40050_METADATA_INVENTORY_SOURCE_V1/build_bounded_existing_text_catalog_once_v1.py")
assert "CURB_SLOPE" in partial
flat = read(L / "FROZEN_FLAT_E0_IDENTITY_REFERENCE_SUPERSEDED_RESTART_20261031_V1/FROZEN_FLAT_E0_EXACT_IDENTITIES_AND_SAVED_BEHAVIOR_REFERENCE.json")
rows = []
expected = dict(E0=("a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a", 641200),
                W35=("ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f", 648360),
                E2=("b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1", 859300),
                E3=("1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8", 866060))
for expert in expected:
    data = read(formal_paths[expert])
    text = read(review_paths[expert])
    sha, adam = expected[expert]
    assert data["passed"] and data["model"]["SHA"] == sha
    rows.append(dict(expert=expert, formal=dict(data["model"]), Adam17=adam,
                     nominal_gas_N=400, policy_Hz=50, physics_us=2500, feedback_Hz=100,
                     formal_format_passed=True, full_skill_accepted=False,
                     native_SuperMimic_port_admitted=False,
                     saved_behavior_review=str(review_paths[expert]),
                     review_text_retained=True))

def put(name, value):
    with (R / name).open("x", encoding="utf8") as file:
        json.dump(value, file, indent=2, ensure_ascii=False)

put("EXPERT189_SAVED_FORMALS_AND_SKILL_GAPS_ACTUAL.json", dict(
    epoch=time.time(), schema="mod4.experts189.saved_scope.v1", experts=rows,
    historical18_is_E0_evaluation_matrix_not18_actors=True,
    remaining_source_lineages=["H1_normal_PPO86B", "E1_CURB20", "E1_SLOPE5"],
    lineage_scope="Saved leads; must join actual later producer before selection; not global latest",
    preserved_original_world_criteria=dict(along_cross_tol="max(0.03,0.1V)",
                                          signed_yaw_tolerance_rad_s=0.2,
                                          requires_complete_same_command_signed_cycles=True),
    no_new_arbitrary_aggregate_pass_rate=True,
    physical_gates=dict(closure_per_env_m=0.002, mimic_rad=0.01,
                        physics_us=2500, TGS=[32, 4], dtype="F32"),
    evidence=evidence, referenced_models_raw_or_NPZ_opened=0,
    earlier_local_reader_errors=[
        dict(kind="bounded workspace file search access denied", path="rmuc2026_work/unpack_verify_4zomhj13", scope="unrelated directory; narrowed to known source roots"),
        dict(kind="source lookup missing", path="E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1/e0_original_profile_catalog_candidate_v1.py", scope="no execution; not a robot failure"),
        dict(kind="tool output truncated", scope="Full allowlisted JSON/text parsed here; no decision from truncated value")]))

model = rows[0]["formal"]
put("E0_189_NEW_CPU_TEACHER_PORT_READ_ONCE_ADMISSION_FROZEN.json", dict(
    schema="mod4.experts189.E0_teacher_CPU_purpose.v1", epoch=time.time(),
    purpose="New authorized E0 teacher-to-native action supervision component, not model statistics or Git",
    expert="E0", source=model, original_whole_CPU_receipt=str(formal_paths["E0"]),
    allowed=dict(checkpoint_byte_opens=1, checkpoint_full_forward_byte_passes=1,
                 checkpoint_decodes=1, deterministic_source_CPU_probe_rows=72,
                 old_raw_NPZ_opens=0, normal86_witness_opens=0,
                 SDK_imports=0, remote_connections=0, CUDA=0, optimizer_steps=0),
    checks=["source identity", "PPO35 256/128/64 ELU keyset and saved tensor fingerprints",
            "unchanged teacher, STD and RNG", "raw6 to original clip6 labeling",
            "student raw-action gradient including outside clip", "50Hz real-terminal pair boundaries"],
    synthetic_probes_not_physical_behavior_or_skill_acceptance=True,
    output="ROOT189_E0_NEW_CPU_TEACHER_PORT_RETURNED_ACTUAL.json"))

put("CURRENT189_BACKGROUND_EXPERT_SKILL_AND_SUPERMIMIC_WORK_ORDER.json", dict(
    epoch=time.time(), human_instruction="后台继续完成归一化完整技能验收和supermimic化",
    authorized=True, no_new_automation_or_Goal=True,
    current188_training_preserved=True, no_current_new_expert_learning=True,
    priority=["E0 native teacher binding and measured rollout collector",
              "E0 retained skill matrix and missing per-cycle acceptance",
              "W35/E2 complete cycle evidence and retained original criteria",
              "E3 genuine full recovery and control-chain closure",
              "remaining complete CURB/SLOPE source joins and 400N50 adaptation",
              "per-expert native students then actual original-plant skill retention"],
    next_local="run189_E0_CPU_teacher_port_once.py",
    next_remote="NOT_READY: separately freeze actual E0 runtime observation/native127+xi31 callback collector; current files are components only",
    native_conversion=dict(method="Frozen PPO teacher -> measured own-MOD4 transitions and action labels -> separate native WM/Pi/Critic training",
                           model_rename_or_parameter_copy_is_not_conversion=True,
                           WM_truth="Only original own PhysX at50Hz, true pre-reset endpoint and actual eight-callback target queues",
                           teacher_policy35="Original processed runtime observation, no guessed reconstruction or re-normalization",
                           old_H1_WM100Hz_not_50Hz_truth=True,
                           frozen_PPO_remains_usable_and_unchanged=True,
                           source_student_model_and_full_learning_caller_pending=True),
    authority="Any future remote: fresh exact local CIM, sole global serial lease, fresh72 active188 or CNone then CLOSE72 before target; learning only original sole72 writer/caps/budget",
    pending_Git="Capture all new189 source/false/actual CPU/workorder + automation receipt; no model/raw read for Git"))
print(json.dumps(dict(passed=True, saved_formals=4, new_model_opens=0,
                      E0_CPU_read_purpose_frozen=True, workorder=str(R / "CURRENT189_BACKGROUND_EXPERT_SKILL_AND_SUPERMIMIC_WORK_ORDER.json"))))
