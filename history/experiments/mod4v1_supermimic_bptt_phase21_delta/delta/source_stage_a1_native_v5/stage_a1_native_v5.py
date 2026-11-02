"""A1 eight-role NONPT source stage only. Default is read-only preflight; --stage writes one NEW root.

No connector, SSH, SDK, Torch, authority import, model stat/read/copy or owner launch.
Source-index V5 is an explicit sealed mapping, not an implicit live-source discovery.
"""
from __future__ import annotations
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import time
import traceback
from types import SimpleNamespace

ROLE_ORDER = ('E3', 'W35', 'CURB_INDEPENDENT113', 'CURB_PROTECTED878',
              'SLOPE135', 'SLOPE_INDEPENDENT50', 'E0', 'E2')
GPU_UUIDS = ('GPU-16828f91-2b45-b646-8dc0-9481138e2842', 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
COUNT_FIELDS = ('policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps',
                'pi_unverified_steps', 'pi_skipped_nonfinite', 'pi_skipped_zero',
                'wm_optimizer_steps', 'aux_optimizer_steps', 'critic_optimizer_steps')
RAW35_VIEW = 'raw35_legacy_held_aux_v1'
VARIANT = 'A1_RAW35_FRESH'
ALGORITHM_FAMILY = 'a1_raw35_legacy_v1'
USD_SHA = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT_SHA = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
POSE_SHA = '73145a1caa7819e0938e66e53a1bb0be73e48d0d06c3cf9cd5dc76e9f0862209'
POSE_BYTES = 16757
OWNER_NAME = 'supermimic_original_owner_shared_app_close_candidate_v5.py'
WORKER_NAME = 'worker_supermimic_bptt_app_close_candidate_v5.py'
SOURCE_INDEX_KIND = 'SEALED_A1_NATIVE_V5_SOURCE_INDEX_V1'
OWNER_PROTECTED_AST_SHA = '09003c42fd80f0ec1e15e3f7db7f3b6d604753bf4fff1a91135cbda7c094aad0'
OWNER_NORMALIZED_MAIN_AST_SHA = '6bfa2852cc01d8af824b17400f4a615602fc343e021a179b3710a915b9942087'
V5_CODE_SEAL_SHA = '59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7'
STAGE_KIND = 'A1_NATIVE_V5_NONPT_STAGE_COMPLETE_V1'
ROOT_MANIFEST_NAME = 'STAGED_ROOT_MANIFEST_V5.json'
STATIC_DIRS = ('runtime', 'lib', 'original_field', 'new_assets', 'assets', 'producer')
TOP_JSONS = {'original_run_manifest.json', 'RM70_BINARY_INSTALL_ACTUAL.json', 'MOD4V1_DERIVATION_INDEX.json',
             'MOD4V1_ASSET_DIFF.json', 'E1_CANONICAL_SOURCE_METADATA.json', 'VARIANT_SOURCE_METADATA.json',
             'CPU_FOUR_LEAF_ACTUAL_COMPLETE.json', 'CPU_FULL_NESTED_OWNER_AUDIT.json',
             'NEW_ACTUAL_TYPED_RUNTIME_DERIVATION_V1.json'}
DENIED_SUFFIXES = {'.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.pyc', '.pyo', '.pickle', '.pkl',
                   '.partial', '.jsonl', '.log', '.lock', '.pt2'}
DENIED_NAMES = {'model', 'models', 'production', 'adaptation', 'checkpoints', 'checkpoint', 'kit',
                'kit_isolation', 'kit_storage', 'private', 'private_train', 'cache', 'caches', 'logs',
                '__pycache__', '.git', '.pytest_cache', 'deriveddatacache', 'tensorboard', 'wandb'}
FORBIDDEN_STATE_NAMES = {'GO_PRODUCTION.json', 'TASK.json', 'ROOT_ADMISSION_ACTUAL.json', 'STOP_AFTER_SAVE.json',
                         'ACTUAL_CANONICAL_READ.json', 'ACTUAL_RESOURCE_LEASES.json', 'INSTALL_MANIFEST.json'}
FIXED_PINS = {
    'three_slot_common_v1.py': 'eaf6aa1a06d2a49570eff54af5447395210c6de9f3a9c43d566d1adad4e53044',
    'single_writer72_authority_V85M_source.py': 'ceba8067ceaffa8f2a978a0165b1ef06fc28b980d5f9da29ba03c760d9c1d98c',
    'shared_gpu_admission_v1.py': '0ed3ca0e1f449a4c63deb1d6ba4f9037672438e1def74ffbb654efa3a7c3c42d',
    'worker_sources/native_supermimic_bridge.py': '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29',
    'worker_sources/ctx_reward_full_resume_candidate_v2.py': '8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac',
    'worker_sources/resume_runtime_contracts_v3.py': 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7',
    'worker_sources/resume_runtime_install_hook_v4.py': '85f2fd4e45802eb94eb2311cf69410e5b20b1264255a2b0b562aa3c67f87405e',
    'worker_sources/command_tracking_torch_candidate_v1.py': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
    'worker_sources/original_role_command_binding_candidate_v2.py': '348d0a09911a36ca9007ab5bb15f0b3e82bac3ab554cb8d73c62f8f0b5a763ea',
    'worker_sources/pose_cache_runtime_adapter_v3.py': POSE_SHA,
    OWNER_NAME: '0f1618046d5751879f0ce40ff4b7424c83303ed1f61066521215c1d40eb76619',
    'worker_sources/' + WORKER_NAME: '7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7',
    'worker_sources/resume_runtime_app_close_v5.py': '208c4774f1033627c01253afe45ade9c426fdd9be70e76328125a59a80a20c5a',
    'worker_sources/app_close_semantics_v5.py': 'd64732c9310da2db59b349ad921862c78a33e2be5b60a442d456e8a62d63f3c1',
}
DYNAMIC_REQUIRED = {OWNER_NAME, 'worker_sources/' + WORKER_NAME,
                    'worker_sources/resume_runtime_app_close_v5.py', 'worker_sources/app_close_semantics_v5.py'}
ROOT_MIRRORS = ('resume_runtime_contracts_v3.py', 'resume_runtime_install_hook_v4.py',
                'resume_runtime_app_close_v5.py', 'app_close_semantics_v5.py')
OPTIONAL_INDEX_PATHS = {'supermimic_original_owner_app_close_candidate_v5.py',
                        'worker_sources/ctx_reward_learner.py'}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha_bytes(raw): return hashlib.sha256(raw).hexdigest()
def is_sha(value): return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def denied_name(name):
    lower = name.casefold()
    return (lower in DENIED_NAMES or 'BUDGET' in name.upper() or Path(name).suffix.casefold() in DENIED_SUFFIXES
            or name in FORBIDDEN_STATE_NAMES or lower.startswith(('private_train_', 'kit_isolation_')))


def safe_relative(value):
    require(isinstance(value, str) and value and '\\' not in value and ':' not in value, 'plain relative POSIX source path required')
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(part not in ('', '.', '..') for part in path.parts), 'source path escaped its root')
    require(not any(denied_name(part) for part in path.parts), 'model/state/cache/budget path is not a source input')
    return path.as_posix()


