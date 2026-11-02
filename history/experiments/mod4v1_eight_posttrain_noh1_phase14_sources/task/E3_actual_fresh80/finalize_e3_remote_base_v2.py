"""Correct the exact E3 producer directory suffix; keep failed stage trial intact."""
from pathlib import Path
import ast
HERE=Path(__file__).resolve().parent
s=(HERE/'prepare_e3_remote_stage_once.py').read_text(encoding='utf-8')
a="MOD4_E3_PPO50_GAS400_2610v97/e2'";b="MOD4_E3_PPO50_GAS400_2610v97/e3'"
assert a in s;s=s.replace(a,b)
ast.parse(s)
with (HERE/'prepare_e3_remote_stage_v2_once.py').open('x',encoding='utf-8') as f:f.write(s)
print('Corrected E3 producer directory /e3 in new stage version; no PT/SDK')
