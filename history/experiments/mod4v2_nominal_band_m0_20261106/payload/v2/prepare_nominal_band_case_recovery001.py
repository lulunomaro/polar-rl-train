"""One exact generator-indent recovery before derived prefix/models/physics."""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent;D=R/'T01_NOMINAL_BAND_M0_V1'
if D.exists():raise RuntimeError('Derived experiment prefix already exists;do not prepare again')
src=R/'prepare_nominal_band_case_once.py';program=ast.parse(src.read_text(encoding='utf-8'))
fn=next(n for n in program.body if isinstance(n,ast.FunctionDef)and n.name=='main')
pos=next(i for i,n in enumerate(fn.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ns'for t in n.targets))
fix="""
lines=(R/'T01_OBSERVABILITY_V1/run_reverse_observe.py').read_text(encoding='utf-8').splitlines()
original=[line for line in lines if line.lstrip()==\"meta['zones'][0]['spawn']=copy.deepcopy(protocol['public_route']['start_ground_m'])\"]
assert len(original)==1
indent=original[0][:-len(original[0].lstrip())]
assert len(indent)==16
changed_values=0;changed_lines=0
for node in ast.walk(tree):
 if not isinstance(node,ast.Constant)or not isinstance(node.value,str)or not node.value.startswith('meta[')or '\\n'not in node.value:continue
 parts=node.value.splitlines();new=[parts[0]]
 for line in parts[1:]:
  assert line.lstrip().startswith('meta[')and len(line)-len(line.lstrip())==17
  new.append(indent+line.lstrip());changed_lines+=1
 node.value='\\n'.join(new);changed_values+=1
assert(changed_values,changed_lines)==(2,3)
with(R/'NOMINAL_BAND_PREP_ATTEMPT001.json').open('x',encoding='utf-8')as f:
 json.dump(dict(error='Inherited unexecutedR26 metadata continuation17spaces vs actual16;compile failed before outputprefix',original_log='prepare_nominal_band_case_001.log',original_sources_unchanged=True,actual_indent=16,corrected_literal_values=2,corrected_continuation_lines=3,models=0,forward=0,physics_steps=0,source_queries=0,recovery='Only inserted metadata continuation indentation uses exact original source indentation'),f,indent=2)
"""
fn.body[pos:pos]=ast.parse(fix).body
ns={'__name__':'_nominal_band_single_indent_recovery','__file__':str(src)}
exec(compile(ast.fix_missing_locations(program),str(src)+'[exact-metadata-indent-recovery]','exec'),ns);ns['main']()
