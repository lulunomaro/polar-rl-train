"""D7/component-V3 full SOURCE identities, distinct from 27 inherited captures.

Never import a producer, execute a lifecycle, or stat/open reports/discovery.
The PREP twelve-test execution is preserved separately from this final check.
"""
from pathlib import Path, PurePosixPath
import ast
import copy
import json
import sys
import good_holdout_contract as C

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORKSPACE = BASE.parent
MAX_SOURCE = 2 * 1024 * 1024
TEXT_EXTENSIONS = {'.py', '.json', '.md', '.txt', '.yml', '.yaml'}
COMPONENT = BASE / 'source_good_holdout_case_final_contract_v3'
D7 = BASE / 'source_stage_good_expert_holdout_v7'
D6 = BASE / 'source_stage_good_expert_holdout_v6'
V4 = BASE / 'source_good_holdout_lifecycle_routes_v4'
COMPONENT_SEAL_PIN = (1090, '3b7356b5a9ca44b0b7e86e5bd73fd424919aa8dccf3a5ce43ea1d7bd1b99a658')
COMPONENT_ROOT = 'e524d81448cf8e007ddcb79ce1cbc28a96431194882af0d62a70e549583df535'
D7_ROOT = '1b2624e17e69046c7c8c5d7cbb6d8ec01dbbe97021dccfccbcd5fa4553003787'
D6_SEAL_PIN = (1699, 'c3d6164ee5edc8fc05dbf2741bd99b3df447b1cbe9f0abf652f82cb0111d952d')
D6_ROOT = '976a1370e4ab6550a004c4ec621694e228a61174bf94eeac68ac797decff4bc2'
D6_MIRROR_PIN = (37206, 'e7be320414a39c70b6b4fc95fdb39295d8068d98f7425c56ff2f4fc6d6aa11ad')
V4_SEAL_PIN = (2975, '4ca6cdf8e6f86d25ca3ebedb0ad92bb9252e536846c9677b2a2539bc67c22396')
V4_ROOT = '1f1a7be709d6de59aa33273d56578293b78580ac37418b99df2f5f2aa68e9549'
V4_INVENTORY_PIN = (155693, 'ea9c86451bdd2f3e6d397f285f1141a0785c35e6e9b27402b6939c767f71e35c')
OLD_COMPONENT = BASE / 'source_good_holdout_teacher_schema_v2'
OLD_INDEX_PIN = (21472, '0012cf17c566e29648418a191a89e1e925db5df8406718f9e0c39b87c83780da')
OLD_RUNTIME_PIN = (56370, '7455449db33ef539a7d8517876a36a4c291d57ebaa1c361943af2343b2370ee2')
AUDIT = BASE / 'source_good_holdout_final_size_contract_audit_v1'
AUDIT_PINS = {'SOURCE_AUDIT.md': (13401, '68487e3690a6f99106416e83236cb522bedd065df9a4c92b9629628503d1848e'),
              'SOURCE_AUDIT.json': (16755, 'b648a00aa3f1c2d090b63b58f257825f5be5353c454e841452b11c692b9b800b')}


def source_path(value):
    C.need(type(value) in (str, type(Path())) or isinstance(value, Path), 'SOURCE path required')
    path = Path(value)
    C.need(path.is_absolute() and '..' not in path.parts, 'absolute lexical SOURCE path required')
    # This check precedes resolve/is_symlink/stat/open: even historical Python
    # captures under discovery are declarations only in this final binding.
    C.need(not {'reports', 'discovery'} & {p.lower() for p in path.parts}, 'historical reports/discovery never stat/opened by final SOURCE inventory')
    C.need(path.suffix.lower() in TEXT_EXTENSIONS and 'budget' not in path.name.lower() and path.name != 'FINAL.json', 'only small SOURCE text, no original FINAL/model/raw/ledger')
    C.need(path.is_relative_to(WORKSPACE), 'SOURCE outside named workspace')
    relative = path.relative_to(WORKSPACE)
    C.need(relative.parts[0] in (BASE.name, 'mod4v1_experts_fulldr_rm70_20261101'), 'unrelated project')
    cursor = path
    while cursor != WORKSPACE:
        C.need(not cursor.is_symlink(), 'SOURCE symlink rejected')
        cursor = cursor.parent
    return path