def identity(path, relative=None):
    require(not any(denied_name(part) for part in path.parts), 'denied file must not be stat/read/hashed')
    raw = path.read_bytes()
    if path.suffix == '.py': ast.parse(raw.decode('utf-8-sig'))
    value = dict(bytes=len(raw), SHA=sha_bytes(raw))
    if relative is not None: value['relative'] = safe_relative(relative)
    return value


def write_bytes_once(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())


def json_bytes(value): return json.dumps(value, indent=2, allow_nan=False).encode('utf-8')
def put_once(path, value): write_bytes_once(path, json_bytes(value))


def read_metadata(path):
    require(path.suffix == '.json' and not denied_name(path.name), 'explicit non-budget JSON metadata required')
    return json.loads(path.read_bytes())


def collect_tree(root):
    """Name rejection precedes ANY DirEntry classification; never follow a symlink."""
    require(not root.is_symlink() and root.is_dir(), 'explicit static tree missing or symlinked')
    rows = []
    def visit(directory, prefix):
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda item: item.name):
                if denied_name(entry.name): continue
                require(not entry.is_symlink(), 'static source symlink is not followed: ' + entry.name)
                relative = (prefix / entry.name).as_posix()
                if entry.is_dir(follow_symlinks=False): visit(Path(entry.path), prefix / entry.name)
                elif entry.is_file(follow_symlinks=False): rows.append((safe_relative(relative), Path(entry.path)))
                else: raise ValueError('special file is not static source: ' + entry.name)
    visit(root, PurePosixPath())
    return rows


