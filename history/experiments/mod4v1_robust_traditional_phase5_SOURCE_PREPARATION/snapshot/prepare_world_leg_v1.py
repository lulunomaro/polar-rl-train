"""New R22-matched sensor-only fore/aft counterfactual runner, 0 physics."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;D=R/'ROUGH_WORLD_LEG_V1'
p=R/'run_rm_grid_height_v1.py';s=p.read_text(encoding='utf-8')
assert s.count('from ground_controller_v4 import GroundController')==1
s=s.replace('from ground_controller_v4 import GroundController','from ROUGH_WORLD_LEG_V1.controller import WorldLegController as GroundController\nfrom streamed_trace_rows_v1 import StreamedRows')
s=s.replace('rows=[];p=None;complete=False',"rows=StreamedRows(out/'trace.jsonl');p=None;complete=False")
s=s.replace("truth_mode=cfg.get('feedback','sensors')=='truth_diagnostic'","truth_mode=False")
s=s.replace("[Path(__file__),ROOT/'physics_bridge.py'","[Path(__file__),ROOT/'ROUGH_WORLD_LEG_V1/controller.py',ROOT/'streamed_trace_rows_v1.py',ROOT/'physics_bridge.py'")
s=s.replace('row=dict(time=', 'row=dict(world_leg_reference=dict(controller.world_log),time=')
s=s.replace('original_error_preserved=True,no_samepurpose_retry=True',"trace_prefix=dict(path=str(rows.path),bytes=rows.bytes,SHA=rows.sha.hexdigest()),original_error_preserved=True,no_samepurpose_retry=True")
tree=ast.parse(s)
class NewRunner(ast.NodeTransformer):
    def visit_If(self,node):
        if isinstance(node.test,ast.Name)and node.test.id=='truth_mode':return None
        return self.generic_visit(node)
    def visit_With(self,node):
        if any(isinstance(x,ast.Constant)and x.value=='trace.jsonl'for x in ast.walk(node.items[0].context_expr)):
            return ast.parse('trace_hash=rows.sha\ntrace_bytes=rows.bytes').body
        return self.generic_visit(node)
tree=ast.fix_missing_locations(NewRunner().visit(tree));text=ast.unparse(tree)+'\n';ast.parse(text)
assert 'truth_diagnostic'not in text and 'rows.sha'in text and 'world_leg_reference'in text
out=R/'run_world_leg_case_v1.py'
with out.open('x',encoding='utf-8')as f:f.write(text)
receipt=dict(kind='NEW_SENSOR_ONLY_R22_MATCHED_RUNNER',physics_steps=0,source=str(p),source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),derived=str(out),derived_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),old_source_modified=False,GT_control_branch_removed=True,trace_rows_streamed_before_memory=True)
with(D/'PREPARATION.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt,indent=2))
