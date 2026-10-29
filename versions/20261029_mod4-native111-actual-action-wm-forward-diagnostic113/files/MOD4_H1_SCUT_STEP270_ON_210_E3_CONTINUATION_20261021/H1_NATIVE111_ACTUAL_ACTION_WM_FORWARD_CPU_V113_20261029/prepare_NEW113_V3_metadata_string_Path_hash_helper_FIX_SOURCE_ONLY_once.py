from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;R=S/"reports"
old=S/"run_NEW113_actual_action_WM_forward_CPU_UNUSED_once_v2.py";s=old.read_text(encoding="utf8")
a="def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()";b="def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()";assert s.count(a)==1
s=s.replace(a,b).replace("FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V2.json","FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V3.json")
compile(s,"NEW113_V3","exec");p=S/"run_NEW113_actual_action_WM_forward_CPU_UNUSED_once_v3.py"
with p.open("x",encoding="utf8",newline="\n") as f:f.write(s)
tree=ast.parse(s);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="H");ns=dict(Path=Path,hashlib=hashlib);exec(compile(ast.Module(body=[fn],type_ignores=[]),"selected_H","exec"),ns)
binding=S/"PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json";assert ns["H"](str(binding))==ns["H"](binding)==hashlib.sha256(binding.read_bytes()).hexdigest()
assert not (R/"NEW113_PURPOSE_CONSUMED_BEFORE_RAW_OR_MODEL_ACTUAL.json").exists()
with (R/"SOURCE113_V2_STRING_PATH_HELPER_REFUSAL_AND_V3_METADATA_FIX_ACTUAL.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),original_error="AttributeError str.read_bytes at sealed source verification before consumed marker/raw/model",selected_H_accepts_exact_string_and_Path=True,numerical_core_unchanged=True,raw_reads=0,checkpoint_decodes=0,original_source_and_error_kept=True),f,indent=2)
seal=(S/"seal_NEW113_actual_forward_CPU_SOURCE_V2_UNUSED_once.py").read_text(encoding="utf8").replace("run_NEW113_actual_action_WM_forward_CPU_UNUSED_once_v2.py","run_NEW113_actual_action_WM_forward_CPU_UNUSED_once_v3.py").replace("FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V2.json","FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V3.json").replace("HANDOFF_FROZEN_NEW113_CPU_ACTUAL_ACTION_FORWARD_UNUSED.md","HANDOFF_FROZEN_NEW113_CPU_ACTUAL_ACTION_FORWARD_UNUSED_V3.md")
compile(seal,"SEALV3","exec")
with (S/"seal_NEW113_actual_forward_CPU_SOURCE_V3_UNUSED_once.py").open("x",encoding="utf8",newline="\n") as f:f.write(seal)

