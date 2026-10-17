"""Diagnose an actual identity rejection; process metadata/signatures only, no UI or signals."""
from pathlib import Path
import ast,json,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';N=W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017'
sys.path[:0]=[str(N/'curb275_final87_frozen3060_v1'),str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')]
import transport_249_exact_desktop_role_stdin_fresh2233_v7 as t
P=R/'E2_CLOSED109_249_CHANGED_DESKTOP_EXACT_SIGNATURES_0820_READONLY_ACTUAL.json';assert not P.exists()
tree=ast.parse((N/'read_3060_exact_new_desktop_roles_signatures_no_UI_or_process_mutation_once.py').read_text('utf8'))
CODE=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='CODE' for y in x.targets))
c=None
try:
 c=t.connect();v=t.py(c,CODE,timeout=120)
except BaseException:v=dict(epoch=time.time(),original_error=traceback.format_exc(),readonly_no_runtime_change=True)
finally:t.close(c)
with P.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(P),roles=[dict(name=x['name'],pid=x['process']['pid'],signature=x['authenticode'],child_count=len(x['children']),parent_child_count=len(x['parent_children'])) for x in v.get('exact_new_desktop_roles',[])],error=v.get('original_error')),ensure_ascii=False))
