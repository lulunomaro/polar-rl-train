"""Keep original failed driver and match its exact commented reset line."""
from pathlib import Path
import ast
HERE=Path(__file__).resolve().parent
s=(HERE/'derive_e3_fresh80_control_sources.py').read_text(encoding='utf-8')
a="a='        env.reset()\\n'"
b="a='        env.reset()  # exactly ONE explicit NEW fresh reset, not a checkpoint resume\\n'"
assert a in s;s=s.replace(a,b)
a=" with (HERE/new).open('x',encoding='utf-8') as f:f.write(text)"
b=" if (HERE/new).exists():\n  assert new=='prepare_e3_remote_stage_once.py' and (HERE/new).read_text(encoding='utf-8')==text\n  continue\n"+a
assert a in s;s=s.replace(a,b)
ast.parse(s)
with (HERE/'derive_e3_fresh80_control_sources_v2.py').open('x',encoding='utf-8') as f:f.write(s)
print('Created E3 control derivation v2; no target execution')
