"""Own F:-workspace synthetic metadata/source only; never import/run four callers."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import unittest
import build_frozen_v2_admission2_callers_v1 as B

HERE = Path(__file__).resolve().parent
PINS, VALUES = B.load_inputs()
SOURCES, OPS = B.render_callers(VALUES)
CLOSED_RAW = VALUES[B.CLOSED_REL]
CLOSED = json.loads(CLOSED_RAW)
# All four original caller headers already import json before the injected fence.
# The isolated definition-only fixture must retain that ordinary module binding.
NS = {'json': json}
exec(compile(B.fence_source(CLOSED_RAW), '<stdlib-fence-definitions>', 'exec'), NS)
ARGS = None


def good_witness():
    return dict(kind='READONLY_POST_FROZEN_V2_ZERO_ADMISSION_RESOURCE_RELEASE_WITNESS_NOT_ADMISSION',
        old_root=NS['_A2_OLD_ROOT'], old_closed_epoch=1793642078.162321,
        old_closed_metadata_SHA=hashlib.sha256(CLOSED_RAW).hexdigest(), observer_only=True,
        old_parent_wait_not_extended=True, resource_release_observed=True, observer_timed_out=False,
        actual=dict(epoch=1793642079.162321, original_frozen_resources_observed_clear=True,
                    original_relevant_leases_clear=True, actual_future_admission_not_guaranteed=True,
                    lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0))


def check_release(w):
    return NS['_a2_check_release'](w, closed_SHA=B.H(CLOSED_RAW), closed_epoch=1793642078.162321)


def code_constant(text):
    return next(n.value for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Constant)
                and isinstance(n.value, str) and 'root=Path(ROOT);expected=EXPECTED;' in n.value)


def ast_dump(text): return ast.dump(ast.parse(text), include_attributes=False)


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.v = copy.deepcopy(CLOSED); self.w = good_witness()

    def test_01_actual_zero_go_closed_source_metadata(self):
        self.assertEqual(NS['_a2_check_closed'](self.v), 1793642078.162321)

    def test_02_old_top_admission_nonnull(self):
        self.v['top']['ACTUAL_GROUP_ADMISSION.json'] = {}
        with self.assertRaises(ValueError): NS['_a2_check_closed'](self.v)

    def test_03_old_empty_children_is_not_null(self):
        self.v['top']['CHILDREN.json'] = []
        with self.assertRaises(ValueError): NS['_a2_check_closed'](self.v)

    def test_04_old_start_or_final_nonnull(self):
        for name in ('GROUP_EVAL_START.json', 'FINAL.json', 'TERMINAL_ROWS.json'):
            v = copy.deepcopy(self.v); v['top'][name] = {}
            with self.assertRaises(ValueError): NS['_a2_check_closed'](v)

    def test_05_old_wait_release_bool_strict(self):
        for name in ('all_own_children_waited', 'original_single_GPU_private_EX_released', 'original_global_finite_EX_released'):
            v = copy.deepcopy(self.v); v['top']['PARENT_EXIT_SCOPE.json'][name] = 1
            with self.assertRaises(ValueError): NS['_a2_check_closed'](v)

    def test_06_old_waited_children_not_empty(self):
        self.v['top']['PARENT_EXIT_SCOPE.json']['child_waits'] = [{'pid': 1}]
        with self.assertRaises(ValueError): NS['_a2_check_closed'](self.v)

    def test_07_old_timeout_and_no_retry_retained(self):
        self.v['top']['PARENT_ORIGINAL_ERROR.json']['errors'] = []
        with self.assertRaises(ValueError): NS['_a2_check_closed'](self.v)

    def test_08_old_role_ready_or_final(self):
        for field in ('FINAL', 'WORKER_SCENE_READY', 'WORKER_EVAL_STARTED', 'PROGRESS'):
            v = copy.deepcopy(self.v); v['rows'][0][field] = {}
            with self.assertRaises(ValueError): NS['_a2_check_closed'](v)

    def test_09_old_closed_identity_changed(self):
        self.v['root'] += '_OTHER'
        with self.assertRaises(ValueError): NS['_a2_check_closed'](self.v)

    def test_10_old_canonical_bool_zero_rejected(self):
        self.v['top']['PARENT_EXIT_SCOPE.json']['canonical_writes'] = False
        with self.assertRaises(ValueError): NS['_a2_check_closed'](self.v)

    def test_11_positive_post_close_release(self):
        self.assertGreater(check_release(self.w), 1793642078.162321)

    def test_12_release_false_rejected(self):
        self.w['resource_release_observed'] = False
        with self.assertRaises(ValueError): check_release(self.w)

    def test_13_actual_resource_false_rejected(self):
        self.w['actual']['original_frozen_resources_observed_clear'] = False
        with self.assertRaises(ValueError): check_release(self.w)

    def test_14_equal_or_earlier_epoch_rejected(self):
        for e in (1793642078.162321, 1793642077, True, float('nan'), float('inf')):
            w = good_witness(); w['actual']['epoch'] = e
            with self.assertRaises(ValueError): check_release(w)

    def test_15_different_close_hash_root_epoch_rejected(self):
        for key, value in (('old_closed_metadata_SHA', 'f'*64), ('old_root', '/OTHER'), ('old_closed_epoch', 1)):
            w = good_witness(); w[key] = value
            with self.assertRaises(ValueError): check_release(w)

    def test_16_release_is_not_permanent_admission(self):
        self.w['actual']['actual_future_admission_not_guaranteed'] = False
        with self.assertRaises(ValueError): check_release(self.w)

    def test_17_release_observer_timed_out_rejected(self):
        self.w['observer_timed_out'] = True
        with self.assertRaises(ValueError): check_release(self.w)

    def test_18_release_nonreadonly_rejected(self):
        self.w['actual']['lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals'] = 1
        with self.assertRaises(ValueError): check_release(self.w)


class SourceAndOwnIoTests(unittest.TestCase):
    def own(self, name):
        p = ARGS.fixtures_root / name; p.mkdir(); return p

    def closed_at(self, project, raw=CLOSED_RAW):
        p = project / B.CLOSED_REL; p.parent.mkdir(parents=True); p.write_bytes(raw)

    def test_19_preparation_does_not_require_release_file(self):
        p = self.own('PREP_WITHOUT_RELEASE'); self.closed_at(p)
        f = NS['_a2_load_fence'](p, False)
        self.assertFalse(f['release_verified']); self.assertIsNone(f['release_witness'])

    def test_20_dispatch_missing_release_fails_closed(self):
        p = self.own('DISPATCH_WITHOUT_RELEASE'); self.closed_at(p)
        with self.assertRaises(FileNotFoundError): NS['_a2_load_fence'](p, True)

    def test_21_dispatch_positive_release_own_fake_only(self):
        p = self.own('DISPATCH_SYNTHETIC_POSITIVE'); self.closed_at(p)
        w = p / NS['_A2_RELEASE_REL']; w.write_text(json.dumps(good_witness()), encoding='utf-8')
        f = NS['_a2_load_fence'](p, True)
        self.assertTrue(f['release_verified']); self.assertEqual(f['release_witness']['SHA256'], B.H(w.read_bytes()))
        self.assertTrue(f['release_witness']['historical_snapshot_not_resource_ownership_or_future_admission'])

    def test_22_changed_closed_bytes_even_same_json_rejected(self):
        p = self.own('CHANGED_CLOSED_BYTES'); self.closed_at(p, CLOSED_RAW + b'\n')
        with self.assertRaises(ValueError): NS['_a2_load_fence'](p, False)

    def test_23_all_four_standalone_ast_and_compile(self):
        self.assertEqual(len(SOURCES), 4)
        for name, text in SOURCES.items(): ast.parse(text); compile(text, name, 'exec')

    def test_24_whitelist_inverse_original_bytes_and_whole_ast(self):
        for old, new in zip(B.TEMPLATES, B.OUTPUTS):
            restored = B.undo(SOURCES[new], OPS[new])
            self.assertEqual(restored.encode('utf-8'), VALUES[old])
            self.assertEqual(ast_dump(restored), ast_dump(VALUES[old]))

    def test_25_stage_from_first_read_V2_and_complete_source_SHA(self):
        text = SOURCES[B.OUTPUTS[1]]
        self.assertNotIn('STAGE_COMPLETE_MICROBATCH_V1.json', text)
        self.assertIn("s.open(p['root']+'/STAGE_COMPLETE_MICROBATCH_V2.json'", text)
        self.assertIn('stager_bytes=32953,stager_SHA=_A2_STAGE_SHA', text)
        self.assertIn("stager_SHA=v['stager_SHA']", text)

    def test_26_dispatch_own_new_standard_report_not_erratum(self):
        text = SOURCES[B.OUTPUTS[2]]
        self.assertIn('reports/FROZEN_E3_W35_BATCH_V2_ADMISSION2_ACTUAL_SOURCE_STAGE_V1.json', text)
        self.assertNotIn('RECEIPT_CORRECTED', text)
        self.assertIn('STAGE_COMPLETE_MICROBATCH_V2.json', text)

    def test_27_dispatch_release_fence_before_ssh_marker_and_parent(self):
        text = SOURCES[B.OUTPUTS[2]]
        fence = text.index('fence=_a2_load_fence(R,True)')
        self.assertLess(fence, text.index('marker.write_text('))
        self.assertLess(fence, text.index('from project_connector import connect72'))
        self.assertEqual(text.count('child=subprocess.Popen('), 1)

    def test_28_remote_parent_launch_ast_unchanged_except_outer_metadata(self):
        old = code_constant(VALUES[B.TEMPLATES[2]])
        new = code_constant(SOURCES[B.OUTPUTS[2]])
        self.assertEqual(new.replace('\nrequest.update(__A2_META__)', ''), old)
        fake_root = NS['_A2_TASKS'] + NS['_A2_PREFIX'] + 'SYNTHETIC'
        for c in (old, new):
            c = c.replace('ROOT', repr(fake_root)).replace('EXPECTED', repr('e'*64)).replace('__GROUP_ID__', repr(fake_root.rsplit('/', 1)[1])).replace('__A2_META__', repr({'synthetic': True}))
            ast.parse(c)

    def test_29_original_parent_ABI_kind_not_version_rewritten(self):
        text = SOURCES[B.OUTPUTS[2]]
        self.assertIn("plan['kind']=='A1_FROZEN_EVAL_MICROBATCH_GROUP_PLAN_V1'", text)
        self.assertIn("parent=root/'single_gpu_e3_w35_a1_frozen_parent_v1.py'", text)
        self.assertIn(B.PARENT_PIN[1], text)
        self.assertNotIn('single_gpu_e3_w35_a1_frozen_parent_v2.py', text)

    def test_30_stager_index_payload_and_original_source_kind_pins(self):
        text = SOURCES[B.OUTPUTS[0]]
        self.assertIn('source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py', text)
        self.assertIn("P=R/'payload_frozen_microbatch_v2'", text)
        self.assertIn(B.STAGE_PIN[1], text); self.assertIn(B.INDEX_PIN[1], text)
        self.assertEqual(len(PINS['verified_unchanged_payload14']), 14)

    def test_31_fresh_source_input_root_own_reports_and_group(self):
        upload = SOURCES[B.OUTPUTS[0]]
        self.assertIn("input_root=root+'_SOURCE_INPUT'", upload)
        self.assertIn("run='MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_ADMISSION2_'", upload)
        for text in SOURCES.values(): self.assertIn("_A2_VERSION = 'V2_ADMISSION2'", text)
        observer = SOURCES[B.OUTPUTS[3]]
        self.assertIn('ACTUAL_FROZEN_E3_W35_BATCH_V2_ADMISSION2_', observer)
        self.assertIn('FROZEN_E3_W35_BATCH_V2_ADMISSION2_LATEST_CLOSED_RESULT_PATH.json', observer)

    def test_32_builder_not_emitting_or_executing_at_import(self):
        self.assertNotIn('project_connector', sys.modules)
        self.assertNotIn('torch', sys.modules)
        self.assertNotIn('isaacsim', sys.modules)
        self.assertTrue(all(not (HERE.parent / n).exists() for n in B.OUTPUTS))
        own = ast.parse(Path(B.__file__).read_bytes())
        imports = [a.name for n in ast.walk(own) if isinstance(n, ast.Import) for a in n.names]
        self.assertNotIn('subprocess', imports); self.assertNotIn('paramiko', imports)

    def test_33_emit_only_four_new_source_in_own_fixture_and_no_overwrite(self):
        p = self.own('FOUR_SOURCE_FILES_ONLY')
        records = B.emit_sources(SOURCES, p)
        self.assertEqual(len(records), 4)
        for r in records: self.assertEqual(B.H((p / r['file']).read_bytes()), r['SHA256'])
        with self.assertRaises(ValueError): B.emit_sources(SOURCES, p)

    def test_34_partial_existing_caller_prevents_all_new_emission(self):
        p = self.own('EXISTING_SOURCE_ABORTS_BEFORE_ANY_WRITE'); (p / B.OUTPUTS[2]).write_text('sentinel', encoding='utf-8')
        with self.assertRaises(ValueError): B.emit_sources(SOURCES, p)
        self.assertEqual(len(tuple(p.iterdir())), 1)

    def test_35_source_group_bind_correct_and_old_purpose_rejected(self):
        p = self.own('BIND_META'); self.closed_at(p); f = NS['_a2_load_fence'](p, False)
        gid = NS['_A2_PREFIX'] + 'SYNTHETIC'
        v = dict(root=NS['_A2_TASKS']+gid, group_id=gid, input_root=NS['_A2_TASKS']+gid+'_SOURCE_INPUT', epoch=1793642081, **NS['_a2_meta'](f))
        NS['_a2_bind'](v, f)
        v['codeVersion'] = 'V2'
        with self.assertRaises(ValueError): NS['_a2_bind'](v, f)

    def test_36_source_group_escape_or_prior_root_rejected(self):
        p = self.own('BIND_BAD_ROOT'); self.closed_at(p); f = NS['_a2_load_fence'](p, False)
        for gid in (NS['_A2_PREFIX']+'../OTHER', 'MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_OLD'):
            v = dict(root=NS['_A2_TASKS']+gid, group_id=gid, epoch=1793642081, **NS['_a2_meta'](f))
            with self.assertRaises(ValueError): NS['_a2_bind'](v, f)

    def test_37_original_observer_waited_semantics_and_copy_limits_preserved(self):
        text = SOURCES[B.OUTPUTS[3]]
        for fragment in ("if exit_value:assert exit_value['all_own_children_waited']is True", 'time.monotonic()+7200', 'time.sleep(20)', 'assert len(raw)<32*1024**2'):
            self.assertIn(fragment, text)
        self.assertIn("source_parent_SHA=_A2_PARENT_SHA", text)

    def test_38_every_actual_caller_header_binds_json_before_fence(self):
        for text in SOURCES.values():
            module = ast.parse(text)
            json_imports = [n for n in module.body if isinstance(n, ast.Import) and any(a.name == 'json' for a in n.names)]
            self.assertTrue(json_imports)
            fence_def = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == '_a2_load_fence')
            self.assertLess(json_imports[0].lineno, fence_def.lineno)

    def argv_report(self, suffix):
        p = self.own(suffix); self.closed_at(p); f = NS['_a2_load_fence'](p, False)
        gid = NS['_A2_PREFIX'] + 'SYNTHETIC'; root = NS['_A2_TASKS'] + gid; source = root + '_SOURCE_INPUT'
        argv = [source+'/stage_a1_microbatch_eval_v2.py', '--original-group-root', NS['_A2_TASKS']+'MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700', '--source-dir', source+'/source', '--source-index', source+'/MICROBATCH_STAGE_INDEX_V2.json', '--native-root', NS['_A2_TASKS']+'MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000', '--new-root', root, '--group-id', gid, '--gpu-uuid', 'GPU-16828f91-2b45-b646-8dc0-9481138e2842', '--preflight-only']
        return dict(root=root, group_id=gid, input_root=source, argv=argv, epoch=1793642081, **NS['_a2_meta'](f)), f

    def test_39_exact_argv_new_root_preflight_and_stage(self):
        v, f = self.argv_report('EXACT_ARGV')
        NS['_a2_bind'](v, f); v['argv'][-1] = '--stage'; NS['_a2_bind'](v, f)

    def test_40_new_metadata_with_historical_argv_rejected(self):
        v, f = self.argv_report('OLD_ARGV_WITH_NEW_META'); v['argv'][10] = NS['_A2_OLD_ROOT']
        with self.assertRaises(ValueError): NS['_a2_bind'](v, f)

    def test_41_no_native_or_GPU_switch_or_extra_stage_flags(self):
        v, f = self.argv_report('GPU_NATIVE_FIXED')
        for position, value in ((8, '/OTHER_NATIVE'), (14, 'GPU_OTHER')):
            bad = copy.deepcopy(v); bad['argv'][position] = value
            with self.assertRaises(ValueError): NS['_a2_bind'](bad, f)
        v['argv'].append('--extra')
        with self.assertRaises(ValueError): NS['_a2_bind'](v, f)

    def test_42_new_group_is_plain_ascii_not_unicode_path(self):
        v, f = self.argv_report('ASCII_GROUP_ONLY'); v.pop('argv'); v.pop('input_root')
        v['group_id'] += '源'; v['root'] = NS['_A2_TASKS'] + v['group_id']
        with self.assertRaises(ValueError): NS['_a2_bind'](v, f)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--fixtures-root', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    ARGS = p.parse_args(); ARGS.fixtures_root = ARGS.fixtures_root.resolve()
    assert ARGS.fixtures_root.is_relative_to(HERE) and not ARGS.fixtures_root.exists() and not ARGS.output.exists()
    ARGS.fixtures_root.mkdir()
    before = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    value = dict(kind='SOURCE_ONLY_STDLIB_AST_SYNTHETIC_METADATA_ADMISSION2_TESTS_V1', testsRun=result.testsRun,
        failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(), seconds=time.perf_counter()-before,
        actual_caller_or_SSH_SDK_GPU_PT_raw_C_locks_Git_parent_operations=0, actual_resource_release_or_new_admission=None,
        fixture_root=str(ARGS.fixtures_root), emitted_new_project_root_callers=False)
    with ARGS.output.open('x', encoding='utf-8') as f: json.dump(value, f, indent=2); f.write('\n')
    print(json.dumps(value, indent=2)); raise SystemExit(0 if result.wasSuccessful() else 1)
