"""Resume only the no-physics preparation prefix; retain original failed source.
Root cause: generator expected 3 leading spaces; actual runtime uses 2.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=R/'T01_ROLL_FORCE_V1';original=R/'prepare_roll_force_v1.py'
assert D.is_dir() and not any(D.iterdir()),'Unexpected prepared prefix: inspect, do not rerun'
text=(R/'runtime_v2.py').read_text(encoding='utf-8')
anchor=next(line for line in text.splitlines()if '# No assignment of old pack.K_6x14:'in line)
actual_indent=len(anchor)-len(anchor.lstrip());assert actual_indent==2
with (D/'PREP_ATTEMPT001.json').open('x',encoding='utf-8')as f:
 json.dump(dict(status='PREP_SOFTWARE_ERROR_PREFIX_RETAINED_ZERO_PHYSICS',source=str(original),
  exception='AssertionError at metadata-comment anchor before runtime/protocol/runner writes',
  root_cause=dict(expected_leading_spaces=3,actual_leading_spaces=actual_indent),
  physics_steps=0,new_models=0,case_started=False,original_script_preserved=True,
  recovery='Locate semantic anchor and retain its indentation; resume only known empty preparation directory'),f,indent=2)
code=original.read_text(encoding='utf-8')
code=code.replace('D.mkdir(exist_ok=False)',"assert D.is_dir() and {p.name for p in D.iterdir()}=={'PREP_ATTEMPT001.json'}")
a=code.index('a="   # No assignment of old pack.K_6x14:')
b=code.index("\nwith (R/'runtime_roll_force_v1.py')",a)
code=code[:a]+'''a=next(line for line in s.splitlines()if '# No assignment of old pack.K_6x14:'in line)
indent=a[:len(a)-len(a.lstrip())]
s=s.replace(a,indent+"self.meta['roll_force_design']=self.controller.roll_force_design.copy()\\n"+a)
'''+code[b:]
exec(compile(code,str(original)+'_recovered','exec'),{'__file__':str(original)})
