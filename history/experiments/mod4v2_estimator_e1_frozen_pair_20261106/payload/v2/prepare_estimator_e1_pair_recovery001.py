"""One exact known metadata-anchor recovery; original failed preparer/log retained."""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent
if (R/'T01_ESTIMATOR_E1_PAIR_V1').exists():raise RuntimeError('Derived pair prefix already exists')
error=R/'ESTIMATOR_CAUCHY_E1_V1/PAIR_PREP_ATTEMPT001.json'
if error.exists():raise RuntimeError('Recovery already attempted')
source=(R/'prepare_estimator_e1_pair_v1.py').read_text(encoding='utf-8');tree=ast.parse(source)
actual=(R/'T01_OBSERVER_AUDIT_V1/run_observer_audit_case.py').read_text(encoding='utf-8')
semantic="meta['original_default_M0_controller_unchanged']=True"
lines=[line for line in actual.splitlines()if line.strip()==semantic]
if len(lines)!=1:raise RuntimeError('Known semantic anchor unavailable')
line=lines[0];indent=line[:len(line)-len(line.lstrip())]
calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='one'and n.args and isinstance(n.args[0],ast.Constant)and isinstance(n.args[0].value,str)and n.args[0].value.strip()==semantic]
if len(calls)!=1:raise RuntimeError('Expected one bad metadata call')
call=calls[0];old=call.args[0].value;old_indent=old[:len(old)-len(old.lstrip())]
if len(old_indent)!=17 or len(indent)!=16:raise RuntimeError('Not the observed17vs16 root cause')
for arg in call.args:
 if not isinstance(arg,ast.Constant)or not isinstance(arg.value,str):raise RuntimeError('Expected literal strings only')
 arg.value='\n'.join(indent+v[len(old_indent):]if v.startswith(old_indent)else v for v in arg.value.split('\n'))
code=compile(ast.fix_missing_locations(tree),str(R/'prepare_estimator_e1_pair_v1.py'),'exec')
error.write_text(json.dumps(dict(failure='literal metadata indentation17 while actual16',stage='before derivedprefix/model/physics/seed draw',
 models=0,physics=0,old_QA_or_raw=0,original_preparer_and_log_kept=True,recovery='exact oneCall/two literals only,indent from actual semantic source line'),indent=2),encoding='utf-8')
namespace={'__name__':'e1_pair_exact_indent_recovery','__file__':str(R/'prepare_estimator_e1_pair_v1.py')}
exec(code,namespace);namespace['main']()
print('E1_PAIR_EXACT_INDENT_RECOVERY_OK;oldpreparer/logkept;0models/physics')
