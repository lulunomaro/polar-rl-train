from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
required=[*sorted((S/"code").glob("*.py")),S/"run_NEW112_qualified111_fixed20s_Fudan270_motion_paired_WM_UNUSED_once.py",S/"verify_SOURCE112_actual_phase_and_contiguous_window_CPU_synthetic_UNUSED_once.py"]
for p in required:ast.parse(p.read_text(encoding="utf8"))
entry=required[-2].read_text(encoding="utf8");helper=(S/"code/run_native112_frozen_flat_WM_N1_once.py").read_text(encoding="utf8");driver=(S/"code/fudan112_frozen_diag_driver_v1.py").read_text(encoding="utf8")
assert "MOD4_H1_FUDAN270_REWARD_COHERENCE_2610v111/seed27" in entry
assert "NATIVE111_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json" in entry
assert "native['iteration']==18597" in helper and "publication['world_updates']==185970" in helper and "publication['policy_updates']==17893" in helper
assert helper.count("torch.load(")==1
assert "input_phase=phases[start-1] if start>0 else None" in driver and "input_supported and not input_air and any(air)" in driver
assert "actor_obs86_for_action=obs[0]" in driver and "raw_original_command3" in driver
assert "actual_executed_actions_only=True" in driver and "no_actor_resampling_or_observation_noise_in_validation=True" in driver
assert "old108" not in helper and "20260928" in helper and "max_controls']==2000" in helper
report=json.loads((S/"reports/SOURCE108_PHASE_CONTIGUITY_8_32_CPU_SYNTHETIC_ACTUAL.json").read_bytes());assert report["passed_source_CPU_only"]
report["scope_correction"]="This NEW112 synthetic fixture inherited SOURCE108 filename/not_actual108 label; it tested selected112 code, not old actual108. No saved model or raw read. Original report kept."
with (S/"reports/SOURCE112_SELECTED_SOURCE_AND_INPUT_PHASE_SCOPE_CPU_ACTUAL.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),passed=True,source_AST_and_exact_lineage=True,one_model_load_for_new_purpose=True,original_physics_reset_reward_encoder_code_111_used=True,input_phase_previous_terminal_first_unknown=True,original_scope_report=report,only_source_CPU_no_remote_or_model=True),f,indent=2)
handoff="NEW112 frozen source only, unused one qualified111 h1 fixedseed20260928/2000controls8000callbacks own-plant N1 mean motion+paired WM purpose. Input qualified111 SHA24f94861...5fa12/global18597-185970WM-17893Pi; no old107/108 model/raw reread. Selected actual111 runtime/source/math/RSL/400/reset/preload/20s/alignedrequest/newheading preserved. New purpose inspects worldheading/command/actualprogress/contact/queue/reward and contiguous8/32 actual-action WM. Previous actual terminal is the window INPUT phase; first input unknown, grounded requires actual support. CPU synthetic phase/contiguity passed only, no actual112 case yet. Before execution: fresh exactLOCALCIM/global serial SSH leasefree; actualCNone/privateEX/light resources/sourceSDK/actualgas/reset all guarded before one source load. One model load/no normal86/no learner/norm/opt/GO/account. Exact270 acceptance unchanged. Never rerun consumed108/111 once. Entry direct Python314 -u -B -X utf8 run_NEW112_qualified111_fixed20s_Fudan270_motion_paired_WM_UNUSED_once.py. Full original text/newraw transfer once; raw index only forGit; no cause or skill claim from synthetic/source proofs."
with (S/"HANDOFF_UNUSED112_NEW_MOTION_PURPOSE.md").open("x",encoding="utf8") as f:f.write(handoff)
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(S.rglob("*")) if p.is_file()]
with (S/"FROZEN_UNUSED_SOURCE112_CPU_REVIEW_COMPLETE_INDEX_V1.json").open("x",encoding="utf8") as f:json.dump(dict(frozen=True,unused=True,source_only=True,files=rows,newpurpose=True,actualcase_not_run=True),f,indent=2)
print(json.dumps(dict(frozen=True,index_SHA=H(S/"FROZEN_UNUSED_SOURCE112_CPU_REVIEW_COMPLETE_INDEX_V1.json"),entry_SHA=H(required[-2]),no_model_or_remote=True)))

