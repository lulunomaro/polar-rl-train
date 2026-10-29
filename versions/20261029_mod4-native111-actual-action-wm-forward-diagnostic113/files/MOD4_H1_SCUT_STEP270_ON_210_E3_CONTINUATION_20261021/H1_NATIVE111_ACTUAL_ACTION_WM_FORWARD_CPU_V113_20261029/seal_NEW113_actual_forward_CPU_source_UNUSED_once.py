from pathlib import Path
import ast,json,hashlib,time
S=Path(__file__).resolve().parent;R=S/"reports"
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((R/"SOURCE113_REAL_CORE_SYNTHETIC_ACTION_SEQUENCE_AND_NEGATIVES_CPU_ACTUAL.json").read_bytes());assert proof["passed_source_CPU_only"] and len(proof["negative_cases_rejected"])==11
files=sorted(S.glob("*.py"))
for p in files:ast.parse(p.read_text(encoding="utf8"))
entry=S/"run_NEW113_actual_action_WM_forward_CPU_UNUSED_once.py"
assert entry.read_text().count("torch.load(")==1
assert "actual_actions_at_every_offset=True" in (S/"actual_action_forward113_core_v1.py").read_text()
with (S/"HANDOFF_FROZEN_NEW113_CPU_ACTUAL_ACTION_FORWARD_UNUSED.md").open("x",encoding="utf8") as f:f.write("NEW113 CPU-only single qualified111 checkpoint decode, WM-only forward. All NEW112 actual control data and source gates BEFORE savedmodel. Exact original normalize_static31/current127/actions6/xi31, ALL valid contiguous1/8/32 windows with actual per-offset actions/context, no policy resampling. Full checkpoint is decoded once, only WM instantiated; no separate normal86/Pi/Critic/optimizer/GPU/SDK/physics/account/SSH. One necessary NEW112 control read and one model integrityhash pass + one checkpointdecode are explicitly budgeted, not stats/Git. Source core passed nonconstant-action closedform/11 negatives and reset exclusions without model/raw. Entry direct env_isaaclabCPUtorch CUDA_VISIBLE_DEVICES='' -B -Xutf8; freshLOCALexactCIM. FrozenWMnorms literal unchanged, no data mutation. CPU vs saved112 GPU rootZ is a consistency readout, no FP32bitwise/physical tolerance gate. Report limited to actual lowhop/slowvelocity domain, overlap not independent, no27cm skill accuracy. Never rerun this consumed entry or old112/111initialreview.")
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in files]
with (S/"FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V1.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),frozen=True,unused=True,source_files=rows,binding_SHA=H(S/"PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json"),proof_SHA=H(R/"SOURCE113_REAL_CORE_SYNTHETIC_ACTION_SEQUENCE_AND_NEGATIVES_CPU_ACTUAL.json"),entry=str(entry),entry_SHA=H(entry)),f,indent=2)
print(json.dumps(dict(source_frozen=True,entry_SHA=H(entry),index_SHA=H(S/"FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V1.json"),model_reads=0,raw_reads=0)))

