"""ZERO_UPDATE bound-only stdlib ONLY: seventeen complete mappings and original static plant; one NEW stage, NEVER dispatch.

Index Windows paths are provenance only; actual input sources are flat basenames.
No selected/mother checkpoint stat, hash, read, copy, decode, SDK, C or lock access.
The only evaluator invocation is full pinned --validate-plan under metadata I/O guards.
"""
from __future__ import annotations
import argparse
import ast
import builtins
import contextlib
import copy
import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import runpy
import sys
import time
import traceback

ROLES = ('E3', 'W35', 'CURB_INDEPENDENT113', 'CURB_PROTECTED878',
         'SLOPE135', 'SLOPE_INDEPENDENT50', 'E0', 'E2')
REQUESTED = ('E3', 'W35')
CONTROLS = dict(E0=1000, E2=1200, E3=160, W35=1600, CURB_PROTECTED878=750,
                CURB_INDEPENDENT113=750, SLOPE135=750, SLOPE_INDEPENDENT50=1000)
INDEX_PIN = (6085, 'd0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a')
ORIGINAL_GROUP_ID = 'MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700'
NATIVE_RUN_ID = 'MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000'
USD = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
VENDOR_PIN = (7, 'ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0')
ALIASES = {'single_gpu_e3_w35_bound_only_parent_v1.py', 'bound_only_native_runtime_v1.py',
    'worker_sources/parent/worker_five_original_n80.py', 'worker_sources/e1/e1_parallel_worker_safe.py',
    'worker_sources/e1/e1_fresh_runtime_bridge.py', 'a1_frozen_eval_runtime_v2.py',
    'frozen_a1_raw35_v1.py', 'pose_cache_runtime_adapter_v3.py', 'app_close_semantics_v5.py',
    'native_supermimic_bridge.py', 'supermimic_vendor_v2/networks.py',
    'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py', 'resume_runtime_contracts_v3.py',
    'bound_only_native_helper_v1.py', 'bound_only_native_route_v1.py', 'producer_bound_probe_guard_v1.py'}
MODEL_SUFFIXES = {'.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.pt2', '.pkl', '.pickle'}
DENIED_SUFFIXES = MODEL_SUFFIXES | {'.pyc', '.pyo', '.partial', '.jsonl', '.log', '.lock'}
DENIED_NAMES = {'model', 'models', 'adaptation', 'production', 'checkpoint', 'checkpoints',
    'kit', 'kit_storage', 'kit_isolation', 'private', 'private_train', 'home', 'tmp',
    'cache', 'caches', '.cache', 'logs', 'log', 'raw', 'reports', 'cases', 'results',
    '__pycache__', '.git', '.pytest_cache', 'deriveddatacache', 'tensorboard', 'wandb'}
COUNTS = ('policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps', 'pi_unverified_steps',
          'pi_skipped_nonfinite', 'pi_skipped_zero', 'wm_optimizer_steps', 'aux_optimizer_steps', 'critic_optimizer_steps')
