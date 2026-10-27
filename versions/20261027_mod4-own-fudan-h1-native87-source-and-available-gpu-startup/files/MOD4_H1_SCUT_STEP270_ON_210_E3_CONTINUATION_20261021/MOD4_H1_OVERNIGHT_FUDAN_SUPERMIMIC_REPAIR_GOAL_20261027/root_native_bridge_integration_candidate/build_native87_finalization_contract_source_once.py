from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
source=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/source/native_finalization_v1.py'
dest=HERE/'native_finalization_own_v3.py';report=L/'reports/NATIVE87_FINALIZATION_EXACT_FUNCTIONS_NEW_ARCH_CONTRACT_ACTUAL.json'
assert not dest.exists() and not report.exists()
raw=source.read_bytes();text=raw.decode('utf8')
old="state_joints=30, actions=6, obs_dim=128, goal_dim=73,"
new="state_joints=30, actions=6, obs_dim=86, goal_dim=146,\n    packed_state_dim=127, dynamic_aux_dim=54, static_context_dim=31,\n    fresh4096_policy_only_bootstrap=True,"
assert text.count(old)==1
text=text.replace(old,new,1)
before=ast.parse(raw.decode('utf8'));after=ast.parse(text)
functions=lambda tree:{x.name:ast.dump(x,include_attributes=False) for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
assert functions(before)==functions(after)
dest.write_bytes(text.encode('utf8'))
report.write_text(json.dumps({'passed':True,'actual_source':str(source),'source_SHA':hashlib.sha256(raw).hexdigest(),'new_source':str(dest),'new_SHA':hashlib.sha256(dest.read_bytes()).hexdigest(),'all_function_and_class_AST_exact':True,'only_new_architecture_contract_constant_changes':True,'new_actual_native_FINAL':False,'source_only':True},indent=2),'utf8')
print(json.dumps({'passed':True,'new_SHA':hashlib.sha256(dest.read_bytes()).hexdigest()}))

