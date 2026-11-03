"""Preserve zero-step generation failure; derive AST-span based generator.
The 001 attempt never wrote the runner or reached any unit/plant/integrator.
"""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;p=R/'prepare_r61_spin_decel_gate_v1.py';s=p.read_text(encoding='utf-8')
D=R/'SPIN_CENTER_DECEL_GATE_V1/preflight001'
with(D/'ERROR.json').open('x',encoding='utf-8')as f:json.dump(dict(status='PREPARER_SOFTWARE_ERROR_ZERO_PHYSICS',preparer_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),error='ValueError: substring not found',line=18,reason='Generator assumed four-space if indentation; actual legacy one-space-per-level style',runner_written=False,unit_frames_executed=0,integrator_steps=0,no_robot_score=True),f,indent=2)
s=s.replace("D=R/'SPIN_CENTER_DECEL_GATE_V1/preflight001'","D=R/'SPIN_CENTER_DECEL_GATE_V1/preflight002'")
old="a=s.index('    if truth_mode:\\n');b=s.index('    active=t>=',a);s=s[:a]+s[b:]"
new="""def drop_node(text,node):
    lines=text.splitlines(keepends=True);return ''.join(lines[:node.lineno-1]+lines[node.end_lineno:])
truth=[n for n in ast.walk(ast.parse(s))if isinstance(n,ast.If)and isinstance(n.test,ast.Name)and n.test.id=='truth_mode']
assert len(truth)==1;s=drop_node(s,truth[0])"""
assert old in s;s=s.replace(old,new)
old="a=s.index(\"   with(out/'trace.jsonl').open('xb')as f:\\n\");b=s.index('   result.update(grade_transitions',a);s=s[:a]+s[b:]"
new="""write_nodes=[n for n in ast.walk(ast.parse(s))if isinstance(n,ast.With)and ast.get_source_segment(s,n).startswith(\"with(out/'trace.jsonl')\")]
assert len(write_nodes)==1;s=drop_node(s,write_nodes[0])"""
assert old in s;s=s.replace(old,new)
a=s.index('a=s.index("   with(out/\'partial_trace.jsonl\')');b=s.index('\ns=s.replace("ROOT/',a)
new="""handler=[n for n in ast.walk(ast.parse(s))if isinstance(n,ast.ExceptHandler)and isinstance(n.type,ast.Name)and n.type.id=='BaseException']
assert len(handler)==1;handler=handler[0];lines=s.splitlines(keepends=True);indent=' '*handler.body[0].col_offset
body=[\"error=traceback.format_exc()\",\"dump(out/'ERROR.json',dict(error=error,controls=len(rows),physics_callbacks=p.tick_phys if p is not None else None,trace_artifact=dict(path=str(rows.path),bytes=rows.bytes,SHA=rows.sha.hexdigest()),original_error_preserved=True,prefix_written_before_memory=True))\",\"raise\"]
s=''.join(lines[:handler.body[0].lineno-1])+''.join(indent+line+'\\n'for line in body)+''.join(lines[handler.end_lineno:])"""
s=s[:a]+new+s[b:];ast.parse(s)
q=R/'prepare_r61_spin_decel_gate_v2.py'
with q.open('x',encoding='utf-8')as f:f.write(s)
print('WROTE',q,'AST_OK; old source and ERROR retained; 0 physics')