POSE_SHA = '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f'
DEPENDENCY_PIN = (22337, 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7')
APP_CLOSE_PIN = (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39')


def need(value, message):
    if not value:
        raise ValueError(message)


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def is_sha(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def lexical(path):
    """No resolve/lstat: checkpoint locations here are metadata, not file observations."""
    return Path(os.path.abspath(os.fspath(path)))


def model_path(path):
    return not isinstance(path, int) and Path(os.fspath(path)).suffix.lower() in MODEL_SUFFIXES


def metadata(path, maximum=8 * 1024 * 1024):
    path = Path(path)
    need(path.suffix == '.json' and 'budget' not in path.name.lower(), 'explicit non-budget JSON metadata only')
    with path.open('rb') as stream:
        raw = stream.read(maximum + 1)
    need(len(raw) <= maximum, 'bounded JSON metadata exceeded: ' + path.name)
    value = json.loads(raw)
    need(type(value) is dict, 'metadata object required: ' + path.name)
    return value, raw


def safe_relative(value):
    need(type(value) is str and value and '\\' not in value and ':' not in value,
         'plain relative POSIX installed alias required')
    parts = value.split('/')
    need(not value.startswith('/') and all(p not in ('', '.', '..') for p in parts), 'relative alias escaped root')
    return value


def denied(name):
    lower = name.lower()
    suffix = Path(name).suffix.lower()
    states = {'go_production.json', 'stop_after_save.json', 'final.json', 'task.json',
              'parent_waited_actual.json', 'owner_started.json', 'owner_current.json',
              'owner_exit_actual.json', 'cohort_final.json', 'group_start.json', 'group_abort.json'}
    return (lower in DENIED_NAMES or lower in states or suffix in DENIED_SUFFIXES
            or (suffix != '.py' and ('budget' in lower or lower.startswith(('private_', 'kit_', 'raw_'))
                or '_raw.' in lower or '_skill_raw' in lower)))


def no_links(root, relative):
    cursor = Path(root)
    need(not cursor.is_symlink(), 'symlink root is not static source')
    for part in PurePosixPath(safe_relative(relative)).parts:
        cursor /= part
        need(not cursor.is_symlink(), 'static source symlink is not followed: ' + relative)
    return cursor


def identity(path):
    path = Path(path)
    # Callers reject every RELATIVE tree component before classification. Absolute
    # input ancestors may legitimately be /home or /tmp on Linux.
    need(not denied(path.name), 'denied path must not be stat/read/hashed')
    digest = hashlib.sha256(); size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk); size += len(chunk)
    return dict(bytes=size, SHA=digest.hexdigest())


def tree(root):
    """Reject names BEFORE DirEntry classification; preserve complete non-denied bytes."""
    root = Path(root)
    need(not root.is_symlink() and root.is_dir(), 'explicit static tree missing or symlinked')
    result = {}
    def visit(directory, prefix):
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda e: e.name):
                if denied(entry.name):
                    continue
                need(not entry.is_symlink(), 'static symlink is not followed: ' + entry.name)
                rel = (prefix / entry.name).as_posix()
                if entry.is_dir(follow_symlinks=False):
                    visit(Path(entry.path), prefix / entry.name)
                elif entry.is_file(follow_symlinks=False):
                    result[rel] = (Path(entry.path), identity(Path(entry.path)))
                else:
                    raise ValueError('special static file: ' + entry.name)
    visit(root, PurePosixPath())
    return result


def digest_tree(items):
    rows = [dict(relative=rel, **info) for rel, (_, info) in sorted(items.items())]
    return dict(files=len(rows), SHA=H(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()))


def source_mappings(source_dir, source_index):
    index, raw = metadata(source_index)
    need((len(raw), H(raw)) == INDEX_PIN, 'sealed seventeen-mapping index pin differs')
    need(index.get('kind') == 'SOURCE_ONLY_17_MAPPINGS_ZERO_UPDATE_BOUND_ONLY_NATIVE_V1', 'index schema differs')
    entries = index.get('entries'); need(type(entries) is list and len(entries) == 17, 'exact seventeen mappings required')
    result = {}; basenames = set(); source_dir = Path(source_dir)
    for entry in entries:
        rel = safe_relative(entry['relative'])
        basename = entry['path'].replace('\\', '/').rsplit('/', 1)[-1]
        need(basename and basename not in ('.', '..') and basename not in basenames, 'flat source basename duplicate')
        basenames.add(basename)
        need(rel in ALIASES and rel not in result, 'duplicate/unknown installed alias')
        path = no_links(source_dir, basename); info = identity(path)
        need((info['bytes'], info['SHA']) == (entry['bytes'], entry['SHA256']), 'flat source pin differs: ' + basename)
        ast.parse(path.read_bytes())  # Validate complete module; never slice/transform it.
        result[rel] = (path, info)
    need(set(result) == ALIASES, 'complete seventeen reference mappings required once')
    return result, dict(path=str(source_index), bytes=len(raw), SHA=H(raw), provenance_paths_not_dereferenced=True)


def semantic_success(row):
    semantic = row.get('semantic_result')
    need(row.get('phase') == 'terminal' and row.get('terminal_all_own_children_waited') is True
         and type(row.get('returncode')) is int and row['returncode'] == 0
         and row.get('original_error') is False, 'original actual-wait terminal row failed')
    need(type(semantic) is dict and semantic.get('kind') == 'ACTUAL_WAIT_APP_CLOSE_SEMANTIC_RESULT_V5'
         and semantic.get('passed_execution') is True
         and semantic.get('original_error') is False and semantic.get('actual_wait_returned') is True
         and type(semantic.get('returncode')) is int and semantic['returncode'] == 0
         and semantic.get('reasons') == [] and semantic.get('error_sidefiles') == [], 'original waited semantic failed')
    return semantic


def producer_final(final, job, entry, run):
    need(final.get('kind') == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
         and final.get('passed_execution') is True and final.get('teacher_unchanged') is True, 'successful actual FINAL required')
    need(final.get('role') == entry['role'] and final.get('role_key') == entry['role_key']
         and final.get('run_id') == run, 'actual producer identity differs')
    need(final.get('actor_view') == 'raw35_legacy_held_aux_v1'
         and final.get('algorithm_family') == 'a1_raw35_legacy_v1'
         and final.get('algorithm_variant') in ('A1_RAW35_FRESH', 'A1_RAW35_RESUME'), 'actual A1 raw35 producer required')
    counts = final.get('counts')
    need(type(counts) is dict and set(counts) == set(COUNTS)
         and all(type(v) is int and v >= 0 for v in counts.values()), 'nine actual nonnegative counts required')
    need(counts['pi_bptt_optimizer_steps'] <= counts['pi_optimizer_steps'] <= counts['policy_attempts']
         and type(final.get('actual_BPTT_policy_steps')) is int
         and final['actual_BPTT_policy_steps'] == counts['pi_bptt_optimizer_steps'], 'actual count order differs')
    checkpoint = final.get('checkpoint')
    need(type(checkpoint) is dict and checkpoint.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved') is True
         and checkpoint.get('teacher_unchanged') is True and checkpoint.get('counts') == counts
         and type(checkpoint.get('bytes')) is int and checkpoint['bytes'] > 0 and is_sha(checkpoint.get('SHA')), 'full checkpoint metadata required')
    location = lexical(checkpoint.get('path', ''))
    need(location.is_relative_to(job / 'production' / 'checkpoints') and location.name.endswith('_complete.pt')
         and '..' not in Path(checkpoint['path']).parts, 'lexically own complete checkpoint required')


def native_boundary(native_root):
    root = lexical(native_root)
    plan, plan_raw = metadata(root / 'OWNER_PLAN.json')
    exit_value, exit_raw = metadata(root / 'OWNER_EXIT_ACTUAL.json')
    cohort, cohort_raw = metadata(root / 'COHORT_FINAL.json')
    run = plan.get('run_id')
    need(run == root.name == NATIVE_RUN_ID and exit_value.get('run_id') == cohort.get('run_id') == run,
         'exact Admission2 own native identity required')
    need(all(exit_value.get(k) is True for k in ('all_own_children_waited', 'original_cost_settled', 'original_leases_released'))
         and exit_value.get('errors') == [] and exit_value.get('H1_excluded') is True, 'native actual wait/cost/lease boundary not closed')
    need(cohort.get('all_own_children_waited') is True and cohort.get('original_cost_settled') is True
         and cohort.get('errors') == [] and cohort.get('H1_excluded') is True, 'native original cohort not normally closed')
    need(not (root / 'OWNER_ORIGINAL_ERROR.json').exists(), 'native original parent error exists')
    entries = plan.get('entries')
    need(type(entries) is list and len(entries) == 8 and {e['role'] for e in entries} == set(ROLES), 'exact native eight-role catalog required')
    rows, go = cohort.get('rows'), cohort.get('go')
    need(type(rows) is dict and type(go) is dict and rows and set(rows) == set(go), 'all actual GO keys must be terminal')
    by_key = {e['role_key']: e for e in entries}; need(len(by_key) == 8 and set(rows) <= set(by_key), 'native role keys differ')
    for key, row in rows.items():
        semantic_success(row)
        need(row.get('key') == key and row.get('role') == by_key[key]['role']
             and go[key].get('role_key') == key and go[key].get('run_id') == run
             and go[key].get('role') == by_key[key]['role'], 'native GO/row role identity differs')
    selected = {}; evidence = {}
    for role in REQUESTED:
        entry = next(e for e in entries if e['role'] == role); key = entry['role_key']
        need(key in rows, 'requested producer was not actually GO/waited')
        job = lexical(entry['job_root']); need(job == root / 'roles' / role, 'exact own native job root required')
        waited, waited_raw = metadata(job / 'PARENT_WAITED_ACTUAL.json')
        need(waited == rows[key], 'original PARENT_WAITED does not match normal cohort row')
        sem = semantic_success(waited)
        for location in (job, job / 'production'):
            with os.scandir(location) as children:
                need(not any('ERROR' in child.name.upper() and child.name.endswith(('.json', '.txt')) for child in children),
                     'original requested worker error sidefile exists')
        final, final_raw = metadata(job / 'production' / 'FINAL.json')  # Exactly ONE byte read; hash the same bytes.
        producer_final(final, job, entry, run)
        need(final == waited.get('final') == sem.get('final'), 'actual FINAL differs from actual-wait semantic evidence')
        selected[role] = dict(own_job_root=str(job), FINAL_path=str(job / 'production' / 'FINAL.json'),
                              FINAL_bytes=len(final_raw), FINAL_SHA=H(final_raw), FINAL=final,
                              run_id=run, role_key=key)
        evidence[role] = dict(FINAL_byte_reads=1, FINAL_SHA=H(final_raw), FINAL_bytes=len(final_raw),
                              PARENT_WAITED_SHA=H(waited_raw), actual_BPTT_policy_steps=final['actual_BPTT_policy_steps'])
    return selected, dict(native_root=str(root), run_id=run, OWNER_PLAN_SHA=H(plan_raw), OWNER_EXIT_SHA=H(exit_raw),
        COHORT_FINAL_SHA=H(cohort_raw), all_own_children_waited=True, original_cost_settled=True,
        original_leases_released=True, actual_canonical_ledger_read_or_written=False,
        actual_closed_metadata_not_a_new_admission=True, producer_evidence=evidence,
        pending_unstarted_roles=cohort.get('pending_unstarted_roles'), checkpoint_stat_hash_open_decode=0)


def paired_plan():
    protocol = dict(pose_source_SHA=POSE_SHA, pose_source_bytes=18161,
        pose_source_version='POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1',
        install_timing='after_env_construction_before_original_single_explicit_reset', seed=20260928, num_envs=80,
        explicit_original_reset_count=1, physics_dt=.0025, control_dt=.02, feedback_hz=100,
        actor_observation='original_noisy_delayed_policy35')
    return dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', reference_planned_protocol=dict(protocol),
        candidate_planned_protocol=dict(protocol), historical_bug_baseline_reused=False, reference_actual_receipt=None)


