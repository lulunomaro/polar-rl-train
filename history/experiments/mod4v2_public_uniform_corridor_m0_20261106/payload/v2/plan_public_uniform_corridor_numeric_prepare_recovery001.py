"""Recover one whitespace anchor before any numeric-refinement source parse or LP."""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent
bad=R/'plan_public_uniform_corridor_numeric_retry001.py';original=R/'plan_public_uniform_corridor_once.py'
D=R/'PUBLIC_UNIFORM_CORRIDOR_V1/NUMERIC_BOUNDARY_RETRY001'
if D.exists():raise RuntimeError('Numeric source query already began;do not replay')
source=bad.read_text(encoding='utf-8');tree=ast.parse(source)
calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='one'and len(n.args)==2 and isinstance(n.args[0],ast.Constant)and isinstance(n.args[0].value,str)and n.args[0].value.lstrip().startswith('if float(np.max(v[:,2]-a*v[:,0]-b*v[:,1]-c))')]
assert len(calls)==1;n=calls[0];old=n.args[0].value;actual=[line for line in original.read_text(encoding='utf-8').splitlines()if line.lstrip()==old.lstrip()];assert len(actual)==1
oldindent=len(old)-len(old.lstrip());newindent=len(actual[0])-len(actual[0].lstrip());assert oldindent==3 and newindent==2
n.args[0].value=actual[0];lines=n.args[1].value.splitlines();assert all(line.startswith(' ')for line in lines);n.args[1].value='\n'.join(line[1:]for line in lines)
receipt=R/'PUBLIC_UNIFORM_CORRIDOR_NUMERIC_PREP_ERROR001.json'
with receipt.open('x',encoding='utf-8')as f:json.dump(dict(error='Exact source anchor assumed3 spaces,actual2;assertbeforeexec/derivedprefix/sourceparse/LP',original_script=bad.name,original_log='plan_public_uniform_corridor_numeric_retry001.log',original_sources_unchanged=True,old_indent=3,actual_indent=2,changed_AST_calls=1,model=0,physics=0,source_parse=0,LP=0,recovery='Only anchor and inserted block use actual semantic line indent'),f,indent=2)
ns={'__name__':'_numeric_corridor_exact_indent_recovery','__file__':str(bad)};exec(compile(ast.fix_missing_locations(tree),str(bad)+'[single-exact-indent-recovery]','exec'),ns);ns['main']()