def source_index_files(source_dir, source_index):
    require(source_index.get('kind') == SOURCE_INDEX_KIND and source_index.get('sealed') is True, 'explicit SEALED V5 source index missing')
    require(source_index.get('v5_code_seal_SHA') == V5_CODE_SEAL_SHA, 'parent V5 code/API seal identity differs')
    require(isinstance(source_index.get('files'), list), 'sealed source file list missing')
    source_dir = source_dir.resolve(strict=True)
    output = {}
    allowed = set(FIXED_PINS) | DYNAMIC_REQUIRED | OPTIONAL_INDEX_PATHS
    for item in source_index['files']:
        rel = safe_relative(item['install_relative']);src_rel = safe_relative(item['source_relative'])
        require(rel in allowed and rel not in output, 'unknown or duplicate installed source path: ' + rel)
        require(is_sha(item.get('SHA')) and type(item.get('bytes')) is int and item['bytes'] > 0, 'explicit source SHA/bytes missing')
        path = source_dir / src_rel
        cursor = source_dir
        for part in PurePosixPath(src_rel).parts:
            cursor = cursor / part
            require(not cursor.is_symlink(), 'source mapping symlink is not followed')
        require(path.resolve(strict=True).is_relative_to(source_dir), 'source mapping escaped sealed source-dir')
        info = identity(path)
        require(info['SHA'] == item['SHA'] and info['bytes'] == item['bytes'], 'sealed source bytes changed: ' + rel)
        if rel in FIXED_PINS: require(info['SHA'] == FIXED_PINS[rel], 'original/frozen source SHA differs: ' + rel)
        output[rel] = (path, info)
    require((set(FIXED_PINS) | DYNAMIC_REQUIRED) <= set(output), 'required V5 worker/owner/close source or original dependency missing')
    require(output['worker_sources/pose_cache_runtime_adapter_v3.py'][1]['bytes'] == POSE_BYTES, 'pose adapter sealed bytes differ')
    for name in ROOT_MIRRORS:
        output[name] = output['worker_sources/' + name]
    core = output['worker_sources/ctx_reward_full_resume_candidate_v2.py']
    if 'worker_sources/ctx_reward_learner.py' in output:
        require(output['worker_sources/ctx_reward_learner.py'][1] == core[1], 'payload core alias differs')
    output['worker_sources/ctx_reward_learner.py'] = core
    verify_owner_AST(output[OWNER_NAME][0])
    return output


def verify_owner_AST(path):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    protected = ast.Module(body=[node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.Assign)) and getattr(node, 'name', None) != 'main'], type_ignores=[])
    require(sha_bytes(ast.dump(protected, include_attributes=False).encode()) == OWNER_PROTECTED_AST_SHA, 'original C/account/admit/helpers/constants AST changed')
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
    text = ast.dump(main, include_attributes=False).replace('worker_supermimic_bptt_pre_reset_candidate_v4.py', '__PINNED_FUTURE_WORKER__').replace(WORKER_NAME, '__PINNED_FUTURE_WORKER__')
    require(sha_bytes(text.encode()) == OWNER_NORMALIZED_MAIN_AST_SHA, 'original authority locks/resource/finite owner main AST changed')


