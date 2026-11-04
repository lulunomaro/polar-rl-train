"""Narrow typed SOURCE-loader/metadata extensions to the complete frozen V4.

No prepare/stage/resource/SDK entry point is invoked by this module. R/T roots
are explicit source-only mirrors; Windows publication paths are provenance.
"""
from __future__ import annotations
from static_source_helpers_v1 import *

HERE = Path(__file__).resolve().parent
R_NAME = 'mod4v1_supermimic_bptt_20261102'
T_NAME = 'mod4v1_experts_fulldr_rm70_20261101'
SCHEMA = 'PHASE1_TYPED_NATIVE_PRODUCER_ABI_V1'
PLAN_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_ONLY_PLAN_V1'
INDEX_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_INDEX_V1'
MIRROR_PIN = (93889, 'c47b837bce45d3fa3c917db437181ee83814feef0ca0c2b67df4f0c6f49d9d90')
FINITE_PIN = (11663, '5b633338090b8801282e8b2ee824d74d413495efa39f93708cda44bff2222155')
ABI_PIN = (9441, 'e805ecb63aa61c81324c62488981a49973a99381dc14cc4d37b911c4a70f696a')
T_RELATIVE = 'NINE_N80_PARALLEL_SOURCE_V8/n80_gpu_capacity.py'
T_PIN = (653, 'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc')
# Exactly package identity + relative member + raw byte identity; never a general
# extension allowlist and never a patch-application permission.
PATCH_PROOFS = {
 ('source_phase1_passive_sensor_capture_v4', 'SOURCE_DIFF.patch'):
   (8378, 'd59e5c2587e93d057c5b9c3498ddfb6b28fdeeecb15189880210de4bb3565fa3'),
 ('source_phase1_actuation_clock_scope_v2', 'C1_TO_C2_SOURCE_DIFF.patch'):
   (6231, 'fe80994ac0db9e24e89a40138b6a62d6825c1bd0c794c9b8c2183a51676b9793'),
}
PATCH_PACKAGE_SEALS = {
 'source_phase1_passive_sensor_capture_v4': '81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3',
 'source_phase1_actuation_clock_scope_v2': '105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b',
}


def source_reference(source_root, t_source_root, value):
    """Strict explicit R/T mapping; no absolute-path or drive-letter fallback."""
    value = str(value).replace('\\', '/')
    choices = []
    for name, base in ((R_NAME, source_root), (T_NAME, t_source_root)):
        marker = '/' + name + '/'
        if marker in value:
            need(value.count(marker) == 1 and base is not None, 'ambiguous/missing explicit SOURCE root')
            relative = value.split(marker, 1)[1]
            choices.append((name, base, relative))
    need(len(choices) == 1, 'unknown/ambiguous SOURCE provenance root')
    name, base, relative = choices[0]
    relative = safe_relative(relative)
    need(not any(denied(p) for p in relative.split('/')), 'non-SOURCE reference denied before filesystem access')
    if name == T_NAME:
        need(relative == T_RELATIVE, 'T mirror is limited to the single fixed original SOURCE')
    return no_links(lexical(base), relative)


def verify_mirror_entries(manifest, source_root, t_source_root):
    """Check whole declared textual inputs, including unselected upstream refs."""
    need(t_source_root is not None, 'explicit --t-source-root is required')
    roots = {'R': lexical(source_root), 'T': lexical(t_source_root)}
    rows = manifest['files']
    need(type(rows) is list and len(rows) == manifest['file_count'], 'complete SOURCE mirror list differs')
    seen = set()
    counts = dict(R=0, T=0)
    for row in rows:
        key, relative = row['root'], safe_relative(row['relative'])
        need(key in roots and (key, relative) not in seen, 'duplicate/unknown SOURCE mirror root')
        need(not any(denied(p) for p in relative.split('/')), 'non-SOURCE mirror input denied before stat/classify')
        suffix = Path(relative).suffix.lower()
        need(suffix in ('.py', '.json', '.md', '.txt', '.patch'), 'non-text SOURCE mirror file')
        pin = (row['bytes'], row['SHA256'])
        if key == 'T':
            need(relative == T_RELATIVE and pin == T_PIN, 'fixed T SOURCE identity differs')
        if suffix == '.patch':
            parts = relative.split('/')
            need(key == 'R' and len(parts) == 2 and PATCH_PROOFS.get(tuple(parts)) == pin,
                 'unqualified SOURCE proof patch')
        path = no_links(roots[key], relative)
        info = identity(path)
        need((info['bytes'], info['SHA']) == pin, 'actual SOURCE mirror dependency differs: ' + relative)
        if suffix == '.py':
            ast.parse(path.read_bytes())
        seen.add((key, relative)); counts[key] += 1
    need(counts == dict(R=manifest['R_file_count'], T=manifest['T_file_count']), 'SOURCE mirror root counts differ')
    return dict(files=len(seen), R=counts['R'], T=counts['T'], explicit_only=True,
                no_windows_fallback=True, all_actual_source_bytes_verified=True)


