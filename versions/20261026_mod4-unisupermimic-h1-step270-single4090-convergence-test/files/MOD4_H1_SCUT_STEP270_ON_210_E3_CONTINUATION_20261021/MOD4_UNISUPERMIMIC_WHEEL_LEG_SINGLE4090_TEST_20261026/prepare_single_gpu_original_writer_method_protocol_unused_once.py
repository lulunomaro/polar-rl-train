"""New isolated one-slot method test, inheriting the original charge function verbatim."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

J = Path(__file__).resolve().parent
T = J.parent
P = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_bytes())
proof = read(P / 'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
assert all(v['actual_cost']['duration_bound_passed'] for v in proof['models'].values())
assert read(J / 'reports/LOCAL_NATIVE30_ACTION6_CPU_V2_ADMITTED.json')['passed']
B = J / 'payload'
B.mkdir()
(B / 'reports').mkdir()
(B / 'job0').mkdir()
(B / 'artifacts').mkdir()
for name in ('mod4_supermimic_adapter.py', 'test_mod4_supermimic_native30_action6_CPU_v2.py', 'run_mod4_supermimic_single4090_finite_worker.py'):
    shutil.copy2(J / name, B / name)
for name in ('ACTUAL_MOD4_OFFLINE_TRANSITION_TEST_INPUT_PRODUCER_INDEX.json', 'HUMAN_UNISUPERMIMIC_ONE_DUAL4090_WHEELLEG_TEST_AUTH_ACTUAL.json'):
    shutil.copy2(J / 'reports' / name, B / 'reports' / name)
shutil.copy2(J / 'artifacts/mod4_native30_action6_saved_transition_test.npz', B / 'artifacts/mod4_native30_action6_saved_transition_test.npz')
for rel in ('rl/contracts/supermimic.py', 'rl/algos/supermimic/geometry.py', 'rl/algos/supermimic/networks.py'):
    p = B / 'upstream/src/unisupermimic' / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(J / 'upstream/src/unisupermimic' / rel, p)
for name in ('three_slot_finite_node_v1.py', 'three_real_gpu_resource_v1.py', 'forwarded_original_owner_control_v1.py'):
    shutil.copy2(P / 'payloads/e2' / name, B / name)
with (B / 'CURRENT_CLOSED80_ORIGINAL_MODELS_AND_COST_CPU_ACTUAL.json').open('x', encoding='utf8') as f:
    json.dump(proof, f, indent=2)

common = (P / 'controllers/three_slot_common_v1.py').read_text('utf8')
needle = 'def valid_ready(row,spec):\n'
assert common.count(needle) == 1
addition = ''' if spec.get('finite_method_test'):
  q=row.get('closed_source_CPU') or {};v=q.get('value') or {}
  return bool(spec['key']=='e2' and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and spec['execution_backend']=='target72' and row.get('key')=='e2' and row.get('phase')=='ready' and not row.get('original_error') and row.get('manifest_SHA')==spec['manifest_SHA'] and q.get('actual_CPU_waited_EXIT0') and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest() and v.get('passed') and v.get('kind')=='UNISUPERMIMIC_MOD4_NATIVE30_ACTION6_FINITE_METHOD_TEST' and v.get('source_SHA')==spec['source_SHA'] and v.get('GPU_UUID')==spec['GPU_UUID'] and v.get('upstream_revision')=='faf7818e8abac3ec6abb8f00e6e904d3577f800b' and v.get('actual_installed_CPU_passed') and v.get('native_joint_states')==30 and v.get('actions')==6 and v.get('source80_actual_cost_models_allout_passed') and v.get('not_production_E2_source_or_skill_qualification'))
'''
updated = common.replace(needle, needle + addition, 1)
assert updated.replace(needle + addition, needle, 1) == common
owner = (P / 'controllers/three_slot_finite_owner_v1.py').read_text('utf8')
assert owner.count("set(specs)=={'h1','e2','recovery'}") == 1
owner = owner.replace("set(specs)=={'h1','e2','recovery'}", "set(specs)=={'e2'}", 1)
owner = owner.replace("cfg['scheduling_authority']=='human_requested_available_experts'", "cfg['scheduling_authority']=='human_one_dual4090_wheelleg_method_test'", 1)
needle = "sum(b.CAPS[k] for k in specs)+9400.860692501068+512+64800"
assert owner.count(needle) == 1
owner = owner.replace(needle, '86412.86069250107', 1)
owner = owner.replace("kind='Linux_H1_STEP270_E3_'", "kind='UNISUPERMIMIC_MOD4_FINITE_METHOD_TEST_'", 1)
for folder in (B, J / 'owner_source'):
    folder.mkdir(exist_ok=True)
    (folder / 'three_slot_common_v1.py').write_text(updated, 'utf8')
(J / 'owner_source/three_slot_finite_owner_v1.py').write_text(owner, 'utf8')

guard = '''"""Actual installed CPU admission for the explicitly new finite method, not E2 production."""
from pathlib import Path
import hashlib,json,os,subprocess
def load(spec,B):
 B=Path(B);assert spec['finite_method_test'] and spec['key']=='e2' and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 source=json.loads((B/'reports/ACTUAL_MOD4_OFFLINE_TRANSITION_TEST_INPUT_PRODUCER_INDEX.json').read_bytes());assert spec['source_SHA']==source['SHA']
 proof=json.loads((B/'CURRENT_CLOSED80_ORIGINAL_MODELS_AND_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and all(v['actual_cost']['duration_bound_passed'] for v in proof['models'].values())
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1');p=subprocess.run([spec['python'],'-B','-X','utf8',str(B/'test_mod4_supermimic_native30_action6_CPU_v2.py'),'--installed'],cwd=B,env=env,capture_output=True,text=True,timeout=90)
 (B/'reports/ACTUAL_INSTALLED_CPU_STDOUT.txt').write_text(p.stdout,'utf8');(B/'reports/ACTUAL_INSTALLED_CPU_STDERR.txt').write_text(p.stderr,'utf8');assert p.returncode==0
 cpu=json.loads((B/'reports/ACTUAL_INSTALLED_NATIVE30_ACTION6_CPU_ADMITTED.json').read_bytes());assert cpu['passed'] and not cpu['CUDA_initialized'] and cpu['source_SHA']==spec['source_SHA']
 v=dict(passed=True,kind='UNISUPERMIMIC_MOD4_NATIVE30_ACTION6_FINITE_METHOD_TEST',source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',actual_installed_CPU_passed=True,native_joint_states=30,actions=6,source80_actual_cost_models_allout_passed=True,not_production_E2_source_or_skill_qualification=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
'''
(B / 'closed_production_continuation_CPU_v2.py').write_text(guard, 'utf8')
dataset = read(J / 'reports/ACTUAL_MOD4_OFFLINE_TRANSITION_TEST_INPUT_PRODUCER_INDEX.json')
spec = dict(key='e2', GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842', execution_backend='target72',
    max_parent_seconds=3900, exit_headroom_seconds=300,
    previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2610v80/e2', previous_exit_kind='node',
    private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock',
    python='/home/lc01/Zonglin Li/zonglin2/run-python.sh', source_SHA=dataset['SHA'],
    closed_production_continuation=True, legacy_node_dispatch_only_not_production_source_claim=True,
    finite_method_test=True, production_script='run_mod4_supermimic_single4090_finite_worker.py')
rows = []
for p in sorted(B.rglob('*')):
    if not p.is_file(): continue
    if p.suffix == '.py': ast.parse(p.read_text('utf8'))
    rows.append(dict(relative=p.relative_to(B).as_posix(), bytes=p.stat().st_size, SHA=H(p)))
manifest = dict(key='e2', source_SHA=dataset['SHA'], kind='UNISUPERMIMIC_MOD4_FINITE_METHOD_TEST_NOT_EXPERT_SOURCE', files=rows)
with (B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json').open('x', encoding='utf8') as f: json.dump(manifest, f, indent=2)
spec['manifest_SHA'] = H(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
q = dict(epoch=time.time(), root='/home/lc01/Zonglin Li/zonglin2/research/UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026/e2',
    owner_root='/mnt/mod4_linux_durable_20261013/UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026/owner',
    payload=str(B), spec=spec, closed80_original_fee_sumonce=proof['actual_cost_sumonce'], closed80_remaining_snapshot=proof['remaining_actual_snapshot'])
with (J / 'reports/REVIEWABLE_FINITE_SINGLE_GPU_METHOD_TEST_PAYLOAD_AND_ORIGINAL_WRITER_PLAN_ACTUAL.json').open('x', encoding='utf8') as f: json.dump(q, f, indent=2)
def function(src, name):
    tree = ast.parse(src)
    return ast.dump(next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name==name), include_attributes=False)
assert function(common, 'charge_values') == function(updated, 'charge_values')
assert function((P / 'controllers/three_slot_finite_owner_v1.py').read_text('utf8'), 'owner').count('charge_values') == function(owner,'owner').count('charge_values')
notice = dict(epoch=time.time(), existing_charge_values_AST_exact=True, original_owner_account_nested_function_unchanged=True,
    owner_only_changes=['exact one e2 slot scheduling','explicit human one-card test authority','strict86412.86069250107 reserve retained','new ledger segment kind label'],
    readiness_only_explicit_new_method_branch_added_original_production_predicates_unchanged=True,
    original_node_resource_private_shared_locks_send_terminal_childwait_bytes_exact=True,
    no_existing_owner_or_runtime_hotpatch=True, no_active_segment_copy_clear_refund_or_second_writer=True,
    new_model_not_production_source=True, no_new_budget=True, source_kind='actual MOD4 saved selected data, not G1 motion or existing expert PT',
    test_worker_self_bound_s=240, original_contract_cap3900_save3600_exit300=True)
with (J / 'reports/NEW_SINGLE_SLOT_METHOD_SCOPE_AND_ORIGINAL_ACCOUNTING_AST_CPU_ACTUAL.json').open('x', encoding='utf8') as f: json.dump(notice, f, indent=2)
print(json.dumps(dict(prepared_single_GPU_method_payload=True, original_accounting_AST_exact=True, no_GO=True)))