def import_pure_gates(path):
    """Only SHA-pinned stdlib V3/V4 gates, never import authority helpers or owner."""
    spec = importlib.util.spec_from_file_location('_a1_stage_original_v3_contracts', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_plan(template, new_root, run_id, contracts, target=3000):
    require(re.fullmatch(r'MOD4V1_A1_RAW35_V5_[A-Za-z0-9_]+', run_id) is not None, 'new explicit A1 run-id required')
    require(template.get('H1_excluded') is True and len(template.get('entries', [])) == 8, 'original eight-role metadata required')
    originals = {entry['role']: entry for entry in template['entries']}
    require(set(originals) == set(ROLE_ORDER), 'exact non-H1 roles required')
    require(type(target) is int and target >= 3000, 'target must retain at least 3000 true BPTT')
    new_root = new_root.resolve(strict=False)
    require(new_root.name == run_id and run_id != template['run_id'], 'new root must carry the new run-id, not the consumed old run')
    old_roots = [Path(entry['job_root']).parent.parent for entry in originals.values()]
    require(all(not new_root.is_relative_to(old) and not old.is_relative_to(new_root) for old in old_roots), 'new root overlaps historical consumed run')
    plan = copy.deepcopy(template)
    plan.update(kind='NEW_A1_RAW35_FRESH_EIGHT_NATIVE_V5_PLAN_NOT_EXECUTION', run_id=run_id,
                H1_excluded=True, algorithm_variant=VARIANT, actor_view=RAW35_VIEW,
                algorithm_family=ALGORITHM_FAMILY, native_counter_start=0,
                old_A0_counts_spliced=False, command_tracking_fixed=False, sensor_projection_exact=False,
                bound_anchor_reward_changes=0, horizon=16, hist=10,
                original_authority_limits_unchanged=dict(parent_seconds=3900, save_seconds=3600, exit_headroom_seconds=300, resource_wait_seconds=1800))
    plan['entries'] = []
    descriptor = dict(kind='POSE_CACHE_RUNTIME_ADAPTER_V3', module='pose_cache_runtime_adapter_v3',
        symbol='install_pose_cache_runtime_adapter_v3', source_relative='worker_sources/pose_cache_runtime_adapter_v3.py',
        SHA=POSE_SHA, bytes=POSE_BYTES, install_timing='after_build_env_before_only_original_reset')
    for role in ROLE_ORDER:
        original = originals[role];entry = copy.deepcopy(original)
        require(entry['family'] in ('formal', 'w35', 'e1'), 'preserve the ORIGINAL plant constructor family')
        require(entry['num_envs'] == 1024 and isinstance(entry['seed'], int), 'original 1024/seed metadata required')
        require(entry['target_bptt_steps'] >= 3000 and isinstance(entry['base_root'], str), 'original base metadata differs')
        require(is_sha(entry['teacher']['SHA']) and type(entry['teacher']['bytes']) is int and entry['teacher']['bytes'] > 10000000, 'teacher METADATA incomplete; never stat this path')
        require(isinstance(entry['teacher']['path'], str) and entry['teacher']['path'], 'teacher metadata path missing')
        for forbidden in ('resume_bptt', 'bridge_adapter'):
            require(entry.get(forbidden) is None, 'fresh A1 must not receive old model/optimizer/history/counter resume')
            entry.pop(forbidden, None)
        entry.update(job_root=str(new_root / 'roles' / role), algorithm_variant=VARIANT, actor_view=RAW35_VIEW,
                     target_bptt_steps=max(target, original['target_bptt_steps']), pose_cache_runtime_adapter=copy.deepcopy(descriptor))
        bound = contracts.bind_future_task_extensions({}, entry)
        require(bound['algorithm_variant'] == VARIANT and bound['actor_view'] == RAW35_VIEW and bound['algorithm_family'] == ALGORITHM_FAMILY, 'actual V3 variant gate differs')
        entry.update(bound)
        entry['expected_fresh_producer_counts'] = {name: 0 for name in COUNT_FIELDS}
        require(entry['seed'] == original['seed'] and entry['teacher'] == original['teacher'] and entry['base_root'] == original['base_root'] and entry['family'] == original['family'], 'original role identity/seed/teacher/plant metadata changed')
        plan['entries'].append(entry)
    return plan


def tree_materials(path):
    rows = collect_tree(path)
    return {relative: (source, identity(source)) for relative, source in rows}


def material_digest(materials):
    rows = [dict(relative=rel, **info) for rel, (_, info) in sorted(materials.items())]
    return dict(files=len(rows), SHA=sha_bytes(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()))


def clone_role_materials(base_root):
    require(not base_root.is_symlink() and base_root.is_dir(), 'explicit original static role root missing')
    output = {}
    for name in STATIC_DIRS:
        path = base_root / name
        require(not path.is_symlink(), 'static top-level tree symlink is not followed')
        if path.is_dir():
            for relative, source in collect_tree(path): output[name + '/' + relative] = (source, identity(source))
    with os.scandir(base_root) as entries:
        for entry in sorted(entries, key=lambda item: item.name):
            if denied_name(entry.name): continue
            if not (Path(entry.name).suffix == '.py' or entry.name in TOP_JSONS): continue
            require(not entry.is_symlink(), 'top-level static source symlink is not followed')
            if entry.is_file(follow_symlinks=False):
                source = Path(entry.path);output[entry.name] = (source, identity(source))
    return output


def prepare(template_path, source_dir, source_index_path, vendor_dir, deps_dir, assets_dir, new_root, run_id, target):
    """Read-only: validate every source/static input BEFORE creating new root."""
    require(not new_root.is_symlink() and not new_root.exists(), 'stage root already exists; no replay or overwrite')
    index = read_metadata(source_index_path)
    sources = source_index_files(source_dir, index)
    template = read_metadata(template_path)
    contracts = import_pure_gates(sources['worker_sources/resume_runtime_contracts_v3.py'][0])
    plan = make_plan(template, new_root, run_id, contracts, target)
    vendor, deps, assets = tree_materials(vendor_dir), tree_materials(deps_dir), tree_materials(assets_dir)
    require({'__init__.py', 'learner.py', 'networks.py', 'geometry.py', 'replay.py'} <= set(vendor), 'original vendor source package incomplete')
    require(deps and assets.get('robot.usd', (None, {}))[1].get('SHA') == USD_SHA and assets.get('import_contract.json', (None, {}))[1].get('SHA') == CONTRACT_SHA, 'static assets/deps missing or original 2c/bae pin differs')
    observed = {name: material_digest(value) for name, value in [('vendor', vendor), ('sm_deps', deps), ('assets', assets)]}
    for name, pin in index.get('tree_pins', {}).items():
        require(name in observed and pin == observed[name], 'parent static tree pin differs: ' + name)
    jobs = {}
    for entry in plan['entries']:
        items = clone_role_materials(Path(entry['base_root']))
        for rel, value in sources.items():
            if rel.startswith('worker_sources/'): items[rel] = value
        for rel, value in vendor.items(): items['worker_sources/supermimic_vendor_v2/' + rel] = value
        for rel, value in deps.items(): items['worker_sources/sm_deps/' + rel] = value
        for target_dir in ('runtime/assets', 'new_assets'):
            for rel, value in assets.items(): items[target_dir + '/' + rel] = value
        jobs[entry['role']] = items
    return dict(plan=plan, sources=sources, jobs=jobs, source_index=index, observed_static_trees=observed,
                template_SHA=identity(template_path)['SHA'], source_index_SHA=identity(source_index_path)['SHA'])


def copy_materials(destination, materials):
    rows = []
    for relative, (source, info) in sorted(materials.items()):
        rel = safe_relative(relative);target = destination / rel
        require(target.resolve().is_relative_to(destination.resolve()), 'copy destination escaped NEW root')
        raw = source.read_bytes()
        require(len(raw) == info['bytes'] and sha_bytes(raw) == info['SHA'], 'source changed after preflight: ' + relative)
        write_bytes_once(target, raw)
        rows.append(dict(relative=rel, **info))
    return rows


def source_only_owner_verify(root, owner_path, plan):
    """Run ONLY original require/verify_sources AST; no owner/helper import and NO real C access."""
    tree = ast.parse(owner_path.read_text(encoding='utf-8'))
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ('require', 'verify_sources')]
    require({node.name for node in selected} == {'require', 'verify_sources'}, 'pinned V5 owner source preflight API missing')
    class CanonicalIdentitySentinel:
        def resolve(self): return self
    sentinel = CanonicalIdentitySentinel()
    def owned_read(path):
        path = Path(path)
        require(path.name == 'INSTALL_MANIFEST.json' and path.resolve().is_relative_to((root / 'roles').resolve()), 'source-only verify attempted non-manifest read')
        return json.loads(path.read_bytes())
    def owned_hash(path):
        path = Path(path)
        require(path.resolve().is_relative_to((root / 'roles').resolve()) and not denied_name(path.name), 'source-only verify attempted non-source hash')
        return identity(path)['SHA']
    namespace = dict(Path=Path, B=root, C=sentinel, ROLES=set(ROLE_ORDER), b=SimpleNamespace(C=sentinel, read=owned_read, H=owned_hash))
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(owner_path) + ':ONLY_SOURCE_VERIFY_AST', 'exec'), namespace)
    namespace['verify_sources'](plan)
    return dict(original_verify_sources_function_AST_executed=True, owner_or_authority_imports=0,
                real_C_stat_read_write=0, canonical_binding_not_checked=True, SDK_PT_GO_GPU_operations=0)


