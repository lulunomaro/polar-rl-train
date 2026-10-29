from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;R=S/"reports"
p=S/"run_NEW113_actual_action_WM_forward_CPU_UNUSED_once.py";s=p.read_text(encoding="utf8")
try:compile(s,str(p),"exec")
except SyntaxError as e:
 with (R/"SOURCE113_V1_SEAL_AND_UNSEALED_ENTRY_SYNTAX_REFUSALS_BEFORE_ANY_READ_ACTUAL.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),original=type(e).__name__,message=str(e),original_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),raw_reads=0,checkpoint_decodes=0,consumed_marker_absent=not (R/"NEW113_PURPOSE_CONSUMED_BEFORE_RAW_OR_MODEL_ACTUAL.json").exists(),sealer_refused_then_caller_also_syntax_refused=True,no_runtime_code_executed=True),f,indent=2)
else:raise AssertionError("expected original syntactic refusal")
lines=s.splitlines();bad=[i for i,x in enumerate(lines) if x.startswith(" print(json.dumps(dict(passed=True")]
assert len(bad)==1;i=bad[0]
lines[i]=' output=dict(passed=True,raw_reads=raw_reads,checkpoint_decodes=checkpoint_decodes,seconds=result["CPU_wall_seconds"],horizons={h:dict(windows=v["all"]["windows"],X_MAE_m=v["all"]["world_position_error"]["x"]["mean_abs"],Vx_MAE_m_s=v["all"]["world_velocity_error"]["x"]["mean_abs"],request_Vx_MAE=v["request_only"]["world_velocity_error"]["x"]["mean_abs"],sign_subset=v["request_only"]["significant_vx_sign_subset"]) for h,v in summaries.items()},one_step_CPU_vs_savedGPU_Z=summaries["1"]["all"]["CPU_vs_saved_GPU_one_step_root_z_max_abs"])'
lines.insert(i+1," print(json.dumps(output),flush=True)")
s="\n".join(lines)+"\n";s=s.replace("FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V1.json","FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V2.json")
compile(s,"NEW113_V2","exec")
v=S/"run_NEW113_actual_action_WM_forward_CPU_UNUSED_once_v2.py"
with v.open("x",encoding="utf8",newline="\n") as f:f.write(s)
seal=(S/"seal_NEW113_actual_forward_CPU_source_UNUSED_once.py").read_text(encoding="utf8")
seal=seal.replace('files=sorted(S.glob("*.py"))','files=[S/x for x in ["actual_action_forward113_core_v1.py","verify_NEW113_real_core_action_sequence_CPU_SOURCE_ONLY_once.py","run_NEW113_actual_action_WM_forward_CPU_UNUSED_once_v2.py"]]')
seal=seal.replace("run_NEW113_actual_action_WM_forward_CPU_UNUSED_once.py","run_NEW113_actual_action_WM_forward_CPU_UNUSED_once_v2.py").replace("FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V1.json","FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V2.json")
compile(seal,"SEAL113_V2","exec")
with (S/"seal_NEW113_actual_forward_CPU_SOURCE_V2_UNUSED_once.py").open("x",encoding="utf8",newline="\n") as f:f.write(seal)
print(json.dumps(dict(selected_V2=str(v),model_reads=0,raw_reads=0,numerical_core_and_synthetic_proof_unchanged=True)))

