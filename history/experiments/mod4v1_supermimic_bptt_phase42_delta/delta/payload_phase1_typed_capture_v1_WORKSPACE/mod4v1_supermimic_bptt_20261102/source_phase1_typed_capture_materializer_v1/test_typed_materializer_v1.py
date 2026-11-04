"""Nine new own-temp SOURCE/AST cases, not the old 44/63/10 suites.

Only complete actual modules are copied for metadata import. Inventories use
explicit own byte fixtures (not an actual V8 tree or measured native vendor7).
No prepare, preflight, stage, parent main, SDK or runtime admission is called.
"""
from __future__ import annotations
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R = HERE.parent
sys.path.insert(0, str(HERE))
import stage_phase1_typed_capture_v1 as materializer
import typed_source_support_v1 as support

PRODUCER = R / 'source_phase1_typed_native_capture_v1'
RESULTS = {}


def actual_metadata():
    index = json.loads((PRODUCER / 'CAPTURE_SOURCE_INDEX.json').read_bytes())
    finite = json.loads((PRODUCER / 'FINITE_SOURCE_BUNDLE.json').read_bytes())
    abi = json.loads((PRODUCER / 'PRODUCER_ABI.json').read_bytes())
    return index, finite, abi


def source_path(value):
    value = value.replace('\\', '/')
    marker = '/' + R.name + '/'
    assert value.count(marker) == 1
    relative = value.split(marker, 1)[1]
    assert not any(materializer.denied(p) for p in materializer.safe_relative(relative).split('/'))
    return R / relative


class OwnFixture:
    """Independent fake origin plus intact Producer modules; never a live root."""
    def __init__(self, base):
        self.base = Path(base)
        self.inputs = self.base / 'independent_original_byte_fixtures'
        self.sources_root = self.base / 'whole_source_inputs'
        self.inputs.mkdir(); self.sources_root.mkdir()
        self.index, finite, self.abi = actual_metadata()
        self.rows = support.validate_finite_rows(self.index, finite, self.abi)
        self.sources, self.originals = {}, {}
        bootstrap = {r['install_relative'] for r in self.index['bootstrap_original_sources']}
        def put(root, alias, raw):
            target = root / alias
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            return target, dict(bytes=len(raw), SHA=materializer.H(raw))
        for row in self.rows:
            raw = source_path(row['path']).read_bytes()
            assert (len(raw), materializer.H(raw)) == (row['bytes'], row['SHA256'])
            alias = row['install_relative']
            if alias in bootstrap:
                self.originals[alias] = put(self.inputs, alias, raw)
            else:
                self.sources[alias] = put(self.sources_root, alias, raw)
        raw = (PRODUCER / 'CAPTURE_SOURCE_INDEX.json').read_bytes()
        self.sources['CAPTURE_SOURCE_INDEX.json'] = put(self.sources_root, 'CAPTURE_SOURCE_INDEX.json', raw)
        # Own opaque bytes are inventory fixtures, not replacement runtime modules.
        for role in materializer.ROLES:
            for name, raw in (('SOURCE_FIXTURE.txt', ('own inventory ' + role).encode()),
                              ('bank.npy', b'OWN_FAKE_STATIC_NPY_BYTES'),
                              ('bank.npz', b'OWN_FAKE_STATIC_NPZ_BYTES')):
                alias = 'runtimes/' + role + '/' + name
                self.originals[alias] = put(self.inputs, alias, raw)
        self.originals['pinned_assets/SOURCE_FIXTURE.txt'] = put(self.inputs, 'pinned_assets/SOURCE_FIXTURE.txt', b'OWN_FAKE_ASSET_BYTES')
        # The actual prepare() vendor7 tree/hash gate is AST-retained, NOT exercised
        # or claimed by these seven fixture metadata entries.
        for n in range(7):
            alias = 'supermimic_vendor_v2/OWN_FIXTURE_' + str(n) + '.txt'
            self.originals[alias] = put(self.inputs, alias, ('own vendor inventory ' + str(n)).encode())
        # A real old full module creates a genuine, dynamically computed alias
        # conflict. No hardcoded assumption that a future V8 input has 3 collisions.
        old = R / 'source_phase1_capture_worker_v4' / 'phase1_capture_runtime.py'
        self.originals['phase1_capture_runtime.py'] = put(self.inputs, 'phase1_capture_runtime.py', old.read_bytes())
        self.materials, self.inventory = materializer.retain_originals(self.originals, self.sources,
            original_root=self.inputs, original_plan_SHA='1' * 64, native_root=self.base / 'NO_NATIVE_ROOT_READ')
        self.bundle = dict(sources=self.sources, originals=self.originals, materials=self.materials,
            index=self.index, active_bindings=self.rows, producer_abi=self.abi)
        future = self.base / 'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_TYPED_V1_OWN_FIXTURE'
        roles = []
        for role in materializer.ROLES:
            row = dict(role=role, controls=materializer.CONTROLS[role], num_envs=80, seed=20260928,
                runtime_root=str(future / 'runtimes' / role), asset_dir=str(future / 'runtimes' / role / 'assets'))
            if role == 'E3':
                row.update(worker='worker_passive_interface_v1.py', capture_controls=64)
            roles.append(row)
        self.plan = dict(kind=support.PLAN_KIND, typed_producer_schema=support.SCHEMA,
            batch_purpose=materializer.PURPOSE, policy_variant='EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY',
            group_id=future.name, GPU_UUID='GPU-00000000-0000-0000-0000-000000000000',
            asset_SHA=materializer.USD, contract_SHA=materializer.CONTRACT, capture_controls=64,
            requested_roles=['E3'], deferred_roles=list(materializer.ROLES[1:]),
            paired_reset_protocol=materializer.paired_plan(), roles=roles, comparison=None,
            overall_eight_pass_rate=None, source_native_enabled=False, staged=False, dispatched=False,
            actual_SDK_executed=False, gate1='UNKNOWN', capture_interface_passed=False, exact=False, stage2_GO=False,
            retained_static_inventory=self.inventory,
            worker_files=[dict(relative=alias, **value[1]) for alias, value in sorted(self.materials.items())])


