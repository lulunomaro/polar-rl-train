"""NEW unexecuted V3 entry from report-fixed V4; stdlib/AST only."""
from pathlib import Path
import ast, hashlib, json
D=Path(__file__).resolve().parent;T=D.parent
old=T/'run_startup_stand_case_v4.py';out=T/'run_startup_stand_case_v5.py'
assert not out.exists(),'Existing new entry: inspect, never overwrite'
text=old.read_text(encoding='utf-8');original=text;changes=[]
def change(a,b,n=1):
    global text
    assert text.count(a)==n,(a,text.count(a))
    text=text.replace(a,b);changes.append({'old':a,'new':b,'occurrences':n})
change('from STARTUP_STAND_V2.controller import StartupStand','from STARTUP_STAND_V3.controller import StartupStand')
change("set(cfg['controller'])=={'operator_enable','recovery_actuation_enable'}","set(cfg['controller'])=={'operator_enable','recovery_tracking_enable','alignment_wheel_enable'}")
change("assert cfg['case_id']!='startup_front065_nominal_v1', 'New strategy requires a new case ID; old case must not replay'","assert cfg['case_id'] not in ('startup_front065_nominal_v1','startup_front065_coupled_v2_nominal1'), 'V1/V2 case IDs are consumed; new strategy requires new ID'")
change('NEW_LYING_STARTUP_COUPLED_LEG_WHEEL_DAMPING_V2_TRAIN','NEW_LYING_STARTUP_TRACKING_ELIGIBLE_ALIGNMENT_V3_TRAIN',2)
change("recovery_actuation_enable_requested=cfg['controller']['recovery_actuation_enable']","recovery_tracking_enable_requested=cfg['controller']['recovery_tracking_enable'],\n            alignment_wheel_enable_requested=cfg['controller']['alignment_wheel_enable']",2)
change('only_shape_verify_leg_K_and_packet_wheel_damping_changed=True','recovery_tracking_and_optional_eligible_pose_alignment_only=True')
change("file_record(ROOT/'STARTUP_STAND_V2/controller.py'),file_record(ROOT/'STARTUP_STAND_V2/PREFLIGHT_RESULT.json')","file_record(ROOT/'STARTUP_STAND_V3/controller.py'),file_record(ROOT/'STARTUP_STAND_V3/PREFLIGHT_RESULT.json')")
change('recovery_actuation_active=bool(controller.recovery_actuation_active)','recovery_tracking_active=bool(controller.recovery_tracking_active),\n            alignment_wheel_active=bool(controller.alignment_wheel_active)')
a,b=ast.parse(original),ast.parse(text)
getloop=lambda x:[n for n in ast.walk(x)if isinstance(n,ast.For)and ast.unparse(n.target)=='k']
assert len(getloop(a))==len(getloop(b))==1 and ast.dump(getloop(a)[0],include_attributes=False)==ast.dump(getloop(b)[0],include_attributes=False)
for name in ('good','healthy','complete','passed'):
    find=lambda x:[n.value for n in ast.walk(x)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)]
    u,v=find(a),find(b);assert len(u)==len(v)==1 and ast.dump(u[0],include_attributes=False)==ast.dump(v[0],include_attributes=False)
assert 'dr.queue_receipt()'in text and 'runtime_receipt'not in text
with out.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
receipt={'status':'V3_NEW_ENTRY_AST_ONLY_NOT_IMPORTED_OR_EXECUTED','old_entry':str(old),'old_SHA':hashlib.sha256(old.read_bytes()).hexdigest(),'new_entry':str(out),'new_SHA':hashlib.sha256(out.read_bytes()).hexdigest(),'changes':changes,'original_loop_and_healthy_good_complete_passed_equal':True,'original_2k_driver_and_private_gate_unchanged':True,'report_uses_existing_queue_receipt':True,'old_two_case_IDs_rejected':True,'no_project_import_model_FK_PHY_QA_Git_agent_execution':True,'profile_B_requires_later_parent_A_eligibility_admission_not_permission_from_entry':True,'PH10pending':True}
with(D/'ENTRY_DERIVATION.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'status':receipt['status'],'entry':str(out),'SHA':receipt['new_SHA'],'PHY':0},ensure_ascii=True))
