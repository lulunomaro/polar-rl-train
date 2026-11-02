"""Create NEW read-only grade bridges, prove actuator AST unchanged. 0 steps."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;D=R/'MINIHOP_V1'
receipts=[]
for label,source,base in (('flat','physics_bridge_v3.py','physics_bridge_v4_grade'),('rm','physics_bridge_rm_buffer_v1.py','physics_bridge_rm_grade_v1')):
    s=(R/source).read_text(encoding='utf-8');tree=ast.parse(s)
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
    method=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=='apply_torque_request')
    original='\n'.join(s.splitlines()[method.lineno-1:method.end_lineno])+'\n'
    assert original.count('mujoco.mj_step(')==1
    drive_line=next(line for line in original.splitlines()if 'self.d.ctrl[:]=bounded;'in line)
    hit_lines=[line for line in original.splitlines()if line.strip()=='hit=False']
    assert len(hit_lines)==1
    hit_line=hit_lines[0]
    drive_indent=drive_line[:len(drive_line)-len(drive_line.lstrip())]
    hit_indent=hit_line[:len(hit_line)-len(hit_line.lstrip())]
    modified=original.replace(drive_line,drive_indent+'self._capture_drivepoint(actual_dq,bounded)\n'+drive_line)
    modified=modified.replace(hit_line,hit_indent+'self._grade_minihop_sample()\n'+hit_line)
    # Original files have one-space class indentation, three-space physics body.
    if modified.count('self._grade_minihop_sample()')!=1:
        raise AssertionError('hook expected exactly once')
    old_ast=ast.parse('class X:\n'+original)
    new_ast=ast.parse('class X:\n'+modified)
    class RemoveHooks(ast.NodeTransformer):
        def visit_Expr(self,node):
            if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Attribute)and node.value.func.attr in('_capture_drivepoint','_grade_minihop_sample'):return None
            return self.generic_visit(node)
    restored=RemoveHooks().visit(new_ast)
    assert ast.dump(old_ast,include_attributes=False)==ast.dump(restored,include_attributes=False)
    output=R/f'physics_bridge_minihop_{label}_v1.py'
    text='"""New instrumentation-only bridge. Hooks never feed control."""\nimport numpy as np,mujoco\nfrom '+base+' import BufferedImuPlant as Base\nfrom MINIHOP_V1.contact_grade import ReadOnlyGrade\nclass MiniHopAuditPlant(ReadOnlyGrade,Base):\n'+modified
    ast.parse(text)
    with output.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
    receipts.append(dict(source=source,source_SHA=hashlib.sha256((R/source).read_bytes()).hexdigest(),derived=output.name,derived_SHA=hashlib.sha256(output.read_bytes()).hexdigest(),read_only_hooks=2,actuation_AST_equal_after_removing_hooks=True,physics_steps=0))
with(D/'BRIDGE_AST.json').open('x',encoding='utf-8')as f:json.dump(receipts,f,indent=2)
print(json.dumps(receipts,indent=2))
