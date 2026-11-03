"""V3 typed two-flag runtime publication after full verified materialization; fixed original27 + independently retained bytes. Good-expert holdout stdlib ONLY: twenty complete pinned mappings and full selected original static trees; NEVER dispatch.

Index Windows paths are provenance only; actual input sources are flat basenames.
No selected/mother checkpoint stat, hash, read, copy, decode, SDK, C or lock access.
Full unchanged metadata modules are imported under model/budget/native guards; make_task and seed negatives are checked. No parent/worker main is called.
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
import tempfile
import sys
import time
import traceback

ROLES = ('E3', 'W35', 'CURB_INDEPENDENT113', 'CURB_PROTECTED878',
         'SLOPE135', 'SLOPE_INDEPENDENT50', 'E0', 'E2')
REQUESTED = ('CURB_PROTECTED878', 'SLOPE135')
ALLOWED_SEEDS = (20260929, 20260930)
SOURCE_NATIVE_ENABLED = SOURCE_STAGED = SOURCE_DISPATCHED = False
COMPLETE_NAME = 'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json'
CONTROLS = dict(E0=1000, E2=1200, E3=160, W35=1600, CURB_PROTECTED878=750,
                CURB_INDEPENDENT113=750, SLOPE135=750, SLOPE_INDEPENDENT50=1000)
INDEX_PIN = (21075, '6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')
ORIGINAL_GROUP_ID = 'MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700'
NATIVE_RUN_ID = 'MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000'
USD = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
VENDOR_PIN = (7, 'ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0')
ALIASES = frozenset(('a1_frozen_eval_runtime_v2.py', 'app_close_semantics_v5.py', 'embedded_teacher_reference_v1.py', 'frozen_a1_raw35_v1.py', 'good_expert_holdout_runtime_v1.py', 'native_supermimic_bridge.py', 'pose_cache_runtime_adapter_v3.py', 'producer_teacher_guard_v1.py', 'resume_runtime_contracts_v3.py', 'single_gpu_good_expert_holdout_parent_v1.py', 'supermimic_vendor_v2/contract.py', 'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/networks.py', 'worker_sources/e1/ROLE_CONTRACTS.json', 'worker_sources/e1/e1_endpoint_predicate.py', 'worker_sources/e1/e1_fresh_runtime_bridge.py', 'worker_sources/e1/e1_parallel_worker_safe.py', 'worker_sources/e1/e1_route80_factories.py', 'worker_sources/e1/worker_curb878_n80.py', 'worker_sources/e1/worker_slope135_n80.py'))
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

SOURCE_DERIVATION_VERSION = 3
ORIGINAL_PLAN_PIN = (14385, '54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')
EXTRA_ORIGINAL_DEPENDENCY = {'relative': 'single_gpu_group_supervisor.py', 'bytes': 9247, 'SHA': '7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27'}
ORIGINAL_DEPENDENCY_SHA = 'a4a530e52b36ff063969248b4f5e9400643a4d0395e8f8271e29f5a896d30ef0'
RETAIN_PREFIX = 'worker_sources/good_holdout_retained_original/'
ORIGINAL_PRESERVATION_NAME = 'RETAINED_ORIGINAL_STATIC_FILES_GOOD_EXPERT_HOLDOUT_V2.json'


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
    need((len(raw), H(raw)) == INDEX_PIN, 'sealed holdout V1 twenty-overlay index pin differs')
    need(index.get('kind') == 'SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_C878_S135_INDEX_V1', 'new source index kind required')
    entries = index.get('overlay_entries')
    need(type(entries) is list and len(entries) == 20, 'exact twenty source overlays required')
    result = {}; basenames = set(); source_dir = Path(source_dir)
    for entry in entries:
        rel = safe_relative(entry['relative'])
        basename = entry['path'].replace('\\', '/').rsplit('/', 1)[-1]
        need(basename not in ('', '.', '..') and basename not in basenames, 'unique flat source basename required')
        basenames.add(basename)
        need(rel in ALIASES and rel not in result, 'unknown/duplicate source alias')
        path = no_links(source_dir, basename); info = identity(path)
        need((info['bytes'], info['SHA']) == (entry['bytes'], entry['SHA256']), 'flat pinned source differs: ' + basename)
        if path.suffix == '.py': ast.parse(path.read_bytes())
        else: need(path.suffix == '.json' and type(metadata(path)[0]) is dict, 'explicit source JSON contract required')
        result[rel] = (path, info)
    need(set(result) == ALIASES, 'all twenty pinned aliases required, including canonical7a092 and AppV6/Base')
    return result, dict(path=str(source_index), bytes=len(raw), SHA=H(raw), provenance_paths_not_dereferenced=True), index


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


def paired_plan(seed):
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'independent holdout seed20260929 or20260930 only')
    protocol = dict(pose_source_SHA=POSE_SHA, pose_source_bytes=18161,
        pose_source_version='POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1',
        install_timing='after_env_construction_before_original_single_explicit_reset', seed=seed, num_envs=80,
        explicit_original_reset_count=1, physics_dt=.0025, control_dt=.02, feedback_hz=100,
        actor_observation='original_noisy_delayed_policy35')
    return dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', reference_planned_protocol=dict(protocol),
        candidate_planned_protocol=dict(protocol), historical_bug_baseline_reused=False, reference_actual_receipt=None)


def preservation_digest(value):
    return H(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def original_dependency_map(old_files, index):
    """Exactly the published 27, not acceptance of an arbitrary extra source."""
    expected = {r['relative']:(r['bytes'],r['SHA256']) for r in index['inherited_original_worker_source_entries']}
    expected.update({r['relative']:(r['bytes'],r['SHA']) for r in index['required_original_pinned_assets']})
    need(len(expected) == 26 and EXTRA_ORIGINAL_DEPENDENCY['relative'] not in expected,
         'fixed prior26 source-index dependency set differs')
    extra = EXTRA_ORIGINAL_DEPENDENCY
    expected[extra['relative']] = (extra['bytes'],extra['SHA'])
    rows = [dict(relative=rel,bytes=n,SHA=sha) for rel,(n,sha) in sorted(expected.items())]
    need(len(expected) == 27 and preservation_digest(rows) == ORIGINAL_DEPENDENCY_SHA,
         'fixed complete original27 dependency provenance differs')
    need(type(old_files) is list and len(old_files) == 27
         and len({r['relative'] for r in old_files}) == 27
         and {r['relative'] for r in old_files} == set(expected),
         'complete original27 worker_files dependency set differs')
    for row in old_files:
        rel = safe_relative(row['relative'])
        need((row['bytes'],row['SHA']) == expected[rel], 'original27 dependency pin differs: ' + rel)
    return expected


def retain_originals(originals, sources, *, original_root, original_plan_SHA, native_root, required):
    """Keep the whole independently read input inventory; relocate only actual byte conflicts."""
    materials = dict(originals); moves = {}; origin = []; baseline = []
    for rel,(path,info) in sorted(originals.items()):
        safe_relative(rel); alias = rel
        if rel in sources and sources[rel][1] != info:
            alias = RETAIN_PREFIX + rel
            need(alias not in originals and alias not in sources and alias not in materials,
                 'retained original alias collides: ' + alias)
            materials[alias] = (path,info); moves[rel] = alias
        origin.append(dict(relative=rel,bytes=info['bytes'],SHA=info['SHA'],input_path=str(path),bytes_read=info['bytes']))
        baseline.append(dict(relative=alias,bytes=info['bytes'],SHA=info['SHA']))
    materials.update(sources); baseline.sort(key=lambda r:r['relative'])
    logical = [{k:r[k] for k in ('relative','bytes','SHA')} for r in origin]
    inventory = dict(kind='GOOD_HOLDOUT_INDEPENDENT_ORIGINAL_STATIC_PRESERVATION_V2',
        baseline=baseline,installed=copy.deepcopy(baseline),baseline_SHA=preservation_digest(baseline),
        installed_status='PLANNED_HASH_IDENTITIES_NOT_ACTUAL_MATERIALIZATION',vendor7_SHA=VENDOR_PIN[1],
        baseline_provenance=dict(kind='INDEPENDENT_COMPLETE_SELECTED_INPUT_TREE_BYTE_INVENTORY_V2',
            original_root=str(original_root),original_plan_SHA=original_plan_SHA,native_root=str(native_root),
            original_logical_rows=origin,original_logical_tree_SHA=preservation_digest(logical),
            source_to_retained=moves,all_original_input_files_read=len(origin),
            operational_raw_model_names_excluded_before_classification=True))
    validate_preservation(inventory,materials,originals=originals,required=required)
    return materials,inventory


def validate_preservation(inventory, materials, *, originals, required, observed=None):
    """Bind independent input paths/hash inventory and actual stream hashes, not two asserted lists."""
    proof = inventory['baseline_provenance']; origin = proof['original_logical_rows']; moves = proof['source_to_retained']
    need(origin and len({r['relative'] for r in origin}) == len(origin), 'unique full original input inventory required')
    logical = [{k:r[k] for k in ('relative','bytes','SHA')} for r in origin]
    actual = [dict(relative=rel,**info) for rel,(_,info) in sorted(originals.items())]
    need(logical == sorted(logical,key=lambda r:r['relative']) and logical == actual
         and preservation_digest(logical) == proof['original_logical_tree_SHA'],
         'provenance is not the complete independently read input tree')
    need(all(r['input_path'] == str(originals[r['relative']][0]) and r['bytes_read'] == r['bytes'] for r in origin),
         'actual original input path/read-byte provenance differs')
    need(proof['all_original_input_files_read'] == len(origin) and set(moves) <= set(originals),
         'original input/relocation domain differs')
    for rel,(n,sha) in required.items():
        need(rel in originals and originals[rel][1] == dict(bytes=n,SHA=sha),
             'required original dependency missing/changed in independent input: ' + rel)
    expected = []
    for row in origin:
        old = safe_relative(row['relative']); alias = moves.get(old,old)
        if old in moves: need(alias == RETAIN_PREFIX + old, 'only exact retained-original namespace permitted')
        need(materials.get(alias,(None,None))[1] == dict(bytes=row['bytes'],SHA=row['SHA']),
             'original byte lost/changed under retained alias: ' + alias)
        expected.append(dict(relative=alias,bytes=row['bytes'],SHA=row['SHA']))
    expected.sort(key=lambda r:r['relative'])
    need(len({r['relative'] for r in expected}) == len(expected) and inventory['baseline'] == expected,
         'retained original baseline is incomplete or duplicates')
    if observed is None:
        installed = expected
    else:
        need(all(r['relative'] in observed for r in expected), 'actual installed stream dropped original bytes')
        installed = [dict(relative=r['relative'],**observed[r['relative']]) for r in expected]
    need(inventory['installed'] == installed == expected and inventory['baseline_SHA'] == preservation_digest(expected),
         'actual installed retained bytes differ from independent original baseline')
    need(all(any(r['relative'].startswith('runtimes/'+role+'/') for r in logical) for role in REQUESTED),
         'both complete selected original runtime inventories required')
    need(any(r['relative'].startswith('pinned_assets/') for r in logical)
         and any(r['relative'].startswith('worker_sources/') for r in logical), 'original asset/worker trees required')
    need(len([r for r in logical if r['relative'].startswith('supermimic_vendor_v2/')]) == 7
         and inventory['vendor7_SHA'] == VENDOR_PIN[1], 'full original vendor7 preservation required')
    return True


def preservation_summary(inventory):
    proof = inventory['baseline_provenance']
    return dict(kind=inventory['kind'],original_static_files=len(inventory['baseline']),
        original_dependency_files=27,baseline_SHA=inventory['baseline_SHA'],
        original_logical_tree_SHA=proof['original_logical_tree_SHA'],
        source_to_retained=proof['source_to_retained'],installed_status=inventory['installed_status'],
        independent_origin_paths_and_read_bytes=True,actual_native_binding='UNKNOWN')


def prepare(original_group_root, source_dir, source_index, native_root, new_root, group_id, gpu_uuid, seed):
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'independent holdout seed20260929 or20260930 only')
    need(Path(new_root).is_absolute(), 'explicit absolute new-root required')
    original_group_root, new_root = lexical(original_group_root), lexical(new_root)
    need(not new_root.is_symlink() and not new_root.exists(), 'each seed requires an absent one-use new-root')
    need(group_id == new_root.name and group_id != ORIGINAL_GROUP_ID and str(seed) in group_id
         and re.fullmatch(r'[A-Za-z0-9_]+', group_id), 'seed-tagged new explicit group-id/root required')
    need(re.fullmatch(r'GPU-[0-9a-f-]+', gpu_uuid) is not None, 'explicit GPU UUID required')
    for old in (original_group_root, lexical(native_root), lexical(source_dir), lexical(source_index).parent):
        need(not new_root.is_relative_to(old) and not old.is_relative_to(new_root), 'new-root overlaps an input')
    producers, boundary = native_boundary(native_root)
    sources, index_receipt, index = source_mappings(source_dir, source_index)
    old, old_raw = metadata(original_group_root / 'GROUP_PLAN.json')
    need((len(old_raw), H(old_raw)) == ORIGINAL_PLAN_PIN, 'fixed published original GROUP_PLAN bytes differ')
    need(old.get('group_id') == original_group_root.name == index['original_group_id'] == ORIGINAL_GROUP_ID
         and old.get('asset_SHA') == USD and old.get('contract_SHA') == CONTRACT, 'exact original V8 group/assets required')
    original_rows = old.get('roles')
    need(type(original_rows) is list and len(original_rows) == 9
         and {r['role'] for r in original_rows} == set(ROLES) | {'H1_normal'}, 'original nine-to-eight catalog differs')
    materials = {}
    for directory in ('worker_sources', 'pinned_assets'):
        for rel, value in tree(original_group_root / directory).items(): materials[directory + '/' + rel] = value
    old_files = old.get('worker_files')
    expected = original_dependency_map(old_files, index)
    for item in old_files:
        rel = safe_relative(item['relative']); need(not any(denied(p) for p in rel.split('/')), 'non-static original worker input')
        need((item['bytes'],item['SHA']) == expected[rel], 'original source-index dependency pin differs: ' + rel)
        src = no_links(original_group_root, rel); info = identity(src)
        need(info == {k:item[k] for k in ('bytes','SHA')}, 'actual original worker-file pin differs: ' + rel)
        materials[rel] = (src, info)
    purpose = 'GOOD_EXPERT_HOLDOUT_C878_S135_SEED' + str(seed) + '_V1'
    plan = dict(kind='GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1', seed=seed, batch_purpose=purpose,
        policy_variant='ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1', enabled=False, staged=False,
        source_native_enabled=False, dispatched=False, group_id=group_id, GPU_UUID=gpu_uuid, asset_SHA=USD, contract_SHA=CONTRACT,
        holdout_protocol=dict(kind='INDEPENDENT_GOOD_EXPERT_HOLDOUT_SEED_PROTOCOL_V1',seed=seed,purpose=purpose,published_baseline_seed=20260928,
            historical_seed_reassessment_counts_as_new_evidence=False,independent_group_per_seed=True,paired_effect_claim=False,
            cohort='original_env_id_mod3_ascending27_descending27_stand26',controls_per_role=750,num_envs=80,original_acceptance_unchanged=True),
        requested_roles=list(REQUESTED), deferred_roles=[r for r in ROLES if r not in REQUESTED],
        comparison=None, relative_improvement=None, paired_actual_reference=None, UID_alignment=None,
        reference_cache_match=None, reward_effect_identification=None, overall_eight_pass_rate=None,
        all_eight_actual_execution_complete=None, actual_resource_admission=None, actual_frozen_evaluation=None,
        paired_reset_protocol=paired_plan(seed), roles=[])
    by_role = {row['role']:row for row in original_rows}
    indexed_roles = {row['role']:row for row in index['required_original_runtime_rows']}
    runtime_receipts = {}
    guard_spec = importlib.util.spec_from_file_location('_holdout_stage_producer_guard', sources['producer_teacher_guard_v1.py'][0])
    guard = importlib.util.module_from_spec(guard_spec); guard_spec.loader.exec_module(guard)
    for role in ROLES:
        row = copy.deepcopy(by_role[role]); need(row.get('controls') == CONTROLS[role], 'original controls differ')
        historical = {k:row.pop(k) for k in list(row) if k.startswith('source_')}
        row.update(historical_mother_source=historical, source_identity='DEFERRED_NOT_A_NEW_CACHE_SOURCE',
                   a1_producer=None, num_envs=80, seed=20260928, status='deferred_not_constructed')
        if role in REQUESTED:
            old_runtime = lexical(row['runtime_root'])
            need(old_runtime == original_group_root / 'runtimes' / role, 'exact selected original runtime tree required')
            reference = indexed_roles[role]
            need(row['runtime_origin'] == reference['runtime_origin'] and row['worker'] == reference['worker'], 'selected original runtime/worker provenance differs')
            files = tree(old_runtime)
            canonical_rel = 'runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json'
            need(canonical_rel in files and metadata(files[canonical_rel][0])[0].get('canonical') == role, 'actual selected E1 canonical metadata differs')
            runtime_receipts[role] = digest_tree(files)
            for rel, value in files.items(): materials['runtimes/' + role + '/' + rel] = value
            asset = lexical(row['asset_dir']); need(asset.is_relative_to(old_runtime), 'original selected asset-dir escaped runtime')
            row.update(runtime_root=str(new_root / 'runtimes' / role),
                asset_dir=str(new_root / 'runtimes' / role / asset.relative_to(old_runtime)), seed=seed, status='requested_source_only',
                a1_producer=producers[role], policy_variant=plan['policy_variant'], actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',
                actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
                original_bootstrap_teacher=guard.teacher_identity(producers[role]['FINAL']['teacher']),
                producer_teacher_freeze_evidence=guard.derive_producer_guard(producers[role]))
            cp = producers[role]['FINAL']['checkpoint']
            row.update(source_path=cp['path'], source_SHA=cp['SHA'], source_bytes=cp['bytes'],
                       source_identity='OWN_A1_FULL_NEW_CHECKPOINT_NOT_MOTHER_OR_OLD_PPO')
        plan['roles'].append(row)
    vendor = tree(Path(native_root) / 'roles' / 'E3' / 'worker_sources' / 'supermimic_vendor_v2')
    observed = digest_tree(vendor)
    need((observed['files'], observed['SHA']) == VENDOR_PIN, 'actual complete original vendor7 tree differs')
    for path,_ in vendor.values(): ast.parse(path.read_bytes())
    need({'__init__.py','learner.py','networks.py','geometry.py','replay.py','contract.py'} <= set(vendor)
         and all('/' not in rel and rel.endswith('.py') for rel in vendor), 'full original flat vendor7 required')
    init = ast.parse(vendor['__init__.py'][0].read_bytes())
    need(len(init.body) == 1 and isinstance(init.body[0],ast.Expr) and isinstance(init.body[0].value,ast.Constant)
         and type(init.body[0].value.value) is str, 'original docstring-only vendor init required; no cropping/stub')
    for rel,value in vendor.items(): materials['supermimic_vendor_v2/' + rel] = value
    originals = dict(materials)
    for rel,value in sources.items():
        if rel.startswith('supermimic_vendor_v2/'): need(materials[rel][1] == value[1], 'vendor/index source mismatch')
    materials, original_preservation = retain_originals(originals, sources, original_root=original_group_root,
        original_plan_SHA=H(old_raw), native_root=native_root, required=expected)
    verify_aliases = ({r['relative'] for r in old_files} | ALIASES | {'supermimic_vendor_v2/' + r for r in vendor}
        | set(original_preservation['baseline_provenance']['source_to_retained'].values()))
    plan['worker_files'] = [dict(relative=rel,**materials[rel][1]) for rel in sorted(verify_aliases)]
    encoded = json.dumps(plan,indent=2,allow_nan=False).encode()
    need(len(encoded) <= 262144, 'plan exceeds sealed metadata bound')
    prepared = dict(plan=plan,materials=materials,originals=originals,original_dependency_files=expected,
        original_preservation=original_preservation,boundary=boundary,source_index=index_receipt,original_plan_SHA=H(old_raw),
        native_vendor=observed,selected_runtime_trees=runtime_receipts,new_root=new_root,encoded_plan=encoded)
    prepared['metadata_validation'] = metadata_validate(prepared)
    return prepared


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


def metadata_validate(prepared, actual_root=None):
    """Full real metadata import closure, never native parent/bridge execution.
    Before stage only text aliases are copied into a disposable import view; all
    actual role/static/vendor materials have already been hashed in full. No new-root
    or native-root is created. After materialization, import the actual target aliases.
    """
    temporary = None
    if actual_root is None:
        temporary = tempfile.TemporaryDirectory(prefix='HOLDOUT_METADATA_IMPORT_ONLY_')
        root = Path(temporary.name)
        for rel,(source,info) in prepared['materials'].items():
            if rel.startswith(('runtimes/','pinned_assets/')) or Path(rel).suffix not in ('.py','.json'): continue
            target = root / safe_relative(rel); target.parent.mkdir(parents=True,exist_ok=True)
            raw = source.read_bytes(); need(dict(bytes=len(raw),SHA=H(raw)) == info,'source changed before metadata import')
            with target.open('xb') as stream: stream.write(raw)
    else: root = Path(actual_root)
    old_path, old_bytecode = list(sys.path), sys.dont_write_bytecode
    old_resolve, old_open, old_io_open, old_stat, old_lstat, old_import = Path.resolve,builtins.open,io.open,os.stat,os.lstat,builtins.__import__
    names = ('good_expert_holdout_runtime_v1','a1_frozen_eval_runtime_v2','producer_teacher_guard_v1',
        'embedded_teacher_reference_v1','frozen_a1_raw35_v1','pose_cache_runtime_adapter_v3',
        'app_close_semantics_v5','resume_runtime_contracts_v3','e1_parallel_worker_safe','e1_fresh_runtime_bridge','e1_route80_factories','e1_endpoint_predicate')
    modules = {name:sys.modules.get(name) for name in names}; avoided=[]
    forbidden = {'torch','numpy','isaacsim','isaaclab','omni','warp','pxr','rsl_rl','tensordict','psutil','fcntl'}
    def guarded(function):
        def call(path,*args,**kwargs):
            need(not model_path(path) and not (not isinstance(path,int) and ('budget' in Path(os.fspath(path)).name.lower()
                 or Path(os.fspath(path)).suffix.lower() == '.lock')), 'metadata attempted model/budget/lock filesystem access')
            return function(path,*args,**kwargs)
        return call
    def resolve(path,*args,**kwargs):
        if model_path(path): avoided.append(str(path)); return lexical(path)
        return old_resolve(path,*args,**kwargs)
    def imported(name,*args,**kwargs):
        need(name.split('.')[0] not in forbidden,'native import is outside metadata closure: ' + name)
        return old_import(name,*args,**kwargs)
    try:
        sys.path[:0] = [str(root),str(root/'worker_sources/e1')]; sys.dont_write_bytecode=True
        for name in names: sys.modules.pop(name,None)
        Path.resolve=resolve; builtins.open=guarded(old_open); io.open=guarded(old_io_open)
        os.stat=guarded(old_stat); os.lstat=guarded(old_lstat); builtins.__import__=imported
        dependency = verify_close_dependency_imports(root/'app_close_semantics_v5.py',root/'resume_runtime_contracts_v3.py')
        runtime = importlib.import_module('good_expert_holdout_runtime_v1')
        for name in ('frozen_a1_raw35_v1','pose_cache_runtime_adapter_v3','e1_parallel_worker_safe','e1_fresh_runtime_bridge','e1_route80_factories','e1_endpoint_predicate'):
            module = importlib.import_module(name)
            expected = root / (('worker_sources/e1/' if name.startswith('e1_') else '') + name + '.py')
            need(Path(module.__file__).resolve() == expected.resolve(),'actual metadata import origin differs: ' + name)
        plan = copy.deepcopy(prepared['plan']); rows = runtime.select_requested_roles(plan)
        need([row['role'] for row in rows] == list(REQUESTED),'metadata exact two roles differs')
        task_checks=[]
        for row in rows:
            task=runtime.make_task(row,plan,9999999999.,[101,102])
            runtime._validate_batch_members(task,row['role'])
            need(task['seed'] == plan['seed'] and task['physics_callbacks'] == 6000 and task['feedback_samples'] == 1500,'metadata task scope differs')
            bad=copy.deepcopy(task); other=ALLOWED_SEEDS[1] if plan['seed']==ALLOWED_SEEDS[0] else ALLOWED_SEEDS[0]
            bad.update(seed=other,batch_purpose=runtime.purpose_for(other),holdout_protocol=runtime.holdout_protocol(other))
            try: runtime._validate_batch_members(bad,row['role'])
            except (ValueError,AssertionError): pass
            else: raise ValueError('cross-seed task/pose was accepted')
            task_checks.append(dict(role=row['role'],seed=task['seed'],make_task_passed=True,cross_seed_pose_rejected=True))
        bad=copy.deepcopy(plan); bad['seed']=20260928
        try: runtime.select_requested_roles(bad)
        except (ValueError,AssertionError): pass
        else: raise ValueError('historical seed incorrectly accepted as holdout')
        need(not any(name.split('.')[0] in forbidden for name in sys.modules),'metadata imported a native module')
        return dict(kind='GOOD_EXPERT_HOLDOUT_REAL_COMPLETE_METADATA_CLOSURE_CHECK_V1',passed=True,
            requested_roles=list(REQUESTED),seed=plan['seed'],purpose=plan['batch_purpose'],dependency_completeness=dependency,
            task_checks=task_checks,historical_seed_rejected=True,full_modules_not_AST_cropped_or_stubbed=True,
            model_path_resolve='LEXICAL_METADATA_ONLY_NO_LSTAT',model_lstats_avoided=len(avoided),
            actual_resource_admission=None,actual_parent_or_worker_main_executed=False,
            metadata_preview_FDs_are_in_memory_placeholders_not_opened=True,
            parent_launches=0,model_stat_open_hash=0,C_lock_SDK_GPU_operations=0)
    finally:
        Path.resolve,builtins.open,io.open,os.stat,os.lstat,builtins.__import__=old_resolve,old_open,old_io_open,old_stat,old_lstat,old_import
        sys.path[:]=old_path; sys.dont_write_bytecode=old_bytecode
        for name,previous in modules.items():
            if previous is None: sys.modules.pop(name,None)
            else: sys.modules[name]=previous
        if temporary is not None:
            need(Path(temporary.name).resolve()==root.resolve() and root.name.startswith('HOLDOUT_METADATA_IMPORT_ONLY_'),'owned metadata temp cleanup target differs')
            temporary.cleanup()


def put_once(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def put_json(path, value):
    put_once(path, (json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def preflight_summary(prepared):
    return dict(kind='SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V3',passed=True,
        source_derivation_version=3,original_preservation=preservation_summary(prepared['original_preservation']),
        source_native_enabled=False,staged=False,dispatched=False,materialized=False,
        new_root=str(prepared['new_root']),group_id=prepared['plan']['group_id'],seed=prepared['plan']['seed'],purpose=prepared['plan']['batch_purpose'],
        requested_roles=list(REQUESTED),deferred_roles=[r for r in ROLES if r not in REQUESTED],
        files=len(prepared['materials']),source_index=prepared['source_index'],native_boundary=prepared['boundary'],
        native_vendor=prepared['native_vendor'],selected_runtime_trees=prepared['selected_runtime_trees'],original_plan_SHA=prepared['original_plan_SHA'],
        metadata_validation=prepared['metadata_validation'],resource_admission=None,actual_frozen_evaluation=None,
        model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,parent_launches=0,new_root_created=False)


def derive_materialized_runtime_plan(source_plan, source_plan_bytes, materials, observed, *, originals, preservation, required):
    """Pure evidence-to-plan derivation; no IO, approval bool, admission or native call.
    Stage owns the observed map populated by its unchanged copy/hash/fsync loop.
    The caller must also run the unchanged complete metadata_validate on this plan
    BEFORE publishing GROUP_PLAN. This helper alone is not a materialization proof.
    """
    need(type(source_plan) is dict and type(source_plan_bytes) is bytes,
         'original SOURCE plan and exact encoded bytes required')
    need(all(source_plan.get(key) is False for key in ('enabled','staged','source_native_enabled','dispatched')),
         'SOURCE plan flags must remain exactly False before materialization publication')
    encoded_source=json.dumps(source_plan,indent=2,allow_nan=False).encode()
    need(encoded_source == source_plan_bytes and len(encoded_source) <= 262144,
         'SOURCE plan bytes changed or exceed original262144 bound')
    seed=source_plan.get('seed')
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'independent holdout seed required before runtime publication')
    purpose='GOOD_EXPERT_HOLDOUT_C878_S135_SEED'+str(seed)+'_V1'
    need(source_plan.get('kind') == 'GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1'
         and source_plan.get('batch_purpose') == purpose, 'runtime publication kind/seed/purpose differs')
    group_id=source_plan.get('group_id')
    need(type(group_id) is str and group_id != ORIGINAL_GROUP_ID and str(seed) in group_id
         and re.fullmatch(r'[A-Za-z0-9_]+',group_id) is not None, 'runtime publication seed-tagged group differs')
    protocol=source_plan.get('holdout_protocol')
    need(type(protocol) is dict and protocol.get('seed') == seed and protocol.get('purpose') == purpose
         and source_plan.get('paired_reset_protocol') == paired_plan(seed), 'runtime publication cross-seed protocol differs')
    need(source_plan.get('requested_roles') == list(REQUESTED)
         and source_plan.get('deferred_roles') == [r for r in ROLES if r not in REQUESTED], 'runtime publication role subset differs')
    roles=source_plan.get('roles')
    need(type(roles) is list and len(roles) == 8 and len({r['role'] for r in roles}) == 8
         and {r['role'] for r in roles} == set(ROLES), 'runtime publication complete8 catalog required')
    need(all(r.get('seed') == seed and r.get('num_envs') == 80 and r.get('controls') == 750
             for r in roles if r['role'] in REQUESTED), 'runtime publication member seed/N80/750 differs')
    need(type(materials) is dict and materials and type(observed) is dict and set(observed) == set(materials),
         'actual stream observations must cover exactly all materialized inputs')
    for rel,(_,info) in materials.items():
        safe_relative(rel)
        need(type(info) is dict and set(info) == {'bytes','SHA'} and type(info['bytes']) is int and info['bytes'] > 0
             and is_sha(info['SHA']) and type(observed[rel]) is dict and type(observed[rel].get('bytes')) is int
             and observed[rel] == info, 'actual materialized stream identity differs: '+rel)
    required_rows=[dict(relative=rel,bytes=n,SHA=sha) for rel,(n,sha) in sorted(required.items())]
    need(len(required_rows) == 27 and preservation_digest(required_rows) == ORIGINAL_DEPENDENCY_SHA,
         'runtime publication requires the fixed complete original27 dependencies')
    need(preservation.get('installed_status') == 'ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES',
         'runtime publication needs actual stream-preservation evidence, not planned identities')
    validate_preservation(preservation,materials,originals=originals,required=required,observed=observed)
    rows=source_plan.get('worker_files')
    need(type(rows) is list and len(rows) == len({r['relative'] for r in rows}) and ALIASES <= {r['relative'] for r in rows},
         'runtime publication complete unique worker aliases required')
    for row in rows:
        rel=safe_relative(row['relative'])
        need(set(row) == {'relative','bytes','SHA'} and rel in materials
             and {k:row[k] for k in ('bytes','SHA')} == materials[rel][1], 'runtime publication worker-file binding differs: '+rel)
    runtime_plan=copy.deepcopy(source_plan)
    runtime_plan.update(enabled=True,staged=True)
    need(dict(runtime_plan,enabled=False,staged=False) == source_plan,
         'runtime publication changed more than the two existing entry flags')
    runtime_bytes=json.dumps(runtime_plan,indent=2,allow_nan=False).encode()
    need(len(runtime_bytes) <= 262144, 'runtime plan exceeds original262144 metadata bound')
    return runtime_plan,runtime_bytes


def stage(prepared):
    root=prepared['new_root']; need(not root.is_symlink() and not root.exists(),'actual materialization root already exists')
    root.mkdir(parents=False,exist_ok=False)
    put_json(root/'STAGE_BEGIN_GOOD_EXPERT_HOLDOUT_V1.json',preflight_summary(prepared))
    try:
        rows=[]
        for rel,(source,info) in sorted(prepared['materials'].items()):
            target=root/safe_relative(rel); target.parent.mkdir(parents=True,exist_ok=True)
            digest=hashlib.sha256(); count=0
            with source.open('rb') as incoming,target.open('xb') as outgoing:
                for chunk in iter(lambda:incoming.read(1024*1024),b''):
                    outgoing.write(chunk);digest.update(chunk);count+=len(chunk)
                outgoing.flush();os.fsync(outgoing.fileno())
            observed=dict(bytes=count,SHA=digest.hexdigest())
            need(observed==info,'source changed after preflight: '+rel)
            rows.append(dict(relative=rel,**observed))
        written={r['relative']:{k:r[k] for k in ('bytes','SHA')} for r in rows}
        preservation=copy.deepcopy(prepared['original_preservation'])
        preservation['installed']=[dict(relative=r['relative'],**written[r['relative']]) for r in preservation['baseline']]
        preservation['installed_status']='ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES'
        validate_preservation(preservation,prepared['materials'],originals=prepared['originals'],
            required=prepared['original_dependency_files'],observed=written)
        preservation_raw=(json.dumps(preservation,indent=2,allow_nan=False)+'\n').encode()
        need(len(preservation_raw)<=8*1024*1024,'independent static preservation metadata exceeds8MiB')
        put_once(root/ORIGINAL_PRESERVATION_NAME,preservation_raw)
        runtime_plan,runtime_bytes=derive_materialized_runtime_plan(
            prepared['plan'],prepared['encoded_plan'],prepared['materials'],written,
            originals=prepared['originals'],preservation=preservation,required=prepared['original_dependency_files'])
        runtime_prepared=dict(prepared,plan=runtime_plan,encoded_plan=runtime_bytes)
        need(runtime_plan['group_id'] == root.name,'runtime plan/root identity differs before publication')
        validation=metadata_validate(runtime_prepared,actual_root=root)
        put_once(root/'GROUP_PLAN.json',runtime_bytes)
        put_json(root/'STAGED_STATIC_FILES_GOOD_EXPERT_HOLDOUT_V1.json',dict(files=rows,source_index=prepared['source_index'],native_boundary=prepared['boundary']))
        receipt=dict(kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3',materialized=True,
            source_derivation_version=3,original_preservation=preservation_summary(preservation),
            original_preservation_file=dict(relative=ORIGINAL_PRESERVATION_NAME,bytes=len(preservation_raw),SHA=H(preservation_raw)),
            source_native_enabled=False,staged=False,dispatched=False,group_id=prepared['plan']['group_id'],root=str(root),
            seed=prepared['plan']['seed'],purpose=prepared['plan']['batch_purpose'],requested_roles=list(REQUESTED),
            source_files=len(rows),metadata_validation=validation,native_boundary=prepared['boundary'],selected_runtime_trees=prepared['selected_runtime_trees'],
            original_plan_SHA=prepared['original_plan_SHA'],GROUP_PLAN_bytes=len(runtime_bytes),GROUP_PLAN_SHA256=H(runtime_bytes),
            model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,
            parent_launches=0,resource_admission=None,actual_frozen_evaluation=None,comparison=None,overall_eight_pass_rate=None)
        put_json(root/COMPLETE_NAME,receipt)
        return receipt
    except BaseException:
        put_json(root/'STAGE_ERROR_GOOD_EXPERT_HOLDOUT_V1.json',dict(error=traceback.format_exc(),dispatched=False,
            root_consumed_no_same_root_retry=True,parent_launches=0))
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('original-group-root','source-dir','source-index','native-root','new-root'):
        parser.add_argument('--'+arg,required=True,type=Path)
    parser.add_argument('--group-id',required=True);parser.add_argument('--gpu-uuid',required=True)
    parser.add_argument('--seed',required=True,type=int,choices=ALLOWED_SEEDS)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--preflight-only',action='store_true');modes.add_argument('--stage',action='store_true')
    args=parser.parse_args()
    prepared=prepare(args.original_group_root,args.source_dir,args.source_index,args.native_root,args.new_root,args.group_id,args.gpu_uuid,args.seed)
    print(json.dumps(stage(prepared) if args.stage else preflight_summary(prepared),indent=2,allow_nan=False))


if __name__=='__main__': main()