def prepare(original_group_root, original_plan, source_dir, source_index, native_root, new_root, group_id, gpu_uuid,
            *, vendor_pin=VENDOR_PIN, collect_action_statistics=False):
    need(type(collect_action_statistics) is bool, 'statistics selection must be an explicit bool')
    original_group_root, new_root = lexical(original_group_root), lexical(new_root)
    need(not new_root.is_symlink() and not new_root.exists(), 'new-root must not exist; no overwrite or retry')
    need(group_id == new_root.name and group_id != ORIGINAL_GROUP_ID
         and re.fullmatch(r'[A-Za-z0-9_]+', group_id), 'new explicit group-id/root name required')
    need(re.fullmatch(r'GPU-[0-9a-f-]+', gpu_uuid) is not None, 'explicit GPU UUID required')
    for old in (original_group_root, lexical(native_root), lexical(source_dir)):
        need(not new_root.is_relative_to(old) and not old.is_relative_to(new_root), 'new-root overlaps an input')
    producers, boundary = native_boundary(native_root)  # Hard prerequisite BEFORE static staging work.
    sources, index_receipt = source_mappings(source_dir, source_index)
    old, old_raw = metadata(original_plan)
    need(old.get('group_id') == original_group_root.name == ORIGINAL_GROUP_ID
         and old.get('asset_SHA') == USD and old.get('contract_SHA') == CONTRACT, 'exact original V8 group/assets required')
    original_rows = old.get('roles')
    need(type(original_rows) is list and len(original_rows) == 9
         and {r['role'] for r in original_rows} == set(ROLES) | {'H1_normal'}, 'original complete nine-to-eight catalog differs')
    materials = {}
    for directory in ('worker_sources', 'pinned_assets'):
        for rel, value in tree(original_group_root / directory).items():
            materials[directory + '/' + rel] = value
    for item in old.get('worker_files', []):
        rel = safe_relative(item['relative']); need(not any(denied(p) for p in rel.split('/')), 'old worker list contains non-static input')
        src = no_links(original_group_root, rel); info = identity(src)
        need(info == {k: item[k] for k in ('bytes', 'SHA')}, 'actual original worker-file pin differs: ' + rel)
        materials[rel] = (src, info)
    need(old.get('worker_files') and len({r['relative'] for r in old['worker_files']}) == len(old['worker_files']), 'unique original worker list required')
    plan = dict(kind='FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_PLAN_V1', batch_purpose='FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1', policy_variant='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1',
        group_id=group_id, GPU_UUID=gpu_uuid, asset_SHA=USD, contract_SHA=CONTRACT,
        requested_roles=list(REQUESTED), deferred_roles=[r for r in ROLES if r not in REQUESTED],
        comparison=None, relative_improvement=None, paired_actual_reference=None, UID_alignment=None,
        reference_cache_match=None, reward_effect_identification=None, overall_eight_pass_rate=None,
        all_eight_actual_execution_complete=None, actual_resource_admission=None, actual_frozen_evaluation=None,
        W35_moving_or_standing_rate_from_combined_events=None, paired_reset_protocol=paired_plan(), roles=[])
    by_role = {row['role']: row for row in original_rows}
    for role in ROLES:
        row = copy.deepcopy(by_role[role]); need(row.get('controls') == CONTROLS[role], 'original controls differ')
        old_runtime = lexical(row['runtime_root'])
        need(old_runtime == original_group_root / 'runtimes' / role, 'original runtime not exact group role tree')
        for rel, value in tree(old_runtime).items():
            materials['runtimes/' + role + '/' + rel] = value
        asset = lexical(row['asset_dir']); need(asset.is_relative_to(old_runtime), 'original asset-dir escaped original role runtime')
        historical = {k: row.pop(k) for k in list(row) if k.startswith('source_')}
        row.update(runtime_root=str(new_root / 'runtimes' / role),
                   asset_dir=str(new_root / 'runtimes' / role / asset.relative_to(old_runtime)),
                   historical_mother_source=historical, source_identity='DEFERRED_NOT_A_NEW_CACHE_SOURCE',
                   a1_producer=None, num_envs=80, seed=20260928)
        if role in REQUESTED:
            row['a1_producer'] = producers[role]; checkpoint = producers[role]['FINAL']['checkpoint']
            row.update(source_path=checkpoint['path'], source_SHA=checkpoint['SHA'], source_bytes=checkpoint['bytes'],
                       source_identity='OWN_A1_FULL_NEW_CHECKPOINT_NOT_MOTHER_OR_OLD_PPO')
            guard_path = sources['producer_bound_probe_guard_v1.py'][0]
            spec = importlib.util.spec_from_file_location('_teacher_guard_stage_v1', guard_path)
            guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
            row.update(policy_variant='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1', actor_semantics='OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE',
                actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
                original_bootstrap_teacher=guard.teacher_identity(producers[role]['FINAL']['teacher']),
                producer_teacher_freeze_evidence=guard.derive_producer_guard(producers[role]),
                bound_only_probe=dict(purpose='FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1', policy_variant='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1',
                    zero_update=True, native_enabled=True, collect_action_statistics=collect_action_statistics))
        plan['roles'].append(row)
    vendor = tree(Path(native_root) / 'roles' / 'E3' / 'worker_sources' / 'supermimic_vendor_v2')
    observed = digest_tree(vendor)
    need((observed['files'], observed['SHA']) == vendor_pin, 'actual native complete seven-file vendor tree differs')
    need({'__init__.py', 'learner.py', 'networks.py', 'geometry.py', 'replay.py', 'contract.py'} <= set(vendor)
         and all('/' not in rel and rel.endswith('.py') for rel in vendor), 'complete flat seven-module vendor required')
    init = ast.parse(vendor['__init__.py'][0].read_bytes())
    need(len(init.body) == 1 and isinstance(init.body[0], ast.Expr)
         and isinstance(init.body[0].value, ast.Constant) and type(init.body[0].value.value) is str,
         'native vendor __init__ must contain docstring only; never rewrite/crop it')
    for rel, value in vendor.items(): materials['supermimic_vendor_v2/' + rel] = value
    for rel, value in sources.items():
        if rel.startswith('supermimic_vendor_v2/'):
            need(materials[rel][1] == value[1], 'native vendor/index source mismatch')
        materials[rel] = value
    verify_aliases = {item['relative'] for item in old['worker_files']} | ALIASES | {'supermimic_vendor_v2/' + rel for rel in vendor}
    plan['worker_files'] = [dict(relative=rel, **materials[rel][1]) for rel in sorted(verify_aliases)]
    encoded = json.dumps(plan, indent=2, allow_nan=False).encode()
    need(len(encoded) <= 262144, 'plan exceeds sealed metadata CLI bound')
    validation = metadata_validate(source_dir, plan_bytes=encoded)
    return dict(plan=plan, materials=materials, boundary=boundary, source_index=index_receipt,
        original_plan_SHA=H(old_raw), native_vendor=observed, new_root=new_root, encoded_plan=encoded,
        metadata_validation=validation)


