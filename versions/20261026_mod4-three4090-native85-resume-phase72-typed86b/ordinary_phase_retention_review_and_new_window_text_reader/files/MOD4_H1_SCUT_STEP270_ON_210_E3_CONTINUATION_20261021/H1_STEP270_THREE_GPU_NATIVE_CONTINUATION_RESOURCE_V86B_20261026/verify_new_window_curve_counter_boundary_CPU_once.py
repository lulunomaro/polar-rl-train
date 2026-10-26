from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent
p=N/'summarize_closed86B_new_native_window_events_text_CPU_unused_once.py'
tree=ast.parse(p.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='first_new')
ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(p),'exec'),ns)
f=ns['first_new'];row=lambda n,t,c,valid=True:dict(update_counters_valid=valid,policy_updates=n,GO_elapsed_s=t,completed_control_rows=c)
assert f([row(58,100,48)],'policy_updates',58)['status']=='no_new_update_in_valid_curve_rows'
value=f([row(58,100,48),row(59,160,72)],'policy_updates',58)
assert value['lower_completed_controls']==48 and value['upper_completed_controls']==72 and value['new_window_count']==1
assert f([row(58,100,48,False),row(59,160,72)],'policy_updates',58)['lower_completed_controls'] is None
rejected=False
try:f([row(57,100,48)],'policy_updates',58)
except ValueError:rejected=True
assert rejected
with (N/'reports/NEW_WINDOW_CUMULATIVE_COUNTER_BOUNDARY_CPU_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(dict(epoch=time.time(),passed=True,fixtures=4,source_path=str(p),source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),actual86B_curve_not_read=True,no_models_or_remote_or_training=True,original_text_reader_reused_without_modification=True),out,indent=2)
print(json.dumps(dict(passed=True,fixtures=4,not_runtime_evidence=True)))
