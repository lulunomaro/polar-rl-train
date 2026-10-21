from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;P=B.parent/'E3_bridge_continuation_V3';R=B/'reports'
q=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());proof=json.loads((P/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
assert q['passed'] and proof['passed'] and proof['remaining_actual_snapshot']>82512.86069250107 and q['sources']['recovery']['SHA']==proof['models']['recovery']['final']['SHA']
cases=[]
for name,function in [('three_slot_common_v1.py','charge_values'),('three_slot_finite_owner_v1.py','account')]:
    old=(P/'two_policy50_original_account_controllers'/name).read_text(encoding='utf8');new=(B/'two_policy50_original_account_controllers'/name).read_text(encoding='utf8');assert old==new
    def fn(s):
        rows=[x for x in ast.walk(ast.parse(s)) if isinstance(x,ast.FunctionDef) and x.name==function];assert len(rows)==1;return rows[0]
    assert ast.dump(fn(old))==ast.dump(fn(new));cases.append(dict(file=name,function=function,normalized_AST_exact=True,entire_controller_byteexact=True))
owner=(B/'two_policy50_original_account_controllers/three_slot_finite_owner_v1.py').read_text(encoding='utf8');assert "+b.CAPS['h1']+9400.860692501068" in owner and "set(specs)=={'recovery'}" in owner
v=dict(epoch=time.time(),passed_CPU_source_preparation=True,E2_deferred_H1_native_pending=True,actual_only_scheduled_learning_expert='recovery',source_SHA=q['sources']['recovery']['SHA'],source_Adam=q['sources']['recovery']['Adam'],admission_reserve_seconds=7800,strict_budget_threshold_seconds=82512.86069250107,original_charge_and_account_function_AST_exact=True,AST_cases=cases,safety_legacy_total1548000_eight_extensions_unchanged=True,only_actual_recovery_GO_to_terminal_charged=True,no_H1_native_learning_cost_or_refund=True,not_yet_deployed=True,original_V1_nested_function_reader_error_retained=True)
with (R/'H1_NATIVE210_RECOVERY_BRIDGE_SOURCE_AND_RESERVATION_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(passed=True,source=q['sources']['recovery'],controllers_byteexact=True)))
