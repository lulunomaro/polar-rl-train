"""Correct only the observed local terminal-loop anchors before first output publication."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;p=D/'prepare_nine_owner_once.py';tree=ast.parse(p.read_text(encoding='utf8'))
orig=D.parent/'mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR4_GENERIC_V2_DATA_PAYLOAD/eight_posttrain_original_owner_v1.py';raw=orig.read_text(encoding='utf8');lines=raw.splitlines(keepends=True);ot=ast.parse(raw)
n=next(n for n in ast.walk(ot)if isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='rc'and isinstance(n.test.ops[0],ast.NotEq))
anchor=lines[n.lineno-1].lstrip()+lines[n.body[0].lineno-1];body_indent=lines[n.body[0].lineno-1][:len(lines[n.body[0].lineno-1])-len(lines[n.body[0].lineno-1].lstrip())];counts=[0,0,0,0]
class Fix(ast.NodeTransformer):
 def visit_Constant(self,node):
  if not isinstance(node.value,str):return node
  v=node.value
  if v.startswith('if p.returncode!=0:\n     completed='):v=anchor;counts[0]+=1
  elif v.startswith('if p.returncode!=0 or not(final'):
   v=v.replace('if p.returncode!=0','if rc!=0',1).replace('\n     completed=','\n'+body_indent+'completed=');counts[1]+=1
  elif v.startswith("put(job/'PARENT_WAITED_ACTUAL.json',dict(role=e['role']"):
   v="put(job/'PARENT_WAITED_ACTUAL.json',rows[key]);del slots[u];c=account(run,go,rows)";counts[2]+=1
  elif v.startswith('q=qualify_v2_waited(job,e,final,p.pid,p.returncode);'):
   v="q=qualify_v2_waited(job,e,final,p.pid,rc);rows[key]['semantic_qualification']=q;rows[key]['original_error']=bool(rc!=0 or not q['qualified']);put(job/'PARENT_WAITED_ACTUAL.json',rows[key]);del slots[u];c=account(run,go,rows)";counts[3]+=1
  return ast.copy_location(ast.Constant(v),node)
tree=Fix().visit(tree);assert counts==[1,1,1,1],counts;ast.fix_missing_locations(tree);exec(compile(tree,str(Path(__file__)),'exec'),{'__name__':'__main__','__file__':str(Path(__file__))})
