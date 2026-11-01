"""Bind original E3 fullstate resume/install aliases, not E2 command aliases."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent
s=(HERE/'build_e3_mod4v1_sources_v2.py').read_text(encoding='utf-8')
s=s.replace('e3_command_checkpoint_v1','e3_fullstate_checkpoint_v1').replace('from e3_fullstate_checkpoint_v1 import install_e3_save_contract','from e3_fullstate_checkpoint_v1 import install as install_chassis_pd_save_contract')
a="prior,prior_ref=read(HERE/'build_e3_mod4v1_sources_v1.py');dependency_fix,dependency_fix_ref=read(HERE/'finalize_e3_contract_dependency_v2.py');refs.extend([prior_ref,dependency_fix_ref])"
assert a in s;s=s.replace(a,a+"\n    prior2,prior2_ref=read(HERE/'build_e3_mod4v1_sources_v2.py');restore_fix,restore_fix_ref=read(HERE/'finalize_e3_restore_anchor_v3.py');refs.extend([prior2_ref,restore_fix_ref])")
ast.parse(s)
new=HERE/'build_e3_mod4v1_sources_v3.py'
with new.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'generator':str(new),'E3_original_fullstate_aliases':True,'PT_or_SDK':False},indent=2))
