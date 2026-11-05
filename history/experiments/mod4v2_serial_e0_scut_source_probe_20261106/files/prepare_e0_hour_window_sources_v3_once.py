"""Adapt only observed source spellings, preserving original stop_reason at the log boundary."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;tree=ast.parse((D/'prepare_e0_hour_window_sources_once.py').read_text(encoding='utf8'));counts=[0,0,0,0]
class Fix(ast.NodeTransformer):
 def visit_Constant(self,n):
  if not isinstance(n.value,str):return n
  if n.value=="            need(not window.in_update and window.updates < task['max_additional_updates'], 'Unbounded/recursive original update')":n.value="            need(not window.in_update and window.updates < task['max_additional_updates'],\n                 'Unbounded/recursive original update')";counts[0]+=1
  if 'result = old_step(*args, **kwargs)'in n.value:n.value=n.value.replace('result = old_step(*args, **kwargs)','result = original_vec_step(*args, **kwargs)');counts[1]+=1
  if n.value.startswith('            reason = window.boundary_reason()\n            if reason:\n                runner.save'):
   n.value=n.value.replace('            if reason:\n                runner.save','            if reason:\n                window.stop_reason = reason\n                runner.save');counts[2]+=1
  if n.value=='        # Original RSL loop publishes source_iter .. source_iter+19 for 20 updates.':n.value=n.value.replace('RSL loop publishes','RSL publishes');counts[3]+=1
  return n
tree=Fix().visit(tree);assert counts==[1,2,1,1],counts;ast.fix_missing_locations(tree);exec(compile(tree,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
