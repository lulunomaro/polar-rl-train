"""Report-only correction after first actual601/12020prefix. No replay."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V1/reporting_fix003';D.mkdir(exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
old=R/'run_startup_stand_case_v2.py';new=R/'run_startup_stand_case_v3.py';b=old.read_bytes();text=b.decode('utf-8')
assert text.count('dr.runtime_receipt()')==1;text=text.replace('dr.runtime_receipt()','dr.queue_receipt()')
# Statically verify the real imported API without importing project/MuJoCo.
p=R.parent/'traditional_control_20261101/dr_components.py';api=ast.parse(p.read_text(encoding='utf-8-sig'))
cls=next(n for n in api.body if isinstance(n,ast.ClassDef)and n.name=='FullDR')
f=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='queue_receipt')
assert len(f.args.args)==1 and not any(isinstance(n,ast.FunctionDef)and n.name=='runtime_receipt'for n in cls.body)
oldloop=next(n for n in ast.walk(ast.parse(b))if isinstance(n,ast.For)and isinstance(n.iter,ast.Call)and isinstance(n.iter.func,ast.Name)and n.iter.func.id=='range'and n.iter.args and isinstance(n.iter.args[0],ast.Constant)and n.iter.args[0].value==1000)
newloop=next(n for n in ast.walk(ast.parse(text))if isinstance(n,ast.For)and isinstance(n.iter,ast.Call)and isinstance(n.iter.func,ast.Name)and n.iter.func.id=='range'and n.iter.args and isinstance(n.iter.args[0],ast.Constant)and n.iter.args[0].value==1000)
assert ast.dump(oldloop,include_attributes=False)==ast.dump(newloop,include_attributes=False)
with new.open('x',encoding='utf-8',newline='')as out:out.write(text)
e=json.loads((R/'results/startup_front065_nominal_v1/ERROR.json').read_bytes());assert(e['controls'],e['physics_steps'])==(601,12020)
receipt=dict(status='REPORT_ONLY_API_CORRECTION_NOT_REEXECUTED',old_runner_SHA=sha(b),new_runner_SHA=sha(new.read_bytes()),
    actual_API_source=str(p),actual_API_source_SHA=sha(p.read_bytes()),API_function_line=f.lineno,control_loop_AST_unchanged=True,
    original_case_ERROR_preserved=True,original_trace_and_physics_untouched=True,original_consumed_controls=601,original_consumed_physics_steps=12020,
    old_or_new_physics_executions_for_fix=0,controller_or_oldQA_replays=0,old_scores_not_rewritten=True,
    next_execution_requires_new_controller_hypothesis_and_new_case_not_bookkeeping_replay=True)
with(D/'RECEIPT.json').open('x',encoding='utf-8')as out:json.dump(receipt,out,indent=2)
print(json.dumps(receipt,indent=2))
