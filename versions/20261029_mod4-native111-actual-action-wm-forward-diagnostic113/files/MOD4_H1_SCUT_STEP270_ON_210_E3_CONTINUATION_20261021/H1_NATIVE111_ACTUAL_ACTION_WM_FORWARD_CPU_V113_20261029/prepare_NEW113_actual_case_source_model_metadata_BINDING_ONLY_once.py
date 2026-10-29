from pathlib import Path
import json,hashlib,time
S=Path(__file__).resolve().parent;T=S.parent
B=T/"MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27";D=T/"H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029";L=T/"MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027";Q=L/"TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V3";R=S/"reports";R.mkdir(exist_ok=True)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
raws=read(D/"reports/FROZEN112_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json");case=read(D/"reports/FROZEN112_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json")
assert raws["passed"] and case["actual_finite_returned"] and case["actual_waited_exit"]==0 and case["actual_case_returned"] and not case["errors"] and case["case"]["passed"]
assert case["case"]["result"]["controls"]==2000 and case["case"]["result"]["physics_callbacks"]==8000
assert case["case"]["result"]["last_termination_terms"]["values"]["time_out"]
assert not any(v for k,v in case["case"]["result"]["last_termination_terms"]["values"].items() if k!="time_out")
row=next(x for x in raws["rows"] if x["relative"]=="case/episode/ACTUAL_100HZ_CONTROLS.jsonl");p=Path(row["local_path"])
assert p.resolve().is_relative_to(D.resolve()) and not p.is_symlink() and p.stat().st_size==row["bytes"]
eb=D/"EVAL_BINDING.json";er=next(x for x in raws["rows"] if x["relative"]=="EVAL_BINDING.json");assert H(eb)==er["SHA"];e=read(eb)
mf=B/"THREE_SLOT_COMPLETE_MANIFEST_V1.json";assert H(mf)==e["runtime_manifest_SHA"]
cpu=Q/"reports/NATIVE111_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json";qual=read(cpu)
assert qual["passed"] and qual["original_normal_duration_account_settled_and_allout"] and qual["fullfinite_modules_norms_threeopts_strict"]
assert qual["model"]["SHA"]=="24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12"
assert e["source_model"]["SHA"]==qual["model"]["SHA"] and e["max_controls"]==2000
model=Path(qual["model"]["local_path"]);assert model.stat().st_size==256235849
source_rows=[x for x in read(mf)["files"] if x["relative"].startswith("source/") and x["relative"].endswith(".py")]
for x in source_rows:assert H(B/x["relative"])==x["SHA"],x["relative"]
binding=dict(schema="mod4.NEW113.actual_action_world_X_velocity_CPU_diagnostic.v1",epoch=time.time(),purpose="NEW necessary teacher-forced worldX/worldVx1/8/32 diagnostic on NEW112 real trajectory; no stats/Git/policy/critic/GPU/physics",
 source_payload=str(B),manifest=str(mf),manifest_SHA=H(mf),source_PY_rows=source_rows,
 formal_local_path=str(model),formal_bytes=256235849,formal_SHA=qual["model"]["SHA"],qualified111_CPU=str(cpu),qualified111_CPU_SHA=H(cpu),
 expected_native_iteration=18597,expected_world_updates=185970,expected_policy_updates=17893,
 actual_case_report=str(D/"reports/FROZEN112_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json"),actual_case_report_SHA=H(D/"reports/FROZEN112_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json"),
 raw_control_producer=row,raw_new_explicit_read_budget=1,full_checkpoint_decode_budget=1,model_integrity_hash_passes=1,
 separate_normal86_file_reads=0,policy_critic_optimizer_construction_or_forward=False,models_and_normalizers_frozen=True,
 normalized_context_source="source/compact_episode_static31_v1.py normalize_static31 exact actual111 source; no substitute/current nominal context",
 declared_horizons=[1,8,32],window_selection="ALL exact contiguous valid starts, overlap explicit; actual actions and per-offset xi only; no resampled policy",
 CPU_wall_budget_seconds=480,required_environment=dict(CUDA_VISIBLE_DEVICES=""),not_population_or27cm_extrapolation=True,
 initial_local_source_read_errors=["Guessed source/sm_deps package path did not exist; rg --files found source/supermimic_wheel_leg_v3.", "Guessed native87_augmented_bridge file did not exist; actual Fudan import points native_wheel_leg_bridge_v4. No old model/raw touched."])
with (S/"PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json").open("x",encoding="utf8") as f:json.dump(binding,f,indent=2)
print(json.dumps(dict(prepared=True,source_PY_verified=len(source_rows),actual_model_or_raw_reads=0,binding_SHA=H(S/"PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json"))))