def verify_source_mirror(source_root, t_source_root):
    manifest, raw = metadata(HERE / 'SOURCE_MIRROR_INPUTS.json', 2 * 1024 * 1024)
    need((len(raw), H(raw)) == MIRROR_PIN, 'fixed complete SOURCE mirror manifest differs')
    need(manifest['kind'] == 'PHASE1_TYPED_MATERIALIZER_R_T_SOURCE_MIRROR_INPUTS_V1'
         and manifest['original_R_332_unmodified'] is True
         and (manifest['R_file_count'], manifest['T_file_count']) == (395, 1), 'complete original R + fixed T mirror required')
    return verify_mirror_entries(manifest, source_root, t_source_root)


def patch_proof_allowed(folder_name, relative, package_sha, pin):
    return (PATCH_PACKAGE_SEALS.get(folder_name) == package_sha
            and PATCH_PROOFS.get((folder_name, relative)) == pin)


def validate_finite_rows(index, finite, abi):
    """All 34 SOURCE identities; bootstrap 2 remain baseline-authoritative."""
    need(index['kind'] == INDEX_KIND and index['source_version'] == 1
         and index['typed_producer_schema'] == SCHEMA, 'typed SOURCE index wire differs')
    need(finite['kind'] == 'PHASE1_TYPED_NATIVE_FINITE_SOURCE_BUNDLE_V1'
         and finite['source_only'] is True and finite['typed_producer_schema'] == SCHEMA,
         'typed finite SOURCE publication differs')
    need(abi['kind'] == SCHEMA and abi['source_only'] is True and abi['actual_native_run'] is False,
         'typed Producer ABI source declaration differs')
    wire = abi['wire']
    need(wire['GROUP_PLAN.kind'] == PLAN_KIND and wire['GROUP_PLAN.typed_producer_schema'] == SCHEMA
         and wire['TASK.kind'] == 'PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_TASK_V1'
         and wire['TASK.integration'] == 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1'
         and wire['TASK.typed_producer_schema'] == SCHEMA
         and wire['purpose'] == 'NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN', 'typed Producer wire contract differs')
    rows = finite['full_module_files']
    expected = index['original17'] + index['new_sources'] + index['dependency_sources']
    expected += index['bootstrap_original_sources'] + [index['producer_abi']]
    need((len(index['original17']), len(index['new_sources']), len(index['dependency_sources']),
          len(index['bootstrap_original_sources'])) == (17, 5, 9, 2), 'typed 17+5+9+2 SOURCE partition differs')
    need(type(rows) is list and len(rows) == 34 and rows == expected, 'complete finite 34 SOURCE identities differ')
    aliases = [safe_relative(row['install_relative']) for row in rows]
    need(len(set(aliases)) == 34 and all(not any(denied(p) for p in alias.split('/')) for alias in aliases),
         'duplicate/non-static finite SOURCE alias')
    bootstrap = {row['install_relative'] for row in index['bootstrap_original_sources']}
    need(bootstrap == {'worker_sources/parent/launch_storage_contract.py',
                       'worker_sources/parent/n80_gpu_capacity.py'}, 'exact independent bootstrap aliases required')
    return rows


def typed_publication(source_root, t_source_root, index, folder):
    finite, raw = metadata(folder / 'FINITE_SOURCE_BUNDLE.json', 2 * 1024 * 1024)
    need((len(raw), H(raw)) == FINITE_PIN, 'fixed finite SOURCE publication bytes differ')
    abi, raw = metadata(folder / 'PRODUCER_ABI.json', 2 * 1024 * 1024)
    need((len(raw), H(raw)) == ABI_PIN, 'fixed Producer ABI publication bytes differ')
    rows = validate_finite_rows(index, finite, abi)
    for row in rows:
        path = source_reference(source_root, t_source_root, row['path'])
        info = identity(path)
        need((info['bytes'], info['SHA']) == (row['bytes'], row['SHA256']), 'finite whole SOURCE file differs')
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
    helper = index['original_capacity_helper']
    path = source_reference(source_root, t_source_root, helper['path'])
    info = identity(path)
    need((info['bytes'], info['SHA']) == T_PIN == (helper['bytes'], helper['SHA256']), 'original fixed T helper differs')
    return rows, abi


