"""Full bounded SOURCE identity inventory; never imports an old producer/helper.

All 396 reviewed text mirror inputs are distinct from the 34 installed aliases.
The three denied historical report references remain unopened declarations.
No original static asset/model/bank payload or native result is inspected here.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import typed_collector_contract as C

HERE = Path(__file__).resolve().parent
R = HERE.parent
T = R.parent/'mod4v1_experts_fulldr_rm70_20261101'
WORKER = R/'source_phase1_typed_native_capture_v1'
MATERIALIZER = R/'source_phase1_typed_capture_materializer_v1'
OLD = R/'source_phase1_capture_result_collector_v4'
BASE_SEAL_PINS = {
    1: (1863, 'c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c'),
    2: (2568, '8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c'),
    3: (3595, '2f6188fe03958bfd237efab6c22ea6f63ffa61c54608144607db5d8bc9ff577f'),
    4: (4866, '23a5267920106b40b1efcf5db7921a16c6418621365d18933f0c9d69bfefc594'),
}
MAXIMUM = 2*1024*1024
PATCH_PROOFS = {
    'source_phase1_passive_sensor_capture_v4/SOURCE_DIFF.patch': (8378, 'd59e5c2587e93d057c5b9c3498ddfb6b28fdeeecb15189880210de4bb3565fa3'),
    'source_phase1_actuation_clock_scope_v2/C1_TO_C2_SOURCE_DIFF.patch': (6231, 'fe80994ac0db9e24e89a40138b6a62d6825c1bd0c794c9b8c2183a51676b9793'),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def lexical(value):
    return str(value).replace('\\', '/').rstrip('/')


def relative(value):
    need(type(value) is str and value and ':' not in value and '\\' not in value
         and not value.startswith('/') and all(p not in ('', '.', '..') for p in value.split('/')),
         'exact reviewed relative SOURCE path required')
    return value


class SourceReader:
    def __init__(self, r_root=R, t_root=T):
        self.roots = {'R': Path(r_root), 'T': Path(t_root)}
        self.rows = {}; self.raw = {}
        need(all(p.is_absolute() for p in self.roots.values()), 'two explicit absolute SOURCE roots required')
        need(not self.roots['R'].resolve().is_relative_to(self.roots['T'].resolve())
             and not self.roots['T'].resolve().is_relative_to(self.roots['R'].resolve()), 'SOURCE roots overlap')

    def path(self, root, rel, expected=None):
        relative(rel)
        need(root in self.roots, 'only explicit R/T SOURCE roots allowed')
        parts = rel.lower().split('/')
        need(not any(p in ('reports', 'states', 'checkpoints', 'budgets', 'locks', '__pycache__') for p in parts)
             and not rel.lower().endswith(('.pt', '.pth', '.npz', '.npy', '.jsonl', '.lock'))
             and parts[-1] not in ('final.json', 'closed_result.json', 'owner_exit_actual.json', 'cohort_final.json'),
             'model/raw/operational/report path denied before stat/open')
        suffix = Path(rel).suffix.lower()
        need(suffix in ('.py', '.json', '.md', '.txt', '.patch'), 'bounded text SOURCE formats only')
        if suffix == '.patch':
            need(root == 'R' and rel in PATCH_PROOFS and tuple(expected or ()) == PATCH_PROOFS[rel],
                 'only two exact SOURCE patch proofs, never runtime modules')
        if root == 'T':
            need(rel == 'NINE_N80_PARALLEL_SOURCE_V8/n80_gpu_capacity.py'
                 and tuple(expected or ()) == (653, 'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc'),
                 'T mirror is only the independent original capacity SOURCE helper')
        path = self.roots[root]/rel
        for p in (path, *path.parents):
            need(not p.is_symlink(), 'SOURCE symlink component rejected')
        need(path.resolve().is_relative_to(self.roots[root].resolve()), 'SOURCE path escapes explicit root')
        return path

    def read(self, root, rel, expected):
        need(type(expected[0]) is int and 0 <= expected[0] <= MAXIMUM and C.digest(expected[1]),
             'complete bounded whole SOURCE identity required')
        path = self.path(root, rel, expected)
        need(path.is_file() and path.stat().st_size <= MAXIMUM, 'bounded regular SOURCE file required')
        data = path.read_bytes()
        need((len(data), sha(data)) == tuple(expected), 'whole SOURCE bytes/SHA differ: '+root+':'+rel)
        data.decode('utf-8-sig')
        if path.suffix.lower() == '.py':
            ast.parse(data.decode('utf-8-sig'), filename=str(path))
        key = root+':'+rel
        row = dict(root=root, relative=rel, path=str(path), bytes=len(data), SHA256=sha(data),
                   full_text_read=True, Python_AST_parsed=path.suffix.lower() == '.py')
        need(key not in self.rows or self.rows[key] == row, 'SOURCE identity changed between references')
        self.rows[key] = row; self.raw[key] = data
        return data

    def read_absolute(self, path, expected):
        value = lexical(path)
        choices = [(name, lexical(root)) for name, root in self.roots.items()
                   if value.startswith(lexical(root)+'/')]
        need(len(choices) == 1, 'declaration must map to exactly one explicit SOURCE root')
        root, prefix = choices[0]
        return self.read(root, value[len(prefix)+1:], expected)

    def seal(self, root, rel, expected, count, declared_root=None):
        raw = self.read(root, rel, expected); value = json.loads(raw)
        files = value.get('files', value.get('members'))
        if type(files) is dict:
            rows = [dict(relative=name, bytes=info['bytes'], SHA256=info.get('SHA256', info.get('sha256')))
                    for name, info in files.items()]
        else:
            need(type(files) is list, 'complete frozen seal members required')
            rows = [dict(relative=row.get('relative', row.get('name')), bytes=row['bytes'], SHA256=row.get('SHA256', row.get('sha256')))
                    for row in files]
        need(len(rows) == count and len({r['relative'] for r in rows}) == count, 'whole seal member count differs')
        prefix = str(Path(rel).parent).replace('\\', '/')
        for row in rows:
            self.read(root, (prefix+'/' if prefix != '.' else '')+relative(row['relative']), (row['bytes'], row['SHA256']))
        actual = value.get('content_root_sha256', value.get('content_root_SHA256'))
        if declared_root is not None:
            need(actual == declared_root, 'published frozen content root literal differs')
        return dict(path=str(self.roots[root]/rel), bytes=len(raw), SHA256=sha(raw), members=rows,
                    declared_content_root=actual, root_literal_authenticated_by_whole_seal=True,
                    arbitrary_root_algorithm_not_invented=True)


def manifest_rows(value):
    references = []; unique = {}
    def visit(item):
        if type(item) is dict:
            if 'source_path' in item or 'source_sha256' in item:
                need('source_path' in item and C.digest(item.get('source_sha256')), 'complete sensor SOURCE declaration required')
                path = lexical(item['source_path']); digest = item['source_sha256']
                need(path not in unique or unique[path] == digest, 'conflicting sensor SOURCE declaration')
                unique[path] = digest; references.append((path, digest))
            for child in item.values():
                visit(child)
        elif type(item) is list:
            for child in item:
                visit(child)
    visit(value)
    return references, unique


def full_functions(raw):
    tree = ast.parse(raw.decode('utf-8-sig')); lines = raw.decode('utf-8-sig').splitlines(keepends=True)
    return {n.name: ''.join(lines[n.lineno-1:n.end_lineno]) for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def derivation_proof():
    old_reader = (OLD/'remote_metadata_reader.py').read_bytes()
    new_reader = (HERE/'remote_metadata_reader.py').read_bytes()
    old_cli = (OLD/'collect_capture_result.py').read_bytes()
    new_cli = (HERE/'collect_capture_result.py').read_bytes()
    unchanged_reader = ('require', 'validate_dispatch', 'terminal_projection', 'project', 'validate_terminal_cache', 'watch')
    unchanged_cli = ('integer', 'same_identity', 'connect_original', 'atomic_closed', 'collect', 'main')
    before = full_functions(old_reader); after = full_functions(new_reader)
    for name in unchanged_reader:
        need(before[name] == after[name], 'complete reader function changed unexpectedly: '+name)
    before_cli = full_functions(old_cli); after_cli = full_functions(new_cli)
    for name in unchanged_cli:
        need(before_cli[name] == after_cli[name], 'complete collector function changed unexpectedly: '+name)
    return dict(whole_V4_reader_SHA256=sha(old_reader), whole_NEW_reader_SHA256=sha(new_reader),
                whole_V4_cli_SHA256=sha(old_cli), whole_NEW_cli_SHA256=sha(new_cli),
                complete_reader_functions_identical=list(unchanged_reader), complete_cli_functions_identical=list(unchanged_cli),
                deliberate_changes=['typed34 complete finite verification and normal whole safe imports',
                    'exact typed wire kinds and actual materialization receipt metadata',
                    'explicit seven payload removal paths instead of old positive whitelist',
                    'cached/post-read immutable signatures without second raw read/hash/parse',
                    'complete stdout16MiB including LF checked before transmission',
                    'preserve failure metadata even if complete closure import fails'],
                AST_cropped_or_stubbed_production_helpers=False)


def build_sources(r_root=R, t_root=T):
    reader = SourceReader(r_root, t_root)
    mat_rel = 'source_phase1_typed_capture_materializer_v1'
    worker_rel = 'source_phase1_typed_native_capture_v1'
    mat = reader.seal('R', mat_rel+'/SOURCE_SEAL.json', C.MATERIALIZER_PINS['SOURCE_SEAL.json'], 28, C.MATERIALIZER_ROOT)
    for name, pin in C.MATERIALIZER_PINS.items():
        reader.read('R', mat_rel+'/'+name, pin)
    mirror = json.loads(reader.raw['R:'+mat_rel+'/SOURCE_MIRROR_INPUTS.json'])
    need(mirror.get('kind') == 'PHASE1_TYPED_MATERIALIZER_R_T_SOURCE_MIRROR_INPUTS_V1'
         and mirror.get('file_count') == 396 and mirror.get('R_file_count') == 395
         and mirror.get('T_file_count') == 1 and mirror.get('active_aliases') == 34
         and mirror.get('overlay_aliases') == 32 and mirror.get('independent_baseline_bootstrap_aliases') == 2,
         'whole reviewed typed mirror396 and finite34 routing required')
    rows = mirror.get('files'); need(type(rows) is list and len(rows) == 396, 'full396 SOURCE rows required')
    need(len({(x['root'], x['relative']) for x in rows}) == 396
         and sum(x['root'] == 'R' for x in rows) == 395 and sum(x['root'] == 'T' for x in rows) == 1,
         'distinct explicit R395/T1 SOURCE mirror required')
    for row in rows:
        reader.read(row['root'], row['relative'], (row['bytes'], row['SHA256']))
    producer = reader.seal('R', worker_rel+'/SOURCE_SEAL.json', C.PRODUCER_SEAL_PIN, 15, C.PRODUCER_ROOT)
    index = json.loads(reader.read('R', worker_rel+'/CAPTURE_SOURCE_INDEX.json', (C.INDEX_BYTES, C.INDEX_SHA)))
    abi = json.loads(reader.read('R', worker_rel+'/PRODUCER_ABI.json', C.ABI_PIN))
    finite = json.loads(reader.read('R', worker_rel+'/FINITE_SOURCE_BUNDLE.json', C.FINITE_PIN))
    observed = C.finite_rows(index, abi)
    expected = {x['install_relative']: (x['bytes'], x['SHA256']) for x in finite['full_module_files']}
    need(len(expected) == 34 and observed == expected, 'full finite bundle/index/ABI differs')
    for row in finite['full_module_files']:
        reader.read_absolute(row['path'], (row['bytes'], row['SHA256']))
    packages = {}
    for key, count in dict(sensor=21, actuation=8, adapter=10, partition=9, codec=7, actuation_clock_scope_v2=5).items():
        ref = index['dependency_seals'][key]
        path = lexical(ref['path']); prefix = lexical(reader.roots['R'])+'/'
        need(path.startswith(prefix), 'dependency seal outside explicit R')
        packages[key] = reader.seal('R', path[len(prefix):], (ref['bytes'], ref['SHA256']), count, ref.get('content_root_sha256'))
        need(len(ref['members']) == count, 'producer complete dependency member declaration differs')
    ref = index['original_B2_reference_seal']; path = lexical(ref['path']); prefix = lexical(reader.roots['R'])+'/'
    old_b2 = reader.seal('R', path[len(prefix):], (ref['bytes'], ref['SHA256']), 13)
    need(ref.get('content_root_sha256') is None and old_b2['declared_content_root'] is None,
         'old B2 null root must remain null; never substitute B4 root')
    actuation = index['all_actuation_original_sources']
    need(len(actuation) == index['actuation_original_source_count'] == 182, 'all182 original actuation SOURCE rows required')
    for rel, pin in actuation.items():
        reader.read('R', rel, (pin['bytes'], pin.get('SHA256', pin.get('sha256'))))
    sensor = index['sensor_source_manifest']; manifest = json.loads(reader.read_absolute(sensor['path'], (sensor['bytes'], sensor['SHA256'])))
    references, unique = manifest_rows(manifest)
    closure = sensor['original_source_closure']; closure_rows = closure['sources']
    expected = {lexical(row['path']): row['SHA256'] for row in closure_rows}
    need(len(references) == closure['pin_references'] == 435 and len(unique) == closure['unique_full_source_files'] == 155
         and expected == unique and len(closure_rows) == 155, 'whole B2 manifest435/155 SOURCE closure differs')
    for row in closure_rows:
        reader.read_absolute(row['path'], (row['bytes'], row['SHA256']))
    baseline_collectors = []
    for number in (1, 2, 3, 4):
        rel = 'source_phase1_capture_result_collector_v'+str(number)+'/SOURCE_SEAL.json'
        baseline_collectors.append(reader.seal('R', rel, BASE_SEAL_PINS[number], 9))
    need(mirror.get('excluded_denied_historical_metadata_references') == 3, 'three historical references stay excluded before I/O')
    return dict(kind='PHASE1_TYPED_COLLECTOR_FULL_SOURCE_PINS_V1', source_only=True,
        explicit_roots={k: str(v) for k,v in reader.roots.items()}, typed_producer_schema=C.SCHEMA,
        producer15=producer, materializer28=mat, dependency_packages=packages, original_B2_reference13=old_b2,
        reviewed_mirror=dict(bytes=C.MATERIALIZER_PINS['SOURCE_MIRROR_INPUTS.json'][0], SHA256=C.MATERIALIZER_PINS['SOURCE_MIRROR_INPUTS.json'][1],
            verified_full_text_inputs=396, R_inputs=395, T_inputs=1, denied_historical_report_references_unopened=3,
            two_patch_proofs_SOURCE_only=True, static_inventory_descriptor_JSON_not_followed=True),
        finite_active_bindings=dict(complete=34, overlay=32, independently_baseline_authoritative_bootstrap=2,
            full_static_baseline_is_not_finite34=True), original_actuation_SOURCE_files=182,
        sensor_source_manifest=dict(pin_references=435, unique_full_python_sources=155,
            full_SOURCE_bytes_and_AST_checked=True, build_manifest_or_reset_binding_verifier_called=False),
        historical_collector_seals=baseline_collectors, derivation=derivation_proof(),
        independently_checked_unique_source_files=len(reader.rows), sources=[reader.rows[k] for k in sorted(reader.rows)],
        old_tests_reexecuted=False, actual_whole_FINAL_or_trace_read=False, model_raw_SDK_Torch_GPU_C_lock_operations=0,
        actual_materializer_prepare_preflight_stage_or_collector_main_calls=0,
        actual_SDK_binding='UNKNOWN', science_consumer_enabled=False, gate1='UNKNOWN',
        capture_interface_passed=False, exact=False, stage2_GO=False)


def verify_sources():
    stored = json.loads((HERE/'SOURCE_PINS.json').read_bytes())
    current = build_sources()
    need(stored == current, 'frozen SOURCE inventory differs from full current text identities')
    return current


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--build', action='store_true'); args = parser.parse_args()
    value = build_sources() if args.build else verify_sources()
    if args.build:
        with (HERE/'SOURCE_PINS.json').open('xb') as stream:
            stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False).encode()+b'\n')
    print(json.dumps(dict(whole_SOURCE_mirror_inputs=396, typed_active_bindings=34,
        independently_checked_unique_SOURCE_files=value['independently_checked_unique_source_files'],
        no_old_suite_or_native_execution=True), sort_keys=True))
