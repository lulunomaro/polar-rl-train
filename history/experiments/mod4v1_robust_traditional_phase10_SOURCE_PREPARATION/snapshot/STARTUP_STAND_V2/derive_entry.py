"""Create NEW unexecuted entry from report-fixed V3; no project imports/run."""
from pathlib import Path
import ast, hashlib, json

D = Path(__file__).resolve().parent
T = D.parent
old = T/'run_startup_stand_case_v3.py'
new = T/'run_startup_stand_case_v4.py'
assert not new.exists(), 'Do not replace an existing entry'
text = old.read_text(encoding='utf-8')
original = text
changes = []

def change(a, b, n=1):
    global text
    assert text.count(a) == n, (a, text.count(a))
    text = text.replace(a, b)
    changes.append({'old': a, 'new': b, 'occurrences': n})

change('from STARTUP_STAND_V1.controller import StartupStand',
       'from STARTUP_STAND_V2.controller import StartupStand')
change("assert cfg['controller']=={'operator_enable':True}",
       "assert set(cfg['controller'])=={'operator_enable','recovery_actuation_enable'} and all(type(x)is bool for x in cfg['controller'].values())\n        assert cfg['case_id']!='startup_front065_nominal_v1', 'New strategy requires a new case ID; old case must not replay'")
change('NEW_LYING_STARTUP_SENSOR_ONLY_TRAIN',
       'NEW_LYING_STARTUP_COUPLED_LEG_WHEEL_DAMPING_V2_TRAIN', 2)
change("init_fixture=file_record(fp),upright_prior=False,startup_or_hardware_qualified=False)",
       "init_fixture=file_record(fp),upright_prior=False,startup_or_hardware_qualified=False,\n            recovery_actuation_enable_requested=cfg['controller']['recovery_actuation_enable'],\n            only_shape_verify_leg_K_and_packet_wheel_damping_changed=True)")
change("file_record(ROOT/'STARTUP_STAND_V1/PREFLIGHT_RESULT.json'),file_record(ROOT/'TALL_ROUGH_BANK_V1/gain_delta0.json'),file_record(fp)]",
       "file_record(ROOT/'STARTUP_STAND_V1/PREFLIGHT_RESULT.json'),file_record(ROOT/'TALL_ROUGH_BANK_V1/gain_delta0.json'),file_record(fp),\n            file_record(ROOT/'STARTUP_STAND_V2/controller.py'),file_record(ROOT/'STARTUP_STAND_V2/PREFLIGHT_RESULT.json')]")
change("actual_initial_xyz_m=initial['xyz'],final_grade=final,controller_phase=controller.log['phase'],controller_fault_reason=controller.fault_reason,",
       "actual_initial_xyz_m=initial['xyz'],final_grade=final,controller_phase=controller.log['phase'],controller_fault_reason=controller.fault_reason,\n            recovery_actuation_enable_requested=cfg['controller']['recovery_actuation_enable'],\n            recovery_actuation_active=bool(controller.recovery_actuation_active),\n            recovery_override_is_NOT_standup_or_support_proof=True,")
old_ast, new_ast = ast.parse(original), ast.parse(text)
loops = lambda a: [n for n in ast.walk(a) if isinstance(n, ast.For) and ast.unparse(n.target) == 'k']
assert len(loops(old_ast)) == len(loops(new_ast)) == 1
assert ast.dump(loops(old_ast)[0], include_attributes=False) == ast.dump(loops(new_ast)[0], include_attributes=False)
for name in ('good','healthy','complete','passed'):
    find = lambda a: [n.value for n in ast.walk(a) if isinstance(n, ast.Assign) and any(isinstance(k, ast.Name) and k.id == name for k in n.targets)]
    a,b=find(old_ast),find(new_ast)
    assert len(a)==len(b)==1 and ast.dump(a[0],include_attributes=False)==ast.dump(b[0],include_attributes=False)
assert 'dr.queue_receipt()' in text and 'runtime_receipt' not in text
real_dr = T.parent/'traditional_control_20261101/dr_components.py'
dr_ast = ast.parse(real_dr.read_text(encoding='utf-8'))
full = next(n for n in dr_ast.body if isinstance(n, ast.ClassDef) and n.name=='FullDR')
method = next(n for n in full.body if isinstance(n, ast.FunctionDef) and n.name=='queue_receipt')
assert [a.arg for a in method.args.args]==['self']
assert not any(isinstance(n, ast.FunctionDef) and n.name=='runtime_receipt' for n in full.body)
with new.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
receipt = {'status':'NEW_ENTRY_STATIC_DERIVATION_ONLY_NOT_EXECUTED',
    'old_entry':str(old),'old_SHA':hashlib.sha256(old.read_bytes()).hexdigest(),
    'new_entry':str(new),'new_SHA':hashlib.sha256(new.read_bytes()).hexdigest(),
    'declared_replacements':changes,'original_control_loop_AST_equal':True,
    'healthy_good_complete_passed_AST_equal':True,'original_2k_support_grade_unchanged':True,
    'FullDR_queue_receipt_defined_self_only':{'path':str(real_dr),'line':method.lineno},
    'old_DR_self_test_called':False,'entry_import_or_execution':False,
    'source_model_FK_PHY_QA_Git_agents_execution':0,'PH10pending':True}
p=D/'ENTRY_DERIVATION.json'
with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'status':receipt['status'],'entry':str(new),'SHA':receipt['new_SHA'],'loop_grade_equal':True,'entry_executed':False}))