def checked_source(value, expected_bytes=None, expected_sha=None):
    path = source_path(value)
    size = path.stat().st_size
    C.need(0 < size <= MAX_SOURCE, 'small SOURCE text bound')
    blob = path.read_bytes()
    C.need(len(blob) == size, 'SOURCE changed during read')
    sha = C.H(blob)
    if expected_bytes is not None:
        C.need(type(expected_bytes) is int and size == expected_bytes, 'SOURCE byte length differs: ' + str(path))
    if expected_sha is not None:
        C.need(C.sha(expected_sha) and sha == expected_sha, 'SOURCE SHA differs: ' + str(path))
    if path.suffix.lower() == '.py':
        ast.parse(blob.decode('utf-8-sig'), filename=str(path))
    return dict(path=path.as_posix(), bytes=size, SHA256=sha, full_bytes_verified=True,
                Python_AST_parsed=path.suffix.lower() == '.py'), blob


def member_root(rows):
    C.need(type(rows) is list and rows and len({r.get('name') for r in rows}) == len(rows), 'unique complete seal member list')
    records = []
    for row in rows:
        name = row.get('name')
        C.need(type(name) is str and PurePosixPath(name).name == name and name not in ('.', '..'), 'flat sealed SOURCE member')
        C.need(type(row.get('bytes')) is int and row['bytes'] > 0 and C.sha(row.get('SHA256')), 'valid sealed SOURCE identity')
        records.append(name + '\t' + str(row['bytes']) + '\t' + row['SHA256'] + '\n')
    return C.H(''.join(sorted(records)).encode())


def checked_seal(path, pin, expected_members, expected_root=None):
    seal_row, blob = checked_source(path, *pin)
    seal = json.loads(blob)
    C.need(len(seal.get('files', [])) == expected_members, 'whole seal member count differs')
    root = member_root(seal['files'])
    C.need(root == seal.get('root_SHA256'), 'whole seal root differs')
    if expected_root is not None:
        C.need(root == expected_root, 'fixed upstream SOURCE root differs')
    checked = []
    for row in seal['files']:
        item, _ = checked_source(Path(path).parent / row['name'], row['bytes'], row['SHA256'])
        checked.append(dict(item, name=row['name']))
    return dict(seal=seal_row, root_SHA256=root, members=checked, count=len(checked), source_members_unchanged=True)


def json_source(path, pin):
    item, raw = checked_source(path, *pin)
    value = json.loads(raw)
    C.need(type(value) is dict, 'SOURCE metadata mapping required')
    return item, value


def row_map(rows):
    C.need(type(rows) is list, 'whole SOURCE row list')
    result = {}
    for row in rows:
        rel = row.get('workspace_relative')
        C.need(type(rel) is str and not rel.startswith('/') and '\\' not in rel and ':' not in rel and all(p not in ('', '.', '..') for p in rel.split('/')), 'lexical workspace SOURCE/declaration path')
        C.need(set(row) == {'workspace_relative', 'bytes', 'SHA256'} and type(row['bytes']) is int and row['bytes'] > 0 and C.sha(row['SHA256']), 'complete declaration row only')
        C.need(rel not in result, 'duplicate logical SOURCE row')
        result[rel] = row
    return result


def split_mirror(mirror, old_mirror):
    current = row_map(mirror['files']); old = row_map(old_mirror['files'])
    C.need(mirror.get('kind') == 'COMPLETE_GOOD_HOLDOUT_V7_PINNED_TEXT_MIRROR_INPUTS' and mirror.get('source_only') is True, 'D7 SOURCE mirror identity')
    C.need(len(current) == 164 and len(old) == 145 and all(current.get(k) == v for k, v in old.items()), 'all previous145 whole row declarations unchanged')
    inherited = row_map(mirror.get('prior_rows_inherited_metadata_not_opened'))
    sensitive = {k: v for k, v in current.items() if {'reports', 'discovery'} & set(PurePosixPath(k).parts)}
    C.need(inherited == sensitive and len(inherited) == 27 and all(old.get(k) == v for k, v in inherited.items()), 'exact inherited27 reports/discovery rows, before any filesystem operation')
    C.need(sum('reports' in PurePosixPath(k).parts for k in inherited) == 9 and sum('discovery' in PurePosixPath(k).parts for k in inherited) == 18, 'nine historical reports plus eighteen discovery captures')
    C.need(mirror.get('prior_mirror_rows') == 145 and mirror.get('prior_rows_rehashed_SOURCE_only') == 118 and mirror.get('no_actual_report_discovery_or_FINAL_opened') is True, 'D7 classification source scope')
    allowed = [v for k, v in current.items() if k not in inherited]
    additions = [v for k, v in current.items() if k not in old]
    C.need(len(allowed) == 137 and len(additions) == 19 and not any({'reports', 'discovery'} & set(PurePosixPath(r['workspace_relative']).parts) for r in additions), '137 eligible SOURCE; nineteen added SOURCE only')
    return current, inherited, allowed, additions


