"""Repair only source-locator indentation from observed original AST; no remote work."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent
original=(D/'E0_HOUR_FROZEN_stage.py').read_text(encoding='utf-8-sig')
lines=original.splitlines()
nodes=[n for n in ast.walk(ast.parse(original)) if isinstance(n,ast.Expr) and "need(actual_task['original_entry']==" in ast.get_source_segment(original,n)]
assert len(nodes)==1
n=nodes[0];actual=lines[n.lineno-1].rstrip();indent=actual[:len(actual)-len(actual.lstrip())]
s=(D/'prepare_e0_scut_hour_frozen_eval_once.py').read_text(encoding='utf8')
tree=ast.parse(s);counts=[0,0]
class Fix(ast.NodeTransformer):
 def visit_Constant(self,node):
  if isinstance(node.value,str) and node.value.startswith("   need(actual_task['original_entry']=="):
   node.value=actual;counts[0]+=1
  elif isinstance(node.value,str) and node.value.startswith("\n   need(actual_task['window_mode']=="):
   node.value='\n'+ '\n'.join(indent+x.lstrip() for x in node.value.splitlines()[1:]);counts[1]+=1
  return node
new=Fix().visit(tree);assert counts==[1,1],counts;ast.fix_missing_locations(new)
record=D/'SCUT_HOUR_EVAL_PREPARER_V1_SOURCE_LOCATOR_ERROR.json';assert not record.exists()
record.write_text(json.dumps(dict(epoch=time.time(),original_preparer='prepare_e0_scut_hour_frozen_eval_once.py',error='literal anchor count: Original family E0 entry unchanged',failed_before_any_six_output_publication=True,actual_original_AST_column=n.col_offset,actual_prefix_spaces=len(indent),repair='Observed original AST statement and its indentation only; inverse edits, every generated source compile, original-resource-function checks retained',SDK_model_GPU_or_remote_execution=0),indent=2),encoding='utf8')
exec(compile(new,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
