"""Keep the exact generic validator-template source path literal in provenance."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent
s=(HERE/'build_e3_mod4v1_sources_v3.py').read_text(encoding='utf-8')
a='MOD4_W35_QUALIFIED343E_CONTINUE327D_20261101_0712';b='MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712'
assert a in s;s=s.replace(a,b)
a="prior2,prior2_ref=read(HERE/'build_e3_mod4v1_sources_v2.py');restore_fix,restore_fix_ref=read(HERE/'finalize_e3_restore_anchor_v3.py');refs.extend([prior2_ref,restore_fix_ref])"
assert a in s;s=s.replace(a,a+"\n    prior3,prior3_ref=read(HERE/'build_e3_mod4v1_sources_v3.py');literal_fix,literal_fix_ref=read(HERE/'finalize_e3_protocol_literal_v4.py');refs.extend([prior3_ref,literal_fix_ref])")
ast.parse(s)
new=HERE/'build_e3_mod4v1_sources_v4.py'
with new.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'generator':str(new),'old_literal_provenance_only':True,'PT_or_SDK':False},indent=2))
