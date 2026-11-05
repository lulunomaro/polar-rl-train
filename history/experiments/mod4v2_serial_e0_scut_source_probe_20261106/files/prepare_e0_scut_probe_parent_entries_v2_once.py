"""Correct only the observed one-space owner body indentation before any output publication."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
owner=ast.parse((D/'source_owner_e0_hour_v1/migration_nine_original_owner_v1.py').read_text(encoding='utf8'));q=next(n for n in owner.body if isinstance(n,ast.FunctionDef)and n.name=='qualify_v2_waited');ip=next(n for n in q.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ip'for t in n.targets));prefix=' '*ip.col_offset
s=(D/'prepare_e0_scut_probe_parent_entries_once.py').read_text(encoding='utf8');tree=ast.parse(s);count=[0,0,0]
class Fix(ast.NodeTransformer):
 def visit_Constant(self,n):
  if isinstance(n.value,str):
   if n.value.startswith("  checks['finite_probe_actual']="):
    n.value=prefix+n.value[2:];count[0]+=1
   elif n.value=="  ip=job/'production/V2_APP_CLOSE_INTENT.json'\n":
    n.value=prefix+n.value[2:];count[1]+=1
   elif n.value.startswith("  ap=job/'production/SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json'"):
    n.value='\n'.join(prefix+x[2:]if x.startswith('  ')else x for x in n.value.split('\n'));count[2]+=1
  return n
Fix().visit(tree);assert count==[1,1,1],count;ast.fix_missing_locations(tree);exec(compile(tree,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
