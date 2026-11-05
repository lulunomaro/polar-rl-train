"""Use the observed original supervisor indentation; publish nothing until all source parses."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;s=(D/'prepare_e0_single_eval_pipeline_once.py').read_text(encoding='utf8')
for a,b in [('if raw.count(old) != 1 or new in raw:','if raw.count(old) != 2 or new in raw:'),('changed = raw.replace(old, new, 1)','changed = raw.replace(old, new)'),('if changed.replace(new, old, 1) != raw:','if changed.replace(new, old) != raw:')]:assert s.count(a)==1;s=s.replace(a,b)
a='    for name in outputs:\n';assert s.count(a)==1;s=s.replace(a,"    for name, source in outputs.items():\n        ast.parse(source); compile(source, str(D/name), 'exec')\n"+a);s=s.replace('--closed E0_SINGLE_ADMISSION2_CLOSED_RESULT_PATH.json','--closed E0_SINGLE_ADMISSION3_CLOSED_RESULT_PATH.json');tree=ast.parse(s);counts=[0,0]
class Fix(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='   if waited:\n    for fd in reversed(locks):':n.value='  if waited:\n   for fd in reversed(locks):';counts[0]+=1
  elif isinstance(n.value,str)and n.value.startswith('   settled,settle_rows=settle_own_card('):n.value='\n'.join(x[1:]if x.startswith(' ')else x for x in n.value.split('\n'));counts[1]+=1
  return n
tree=Fix().visit(tree);assert counts==[1,1],counts;ast.fix_missing_locations(tree);exec(compile(tree,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
