"""ONE root-cause recovery: original prep expected3spaces, live runtime uses2.
Original failed generator/log untouched. Patch only that AST call's two string
constants using the already-read actual semantic line; no blind anchor retries.
"""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent;P=R/'prepare_reference_static_ff_v1.py'
D=R/'T01_REFERENCE_STATIC_FF_V1';runtime=R/'runtime_reference_static_ff_v1.py'
if D.exists()or runtime.exists():raise RuntimeError('Unexpected derived prefix; do not regenerate')
original=P.read_text(encoding='utf-8');live=(R/'runtime_v2.py').read_text(encoding='utf-8')
semantic='self.estimate=None;self.packet=None;self.last_tau=np.zeros(6);self.controls=0'
lines=[line for line in live.splitlines()if line.strip()==semantic]
if len(lines)!=1:raise RuntimeError('Actual semantic anchor not unique')
actual=lines[0];indent=actual[:-len(semantic)]
if indent!='  ':raise RuntimeError('Expected proven runtime body indentation2')
class Exact(ast.NodeTransformer):
 def __init__(self):self.changed=0
 def visit_Call(self,node):
  node=self.generic_visit(node)
  if isinstance(node.func,ast.Name)and node.func.id=='replace'and len(node.args)==3 and isinstance(node.args[0],ast.Name)and node.args[0].id=='runtime'and isinstance(node.args[1],ast.Constant)and node.args[1].value=='   '+semantic:
   node.args[1].value=actual
   node.args[2].value=indent+'self.meta.update(reference_static_ff_design=self.controller.reference_ff_design,reference_ff_is_not_measured_force=True)\n'+actual
   self.changed+=1
  return node
patch=Exact();tree=patch.visit(ast.parse(original,str(P)));ast.fix_missing_locations(tree)
if patch.changed!=1:raise RuntimeError('Expected exact single failed AST anchor')
record=dict(status='PREP_ONLY_FAILURE_BEFORE_DERIVED_PREFIX_RECOVERED_BY_EXACT_ACTUAL_INDENT',
 original_script=P.name,original_log='prepare_reference_static_ff_v1_001.log',expected_spaces=3,actual_spaces=2,
 patched_AST_calls=1,simulation_model_builds=0,physics_steps=0,robot_case_failure=False,original_source_modified=False)
with (R/'REFERENCE_STATIC_FF_PREP_ATTEMPT001.json').open('x',encoding='utf-8')as f:json.dump(record,f,indent=2)
exec(compile(tree,str(P)+'::single_indent_recovery','exec'),{'__file__':str(P),'__name__':'__main__'})
print('RECOVERED_EXACT_3_TO_2_INDENT_ONLY',flush=True)