class TypedMaterializerTests(unittest.TestCase):
    def test_01_complete_derivation_helpers_and_parent(self):
        old = R / 'source_phase1_capture_materializer_v4'
        self.assertEqual((HERE / 'static_source_helpers_v1.py').read_bytes(), (old / 'static_source_helpers_v1.py').read_bytes())
        helper = ast.parse((HERE / 'static_source_helpers_v1.py').read_bytes())
        self.assertEqual(len([n for n in helper.body if isinstance(n, ast.FunctionDef)]), 17)
        before = {n.name:n for n in ast.parse((old / 'stage_phase1_capture_v4.py').read_bytes()).body if isinstance(n, ast.FunctionDef)}
        after = {n.name:n for n in ast.parse((HERE / 'stage_phase1_typed_capture_v1.py').read_bytes()).body if isinstance(n, ast.FunctionDef)}
        report = json.loads((HERE / 'FUNCTION_DIFF.json').read_bytes())
        self.assertEqual(set(before), set(after))
        for name in report['same_complete_functions']:
            self.assertEqual(ast.dump(before[name]), ast.dump(after[name]))
        self.assertEqual((PRODUCER / 'single_gpu_passive_capture_parent_v1.py').read_bytes(),
                         (R / 'source_phase1_capture_worker_v4' / 'single_gpu_passive_capture_parent_v1.py').read_bytes())
        RESULTS['unchanged'] = dict(shared_helpers=17, complete_original_top_functions=14,
            same_stage_functions=len(report['same_complete_functions']), changed_stage_functions=len(report['necessary_changed_complete_functions']),
            parent_whole_bytes_identical=True)

    def test_02_complete_34_partition_and_new_wire(self):
        index, finite, abi = actual_metadata()
        rows = support.validate_finite_rows(index, finite, abi)
        self.assertEqual(len(rows), 34)
        for mutate in ('drop', 'duplicate', 'old_plan_wire', 'old_index_wire'):
            i, f, a = copy.deepcopy(index), copy.deepcopy(finite), copy.deepcopy(abi)
            if mutate == 'drop': f['full_module_files'].pop()
            if mutate == 'duplicate': f['full_module_files'][-1] = copy.deepcopy(f['full_module_files'][0])
            if mutate == 'old_plan_wire': a['wire']['GROUP_PLAN.kind'] = 'PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1'
            if mutate == 'old_index_wire': i['kind'] = 'PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1'
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                support.validate_finite_rows(i, f, a)
        RESULTS['finite'] = dict(aliases=34, overlays=32, independent_bootstrap=2, structural_negatives=4)

    def test_03_explicit_R_T_mirror_missing_dependency_and_lexical_denial(self):
        with tempfile.TemporaryDirectory(prefix='typed_mirror_own_') as name:
            root = Path(name); r, t = root / 'R', root / 'T'; r.mkdir(); t.mkdir()
            index, finite, abi = actual_metadata()
            base = next(x for x in finite['full_module_files'] if x['install_relative'] == 'resume_runtime_contracts_v3.py')
            (r / 'resume_runtime_contracts_v3.py').write_bytes(source_path(base['path']).read_bytes())
            target = t / support.T_RELATIVE; target.parent.mkdir(parents=True)
            target.write_bytes(source_path(next(x for x in index['bootstrap_original_sources'] if x['install_relative'].endswith('n80_gpu_capacity.py'))['path']).read_bytes())
            manifest = dict(file_count=2, R_file_count=1, T_file_count=1, files=[
                dict(root='R', relative='resume_runtime_contracts_v3.py', bytes=base['bytes'], SHA256=base['SHA256']),
                dict(root='T', relative=support.T_RELATIVE, bytes=support.T_PIN[0], SHA256=support.T_PIN[1])])
            self.assertEqual(support.verify_mirror_entries(manifest, r, t)['files'], 2)
            missing = copy.deepcopy(manifest); missing['files'][0]['relative'] = 'missing_full_Base.py'
            with self.assertRaises((ValueError, FileNotFoundError)):
                support.verify_mirror_entries(missing, r, t)
            with self.assertRaises(ValueError): support.verify_mirror_entries(manifest, r, None)
            wrong = copy.deepcopy(manifest); wrong['files'][1]['relative'] = 'unrelated.py'
            with self.assertRaises(ValueError): support.verify_mirror_entries(wrong, r, t)
            bad = dict(file_count=1, R_file_count=1, T_file_count=0, files=[dict(root='R', relative='models/NEVER.pt', bytes=0, SHA256='0'*64)])
            original_no_links = support.no_links
            filesystem_calls = []
            def unexpected_filesystem(*args, **kwargs):
                filesystem_calls.append((args, kwargs))
                raise AssertionError('filesystem reached')
            try:
                support.no_links = unexpected_filesystem
                with self.assertRaises(ValueError): support.verify_mirror_entries(bad, r, t)
                self.assertEqual(filesystem_calls, [])
            finally:
                support.no_links = original_no_links
            with self.assertRaises(ValueError): support.source_reference(r, t, 'F:/UNDECLARED/never.py')
        RESULTS['mirror'] = dict(explicit_R_T=True, missing_dependency_rejected=True,
            wrong_or_missing_T_rejected=True, model_name_denied_before_stat=True, drive_fallback=False)

    def test_04_full_original_metadata_modules_and_real_64_128_tasks(self):
        with tempfile.TemporaryDirectory(prefix='typed_full_modules_own_') as name:
            fixture = OwnFixture(name)
            result = materializer.metadata_validate(fixture.bundle, fixture.plan)
            self.assertTrue(result['passed']); self.assertTrue(result['ROOT_equals_HERE'])
            self.assertEqual(result['positive_task_controls'], [64, 128])
            self.assertEqual(result['active_bindings']['complete_bindings'], 34)
            self.assertEqual(result['negative_tasks_rejected'], 12)
            self.assertNotIn('phase1_sealed_actuation_tap', result['full_safe_module_names'])
            self.assertIn('phase1_sealed_actuation_c2', result['full_safe_module_names'])
            self.assertIn('phase1_sealed_actuation_tap', result['namespace_cleanup_watchlist'])
            self.assertTrue(result['complete_AppV6_Base']['helper_base_is_actual_imported_contracts'])
            self.assertTrue(all(row['full_original_module'] and not row['AST_cropped_or_stubbed']
                                for row in result['complete_AppV6_Base']['modules'].values()))
            self.assertEqual(result['resource_operations'], 0)
            self.assertFalse(result['native_worker_main_executed'])
            RESULTS['whole_metadata'] = result

    def test_05_missing_Base_and_changed_active_bytes(self):
        with tempfile.TemporaryDirectory(prefix='typed_missing_base_own_') as name:
            fixture = OwnFixture(name)
            bad = dict(fixture.bundle, materials=dict(fixture.materials))
            del bad['materials']['resume_runtime_contracts_v3.py']
            with self.assertRaises(ValueError): support.verify_active_aliases(fixture.rows, bad)
            path, info = fixture.sources['resume_runtime_contracts_v3.py']
            raw = path.read_bytes()
            try:
                path.write_bytes(raw + b'\n# OWN MUTATION\n')
                with self.assertRaises(ValueError): support.verify_active_aliases(fixture.rows, fixture.bundle)
            finally:
                path.write_bytes(raw)
        RESULTS['active_negatives'] = dict(missing_whole_Base=True, observed_source_mutation=True)

    def test_06_actual_full_runtime_ROOT_equals_HERE_without_stubs(self):
        with tempfile.TemporaryDirectory(prefix='typed_root_own_') as name:
            fixture = OwnFixture(name)
            before_path = list(sys.path); before = sys.modules.get('phase1_capture_contract')
            key = '_typed_own_complete_runtime'
            try:
                sys.modules.pop('phase1_capture_contract', None)
                sys.path.insert(0, str(fixture.sources_root))
                source = fixture.sources_root / 'phase1_capture_runtime.py'
                spec = importlib.util.spec_from_file_location(key, source)
                runtime = importlib.util.module_from_spec(spec); sys.modules[key] = runtime
                spec.loader.exec_module(runtime)
                self.assertTrue(support.require_import_root(fixture.sources_root, runtime))
                with self.assertRaises(ValueError): support.require_import_root(fixture.base / 'other_root', runtime)
                tree = ast.parse(source.read_bytes())
                fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_installed_root')
                self.assertIn('group == installed_root', ast.unparse(fn))
                entry = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'task_args')
                self.assertIn('validate_installed_root(group, HERE)', ast.unparse(entry))
            finally:
                sys.path[:] = before_path; sys.modules.pop(key, None)
                if before is None: sys.modules.pop('phase1_capture_contract', None)
                else: sys.modules['phase1_capture_contract'] = before
        RESULTS['root'] = dict(full_runtime_module_imported=True, ROOT_equals_HERE=True,
            wrong_root_rejected=True, real_task_args_or_actual_B_directory_calls=0)

    def test_07_independent_origin_and_dynamic_retained_oldbytes(self):
        with tempfile.TemporaryDirectory(prefix='typed_origin_own_') as name:
            fixture = OwnFixture(name)
            inv = fixture.inventory
            self.assertTrue(materializer.validate_preservation(inv, fixture.materials, originals=fixture.originals))
            moves = inv['baseline_provenance']['source_to_retained']
            self.assertEqual(set(moves), {'phase1_capture_runtime.py'})
            old = fixture.originals['phase1_capture_runtime.py']
            self.assertEqual(fixture.materials[moves['phase1_capture_runtime.py']], old)
            bad = copy.deepcopy(inv); bad['baseline_provenance']['original_logical_tree_SHA256'] = '0'*64
            with self.assertRaises(ValueError): materializer.validate_preservation(bad, fixture.materials, originals=fixture.originals)
            bad = copy.deepcopy(inv); bad['baseline_provenance']['original_logical_rows'][0]['input_path'] = str(Path(name)/'not_original')
            with self.assertRaises(ValueError): materializer.validate_preservation(bad, fixture.materials, originals=fixture.originals)
            missing = dict(fixture.materials); del missing[moves['phase1_capture_runtime.py']]
            with self.assertRaises(ValueError): materializer.validate_preservation(inv, missing, originals=fixture.originals)
        RESULTS['retention'] = dict(own_fixture_dynamic_conflicts=1, no_assumption_of_3=True,
            independent_origin_digest_and_input_paths_checked=True, original_full_V4_runtime_bytes_retained=True,
            missing_retained_bytes_rejected=True)

    def test_08_own_stream_observation_binds_oldbytes(self):
        with tempfile.TemporaryDirectory(prefix='typed_stream_own_') as name:
            fixture = OwnFixture(name); observed = {}
            out = Path(name) / 'OWN_STREAM_ONLY'; out.mkdir()
            for alias, (source, expected) in fixture.materials.items():
                target = out / alias; target.parent.mkdir(parents=True, exist_ok=True)
                h = hashlib.sha256(); count = 0
                with source.open('rb') as incoming, target.open('xb') as outgoing:
                    for chunk in iter(lambda: incoming.read(127), b''):
                        outgoing.write(chunk); h.update(chunk); count += len(chunk)
                observed[alias] = dict(bytes=count, SHA=h.hexdigest())
                self.assertEqual(observed[alias], expected)
            inv = copy.deepcopy(fixture.inventory)
            inv['installed'] = [dict(relative=r['relative'], bytes=observed[r['relative']]['bytes'], SHA256=observed[r['relative']]['SHA']) for r in inv['baseline']]
            self.assertTrue(materializer.validate_preservation(inv, fixture.materials, originals=fixture.originals, observed=observed))
            retained = next(iter(inv['baseline_provenance']['source_to_retained'].values()))
            observed[retained] = dict(bytes=observed[retained]['bytes'], SHA='0'*64)
            with self.assertRaises(ValueError): materializer.validate_preservation(inv, fixture.materials, originals=fixture.originals, observed=observed)
        RESULTS['stream'] = dict(own_temp_stream_bytes_measured=True, retained_stream_tamper_rejected=True,
            actual_stage_calls=0, actual_original_roots_read=0)

    def test_09_exact_SOURCE_patch_pins_and_original_stage_order(self):
        for (package, relative), pin in support.PATCH_PROOFS.items():
            sha = support.PATCH_PACKAGE_SEALS[package]
            self.assertTrue(support.patch_proof_allowed(package, relative, sha, pin))
            for values in ((package, relative, '0'*64, pin), (package, 'extra.patch', sha, pin),
                           ('foreign_package', relative, sha, pin), (package, relative, sha, (pin[0]+1, pin[1]))):
                self.assertFalse(support.patch_proof_allowed(*values))
        source = (HERE / 'stage_phase1_typed_capture_v1.py').read_text(encoding='utf-8')
        tree = ast.parse(source); node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        text = ast.get_source_segment(source, node)
        positions = [text.index(s) for s in ('for rel,(source,info)', 'os.fsync(outgoing.fileno())',
            'validate_preservation(inv', "put_once(root/'GROUP_PLAN.json'", 'metadata_validate(prepared', 'put_json(root/COMPLETE_NAME')]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('observed=written', text)
        self.assertIn('materialized=True,parent_launches=0', text)
        self.assertEqual(materializer.ROOT_PREFIX, 'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')
        self.assertTrue('MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_TYPED_V1_FUTURE_UNCONSUMED'.startswith(materializer.ROOT_PREFIX))
        # This null is an immutable original declaration, not a gap to patch.
        self.assertIsNone(actual_metadata()[0]['original_B2_reference_seal']['content_root_sha256'])
        RESULTS['stage_AST'] = dict(full_stream_fsync_observed_and_actual_root_metadata_before_complete=True,
            completion_filename_unchanged=materializer.COMPLETE_NAME, no_prepare_or_stage_execution=True,
            exact_patch_triple_pin_rules=True, B2_declared_null_unchanged=True)


if __name__ == '__main__':
    unittest.main()