def normalized_nodes(raw):
    text = raw.decode('utf-8-sig'); tree = ast.parse(text)
    return text, tree, {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def compare_complete_sources():
    _, before_runtime = checked_source(OLD_COMPONENT / 'good_expert_holdout_runtime_v1.py', *OLD_RUNTIME_PIN)
    _, after_runtime = checked_source(COMPONENT / 'good_expert_holdout_runtime_v1.py', *C.RUNTIME_PIN)
    a, at, an = normalized_nodes(before_runtime); b, bt, bn = normalized_nodes(after_runtime)
    changed = {'close_original_eval_resources', 'evaluate_waited_eval_case', 'grade_closed_reference_group'}
    C.need(set(an) == set(bn) and len(an) == 32, 'thirty full functions and two full classes retained')
    C.need(b.count(', maximum=CASE_FINAL_MAX') == 3 and b.count('CASE_FINAL_MAX = 2097152\n') == 1, 'exact three finite case FINAL call sites')
    C.need(b.replace('CASE_FINAL_MAX = 2097152\n', '').replace(', maximum=CASE_FINAL_MAX', '') == a, 'whole runtime reverse bytes equal D6')
    unchanged = []
    for name in an:
        if name not in changed:
            C.need(ast.dump(an[name], include_attributes=False) == ast.dump(bn[name], include_attributes=False) and ast.get_source_segment(a, an[name]) == ast.get_source_segment(b, bn[name]), 'whole runtime node differs: ' + name)
            unchanged.append(name)
    C.need(len([n for n in unchanged if isinstance(an[n], ast.FunctionDef)]) == 27 and len([n for n in unchanged if isinstance(an[n], ast.ClassDef)]) == 2, 'runtime27 full functions plus two classes unchanged')
    _, old_stage = checked_source(D6 / 'stage_good_expert_holdout_v6.py', 53543, 'df7c144542db0e51bc8f79e41fc2cd39dfcab4c27e8dae685a4fd94a70f7db34')
    sp = C.STAGER_SOURCE_PINS['source']; _, new_stage = checked_source(sp['path'], sp['bytes'], sp['SHA256'])
    sa, _, sn = normalized_nodes(old_stage); sb, _, tn = normalized_nodes(new_stage)
    C.need(set(sn) == set(tn) and len(sn) == 31, 'all31 complete materializer functions retained')
    for name in sn:
        old_text = ast.get_source_segment(sa, sn[name]); new_text = ast.get_source_segment(sb, tn[name])
        if name in ('preflight_summary', 'stage'):
            C.need(new_text.replace('_V7', '_V6').replace('source_derivation_version=7', 'source_derivation_version=6') == old_text, 'only D7 typed labels in complete function: ' + name)
        else:
            C.need(old_text == new_text and ast.dump(sn[name], include_attributes=False) == ast.dump(tn[name], include_attributes=False), 'whole D7 materializer function differs: ' + name)
    return dict(runtime_full_source_reverse_equal_D6=True, runtime_unchanged_functions=27,
                runtime_unchanged_classes=2, runtime_explicit_case_read_calls=3,
                runtime_default_metadata_not_changed=True, D7_materializer_unchanged_functions=29,
                D7_only_two_function_labels_changed=True, production_modules_imported=False,
                SOURCE_AST_only_not_runtime_substitution=True)


def active_overlay(component, old_component, materializer):
    entries = component.get('overlay_entries'); previous = old_component.get('overlay_entries')
    C.need(type(entries) is list and len(entries) == 20 and type(previous) is list and len(previous) == 20, 'twenty complete overlay rows')
    rows = {r['relative']: r for r in entries}; old = {r['relative']: r for r in previous}
    C.need(len(rows) == len(old) == 20 and set(rows) == set(C.OVERLAY_PINS), 'unique exact twenty aliases')
    C.need({k for k in rows if rows[k] != old[k]} == {'good_expert_holdout_runtime_v1.py'}, 'only one runtime row differs; other nineteen whole rows retained')
    C.need({k: v for k, v in component.items() if k not in ('overlay_entries', 'case_final_contract_source_revision')} == {k: v for k, v in old_component.items() if k != 'overlay_entries'}, 'all old index metadata and teacher revision2 retained')
    revision = component.get('case_final_contract_source_revision', {})
    C.need(type(revision.get('revision')) is int and revision['revision'] == 3 and revision.get('CASE_FINAL_MAX') == C.CASE_FINAL_MAX and revision.get('source_only') is True and revision.get('actual_native_binding') == 'UNKNOWN', 'separate V3 case revision, not old format identity')
    mapping = materializer.get('flat_source_dir_complete20_mapping')
    C.need(type(mapping) is list and len(mapping) == 20 and {r['relative'] for r in mapping} == set(rows), 'real whole flat20 SOURCE mapping')
    verified = []
    for row in entries:
        alias = row['relative']; pin = C.OVERLAY_PINS[alias]
        C.need((row['bytes'], row['SHA256']) == pin, 'active overlay pin differs: ' + alias)
        item, _ = checked_source(row['path'], *pin)
        flat = next(r for r in mapping if r['relative'] == alias)
        C.need(flat['flat_name'] == row['path'].replace('\\', '/').rsplit('/', 1)[-1] and (flat['bytes'], flat['SHA256']) == pin and WORKSPACE / flat['source_workspace_relative'] == Path(row['path']), 'exact normalized basename and provenance mapping')
        verified.append(dict(item, relative=alias, flat_name=flat['flat_name']))
    return verified


def provenance(materializer, current, inherited):
    publication = materializer.get('typed_runtime_publication', {})
    C.need(materializer.get('kind') == 'SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V7' and type(materializer.get('source_derivation_version')) is int and materializer['source_derivation_version'] == 7, 'exact D7 SOURCE index')
    C.need(publication.get('stage_receipt_kind') == C.STAGE_KIND and type(publication.get('source_derivation_version')) is int and publication['source_derivation_version'] == 7 and publication.get('COMPLETE_NAME') == C.STAGE_NAME, 'D7 typed runtime wire and preserved COMPLETE V1')
    C.need(publication.get('source_receipt') == dict(materialized=True, source_native_enabled=False, staged=False, dispatched=False) and publication.get('runtime_plan_changes_only') == dict(enabled=True, staged=True) and publication.get('runtime_plan_source_native_enabled') is False and publication.get('runtime_plan_dispatched') is False, 'SOURCE false versus future runtime two flags distinct')
    C.need(publication.get('original_plan_wire_pin') == dict(bytes=C.ORIGINAL_PLAN_PIN[0], SHA256=C.ORIGINAL_PLAN_PIN[1]) and publication.get('root_rule', '').endswith('no fixed PREFIX'), 'raw wire and nonPREFIX root unchanged')
    wire = materializer['original_group_plan_wire_identity']
    C.need(wire.get('runtime_ORIGINAL_PLAN_PIN') == dict(bytes=C.ORIGINAL_PLAN_PIN[0], SHA256=C.ORIGINAL_PLAN_PIN[1]) and wire.get('PUBLISHED_ORIGINAL_PLAN_PIN') == dict(bytes=C.PUBLISHED_ORIGINAL_PLAN_PIN[0], SHA256=C.PUBLISHED_ORIGINAL_PLAN_PIN[1]) and wire.get('decoded_canonical_SHA256') == C.ORIGINAL_PLAN_CANONICAL_SHA256 and wire.get('literal_wire_bytes_equal') is False and wire.get('canonical_equivalence_does_not_relax_raw_wire_pin') is True, 'wire/published/canonical three identities retained without opening historical capture')
    C.need(materializer.get('source_mirror') == dict(name='SOURCE_MIRROR_INPUTS.json', bytes=D6_MIRROR_PIN[0], SHA256=D6_MIRROR_PIN[1], files_count=145), 'historical D6 mirror reference retained; current164 is independently D7-seal-bound')
    declared = []
    for row in materializer.get('root_canonical_metadata', []):
        rel = row['workspace_relative']; expected = {k: v for k, v in row.items() if k != 'role'}
        C.need(row.get('role') in C.REQUESTED and inherited.get(rel) == expected, 'ROOT capture identity declaration retained without opening')
        declared.append(row)
    diagnostic = materializer.get('source_input_diagnostic', {})
    captures = diagnostic.get('local_captures', [])
    C.need(len(declared) == 2 and len(captures) == 15 and all(inherited.get(r['workspace_relative']) == r for r in captures), 'ROOT2 and core15 are historical declarations this round')
    C.need(diagnostic.get('parent_read_once_counts_are_historical_not_local_read_counts') is True and diagnostic.get('source_modules_not_executed_here') is True and diagnostic.get('native_pass_claim') is False, 'historical capture/source/native scopes')
    return dict(typed_revision=7, COMPLETE_NAME=C.STAGE_NAME, runtime_plan_flags_not_new_admission=True,
                original_plan_raw_pin=list(C.ORIGINAL_PLAN_PIN), published_plan_pin=list(C.PUBLISHED_ORIGINAL_PLAN_PIN),
                decoded_canonical_SHA256=C.ORIGINAL_PLAN_CANONICAL_SHA256,
                wire_canonical_equivalence_is_inherited_not_redecoded=True,
                root_metadata2_declarations=declared, core15_capture_declarations=captures,
                no_historical_capture_stat_read_or_decode=True,
                parent_original_once_counts_not_local_counts=True,
                historical_D6_mirror_reference_preserved=True,
                current_D7_mirror_identity_bound_by_own_final_seal=True,
                source_false_flags_not_copy_failure=True, native_waits_and_two_EX_unchanged=True)


def build_sources():
    C.require_final_pins()
    C.need(C.CASE_FINAL_MAX == 2097152 and C.PLAN_MAX == 262144 and C.GROUP_MAX == 8388608 and C.EXPORT_MAX == 16777216, 'four independent metadata/export caps unchanged')
    sp = C.STAGER_SOURCE_PINS
    d7 = checked_seal(sp['seal']['path'], (sp['seal']['bytes'], sp['seal']['SHA256']), 8, D7_ROOT)
    component_seal = checked_seal(COMPONENT / 'SOURCE_SEAL.json', COMPONENT_SEAL_PIN, 4, COMPONENT_ROOT)
    fixed = {}
    for key in ('source', 'index', 'mirror'):
        row = sp[key]; item, raw = checked_source(row['path'], row['bytes'], row['SHA256']); fixed[key] = item
        if key == 'index': materializer = json.loads(raw)
        if key == 'mirror': mirror = json.loads(raw)
    _, old_mirror = json_source(D6 / 'SOURCE_MIRROR_INPUTS.json', D6_MIRROR_PIN)
    current, inherited, allowed, additions = split_mirror(mirror, old_mirror)
    verified = []
    for row in allowed:
        item, _ = checked_source(WORKSPACE / row['workspace_relative'], row['bytes'], row['SHA256'])
        verified.append(dict(item, workspace_relative=row['workspace_relative']))
    component_row, component = json_source(COMPONENT / 'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V3.json', C.INDEX_PIN)
    old_component_row, old_component = json_source(OLD_COMPONENT / 'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json', OLD_INDEX_PIN)
    flat20 = active_overlay(component, old_component, materializer)
    C.need(materializer['source_index'] == dict(workspace_relative=component_row['path'].removeprefix(WORKSPACE.as_posix() + '/'), bytes=C.INDEX_PIN[0], SHA256=C.INDEX_PIN[1]), 'D7 active component index exact identity')
    old_v4 = checked_seal(V4 / 'SOURCE_SEAL.json', V4_SEAL_PIN, 12, V4_ROOT)
    _, old_inventory = json_source(V4 / 'SOURCE_PINS.json', V4_INVENTORY_PIN)
    legacy = {}
    for name, group in {'original_good14': old_inventory['original_good14_seal'], **old_inventory['prior_materializer_seals'], **old_inventory['prior_routes12_seals'], 'teacher_component5': old_inventory['component5_seal']}.items():
        seal = group['seal']; legacy[name] = checked_seal(seal['path'], (seal['bytes'], seal['SHA256']), group['count'], group['root_SHA256'])
    d6 = checked_seal(D6 / 'SOURCE_SEAL.json', D6_SEAL_PIN, 8, D6_ROOT)
    expected_additions = []
    for group in (d6, component_seal):
        expected_additions += [dict(workspace_relative=Path(r['path']).relative_to(WORKSPACE).as_posix(), bytes=r['bytes'], SHA256=r['SHA256']) for r in group['members'] + [group['seal']]]
    expected_additions += [dict(workspace_relative=(AUDIT / name).relative_to(WORKSPACE).as_posix(), bytes=pin[0], SHA256=pin[1]) for name, pin in AUDIT_PINS.items()]
    for name in ('collect_good_holdout_result.py', 'good_holdout_contract.py', 'good_holdout_remote_reader.py'):
        row = next(r for r in old_v4['members'] if r['name'] == name)
        expected_additions.append(dict(workspace_relative=Path(row['path']).relative_to(WORKSPACE).as_posix(), bytes=row['bytes'], SHA256=row['SHA256']))
    C.need(len(expected_additions) == 19 and row_map(additions) == row_map(expected_additions), 'exact new19: D6nine + audit2 + oldCFF3 + component5')
    proof = compare_complete_sources()
    return dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_INVENTORY_V5',
                scope='D7_CASE_COMPONENT_V3_ACTIVE20_SOURCE137_HISTORICAL27_UNOPENED',
                active_index=component_row, historical_D6_index=old_component_row,
                active20_full_sources=flat20, component4_seal=component_seal, D7_final8_seal=d7,
                D7_fixed_refs=fixed, D6_prior8_seal=d6, prior_V4_lifecycle12_seal=old_v4,
                additional_legacy_seals=legacy,
                D7_logical_mirror=dict(declared=164, full_eligible_SOURCE_verifications=137,
                    inherited_reports_discovery_declarations=list(inherited.values()),
                    inherited_unopened=27, inherited_reports=9, inherited_discovery=18,
                    previous145_whole_rows_unchanged=True, eligible_previous_SOURCE=118,
                    added19_SOURCE=additions, verified=verified, all164_fresh_rehashed=False,
                    no_historical_report_discovery_FINAL_stat_read_or_decode=True,
                    original_V4_136plus9_inventory_retained_as_history_not_current_scope=True,
                    logical164_plus_D7own9_is_not_flat20=True),
                raw_and_capture_provenance=provenance(materializer, current, inherited),
                complete_SOURCE_diff=proof, runtime_aliases=20, other19_whole_overlay_rows_unchanged=True,
                guard_identity_unchanged=True, original_parent_unchanged=True,
                source_verification_groups_overlap_not_a_disjoint_total=True,
                PREP12_not_rerun=True, final_check_is_source_identity_not_second_test_suite=True,
                actual_prepare_preflight_stage_main=False, actual_controller_reader_or_collector=False,
                actual_SSH_SDK_GPU_Torch=False, actual_model_raw_reports_C_or_lock_access=False,
                actual_native_binding='UNKNOWN', actual_quality=None, stage2_GO=False)


def verify_sources():
    C.require_final_pins()
    current = build_sources()
    recorded = json.loads((HERE / 'SOURCE_PINS.json').read_bytes())
    C.need(recorded == current, 'SOURCE inventory differs from complete SOURCE/declaration split')
    return current


if __name__ == '__main__':
    if sys.argv[1:] == ['--build']:
        value = build_sources()
        with (HERE / 'SOURCE_PINS.json').open('x', encoding='utf-8', newline='\n') as writer:
            json.dump(value, writer, ensure_ascii=False, indent=2, allow_nan=False)
            writer.write('\n')
    elif not sys.argv[1:]:
        value = verify_sources()
    else:
        raise SystemExit('SOURCE-only usage: --build | no args for read-only verification')
    print(json.dumps(dict(runtime_aliases=value['runtime_aliases'], full_eligible_SOURCE=137,
                          inherited_unopened=27, no_native_or_test_replay=True)))
