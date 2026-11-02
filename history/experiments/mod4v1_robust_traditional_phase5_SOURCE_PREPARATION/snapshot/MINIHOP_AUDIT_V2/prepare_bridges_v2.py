"""Derive only two observer hooks and prove full actuator-method AST equality."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
HOOKS={'_capture_drivepoint','_grade_minihop_sample'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def method(tree):
    return next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='apply_torque_request')
def canonical(node):return ast.dump(node,include_attributes=False)
class Strip(ast.NodeTransformer):
    def __init__(self):self.removed=[]
    def visit_Expr(self,node):
        v=node.value
        if isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and isinstance(v.func.value,ast.Name)and v.func.value.id=='self'and v.func.attr in HOOKS:
            expected=2 if v.func.attr=='_capture_drivepoint'else 0
            assert len(v.args)==expected and not v.keywords
            if expected:assert [canonical(x)for x in v.args]==[canonical(ast.Name(id=n,ctx=ast.Load()))for n in ('actual_dq','bounded')]
            self.removed.append(v.func.attr);return None
        return self.generic_visit(node)
def main():
    fr=json.loads((HERE/'SOURCE_FREEZE.json').read_bytes());known={r['path']:r['sha256']for r in fr['old_files']+fr['sources']};rows=[]
    for label,source,base in (('flat','physics_bridge_v3.py','physics_bridge_v4_grade'),('rm','physics_bridge_rm_buffer_v1.py','physics_bridge_rm_grade_v1')):
        src=ROOT/source;old=ROOT/f'physics_bridge_minihop_{label}_v1.py'
        assert sha(src)==known[str(src.resolve())]and sha(old)==known[str(old.resolve())]
        text=old.read_text(encoding='utf-8');node=method(ast.parse(text));body='\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])+'\n'
        strip=Strip();restored=strip.visit(copy.deepcopy(node));original=method(ast.parse(src.read_text(encoding='utf-8')))
        assert canonical(restored)==canonical(original)and strip.removed==['_capture_drivepoint','_grade_minihop_sample']
        output=HERE/f'physics_bridge_minihop_{label}_v2.py'
        derived='"""Private v2 observer hooks; actuator method byte-identical to v1."""\nimport numpy as np,mujoco\nfrom '+base+' import BufferedImuPlant as Base\nfrom MINIHOP_AUDIT_V2.contact_grade_v2 import ReadOnlyGrade\nclass MiniHopAuditPlant(ReadOnlyGrade,Base):\n'+body
        newnode=method(ast.parse(derived));assert canonical(newnode)==canonical(node)
        stripper=Strip();assert canonical(stripper.visit(copy.deepcopy(newnode)))==canonical(original)
        with output.open('x',encoding='utf-8',newline='\n')as f:f.write(derived)
        rows.append(dict(source=str(src),source_sha256=sha(src),old_v1_bridge=str(old),old_v1_sha256=sha(old),derived=str(output),derived_sha256=sha(output),hook_signatures_unchanged=True,hook_order=strip.removed,full_apply_AST_equal_to_v1=True,full_apply_AST_equal_original_after_removing_exact_two_hooks=True,raw_servo_hook_added=False,physics_steps=0))
    with(HERE/'BRIDGE_AST.json').open('x',encoding='utf-8')as f:json.dump(rows,f,indent=2)
    print(json.dumps(dict(status='BOTH_FULL_ACTUATOR_ASTS_PROVED',bridges=rows,physics_steps=0)))
if __name__=='__main__':main()