def verify_close_dependency_imports(app_source, base_source):
    """Real full-module imports, no stubs or SDK instance/close calls."""
    app_source, base_source = Path(app_source), Path(base_source)
    receipts = {}
    for label, path, pin, extra in (
        ('contracts', base_source, DEPENDENCY_PIN, set()),
        ('AppV6', app_source, APP_CLOSE_PIN, {'resume_runtime_contracts_v3'})):
        raw = path.read_bytes()
        need((len(raw), H(raw)) == pin, 'close dependency source pin differs: ' + label)
        parsed = ast.parse(raw)
        roots = set()
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import): roots.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: roots.add(node.module.split('.')[0])
        need(roots <= set(sys.stdlib_module_names) | {'__future__'} | extra,
             'unexpected non-stdlib close dependency import: ' + label)
        receipts[label] = dict(path=str(path), bytes=len(raw), SHA256=H(raw), import_roots=sorted(roots),
                               full_original_module=True, AST_cropped_or_stubbed=False)
    names = ('app_close_semantics_v5', 'resume_runtime_contracts_v3')
    before = {name: sys.modules.get(name) for name in names}
    try:
        for name in names: sys.modules.pop(name, None)
        base_spec = importlib.util.find_spec('resume_runtime_contracts_v3')
        need(base_spec is not None and Path(base_spec.origin).resolve() == base_source.resolve(),
             'real base dependency must resolve in the actual source/stage root')
        base = importlib.import_module('resume_runtime_contracts_v3')
        need(Path(base.__file__).resolve() == base_source.resolve(), 'actual contracts import origin differs')
        app_spec = importlib.util.spec_from_file_location('app_close_semantics_v5', app_source)
        app = importlib.util.module_from_spec(app_spec)
        sys.modules['app_close_semantics_v5'] = app
        app_spec.loader.exec_module(app)  # Entire unchanged helper, including its real import at line 23.
        need(app._base is base and base.FINAL_KIND == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
             and callable(base.evaluate_waited_worker), 'helper must bind real complete contracts module')
        need(app.SOURCE_CODE_VERSION == 'V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES', 'actual AppV6 version differs')
        need(not any(name in sys.modules for name in ('torch', 'isaacsim', 'omni')), 'dependency check imported native package')
        return dict(kind='REAL_COMPLETE_APP_V6_CONTRACTS_IMPORT_CHECK_V2', passed=True,
                    modules=receipts, helper_base_is_actual_imported_contracts=True,
                    model_C_lock_SDK_GPU_operations=0, actual_SimulationApp_binding=None,
                    actual_close_or_wait_performed=False)
    finally:
        for name, old in before.items():
            if old is None: sys.modules.pop(name, None)
            else: sys.modules[name] = old