def verify_active_aliases(rows, bundle, *, actual_root=None):
    need(type(rows) is list and len(rows) == 34 and len({row['install_relative'] for row in rows}) == 34,
         'all 34 active bindings required')
    bootstrap = {'worker_sources/parent/launch_storage_contract.py', 'worker_sources/parent/n80_gpu_capacity.py'}
    for row in rows:
        alias = safe_relative(row['install_relative'])
        need(alias in bundle['materials'], 'complete active alias missing: ' + alias)
        source, info = bundle['materials'][alias]
        need((info['bytes'], info['SHA']) == (row['bytes'], row['SHA256']), 'active alias pin differs: ' + alias)
        if alias in bootstrap:
            need(alias in bundle['originals'] and alias not in bundle['sources']
                 and bundle['materials'][alias] == bundle['originals'][alias], 'bootstrap origin is not independent baseline')
        else:
            need(alias in bundle['sources'], 'finite overlay missing: ' + alias)
        path = no_links(Path(actual_root), alias) if actual_root is not None else source
        observed = identity(path)
        need(observed == info, 'active alias actual bytes differ: ' + alias)
    return dict(complete_bindings=34, overlay_bindings=32, independent_original_bootstrap_bindings=2,
                all_complete_source_bytes_verified=True)


def require_import_root(root, runtime):
    expected = Path(root).resolve()
    need(Path(runtime.__file__).resolve().parent == expected == runtime.HERE,
         'full runtime imported from a different root; ROOT must equal HERE')
    return True


def validate_task_metadata(runtime, contract, plan, index):
    """Real unchanged Producer validators/make_task only; no task_args/admission."""
    # Preserve V4's validation of the actual supplied plan before exercising
    # the two additional pure-metadata positive variants. validate_plan itself
    # does not own the control bound: real make_task -> validate_task does.
    selected = contract.validate_plan(plan, index)
    original_task = runtime.make_task(selected[0], plan, 2000., [101, 102])
    need(original_task['controls'] == plan['capture_controls'], 'original plan/task controls differ')
    tasks = []
    for controls in (64, 128):
        candidate = copy.deepcopy(plan)
        candidate['capture_controls'] = controls
        selected = [row for row in candidate['roles'] if row['role'] == 'E3']
        need(len(selected) == 1, 'exact E3 metadata row required')
        selected[0]['capture_controls'] = controls
        task = runtime.make_task(selected[0], candidate, 2000., [101, 102])
        contract.validate_task(task)
        need(task['controls'] == controls and task['model_PT_reads'] == 0
             and not any(key in task for key in ('teacher_path', 'source_path', 'checkpoint', 'a1_producer')),
             'synthetic typed task carries model fallback')
        tasks.append(task)
    negatives = [('controls', 160), ('controls', False), ('controls', 64.0),
                 ('seed', 20260929), ('requested_roles', ['E3', 'W35']),
                 ('checkpoint', 'NO_FILE_MODEL_DESCRIPTOR'),
                 ('kind', 'PHASE1_PASSIVE_CAPTURE_E3_N80_TASK_V1'),
                 ('integration', 'PHASE1_PASSIVE_CAPTURE_SOURCE_V1'),
                 ('typed_producer_schema', 'UNKNOWN_SCHEMA')]
    rejected = 0
    for key, value in negatives:
        bad = copy.deepcopy(tasks[0]); bad[key] = value
        try:
            contract.validate_task(bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('typed task negative unexpectedly passed: ' + key)
    for key, value in (('kind', 'PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1'),
                       ('typed_producer_schema', 'UNKNOWN_SCHEMA'), ('capture_controls', 160)):
        bad = copy.deepcopy(plan); bad[key] = value
        try:
            if key == 'capture_controls':
                runtime.make_task(selected[0], bad, 2000., [101, 102])
            else:
                contract.validate_plan(bad, index)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('typed plan/task negative unexpectedly passed: ' + key)
    return dict(actual_plan_controls=original_task['controls'], positive_controls=[64, 128],
                control_bound_owner='original prepare + real make_task -> validate_task; not validate_plan alone',
                real_task_and_plan_negative_checks=rejected,
                placeholder_fds_not_inspected=True, task_args_or_resource_admission_called=False,
                TASK_kind=tasks[0]['kind'], TASK_integration=tasks[0]['integration'],
                typed_producer_schema=tasks[0]['typed_producer_schema'])
