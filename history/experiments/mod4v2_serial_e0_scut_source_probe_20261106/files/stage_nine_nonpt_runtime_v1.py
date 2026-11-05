"""Stage a NEW nine-role MOD4v2 software group, never an owner or native GO.

Remote-only source; standard library only.  Copy complete non-PT runtime trees,
including static NPZ/NPY, without importing or AST-pruning their dependencies.
The caller uploads SOURCE_PLAN.json, v2_package/, helpers/, the shared worker,
and optional per-role .py/.json overlays before invoking this script ONCE.
Selected checkpoint paths remain inert JSON strings: no Path/stat/hash/read.
No SDK, GPU, subprocess, SSH, C/ledger, lock, TASK/GO or training operation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil

TASKS_ROOT = Path('/home/lc01/Zonglin Li/zonglin2/tasks')
CURRENT_NINE = TASKS_ROOT / 'MOD4V1_CURRENT_NINE_FROZEN_ASSESSMENT_20261104_090739_1793754459497533800'
ROLES = ('E0', 'E2', 'E3', 'H1_normal', 'W35', 'CURB_PROTECTED878',
         'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50')
COPY_DIRS = ('runtime', 'lib', 'original_field', 'new_assets', 'assets', 'job0')
DEFAULT_ENTRIES = {
    'E0': 'runtime/isaac/mod4/train_mod4v1_e0.py',
    'E2': 'runtime/isaac/mod4/train_mod4v1_e2.py',
    'E3': 'runtime/isaac/mod4/train_mod4v1_e3.py',
    'H1_normal': 'job0/runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py',
    'W35': 'runtime/isaac/mod4/train_mod4v1_w35.py',
    'CURB_PROTECTED878': 'runtime/isaac/mod4/train_host72_backend_admission_v1.py',
    'CURB_INDEPENDENT113': 'runtime/isaac/mod4/train_independent_owned_axis_v1.py',
    'SLOPE135': 'runtime/isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py',
    'SLOPE_INDEPENDENT50': 'runtime/isaac/mod4/train_independent_owned_axis_v1.py',
}
DEFAULT_FAMILIES = {'E0': 'e0_e2_e3', 'E2': 'e0_e2_e3', 'E3': 'e0_e2_e3',
                    'H1_normal': 'h1', 'W35': 'w35'}
# Check every suffix/name BEFORE is_file/is_dir, copy2, read_bytes or stat.
NO_SUFFIXES = {'.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.pyc', '.pyo',
               '.partial', '.jsonl', '.log', '.raw', '.lock'}
NO_DIR_NAMES = {'__pycache__', '.git', '.pytest_cache', '.mypy_cache',
                'weights', 'models', 'checkpoints', 'production', 'raw',
                'rawlogs', 'raw_logs', 'logs', 'log', 'telemetry', 'tensorboard',
                'wandb', 'kit_isolation', 'warp_cache', 'xdg_cache'}
NO_OUTPUT_NAMES = {'TASK.json', 'GO_PRODUCTION.json', 'ROOT_ADMISSION_ACTUAL.json',
                   'WORKER_SCENE_READY.json', 'OWNER_STARTED.json',
                   'STAGE_COMPLETE.json', 'OWNER_PLAN.json',
                   'SOURCE_MANIFEST_V2.json'}
IMMUTABLE_JSON = {
    'original_run_manifest.json', 'RM70_BINARY_INSTALL_ACTUAL.json',
    'MOD4V1_DERIVATION_INDEX.json', 'MOD4V1_ASSET_DIFF.json',
    'E1_CANONICAL_SOURCE_METADATA.json', 'VARIANT_SOURCE_METADATA.json',
    'CPU_FOUR_LEAF_ACTUAL_COMPLETE.json', 'CPU_FULL_NESTED_OWNER_AUDIT.json',
    'NEW_ACTUAL_TYPED_RUNTIME_DERIVATION_V1.json',
}
NATIVE_PENDING = 'PENDING_ACTUAL_FRESH_V2_WORKER_INITIALIZATION'
OWNER_KIND = 'MOD4V2_NINE_ORIGINAL_OWNER_SOURCE_PLAN_V1'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def excluded_name(name):
    """Pure name test: it performs no filesystem access, including on PT."""
    return (bool({s.lower() for s in PurePosixPath(name).suffixes} & NO_SUFFIXES) or
            name.lower() in NO_DIR_NAMES or name in NO_OUTPUT_NAMES or
            name.startswith('events.out.tfevents') or
            name.upper().startswith('TRAINING_BUDGET'))


def relative_path(value):
    need(isinstance(value, str) and value and '\\' not in value,
         'Expected a nonempty POSIX relative path')
    rel = PurePosixPath(value)
    need(not rel.is_absolute() and all(p not in ('', '.', '..') for p in rel.parts),
         'Path must remain within its declared root: ' + value)
    need(all(not excluded_name(p) for p in rel.parts),
         'Excluded source/output name in relative path: ' + value)
    return Path(*rel.parts)


def checked_regular(path):
    """Name first, then metadata; never follow a source symlink into a PT."""
    path = Path(path)
    need(not excluded_name(path.name), 'Excluded file name: ' + str(path))
    need(not path.is_symlink(), 'Materialized non-symlink input required: ' + str(path))
    need(path.is_file(), 'Required non-PT file missing: ' + str(path))
    return path


def file_record(path, root):
    path = checked_regular(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    return dict(relative=path.relative_to(root).as_posix(), bytes=len(raw),
                SHA=digest, SHA256=digest)


def put_new(path, value):
    """Only new manifests/owner plan; never replace a pre-existing output."""
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def copy_regular(source, destination):
    checked_regular(source)
    return shutil.copy2(source, destination)


def ignore_tree(path, names):
    ignored = []
    for name in names:
        if excluded_name(name):
            ignored.append(name)
            continue
        # This is reached only after the pure suffix exclusion above.
        need(not (Path(path) / name).is_symlink(),
             'Materialized source tree required: ' + str(Path(path) / name))
    return ignored


def tree_records(root, relative_to):
    """Record every retained static file; never inventory excluded children."""
    need(not excluded_name(root.name), 'Excluded inventory root')
    need(not root.is_symlink() and root.is_dir(), 'Required materialized directory: ' + str(root))
    rows = []
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if excluded_name(child.name):
            continue
        need(not child.is_symlink(), 'Source symlink not inventoried: ' + str(child))
        if child.is_dir():
            rows.extend(tree_records(child, relative_to))
        else:
            rows.append(file_record(child, relative_to))
    return rows


def original_root_json(name, extra_names):
    if excluded_name(name):
        return False
    return (name in IMMUTABLE_JSON or name in extra_names or
            (name.endswith('.json') and 'manifest' in name.lower()))


def overlay_upload(upload, destination):
    if not upload.exists():
        return []
    need(not upload.is_symlink() and upload.is_dir(), 'Invalid upload directory')
    copied = []
    def walk(directory):
        for source in sorted(directory.iterdir(), key=lambda p: p.name):
            # Excluded upload names fail without even stat-ing that name.
            need(not excluded_name(source.name), 'Excluded upload name: ' + source.name)
            need(not source.is_symlink(), 'Upload must be materialized')
            if source.is_dir():
                walk(source)
                continue
            need(source.suffix.lower() in ('.py', '.json'), 'Upload only .py/.json: ' + source.name)
            rel = source.relative_to(upload)
            need(source.name not in IMMUTABLE_JSON and
                 'derivation' not in source.name.lower() and
                 source.name.lower() != 'original_run_manifest.json',
                 'Original immutable provenance may not be overlaid: ' + rel.as_posix())
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            copy_regular(source, target)
            copied.append(rel.as_posix())
    walk(upload)
    return copied


def source_metadata(entry):
    required = ('source_path', 'source_SHA', 'source_bytes', 'source_iteration', 'source_LR')
    for key in required:
        need(key in entry, 'Missing source metadata field: ' + key)
    need(isinstance(entry['source_path'], str) and entry['source_path'].endswith('.pt'),
         'Selected model path must remain an inert .pt metadata string')
    need(isinstance(entry['source_SHA'], str) and len(entry['source_SHA']) == 64 and
         all(c in '0123456789abcdef' for c in entry['source_SHA']), 'Invalid saved source SHA')
    need(type(entry['source_bytes']) is int and entry['source_bytes'] > 0,
         'Invalid saved source byte count')
    need('source_Adam_step' in entry or 'source_Adam17' in entry,
         'Missing saved Adam17 metadata')
    # No Path construction, stat or hash of source_path occurs here.
    result = {key: copy.deepcopy(value) for key, value in entry.items()
              if key.startswith('source_')}
    return result


def prepare_entries(plan, base):
    need(isinstance(plan, dict) and isinstance(plan.get('entries'), list), 'SOURCE_PLAN entries required')
    entries = plan['entries']
    need(len(entries) == 9 and {e['role'] for e in entries} == set(ROLES),
         'Exactly all nine roles including H1_normal required')
    need(plan.get('H1_excluded', False) is False, 'H1 belongs to this new source stage')
    need(not (base / 'roles').is_symlink(), 'B/roles must remain inside the new group')
    prepared = []
    for raw in entries:
        entry = copy.deepcopy(raw)
        role = entry['role']
        metadata = source_metadata(entry)
        origin = Path(entry['runtime_origin'])
        expected = CURRENT_NINE / 'runtimes' / role
        need(origin == expected, 'runtime_origin must be currentNine runtime_root: ' + role)
        need(not origin.is_symlink() and origin.is_dir(), 'Missing original runtime directory: ' + str(origin))
        destination = base / 'roles' / role
        need(not destination.exists(), 'New role directory must be unused: ' + str(destination))
        if 'job_root' in entry:
            need(Path(entry['job_root']) == destination, 'job_root must equal B/roles/role')
        relative_entry = relative_path(entry.get('entry', DEFAULT_ENTRIES[role]))
        need(relative_entry.suffix == '.py', 'Original entry must be a relative .py path')
        if role == 'H1_normal':
            need(relative_entry.parts[0] == 'job0', 'H1 must retain the original job0 structure')
        entry.update(job_root=str(destination), runtime_root=str(destination),
                     original_runtime_root=str(destination), entry=relative_entry.as_posix(),
                     original_entry=relative_entry.as_posix(), manifest_file='SOURCE_MANIFEST_V2.json')
        entry.setdefault('source_family', DEFAULT_FAMILIES.get(role, 'e1'))
        entry.setdefault('role_key', role)
        entry.setdefault('source_Adam_step', entry.get('source_Adam17'))
        for key, default in dict(steps_per_env=24, max_additional_updates=20,
                                 num_envs=20000, max_parent_seconds=3900,
                                 save_after_seconds=3600, exit_headroom_seconds=300).items():
            entry.setdefault(key, default)
        entry.setdefault('worker_argv', ['{RUN}/worker_mod4v2_expert_migration_v1.py',
                                         '--task', '{JOB}/TASK.json', '--out', '{JOB}/production'])
        entry.setdefault('final_file', 'production/V2_MIGRATION_FINAL.json')
        entry.setdefault('final_updates_key', 'completed_actual_updates')
        entry.setdefault('stop_relative', 'STOP_AFTER_SAVE.json')
        prepared.append((entry, origin, destination, metadata))
    return prepared


def shared_inventory(base):
    rows = []
    for name in ('v2_package', 'helpers'):
        rows.extend(tree_records(base / name, base))
    for name in ('SOURCE_PLAN.json', 'stage_nine_nonpt_runtime_v1.py',
                 'worker_mod4v2_expert_migration_v1.py', 'V2_LOCAL_VALIDATION.json'):
        rows.append(file_record(base / name, base))
    return sorted(rows, key=lambda row: row['relative'])


def stage(base):
    base = Path(base).resolve(strict=True)
    need(base.is_relative_to(TASKS_ROOT) and base != TASKS_ROOT and
         not base.is_relative_to(CURRENT_NINE), 'New group root outside old runtime required')
    for name in ('OWNER_PLAN.json', 'OWNER_STARTED.json', 'ROOT_ADMISSION_ACTUAL.json', 'GO_PRODUCTION.json'):
        need(not (base / name).exists(), 'Source stage is single-use: ' + name)
    plan = json.loads(checked_regular(base / 'SOURCE_PLAN.json').read_text(encoding='utf-8-sig'))
    prepared = prepare_entries(plan, base)
    shared = shared_inventory(base)
    rows = []
    normalized_entries = []
    for entry, origin, destination, metadata in prepared:
        destination.mkdir(parents=True, exist_ok=False)
        for name in COPY_DIRS:
            source = origin / name
            # These are fixed directory names, never selected checkpoint paths.
            need(not source.is_symlink(), 'Materialized directory required: ' + str(source))
            if source.is_dir():
                shutil.copytree(source, destination / name, ignore=ignore_tree,
                                copy_function=copy_regular, dirs_exist_ok=False)
        required = entry.get('required_immutable_files', [])
        extra_names = set()
        for item in required:
            value = item['relative'] if isinstance(item, dict) else item
            rel = relative_path(value)
            if len(rel.parts) == 1 and rel.suffix == '.json' and 'native' not in rel.name.lower():
                extra_names.add(rel.name)
        for source in sorted(origin.iterdir(), key=lambda p: p.name):
            # Pure suffix/name gate BEFORE is_file: root PTs are never stat-ed.
            if excluded_name(source.name):
                continue
            if source.suffix == '.py' or original_root_json(source.name, extra_names):
                need(not source.is_symlink(), 'Materialized root source required: ' + str(source))
                if source.is_file():
                    copy_regular(source, destination / source.name)
        overlays = overlay_upload(base / 'uploads' / entry['role'], destination)
        checked_regular(destination / relative_path(entry['entry']))
        skipped_native_requirements = []
        for item in required:
            value = item['relative'] if isinstance(item, dict) else item
            rel = relative_path(value)
            if 'native' in rel.name.lower():
                skipped_native_requirements.append(rel.as_posix())
                continue  # A V1 native proof is neither required nor credited for V2.
            record = file_record(destination / rel, destination)
            expected = item.get('SHA', item.get('SHA256')) if isinstance(item, dict) else None
            if expected:
                need(record['SHA'] == expected, 'Original immutable digest differs: ' + rel.as_posix())
        manifest_relative = entry.get('original_run_manifest_relative')
        if manifest_relative is not None:
            rel = relative_path(manifest_relative)
            need(rel.suffix == '.json', 'Original run manifest must be JSON')
            checked_regular(destination / rel)
        else:
            candidates = ('original_run_manifest.json', 'job0/original_run_manifest.json')
            for candidate in candidates:
                if (destination / candidate).is_file():
                    manifest_relative = candidate
                    break
        if manifest_relative is not None:
            entry['original_run_manifest_relative'] = manifest_relative
        files = tree_records(destination, destination)
        manifest = dict(
            schema='mod4v2.nine_nonpt_source_manifest.v2',
            kind='MOD4V2_NONPT_SOURCE_STAGE_NOT_NATIVE_GO', role=entry['role'],
            source_runtime_origin=str(origin), job_root=str(destination),
            original_entry=entry['entry'], source_model_metadata=metadata,
            source_SHA=entry['source_SHA'], source_bytes=entry['source_bytes'],
            source_iteration=entry['source_iteration'], source_PT_copied=False,
            native0PT_status=NATIVE_PENDING, source_stage_not_nativeGO=True,
            original_run_and_derivation_indices_rewritten=False,
            legacy_native_proof_requirements_not_applied=skipped_native_requirements,
            files=files, shared_files=shared, overlay_files=overlays,
            static_NPZ_NPY_preserved_without_decode=True,
            selected_PT_stat_hash_decode=0, SDK_GPU_GO_C_or_lock_operations=0,
            owner_not_launched=True)
        path = destination / 'SOURCE_MANIFEST_V2.json'
        put_new(path, manifest)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()  # Own new JSON only.
        entry['source_manifest_SHA'] = digest
        entry['manifest_SHA'] = digest
        entry['native0PT_status'] = NATIVE_PENDING
        entry['source_stage_not_nativeGO'] = True
        normalized_entries.append(entry)
        rows.append(dict(role=entry['role'], nonPTfiles=len(files),
                         manifest_file='SOURCE_MANIFEST_V2.json', manifest_SHA=digest,
                         runtime_origin=str(origin), job_root=str(destination),
                         native0PT_status=NATIVE_PENDING))
    owner_plan = copy.deepcopy(plan)
    owner_plan.update(kind=OWNER_KIND, H1_excluded=False, entries=normalized_entries,
                      source_stage_not_nativeGO=True, native0PT_status=NATIVE_PENDING,
                      shared_files=shared, source_plan_file='SOURCE_PLAN.json',
                      selected_PT_stat_hash_decode=0, SDK_GPU_GO_C_or_lock_operations=0,
                      owner_not_launched=True, rows=rows)
    put_new(base / 'OWNER_PLAN.json', owner_plan)
    result = dict(root=str(base), roles=rows, source_stage_not_nativeGO=True,
                  native0PT_status=NATIVE_PENDING, selected_PT_stat_hash_decode=0,
                  SDK_GPU_GO_C_or_lock_operations=0, owner_not_launched=True)
    print(json.dumps(result, allow_nan=False))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', help='New remote group B')
    parser.add_argument('--job-root', dest='job_root', help='New remote group B')
    args = parser.parse_args()
    need(bool(args.root) != bool(args.job_root), 'Supply exactly one B or --job-root B')
    stage(args.job_root or args.root)


if __name__ == '__main__':
    main()
