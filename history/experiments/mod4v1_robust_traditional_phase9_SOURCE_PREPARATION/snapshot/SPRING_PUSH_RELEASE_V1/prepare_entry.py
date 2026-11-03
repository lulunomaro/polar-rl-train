"""Mechanical derivation; source/AST only. Does not import/execute old entry."""
from pathlib import Path
import ast,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;p=R/'run_manual_position_v4.py';old=p.read_text(encoding='utf-8');new=old

def once(a,b):
    global new
    assert new.count(a)==1,a;new=new.replace(a,b)
once('sys.path.insert(0,str(Path(__file__).resolve().parent))','sys.path.insert(0,str(Path(__file__).resolve().parents[1]))')
once('from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop','from SPRING_PUSH_RELEASE_V1.controller import MiniHop\nfrom SPRING_PUSH_RELEASE_V1.binding import prepare as spring_prepare,ctor_kwargs as spring_ctor_kwargs,data_sha as spring_data_sha')
once('def source_manifest(scene,cfg):','def source_manifest(scene,cfg,spring_binding=None):\n    if spring_binding is None:spring_binding=spring_prepare(cfg)')
new=new.replace("kind='NEW_MANUAL_ODOMETRY_NEXT_TICK_TRAIN'","kind='NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN'")
assert new.count('relative_V3_push_flight_capture_equations_unchanged=True')==2
new=new.replace('relative_V3_push_flight_capture_equations_unchanged=True','relative_V3_push_flight_capture_equations_unchanged=False,only_push_nominal_spring_ff_changed=True,flight_and_capture_equations_unchanged=True')
once('    return v\n','    v.update(config=cfg,spring_release_requested=spring_binding[\'requested\'],nominal_gas_endpoint_data_SHA=spring_data_sha(spring_binding))\n    v[\'files\'] += [file_record(ROOT/\'SPRING_PUSH_RELEASE_V1/controller.py\'),file_record(ROOT/\'SPRING_PUSH_RELEASE_V1/binding.py\')]\n    if spring_binding[\'data_record\']is not None:v[\'files\'] += [spring_binding[\'data_record\'],spring_binding[\'helper_record\']]\n    return v\n')
once('    try:\n        scene=','    try:\n        spring_binding=spring_prepare(cfg) # Must validate cache before any real plant construction.\n        scene=')
once("source_manifest(scene,cfg))","source_manifest(scene,cfg,spring_binding))")
once("end=load_gain(ROOT/cfg['end_gain_file']);landing=load_landing_gain(cfg['landing_gain'])","end=load_gain(ROOT/cfg['end_gain_file']);landing=load_landing_gain(cfg['landing_gain'])\n        spring_kwargs=spring_ctor_kwargs(spring_binding,start,end,landing)")
once("hop=MiniHop(start,end,geom,cfg['hop'],landing_gain=landing)","hop=MiniHop(start,end,geom,cfg['hop'],landing_gain=landing,**spring_kwargs)")
once('result=dict(kind=\'NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN\',config=cfg,','result=dict(kind=\'NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN\',spring_release_enabled=bool(hop.spring_release_active),nominal_gas_endpoint_data_SHA=spring_data_sha(spring_binding),config=cfg,')
new=new.replace('Manual relative odometry schedules a future trigger; phase durations and torque equations are V3.','Manual relative odometry schedules a future trigger; only timed-push nominal spring FF changes when enabled.')
oldtree=ast.parse(old);tree=ast.parse(new)
def main(t):return next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='main')
a=main(oldtree);b=main(tree);oa=next(n for n in ast.walk(a)if isinstance(n,ast.For));nb=next(n for n in ast.walk(b)if isinstance(n,ast.For));assert ast.dump(oa)==ast.dump(nb)
protected=('complete','hard','guide','peak','final','progress','main_pass','crossed','next_free','local_pass')
def assignments(t):
 return{n.targets[0].id:ast.dump(n)for n in ast.walk(t)if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in protected}
assert assignments(a)==assignments(b)
with(O/'run_manual_spring_push_v1.py').open('x',encoding='utf-8',newline='\n')as f:f.write(new)
with(O/'ENTRY_AST.json').open('x',encoding='utf-8')as f:json.dump(dict(status='PASS_STATIC_DERIVATION_ONLY',old_entry_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_entry_SHA=hashlib.sha256((O/'run_manual_spring_push_v1.py').read_bytes()).hexdigest(),loop_AST_bitidentical=True,protected_grade_gate_assignments_identical=list(protected),driver_changed=False,old_sources_modified=False,metadata_kind='NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN',relative_V3_equations_claim=False),f,indent=2)
print('ENTRY_DERIVED loop/good/main/local AST unchanged; no entry execution')
