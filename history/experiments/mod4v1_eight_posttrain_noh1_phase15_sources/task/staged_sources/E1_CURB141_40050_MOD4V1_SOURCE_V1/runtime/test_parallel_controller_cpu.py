"""CPU authority/cadence tests; no simulator, learning, CUDA or ledger writes."""
from pathlib import Path
import ast,json
p=Path(__file__).with_name('supervise_sensor_parallel_continuation.py');tree=ast.parse(p.read_text());action_node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='action');scope={};exec(compile(ast.Module(body=[action_node],type_ignores=[]),str(p),'exec'),scope);action=scope['action']
assert action(1000)=='continue_same_validated_scope'
assert action(120)=='saved_window_or_budget_boundary' and action(119)=='saved_window_or_budget_boundary'
assert action(1000,handover=True)=='saved_handover'
assert action(1000,attention=True)=='saved_attention'
assert action(1000,handover=True,attention=True)=='saved_attention'
# Pending frozen feedback is not a condition in action: four safe blocks are
# possible without a desktop wake; real attention/next-scope/budget preempts it.
events=[action(remaining) for remaining in (21000,14000,7000,120)]
assert events==['continue_same_validated_scope']*3+['saved_window_or_budget_boundary']
text=p.read_text();assert 'CAP=21600' in text and 'PARALLEL_BLOCK_' in text and 'time.sleep(15)' in text and 'STOP_AFTER_SAVE' in text
assert 'kill(' not in text and 'start_segment(' not in text and 'account_segment(' not in text
print(json.dumps(dict(passed=True,contracts=8,no_learning=True,no_CUDA_initialized=True,scope='Authority and bounded cadence; real source/resume verification separate')))