def stage(prepared, root):
    root = root.resolve(strict=False)
    require(not root.exists() and root.name == prepared['plan']['run_id'], 'NEW stage root must be unused')
    root.mkdir(parents=False, exist_ok=False)
    try:
        put_once(root / 'STAGE_BEGIN_V5.json', dict(kind='NEW_NONPT_STAGE_BEGIN_V5', run_id=prepared['plan']['run_id'], epoch=time.time(), owner_launches=0))
        plan = prepared['plan']
        # SCHEDULE_PUBLIC is ORIGINAL helper configuration, never a budget/ledger.
        schedule = {'experts': {entry['role_key']: dict(max_parent_seconds=3900, GPU_UUID=GPU_UUIDS[i % 2]) for i, entry in enumerate(plan['entries'])}}
        put_once(root / 'SCHEDULE_PUBLIC.json', schedule)
        put_once(root / 'OWNER_PLAN.json', plan);put_once(root / 'SOURCE_PLAN.json', plan)
        put_once(root / 'STAGED_SOURCE_INDEX_V5.json', prepared['source_index'])
        root_materials = {rel: value for rel, value in prepared['sources'].items() if not rel.startswith('worker_sources/')}
        root_rows = copy_materials(root, root_materials)
        role_rows = []
        for entry in plan['entries']:
            job = root / 'roles' / entry['role'];job.mkdir(parents=True, exist_ok=False)
            files = copy_materials(job, prepared['jobs'][entry['role']])
            manifest = dict(kind='ACTUAL_A1_NATIVE_V5_NONPT_SOFTWARE_INSTALL_NOT_SDK_ADMISSION', source_PT_copied=False,
                selected_PT_stat_read_or_copy=False, asset_USD_SHA=USD_SHA, asset_contract_SHA=CONTRACT_SHA,
                teacher_metadata=entry['teacher'], actor_view=RAW35_VIEW, algorithm_variant=VARIANT, algorithm_family=ALGORITHM_FAMILY,
                expected_fresh_producer_counts=entry['expected_fresh_producer_counts'], files=files)
            put_once(job / 'INSTALL_MANIFEST.json', manifest)
            role_rows.append(dict(role=entry['role'], files=len(files), manifest_SHA=sha_bytes((job / 'INSTALL_MANIFEST.json').read_bytes())))
        preflight = source_only_owner_verify(root, root / OWNER_NAME, plan)
        for name in ('SCHEDULE_PUBLIC.json', 'OWNER_PLAN.json', 'SOURCE_PLAN.json', 'STAGED_SOURCE_INDEX_V5.json'):
            root_rows.append(dict(relative=name, **identity(root / name)))
        put_once(root / ROOT_MANIFEST_NAME, dict(kind='A1_V5_ROOT_SOFTWARE_AND_CONFIG_MANIFEST', files=root_rows, roles=role_rows))
        complete = dict(kind=STAGE_KIND, staged=True, run_id=plan['run_id'], root=str(root), order=list(ROLE_ORDER), rows=role_rows,
            source_index_SHA=prepared['source_index_SHA'], template_source_plan_SHA=prepared['template_SHA'],
            root_manifest_SHA=identity(root / ROOT_MANIFEST_NAME)['SHA'], schedule_SHA=identity(root / 'SCHEDULE_PUBLIC.json')['SHA'],
            owner_plan_SHA=identity(root / 'OWNER_PLAN.json')['SHA'], owner_relative=OWNER_NAME,
            observed_static_trees=prepared['observed_static_trees'], source_only_owner_preflight=preflight,
            original_authority_helpers_byte_identical=True, original_C_locks_reserve_finite_limits_not_touched=True,
            selected_PT_stat_read_copy=0, SDK_GPU_GO_authority_imports=0, owner_launches=0,
            A1_fresh_native_counter_start=0, old_A0_4912_not_spliced=True, native_execution_or_skill_proof=False)
        put_once(root / 'STAGE_COMPLETE_V5.json', complete)
        return complete
    except BaseException:
        put_once(root / 'STAGE_ERROR_V5.json', dict(kind='PRESERVED_NONPT_STAGE_ERROR_V5_NO_DISPATCH', error=traceback.format_exc(), epoch=time.time(), no_automatic_replay=True))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template-plan', 'source-dir', 'source-index', 'vendor-dir', 'sm-deps-dir', 'assets-dir', 'new-root'):
        aliases = {'template-plan': ['--template-plan', '--source-plan'], 'sm-deps-dir': ['--sm-deps-dir', '--deps-dir']}.get(name, ['--' + name])
        parser.add_argument(*aliases, dest=name.replace('-', '_'), type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--target-bptt-steps', type=int, default=3000)
    parser.add_argument('--stage', action='store_true', help='write the fully validated NEW root; never launch owner')
    args = parser.parse_args()
    prepared = prepare(args.template_plan, args.source_dir, args.source_index, args.vendor_dir, args.sm_deps_dir,
                       args.assets_dir, args.new_root, args.run_id, args.target_bptt_steps)
    if args.stage:
        value = stage(prepared, args.new_root)
    else:
        value = dict(kind='READ_ONLY_A1_V5_SOURCE_PREFLIGHT', passed=True, root=str(args.new_root), run_id=args.run_id,
                     order=list(ROLE_ORDER), source_files=len(prepared['sources']), role_files={k: len(v) for k, v in prepared['jobs'].items()},
                     observed_static_trees=prepared['observed_static_trees'], stage_writes=0, owner_launches=0, PT_SDK_GPU_GO_C_locks=0)
    print(json.dumps(value, indent=2))


if __name__ == '__main__': main()
