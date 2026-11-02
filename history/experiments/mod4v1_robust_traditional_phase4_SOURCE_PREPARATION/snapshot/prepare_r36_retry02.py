"""Preserve R36 attempt01 (AST indent failure, zero physical cases).
Only repair generated except indentation, then prepare NEW attempt02 sources.
"""
from pathlib import Path
import ast
R = Path(__file__).resolve().parent
s = (R/'prepare_r36_heading_v2.py').read_text(encoding='utf-8')
needle = 'lines[i:i+3] = ["   dump('
assert s.count(needle) == 1
s = s.replace(needle, 'lines[i:i+3] = ["  dump(')
needle = "def fresh(path, content):\n    with path.open('x', encoding='utf-8', newline='\\n') as f:"
assert s.count(needle) == 1
s = s.replace(needle, "def fresh(path, content):\n    if path.name == 'heading_hold_controller_v2.py' and path.exists():\n        assert path.read_text(encoding='utf-8') == content, 'prior bool-only source differs'\n        return\n    with path.open('x', encoding='utf-8', newline='\\n') as f:")
s = s.replace('run_heading_hold_case_v2.py', 'run_heading_hold_case_v3.py')
ast.parse(s)
with (R/'prepare_r36_heading_v3.py').open('x', encoding='utf-8', newline='\n') as f:
    f.write(s)
s = (R/'launch_r36_heading_train.py').read_text(encoding='utf-8')
s = s.replace('batches/r36_heading26', 'batches/r36b_heading26').replace('prepare_r36_heading_v2.py', 'prepare_r36_heading_v3.py').replace('run_heading_hold_case_v2.py', 'run_heading_hold_case_v3.py').replace("case = f'r36_heading_", "case = f'r36b_heading_")
ast.parse(s)
with (R/'launch_r36b_heading_train.py').open('x', encoding='utf-8', newline='\n') as f:
    f.write(s)
print('R36_ATTEMPT01_ZERO_PHYSICS_PRESERVED_NEW02_AST_OK')
