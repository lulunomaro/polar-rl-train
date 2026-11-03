"""Derive only imports/package bootstrap and honest metadata; preserve main law."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lock=json.loads((D/'SOURCE_LOCK.json').read_bytes());assert sha(D/'METHOD.json')==lock['method_SHA']
for x in lock['sources']:assert sha(Path(x['path']))==x['SHA']
src=R/'run_manual_position_v4.py';text=src.read_text(encoding='utf-8')
text=text.replace('sys.path.insert(0,str(Path(__file__).resolve().parent))','sys.path.insert(0,str(Path(__file__).resolve().parents[2]))')
text=text.replace('from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop','from MINIHOP_AIR_PITCH_REF_V1.attempt002.controller import MiniHop')
old=ast.parse(text);node=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name=='source_manifest')
new='''def source_manifest(scene,cfg):
    v=landing_manifest(scene,cfg)
    enabled=cfg.get('hop',{}).get('air_pitch_ref_enable',False)
    assert type(enabled)is bool
    v.update(kind='NEW_MANUAL_ODOMETRY_AIR_REF_AND_CONTINUOUS_CAPTURE_ANCHOR_TRAIN',
             scope='local TRAIN hypothesis only; no whole-RM/contact or dynamic admission',
             command_changed=True,controller_equations_unchanged=False,
             relative_V3_push_flight_capture_equations_unchanged=not enabled,
             original_position_trigger_launch_push_observer_unchanged=True,
             air_reference_and_continuous_capture_anchor_enabled=enabled,
             air_reference_fixed_parameters=dict(kp=.25,kd=.04,h_min_rad=-.10,h_max_rad=.03,rate_rad_s=1.,period_s=.01),
             private_bounds_not_controller_inputs=True,PH7_pending=True,
             default_operator_enable=False,automatic_obstacle_or_contact_FSM=False)
    here=Path(__file__).resolve().parent
    v['files'] += [file_record(ROOT/'MINIHOP_POSITION_TRIGGER_V1/controller.py'),file_record(here/'controller.py'),file_record(Path(__file__)),file_record(here/'METHOD.json'),file_record(here/'SOURCE_LOCK.json'),file_record(ROOT/'MANUAL_FIRST_BAR_V1/grade_rows.py'),file_record(ROOT/'MANUAL_FIRST_BAR_V1/grade_rows_v2.py')]
    return v
'''
lines=text.splitlines(keepends=True);lines[node.lineno-1:node.end_lineno]=[new];text=''.join(lines)
text=text.replace("kind='NEW_MANUAL_ODOMETRY_NEXT_TICK_TRAIN',config=cfg","kind='NEW_MANUAL_ODOMETRY_AIR_REF_AND_CONTINUOUS_CAPTURE_ANCHOR_TRAIN',config=cfg")
text=text.replace('relative_V3_push_flight_capture_equations_unchanged=True,command_schedule_changed=True','relative_V3_push_flight_capture_equations_unchanged=not bool(cfg[\'hop\'].get(\'air_pitch_ref_enable\',False)),command_schedule_changed=True')
text=text.replace('H5_or_old_scores_modified=False,PH6_pending=True','H5_or_old_scores_modified=False,PH7_pending=True')
text=text.replace(ast.get_docstring(ast.parse(text)), 'NEW fixed TRAIN estimated-air reference plus continuous capture-anchor entry.\nOriginal position scheduler, phase durations, observer, actuator and private grade\nremain read-only. Main control loop is unchanged; the new controller changes\nair/capture leg references only when its explicit default-false flag is enabled.')
a=ast.parse(src.read_text(encoding='utf-8'));b=ast.parse(text)
main=lambda tree:next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
loop=lambda t:next(n for n in main(t).body if isinstance(n,ast.Try)).body
aloop=next(n for n in ast.walk(main(a))if isinstance(n,ast.For));bloop=next(n for n in ast.walk(main(b))if isinstance(n,ast.For))
assert ast.dump(aloop,include_attributes=False)==ast.dump(bloop,include_attributes=False)
# Normalize only the three result-metadata fields, then compare entire main AST.
na=main(a);nb=main(b)
for n in ast.walk(nb):
    if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='dict':
        keys={k.arg for k in n.keywords}
        if 'kind'in keys and 'config'in keys and 'controller_truth_inputs'in keys:
            for k in n.keywords:
                if k.arg=='kind':k.value=ast.Constant(value='NEW_MANUAL_ODOMETRY_NEXT_TICK_TRAIN')
                elif k.arg=='relative_V3_push_flight_capture_equations_unchanged':k.value=ast.Constant(value=True)
                elif k.arg=='PH7_pending':k.arg='PH6_pending'
assert ast.dump(na,include_attributes=False)==ast.dump(nb,include_attributes=False)
out=D/'run_manual_air_pitch_ref_v1.py'
with out.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
record=dict(kind='DERIVED_ENTRY_AST_NO_CONTROL_ACTUATOR_OR_GRADE_CHANGE',source=str(src),source_SHA=sha(src),entry_SHA=sha(out),
    control_loop_AST_identical=True,entire_main_AST_identical_except_three_result_metadata_fields=True,
    constructor_call_unchanged=True,bootstrap_change='package parents[2] to actual workspace root',
    new_import='MINIHOP_AIR_PITCH_REF_V1.attempt002.controller.MiniHop',source_manifest_only_metadata_extension=True,
    physics_or_controller_execution=False)
with(D/'ENTRY_AST.json').open('x',encoding='utf-8')as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record,indent=2))
