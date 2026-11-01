"""Use actual97 installer dependency local_path, never guess the asset parent."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent
s=(HERE/'build_e3_mod4v1_sources_v1.py').read_text(encoding='utf-8')
a="read(old/'assets/import_contract.json',utility.OLD_CONTRACT_SHA)"
b="read(Path(rows['runtime/assets/import_contract.json']['local_path']),utility.OLD_CONTRACT_SHA)"
assert a in s;s=s.replace(a,b)
a="template,template_ref=read(STAGED/'E2_builder/build_e2_mod4v1_sources_v5.py');driver,driver_ref=read(HERE/'derive_e3_builder_v1.py');refs.extend([template_ref,driver_ref])"
assert a in s;s=s.replace(a,a+"\n    prior,prior_ref=read(HERE/'build_e3_mod4v1_sources_v1.py');dependency_fix,dependency_fix_ref=read(HERE/'finalize_e3_contract_dependency_v2.py');refs.extend([prior_ref,dependency_fix_ref])")
ast.parse(s)
new=HERE/'build_e3_mod4v1_sources_v2.py'
with new.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'generator':str(new),'actual97_dependency_path_used':True,'E3_PT_or_SDK':False},indent=2))
