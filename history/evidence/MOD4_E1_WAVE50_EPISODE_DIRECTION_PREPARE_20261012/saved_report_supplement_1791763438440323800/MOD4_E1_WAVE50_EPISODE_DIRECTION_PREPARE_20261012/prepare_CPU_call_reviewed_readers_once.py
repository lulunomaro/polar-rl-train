"""Preserve the actual reader TypeError; independently fix only unexecuted j arity."""
from wave_direction_io import *
import ast
names=[]
for old,new,var in (('verify_direction_initial_transition_saved_PPO_cpu_actual.py','verify_direction_initial_transition_CPU_call_reviewed_actual.py','root'),('read_direction_own_formal_cpu_actual.py','read_direction_own_formal_CPU_call_reviewed_actual.py','run')):
 s=(D/old).read_text();bad="j("+var+"/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json')";good="j("+var+"/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json')";assert s.count(bad)==1;s=s.replace(bad,good);tree=ast.parse(s)
 call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='run')
 code=call.args[1].func.value.value;treecode=ast.parse(code)
 assert all(len(n.args)==1 for n in ast.walk(treecode) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='j')
 assert "'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json')" in s
 p=D/new;assert not p.exists();p.write_text(s,encoding='utf8',newline='\n');names.append(new)
save('CPU_CALL_READER_SCHEMA_REVIEW.json',dict(epoch=time.time(),original_reader_TypeError_retained=True,original_general_replacement_added_second_argument_to_single_argument_j=True,independent_readers=names,embedded_remote_j_call_arity_AST_checked=True,nine_startup_marker_tuple_and_all_strict_validators_preserved=True,no_GPU_or_physics_failure_or_replay=True))
print(json.dumps(dict(independent_reader_call_arity_reviewed=True,strict_validators_unchanged=True)))
