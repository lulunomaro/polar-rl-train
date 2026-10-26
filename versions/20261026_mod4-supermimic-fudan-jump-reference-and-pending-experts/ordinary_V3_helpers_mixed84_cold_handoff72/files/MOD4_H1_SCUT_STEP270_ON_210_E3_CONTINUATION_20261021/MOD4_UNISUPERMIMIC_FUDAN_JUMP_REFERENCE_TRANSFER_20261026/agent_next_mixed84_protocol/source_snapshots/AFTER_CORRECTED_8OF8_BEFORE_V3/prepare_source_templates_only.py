"""Run only this source-template generator. Never imports transport or live code."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
T = HERE.parent.parent
NORMAL = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
NATIVE = T / 'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026'
snap = HERE / 'source_snapshots'
snap.mkdir()
(HERE / 'reports').mkdir()
(HERE / 'diffs').mkdir()
index = []


def source(path, label):
    raw = path.read_bytes()
    with (snap / label).open('xb') as stream:
        stream.write(raw)
    index.append(dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest(), snapshot=str(snap / label)))
    return raw.decode('utf8')


def output(name, text, old=None):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    ast.parse(text)
    with path.open('x', encoding='utf8', newline='') as stream:
        stream.write(text)
    if old is not None:
        diff = ''.join(difflib.unified_diff(old.splitlines(True), text.splitlines(True),
                                          fromfile='READ_ONLY_REFERENCE', tofile=name))
        with (HERE / 'diffs' / (name.replace('/', '_') + '.diff')).open('x', encoding='utf8') as stream:
            stream.write(diff)


old_proof = "proof=read(B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json');assert key in ('h1','recovery') and proof['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic' and set(proof['models'])=={'h1','recovery'} and set(proof['original_slots_cost'])=={'h1','e2','recovery'} and proof['native_method']['original_terminal']['original_error'] and proof['native_method']['present'] is False and abs(proof['actual_cost_sumonce']-sum(v['charged_seconds'] for v in proof['original_slots_cost'].values()))<1e-5 and all(v['duration_bound_passed'] for v in proof['original_slots_cost'].values())"
new_proof = "proof=read(B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json');assert key in ('h1','recovery') and proof['passed'] and set(proof['models'])=={'h1','e2','recovery'} and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free'] and all(v['actual_cost']['duration_bound_passed'] for v in proof['models'].values()) and abs(proof['actual_cost_sumonce']-sum(v['actual_cost']['charged_seconds'] for v in proof['models'].values()))<1e-5"
for key, role in (('h1', 'closed_production_continuation_CPU_v2.py'),
                  ('recovery', 'original_account_policy50_source_CPU.py')):
    old = source(NORMAL / 'payloads' / key / role, '83B_' + key + '_' + role)
    new = old.replace('NORMAL_THREE_83B_PRODUCTION_SOURCE_AUTH_ACTUAL.json', 'MIXED84_NORMAL_PRODUCTION_SOURCE_AUTH_ACTUAL.json')
    new = new.replace('actual_closed_production_pair_native_diagnostic_all3_cost_same_V8', 'actual_closed83B_healthy_three_same_V8_baseline')
    assert new.count(old_proof) == 1
    new = new.replace(old_proof, new_proof, 1)
    output('normal_' + key + '_source_guard_TEMPLATE.py', new, old)

for name in ('three_slot_common_v1.py', 'three_slot_finite_owner_v1.py',
             'three_slot_finite_node_v1.py', 'three_real_gpu_resource_v1.py',
             'forwarded_original_owner_control_v1.py'):
    old = source(NORMAL / 'controllers' / name, '83B_' + name)
    if name == 'three_slot_common_v1.py':
        needle_ready='def valid_ready(row,spec):'
        assert old.count(needle_ready)==1
        new = old.replace(needle_ready,
            "def valid_ready(row,spec):\n if spec.get('finite_method_test'):\n  from mixed84_protocol_v1 import native_valid_ready\n  return native_valid_ready(row,spec)", 1)
        needle = "(15669 if spec['key']=='h1' else 7000)"
        assert new.count(needle) == 1
        new = new.replace(needle, "(15669 if spec['key']=='h1' or spec.get('finite_method_test') else 7000)", 1)
        output('owner_controller_templates/' + name, new, old)
        output('native_controller_templates/' + name, new)
    elif name == 'three_real_gpu_resource_v1.py':
        needle = "(15669 if spec['key']=='h1' else 7000)"
        assert old.count(needle) == 1
        new = old.replace(needle, "(15669 if spec['key']=='h1' or spec.get('finite_method_test') else 7000)", 1)
        output('native_controller_templates/' + name, new, old)
        output('owner_controller_templates/' + name, old)
    else:
        output('owner_controller_templates/' + name, old)
module = (HERE / 'mixed84_protocol_v1.py').read_text('utf8')
output('owner_controller_templates/mixed84_protocol_v1.py', module)

worker = source(NATIVE / 'payloads/e2/h1_unisupermimic_step270_worker_v1.py', '82Q_native_worker.py')
newworker = worker.replace('UNISUPERMIMIC_ACTUAL_H1_STEP270_CROSSHOST_SOURCE_SDK_CPU',
                          'UNISUPERMIMIC_FUDAN_H1_83B_CROSSHOST_SOURCE_SDK_CPU_V84')
assert newworker != worker
output('h1_unisupermimic_step270_worker_v84_TEMPLATE.py', newworker, worker)

installer = source(NATIVE / 'e2_target72_same_backend_install_source_v1.py', '82Q_e2_installer.py')
tree = ast.parse(installer)
code = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)))
loop_start = code.index("for row in v['manifest']['files']:")
loop_end = code.index('\nprint(json.dumps(', loop_start)
original_copy_loop = code[loop_start:loop_end]
prefix = '''from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
B=Path(v['root']);s=v['spec'];old=Path(s['previous_runtime_root']);owned=Path('/home/lc01/Zonglin Li/zonglin2')
assert s['key']=='e2' and s['h1_step270_method_test'] and s['finite_method_test'] and s['execution_backend']=='target72' and s['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and not s.get('cross_host_qualified_source')
assert str(B)==str(owned/'tasks/H1step270_mixed_supermimic_fudan_2610v84/e2') and str(old)==str(owned/'tasks/H1step270_three_experts_2610v83b/e2') and B.resolve().is_relative_to(owned.resolve())
proof=v['closedproof'];assert proof['passed'] and set(proof['models'])=={'h1','e2','recovery'} and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
assert proof['models']['h1']['final']['SHA']==s['source_SHA']=='8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6' and proof['models']['h1']['Adam']==s['source_Adamstep']==829700
assert proof['models']['e2']['final']['SHA']=='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f' and proof['models']['e2']['Adam']==857460
assert all(x['actual_cost']['duration_bound_passed'] for x in proof['models'].values()) and abs(proof['actual_cost_sumonce']-sum(x['actual_cost']['charged_seconds'] for x in proof['models'].values()))<1e-5
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['terminal_all_own_children_waited'] and r['returncode']==0 and not r['original_error'] and not r['errors'] and r['final']['passed'] and r['final']['final']['SHA']==proof['models']['e2']['final']['SHA']
assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for p in (Path(s['private_lock']),owned/'state/finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines())
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x);assert int(line.split(',')[-1])>15669
assert not B.exists();B.mkdir(parents=True);before={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};need=[];copied=0
'''
suffix = "\nprint(json.dumps(dict(epoch=time.time(),root=str(B),need_upload=need,source_files_reused=copied,GPU_line=line,durable_free=shutil.disk_usage(owned).free,healthy83B_E2_physical_slot_closed=True,H1_83B_source_is_separate=True,no_native82Q_source_promotion=True,no_GO_or_canonical_write=True)))\n"
new_code = prefix + original_copy_loop + suffix
ast.parse(new_code)
output('e2_healthy83B_physical_resource_install84_TEMPLATE.py', '"""Remote code TEMPLATE; never executed by source preparation."""\nCODE = ' + repr(new_code) + '\n')
with (HERE / 'diffs/e2_installer_remote_body.diff').open('x', encoding='utf8') as stream:
    stream.write(''.join(difflib.unified_diff(code.splitlines(True), new_code.splitlines(True), fromfile='HISTORICAL82Q', tofile='NEW84_HEALTHY83B')))

deploy = source(NATIVE / 'deploy_actual82q_checkpoint_context_fixed_H1_method_original_writer_unused_once.py', '82Q_deployer.py')
new = deploy.replace('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026', 'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026')
new = new.replace('DEPLOYER_REUSED_H1_HELPER_82Q_EXACT_SOURCE.py', 'DEPLOYER_REUSED_H1_HELPER_84_EXACT_SOURCE.py')
new = new.replace('from e2_target72_same_backend_install_source_v1 import CODE', 'from e2_healthy83B_physical_resource_install84_TEMPLATE import CODE')
new = new.replace("test_native_h1_goal_mdp_and_learner_CPU_v1.py", "test_native_h1_fudan_reference_CPU_v84.py")
new = new.replace("reports/NATIVE_H1_GOAL_MDP_AND_LEARNER_CPU_V1_ACTUAL.json", "reports/NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V84_ACTUAL.json")
needle = "assert q['passed'] and set(q['specs'])=={'h1','e2','recovery'} and receipt['passed']"
assert new.count(needle) == 1
new = new.replace(needle, needle + ";from mixed84_protocol_v1 import validate_reference_preparation;validate_reference_preparation(q['reference_preparation']);assert q['preparation_scope']=='SOURCE_PREPARED_NOT_TARGET_ADMITTED'", 1)
new = new.replace('no_active80_hotpatch=True', 'no_active83B_hotpatch=True')
output('deploy_mixed84_original_writer_TEMPLATE.py', new, deploy)
helper = source(NORMAL / 'DEPLOYER_REUSED_H1_HELPER_83B_EXACT_SOURCE.py', '83B_H1_deployer_helper.py')
assert helper.count('82512.86069250107') == 1
output('DEPLOYER_REUSED_H1_HELPER_84_EXACT_SOURCE_TEMPLATE.py', helper.replace('82512.86069250107', '86412.86069250107'), helper)

collector = source(NORMAL / 'collect_actual_three83B_finals_original_cost_unused_once.py', '83B_collector.py')
new = collector.replace("R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'", "R/'MIXED84_ACTUAL_GO_BASELINES_AND_NATIVE_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'")
new = new.replace("p=N/'current_three_closed_models'/key/PurePosixPath(row['path']).name;", "p=N/('current_native_H1_method_fullstate' if key=='e2' else 'current_baseline_closed_models')/key/PurePosixPath(row['path']).name;")
new = new.replace("complete_models=complete,all_texts=texts", "complete_models={k:v for k,v in complete.items() if k!='e2'},native_H1_method_fullstate=complete['e2'],all_texts=texts")
new = new.replace("'THREE_EXPERT_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'", "'MIXED84_BASELINES_NATIVE_H1_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'")
output('collect_mixed84_finals_original_cost_TEMPLATE.py', new, collector)

# Reference metadata snapshots only. No model/raw/NPZ/USD content is read.
for path, label in (
    (NORMAL / 'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json', '83B_complete_metadata.json'),
    (NORMAL / 'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json', '83B_detached_metadata.json'),
    (NORMAL / 'payloads/h1/same_optimized_source_contract_metadata_candidate_v1.py', 'metadata_exact_CRLF.py'),
    (NATIVE / 'payloads/e2/job0/runtime/isaac/mod4/sensor_a0_runtime.py', 'sensor_a0_runtime.py')):
    source(path, label)
with (HERE / 'reports/SOURCE_SNAPSHOT_INDEX_ACTUAL.json').open('x', encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(), source_only=True, files=index,
                   no_payload_or_model_copy_no_TASK_GO_no_network=True,
                   Git_status='PENDING_ROOT_PHASE_ARCHIVE'), stream, indent=2)
pending = dict(status='PENDING_ACTUAL_FUDAN_REFERENCE_ADAPTER_AND_ROOT_INTEGRATION',
               reference_bundle=None, native_candidate_files=None,
               reference_artifact_path=None, reference_provenance_path=None,
               adapter_CPU_report_path=None,
               actual_target_fresh_SDK_CPU=None, actual_target_native_CPU=None,
               all_unfinished_experts_queue='PRESERVED_PARENT_QUEUE_FIRST_H1_ONLY',
               candidate_V10_reward_deployment=False,
               ready=False, admitted=False, GO=False, templates_executed=False)
with (HERE / 'MIXED84_INTEGRATION_PENDING.json').open('x', encoding='utf8') as stream:
    json.dump(pending, stream, indent=2)
print(json.dumps(dict(source_templates_generated=True, ready=False, admitted=False, no_TASK_GO_or_payload_created=True)))
