from pathlib import Path
import ast,json,time
S=Path(__file__).resolve().parent
old=S/"run_NEW_E0_V1_reviewed_secure_ingress_UNUSED_once.py";s=old.read_text(encoding="utf8")
a='helper=S.parent/"MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/run_NEW_E2_V4_original_height_secure_ingress_V2_rootpath_UNUSED_once.py"'
b='helper=S.parent/"MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/run_NEW_E2_V4_FIRST360_reviewed_secure_ingress_UNUSED_once.py"'
assert s.count(a)==1;s=s.replace(a,b)
a='sp=importlib.util.spec_from_file_location("original_same86_secure_recover_definitions_only",helper);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)'
b='tree=ast.parse(helper.read_text(encoding="utf8")); selected=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom)) or isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ("SESSION","EVENT") for t in x.targets) or isinstance(x,ast.FunctionDef) and x.name=="recover"]; assert len([x for x in selected if isinstance(x,ast.FunctionDef)])==1; ns={};exec(compile(ast.Module(body=selected,type_ignores=[]),str(helper),"exec"),ns);m=types.SimpleNamespace(recover=ns["recover"])'
assert s.count(a)==1;s=s.replace(a,b).replace("import hashlib,importlib.util,json,subprocess,sys,time,traceback","import ast,types,hashlib,importlib.util,json,subprocess,sys,time,traceback")
s=s.replace("ROOT_E0_V1_","ROOT_E0_V1_V2_")
compile(s,"NEW_E0_secure_v2","exec")
v=S/"run_NEW_E0_V1_V2_AST_RECOVER_ONLY_reviewed_secure_ingress_UNUSED_once.py"
with v.open("x",encoding="utf8",newline="\n") as f:f.write(s)
with (S/"reports/ROOT_E0_SECURE_V1_EXECUTABLE_HELPER_IMPORT_REFUSAL_AND_V2_AST_REPAIR.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),original_false="V1 imported an executable repair-wrapper whose top-level exec reached old E2 main; consumed marker refused before newmarker/credential/network. E0 entry remains unused. Original errors preserved, including old helper error newly saved under N111/reports.",selected_v2="AST only imports + exact SESSION/EVENT assignments + recover definition from plain first360 source; never compiles any main/if/body or old entry.",no_PT_or_remote_on_failed_V1=True,no_relaxed_consume_guard=True),f,indent=2)