def metadata_validate(root, *, plan_bytes=None):
    """Execute the COMPLETE pinned metadata CLI, never parent/worker or cropped AST.

    Its existing checkpoint Path.resolve is made lexical ONLY for model suffixes,
    avoiding implicit lstat. The actual future admitted cache still verifies real bytes.
    Explicit file guards reject model/budget I/O; no physical model containment claim.
    """
    root = Path(root); old_path = list(sys.path); old_argv = sys.argv; old_bytecode = sys.dont_write_bytecode
    old_resolve, old_open, old_io_open = Path.resolve, builtins.open, io.open
    old_stat, old_lstat = os.stat, os.lstat
    watched = ('a1_frozen_eval_runtime_v2', 'bound_only_native_runtime_v1', 'bound_only_native_helper_v1', 'bound_only_native_route_v1', 'frozen_a1_raw35_v1', 'producer_bound_probe_guard_v1', 'app_close_semantics_v5', 'resume_runtime_contracts_v3')
    old_modules = {name: sys.modules.get(name) for name in watched}; avoided = []
    def resolve(path, *args, **kwargs):
        if model_path(path): avoided.append(str(path)); return lexical(path)
        return old_resolve(path, *args, **kwargs)
    def guarded(function):
        def call(path, *args, **kwargs):
            need(not model_path(path) and not (not isinstance(path, int) and 'budget' in Path(os.fspath(path)).name.lower()),
                 'metadata validation attempted model or budget filesystem access')
            if function in (old_open, old_io_open) and plan_bytes is not None and not isinstance(path, int) and lexical(path) == lexical(root / 'GROUP_PLAN.json'):
                mode = args[0] if args else kwargs.get('mode', 'r')
                need(mode == 'rb', 'in-memory preflight plan is read-only bytes')
                return io.BytesIO(plan_bytes)
            return function(path, *args, **kwargs)
        return call
    output = io.StringIO()
    try:
        sys.path.insert(0, str(root)); sys.argv = [str(root / 'bound_only_native_runtime_v1.py'), '--validate-plan', str(root / 'GROUP_PLAN.json')]
        sys.dont_write_bytecode = True
        for name in watched: sys.modules.pop(name, None)
        Path.resolve = resolve; builtins.open = guarded(old_open); io.open = guarded(old_io_open)
        os.stat = guarded(old_stat); os.lstat = guarded(old_lstat)
        dependency = verify_close_dependency_imports(
            root / ('app_close_semantics_v6.py' if plan_bytes is not None else 'app_close_semantics_v5.py'),
            root / 'resume_runtime_contracts_v3.py')
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(root / 'bound_only_native_runtime_v1.py'), run_name='__main__')
        result = json.loads(output.getvalue())
        need(result.get('policy_variant') == 'A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1' and result.get('zero_update_bound_probe') is True and result.get('actual_native_enabled') is False, 'bound-only metadata CLI variant differs')
        need(result.get('requested_roles') == list(REQUESTED) and result.get('resources_acquired') == result.get('model_opens') == 0,
             'sealed metadata CLI did not validate exact requested batch')
        need('torch' not in sys.modules and 'isaacsim' not in sys.modules, 'metadata CLI imported native package')
        result.update(dependency_completeness=dependency, model_path_resolve='LEXICAL_METADATA_ONLY_NO_LSTAT', model_lstats_avoided=len(avoided),
                      physical_checkpoint_containment_observed=None, parent_or_worker_executed=False)
        return result
    finally:
        Path.resolve, builtins.open, io.open = old_resolve, old_open, old_io_open
        os.stat, os.lstat = old_stat, old_lstat
        sys.path[:] = old_path; sys.argv = old_argv; sys.dont_write_bytecode = old_bytecode
        for name, previous in old_modules.items():
            if previous is None: sys.modules.pop(name, None)
            else: sys.modules[name] = previous


