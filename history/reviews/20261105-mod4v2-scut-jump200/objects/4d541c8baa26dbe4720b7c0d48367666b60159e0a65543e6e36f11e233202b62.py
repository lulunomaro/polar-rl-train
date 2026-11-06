"""Execute only the actual worker's finally AST with an injected save failure."""
from pathlib import Path
from types import SimpleNamespace
import ast
import json
import time


N=Path(__file__).resolve().parent
P=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut/supermimic_train.py')
tree=ast.parse(P.read_text(encoding='utf-8'))
main=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='main')
body=next(node for node in main.body if isinstance(node,ast.Try)).finalbody
flags=dict(bridge_closed=False,env_closed=False,close_intent_written=False)
def fail_save(*args):
    raise OSError('INJECTED_CHECKPOINT_WRITE_FAILURE_CPU_ONLY')
namespace=dict(learner=object(),final_saved=False,save=fail_save,
    job=Path('CPU_FIXTURE_NO_PT_WRITTEN'),source_ref={},error='fixture',time=time,
    bridge=SimpleNamespace(close=lambda:flags.update(bridge_closed=True)),
    env=SimpleNamespace(close=lambda:flags.update(env_closed=True)),
    put=lambda *args:flags.update(close_intent_written=True))
try:
    exec(compile(ast.fix_missing_locations(ast.Module(body=body,type_ignores=[])),str(P),'exec'),namespace)
except OSError as exc:
    assert str(exc)=='INJECTED_CHECKPOINT_WRITE_FAILURE_CPU_ONLY'
else:
    raise AssertionError('Expected save failure')
assert not any(flags.values())
out=N/'supermimic_abstraction_audit_cpu/SAVE_FAILURE_CLEANUP.json'
out.write_text(json.dumps(dict(epoch=time.time(),source=str(P),flags=flags,
    finding='Interrupted-checkpoint save failure exits finally before bridge.close/env.close/close-intent; cleanup is not independently guaranteed by this worker.',
    scope='Actual finally statements, CPU stand-ins and injected OSError. Owner deadline fallback may still clean up a real worker; no real resource leak was created or observed.',
    production_PT_reads=0,PT_writes=0,real_physics_steps=0,optimizer_updates=0,
    production_source_changes=0,SSH=0),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(out),reproduced=True,flags=flags),ensure_ascii=False))
