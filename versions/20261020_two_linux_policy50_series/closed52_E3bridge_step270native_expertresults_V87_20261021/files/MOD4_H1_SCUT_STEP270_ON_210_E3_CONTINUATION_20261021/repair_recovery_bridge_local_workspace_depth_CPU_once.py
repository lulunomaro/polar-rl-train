from pathlib import Path
import json,ast,time,runpy
B=Path(__file__).resolve().parent;D=B/'E3_bridge_continuation';old=D/'prepare_actual_recovery_bridge_closed_source_once.py';s=old.read_text().replace("B.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021'","B.parent.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021'")
assert s!=old.read_text() and not (D/'two50_payloads').exists();path=D/'prepare_actual_recovery_bridge_closed_source_V2_once.py';path.open('x',encoding='utf8').write(s);ast.parse(s);runpy.run_path(str(path),run_name='__main__')
base=B.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/bound_controllers/three_slot_finite_owner_v1.py';new=D/'two_policy50_original_account_controllers/three_slot_finite_owner_v1.py'
def account(p):return ast.dump(next(n for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name=='account'),include_attributes=False)
assert account(base)==account(new)
v=dict(epoch=time.time(),passed_CPU_source_preparation=True,original_workspace_depth_error_and_source_retained=True,repair='Only local workspace-relative budget receipt/controller source path depth; no remote or GPU failure',E2_deferred_H1_native_pending=True,actual_only_scheduled_learning_expert='recovery',admission_reserve_seconds=7800,strict_budget_threshold_seconds=82512.86069250107,original_charge_and_account_function_AST_exact=True,safety_legacy_total1548000_eight_extensions_unchanged=True,only_actual_recovery_GO_to_terminal_charged=True,no_H1_native_learning_cost_or_refund=True,not_yet_deployed=True)
(D/'reports/H1_NATIVE210_RECOVERY_BRIDGE_SOURCE_AND_RESERVATION_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(v))
