from pathlib import Path
import json,ast,shutil,time,runpy,hashlib
B=Path(__file__).resolve().parent;W=B.parent;D=B/'E3_bridge_continuation';D.mkdir();(D/'reports').mkdir()
P=W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021';F=W/'MOD4_TWO_LINUX_POLICY50_COHORT_53_20261021';proof=json.loads((P/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled']
config=json.loads((F/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').read_bytes());config.update(cohort_id='H1_NATIVE210_RECOVERY_BRIDGE_20261021_V1',roots={'recovery':'/home/lc01/Zonglin Li/zonglin2/tasks/H1s270_E3bridge_2110v1/recovery'},owner_root='/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2110v1/owner',human_E2_deferred_for_H1_native=True)
(D/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').open('x',encoding='utf8').write(json.dumps(config,indent=2));shutil.copy2(F/'original_account_policy50_source_same_clock_v2_CPU.py',D/'original_account_policy50_source_same_clock_v2_CPU.py')
s=(F/'prepare_following_two50_closed_sources_CPU_once.py').read_text();s=s.replace("for key in ('e2','recovery'):","for key in ('recovery',):")
needle=" for key in ('recovery',):"
patch=""" owner_path=controllers/'three_slot_finite_owner_v1.py';owner=owner_path.read_text('utf8');owner=owner.replace(\"set(specs)=={'e2','recovery'}\",\"set(specs)=={'recovery'}\").replace(\"cfg['deferred_experts']==['h1']\",\"cfg['deferred_experts']==['e2','h1']\").replace(\"kind='Linux_AVAILABLE_E2_E3_'\",\"kind='Linux_RECOVERY_WHILE_H1_NATIVE210_'\").replace(\"sum(b.CAPS[k] for k in specs)+9400.860692501068\",\"sum(b.CAPS[k] for k in specs)+b.CAPS['h1']+9400.860692501068\");owner_path.write_text(owner,'utf8')
"""
assert needle in s;s=s.replace(needle,patch+needle)
path=D/'prepare_actual_recovery_bridge_closed_source_once.py';path.open('x',encoding='utf8').write(s);ast.parse(s);runpy.run_path(str(path),run_name='__main__')
base=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/bound_controllers/three_slot_finite_owner_v1.py';new=D/'two_policy50_original_account_controllers/three_slot_finite_owner_v1.py'
def account(p):return ast.dump(next(n for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name=='account'),include_attributes=False)
assert account(base)==account(new)
v=dict(epoch=time.time(),passed_CPU_source_preparation=True,recovery_source=proof['models']['recovery'],H1_native_source_preparation_deferred_no_GO=True,E2_deferred=True,actual_only_scheduled_learning_expert='recovery',admission_reserve_seconds=7800,strict_budget_threshold_seconds=82512.86069250107,safety64800_and_legacy9912_860692501068_and_original_total1548000_extensions8_unchanged=True,original_charge_and_account_function_AST_exact=True,only_actual_recovery_GO_to_terminal_is_charged_no_H1_native_learning_interval=True,no_new_canonical_path_or_ledger_or_refund=True,not_yet_deployed=True,human_routing_report=str(B/'reports/HUMAN_ROUTING_AUTHORITY_AND_CURRENT_BOUNDARY_ACTUAL.json'))
(D/'reports/H1_NATIVE210_RECOVERY_BRIDGE_SOURCE_AND_RESERVATION_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps({k:x for k,x in v.items() if k!='recovery_source'}))
