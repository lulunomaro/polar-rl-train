"""Complete unpublished evaluator sources with observed two-space original statement indents."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent
stage=(D/'E0_HOUR_FROZEN_stage.py').read_text(encoding='utf-8-sig');sl=stage.splitlines()
st=[n for n in ast.walk(ast.parse(stage))if isinstance(n,ast.Expr)and "need(actual_task['original_entry']==" in ast.get_source_segment(stage,n)];assert len(st)==1
actual=sl[st[0].lineno-1].rstrip();si=' '*st[0].col_offset
parent=(D/'E0_HOUR_FROZEN_parent.py').read_text(encoding='utf-8-sig')
qn=next(n for n in ast.parse(parent).body if isinstance(n,ast.FunctionDef)and n.name=='qualify_waited_e0')
pa=[n for n in ast.walk(qn)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Subscript)and isinstance(x.slice,ast.Constant)and x.slice.value=='original_env_close_returned'for x in n.targets)];assert len(pa)==1
pi=' '*pa[0].col_offset
text=(D/'prepare_e0_scut_hour_frozen_eval_once.py').read_text(encoding='utf8');tree=ast.parse(text);counts=[0,0,0,0]
class Fix(ast.NodeTransformer):
 def visit_Constant(self,node):
  if isinstance(node.value,str)and node.value.startswith("   need(actual_task['original_entry']=="):
   node.value=actual;counts[0]+=1
  elif isinstance(node.value,str)and node.value.startswith("\n   need(actual_task['window_mode']=="):
   node.value='\n'+'\n'.join(si+x.lstrip()for x in node.value.splitlines()[1:]);counts[1]+=1
  elif node.value=="   checks['original_env_close_returned']=":
   node.value=pi+"checks['original_env_close_returned']=";counts[2]+=1
  elif isinstance(node.value,str)and node.value.startswith("   scut=f.get('actual_SCUT_binding')"):
   rows=[x for x in node.value.splitlines()if x.strip()]
   # Every original row is one complete statement; all content remains identical.
   for row in rows:ast.parse(row.lstrip())
   node.value='\n'.join(pi+x.lstrip()for x in rows)+'\n';counts[3]+=1
  return node
new=Fix().visit(tree);assert counts==[1,1,1,1],counts;ast.fix_missing_locations(new)
rp=D/'SCUT_HOUR_EVAL_PREPARER_V2_PARENT_LOCATOR_ERROR.json';assert not rp.exists()
rp.write_text(json.dumps(dict(epoch=time.time(),error="literal anchor count: checks['original_env_close_returned']",all_six_sources_still_unpublished=True,actual_stage_indent=len(si),actual_parent_qualification_indent=len(pi),repair='Only observed source statement indentation and same-level injected checks; content of every check retained; compile all before exclusive publication',remote_model_SDK_GPU_operations=0),indent=2),encoding='utf8')
exec(compile(new,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