def put_once(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def put_json(path, value):
    put_once(path, (json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def preflight_summary(prepared):
    return dict(kind='SOURCE_BOUND_ONLY_NATIVE_PREFLIGHT_NO_ADMISSION_V1', passed=True,
        new_root=str(prepared['new_root']), requested_roles=list(REQUESTED), deferred_roles=list(ROLES[2:]),
        files=len(prepared['materials']), source_index=prepared['source_index'], native_boundary=prepared['boundary'],
        native_vendor=prepared['native_vendor'], original_plan_SHA=prepared['original_plan_SHA'],
        metadata_validation=prepared['metadata_validation'], resource_admission=None, actual_frozen_evaluation=None, comparison=None, overall_eight_pass_rate=None,
        model_stat_hash_open_decode=0, C_lock_SDK_GPU_GO_operations=0, parent_launches=0, staged=False, actual_native_enabled=False)


def stage(prepared):
    root = prepared['new_root']; need(not root.is_symlink() and not root.exists(), 'actual stage root already exists')
    root.mkdir(parents=False, exist_ok=False)  # once only; no automatic cleanup or overwrite after failure
    put_json(root / 'STAGE_BEGIN_BOUND_ONLY_NATIVE_V1.json', preflight_summary(prepared))
    try:
        rows = []
        for rel, (source, info) in sorted(prepared['materials'].items()):
            target = root / safe_relative(rel); target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(); count = 0
            with source.open('rb') as incoming, target.open('xb') as outgoing:
                for chunk in iter(lambda: incoming.read(1024 * 1024), b''):
                    outgoing.write(chunk); digest.update(chunk); count += len(chunk)
                outgoing.flush(); os.fsync(outgoing.fileno())
            need(dict(bytes=count, SHA=digest.hexdigest()) == info, 'source changed after preflight: ' + rel)
            rows.append(dict(relative=rel, **info))
        put_once(root / 'GROUP_PLAN.json', prepared['encoded_plan'])
        validation = metadata_validate(root)
        put_json(root / 'STAGED_STATIC_FILES_BOUND_ONLY_NATIVE_V1.json', dict(files=rows, source_index=prepared['source_index'],
            actual_source_index_aliases=sorted(ALIASES), native_boundary=prepared['boundary']))
        receipt = dict(kind='SOURCE_BOUND_ONLY_NATIVE_STAGE_COMPLETE_NOT_DISPATCH_V1', staged=True, actual_native_enabled=False,
            group_id=prepared['plan']['group_id'], root=str(root), requested_roles=list(REQUESTED),
            source_files=len(rows), metadata_validation=validation, native_boundary=prepared['boundary'],
            original_plan_SHA=prepared['original_plan_SHA'], model_stat_hash_open_decode=0,
            C_lock_SDK_GPU_GO_operations=0, parent_launches=0, resource_admission=None,
            actual_frozen_evaluation=None, comparison=None, overall_eight_pass_rate=None)
        put_json(root / 'STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json', receipt)
        return receipt
    except BaseException:
        put_json(root / 'STAGE_ERROR_BOUND_ONLY_NATIVE_V1.json', dict(error=traceback.format_exc(), dispatch=False,
            root_consumed_no_same_root_retry=True, parent_launches=0))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('original-group-root', 'source-dir', 'source-index', 'native-root', 'new-root'):
        parser.add_argument('--' + arg, required=True, type=Path)
    parser.add_argument('--original-group-plan', '--original-plan', '--plan', type=Path)
    parser.add_argument('--group-id', required=True); parser.add_argument('--gpu-uuid', required=True)
    parser.add_argument('--collect-action-statistics', action='store_true', help='Read-only SAME-forward scalar reductions; default off, host synchronization affects walltime only.')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--preflight-only', action='store_true'); modes.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    plan_path = args.original_group_plan
    if plan_path is None: plan_path = lexical(args.original_group_root) / 'GROUP_PLAN.json'
    elif not plan_path.is_absolute(): plan_path = lexical(args.original_group_root) / plan_path
    prepared = prepare(args.original_group_root, plan_path, args.source_dir, args.source_index,
                       args.native_root, args.new_root, args.group_id, args.gpu_uuid, collect_action_statistics=args.collect_action_statistics)
    print(json.dumps(stage(prepared) if args.stage else preflight_summary(prepared), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
