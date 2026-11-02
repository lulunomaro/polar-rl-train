"""Own synthetic bytes only. No original/actual JSONL, PT, SDK or environment."""
import ast
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr

import w35_original_row_split_consumer_v1 as c

HERE = Path(__file__).resolve().parent
SOURCE_ROOT = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8')
SHA = 'a' * 64
CONSTANTS = {'source_SHA', 'record_type', 'end_reason', 'axis_semantics', 'signed_yaw_tolerance',
             'not_full_expert_or_signed2pi_cycle_graduation', 'original_route_x', 'original_route_y',
             'original_catalog_goal_radius', 'goal_is_observer_only_not_a_new_reward_reset_or_skill_gate'}


def row(uid=1, **updates):
    value = dict(source_SHA=SHA, record_type=c.TARGET, env_id=0, episode_uid=0,
                 command_uid=uid, same_UID_segment=0, source_E1_episode=3, original_command_counter=uid,
                 first_control=0, last_control=0, controls=1, first_physics_tick=0, last_physics_tick=8,
                 seconds=.02, standing=False, start_observed=True, original_kinematic_bounds_met=True,
                 natural_complete_nonterminal_interval=True, complete_interval_bounds_fact=True,
                 terminated_before_reset=False, truncated_before_reset=False, end_reason='original_resample',
                 sampled_BODY_command=[0., 0., 0.], nominal_speed=0., signed_yaw_tolerance=.2,
                 not_full_expert_or_signed2pi_cycle_graduation=True,
                 original_terminal_reason_time_out=False)
    value.update(updates)
    return value


def fixture(rows, *, dropped=0):
    """Independent synthetic encoding of the published positional wire schema."""
    schemas, keys, encoded_rows, by_schema = [], {}, [], []
    for value in rows:
        fields = sorted(value)
        constants = {k: value[k] for k in fields if k in CONSTANTS}
        key = (tuple(fields), c._encoded(constants))
        if key not in keys:
            sid = len(schemas); keys[key] = sid
            schemas.append(dict(schema_id=sid, fields=fields, constants=constants,
                                positional_fields=[k for k in fields if k not in constants]))
            by_schema.append(0)
        sid = keys[key]; by_schema[sid] += 1
        encoded_rows.append(c._encoded([sid, [value[k] for k in schemas[sid]['positional_fields']]]) + b'\n')
    header = dict(format=c.FORMAT, source_model_SHA=SHA, producer_metadata=None, data_basename=c.DATA_NAME,
                  byte_limit=c.MAX_DATA, schemas=schemas, field_union=sorted({k for s in schemas for k in s['fields']}))
    raw = b''.join(encoded_rows); header_raw = c._encoded(header)
    producer = dict(path='/own_synthetic/' + c.DATA_NAME, bytes=len(raw), rows=len(rows), SHA=hashlib.sha256(raw).hexdigest(),
                    format=c.FORMAT, schema_path='/own_synthetic/' + c.SCHEMA_NAME,
                    schema_bytes=len(header_raw), schema_SHA=hashlib.sha256(header_raw).hexdigest(),
                    schema_count=len(schemas), rows_by_schema=by_schema, field_union=header['field_union'],
                    retained_total_bytes=len(raw) + len(header_raw), retained_byte_limit=c.MAX_DATA,
                    dropped_rows=dropped, attempted_rows=len(rows) + dropped, retention_limited=dropped > 0)
    commands = [r for r in rows if r.get('record_type') == c.TARGET]
    events = dict(natural_complete_intervals=sum(r.get('natural_complete_nonterminal_interval') is True for r in commands),
                  complete_kinematic_bounds_met=sum(r.get('complete_interval_bounds_fact') is True for r in commands),
                  complete_kinematic_false=sum(r.get('natural_complete_nonterminal_interval') is True and r.get('complete_interval_bounds_fact') is False for r in commands),
                  partial_intervals=sum(r.get('natural_complete_nonterminal_interval') is False for r in commands))
    final = dict(kind='OWN_SYNTHETIC_WORKER_FINAL_NOT_ACTUAL', role='W35', group_id='OWN_SYNTHETIC_GROUP',
                 passed_execution=True, num_envs=80, controls=1600, source_cache=dict(source_SHA=SHA),
                 skill=dict(original_RM70_interval_route_facts=dict(events=events, producer=producer)))
    return dict(raw=raw, schema=header, schema_raw=header_raw, producer=producer, final=final)


def consume(value, **kwargs):
    params = dict(schema=value['schema'], schema_raw=value['schema_raw'], producer=value['producer'],
                  case_metadata=value['final'], expected_group_id='OWN_SYNTHETIC_GROUP',
                  expected_role='W35', expected_source_sha=SHA, data_basename=c.DATA_NAME)
    params.update(kwargs)
    return c.stream_consume(io.BytesIO(value['raw']), **params)


class OriginalFactsTests(unittest.TestCase):
    def test_moving_standing_and_partial_are_separate_exact_n_N(self):
        rows = [row(), row(2, original_kinematic_bounds_met=False, complete_interval_bounds_fact=False),
                row(3, standing=True), row(4, standing=True, natural_complete_nonterminal_interval=False,
                                           complete_interval_bounds_fact=False, end_reason='window_end_partial')]
        result = consume(fixture(rows))
        self.assertEqual((result['groups']['moving']['n'], result['groups']['moving']['N']), (1, 2))
        self.assertEqual((result['groups']['standing']['n'], result['groups']['standing']['N']), (1, 1))
        self.assertEqual(result['groups']['standing']['partial'], 1)
        self.assertEqual(result['groups']['moving']['rate'], .5)
        self.assertTrue(result['all_original_complete_population_coverage_verified'])
        self.assertIsNone(result['relative'])
        self.assertIsNone(result['full_expert_skill_rate'])

    def test_standing_never_inferred_from_zero_vx(self):
        result = consume(fixture([row(sampled_BODY_command=[0, 0, 0])]))
        self.assertEqual(result['groups']['moving']['N'], 1)
        self.assertEqual(result['groups']['standing']['N'], 0)

    def test_original_true_standing_not_overridden_by_nonzero_vx(self):
        result = consume(fixture([row(standing=True, sampled_BODY_command=[3., 0, 0])]))
        self.assertEqual(result['groups']['standing']['N'], 1)

    def test_original_false_fact_not_recomputed_from_perfect_numeric_error(self):
        result = consume(fixture([row(original_kinematic_bounds_met=False, complete_interval_bounds_fact=False,
                                      along_nominal_error_m_s=0., cross_speed_m_s=0., signed_yaw_error_rad_s=0.)]))
        self.assertEqual(result['groups']['moving']['false'], 1)
        self.assertEqual(result['groups']['moving']['rate'], 0.)

    def test_all_partial_n_zero_means_rate_and_wilson_null(self):
        result = consume(fixture([row(natural_complete_nonterminal_interval=False, complete_interval_bounds_fact=False,
                                      terminated_before_reset=True, end_reason='original_reset')]))
        self.assertEqual(result['groups']['moving']['partial'], 1)
        self.assertIsNone(result['groups']['moving']['rate'])
        self.assertIsNone(result['groups']['moving']['wilson95'])
        self.assertEqual(result['groups']['moving']['terminated_before_reset_true'], 1)

    def test_missing_standing_is_unknown_not_moving(self):
        value = row(); del value['standing']
        result = consume(fixture([value]))
        self.assertEqual(result['groups']['unknown_standing']['unknown'], 1)
        self.assertEqual(result['groups']['moving']['N'], 0)

    def test_integer_bool_is_unknown(self):
        for field in c.BOOLS:
            with self.subTest(field=field):
                result = consume(fixture([row(**{field: 1})]))
                self.assertEqual(sum(g['N'] for g in result['groups'].values()), 0)
                self.assertIn('missing_or_nonBoolean_' + field, result['unknown_reason_counts'])

    def test_missing_each_UID_is_unknown(self):
        for field in c.IDENTITY + c.SOURCE_UID:
            with self.subTest(field=field):
                value = row(); del value[field]
                result = consume(fixture([value]))
                self.assertEqual(result['groups']['moving']['unknown'], 1)
                self.assertIsNone(result['groups']['moving']['rate'])

    def test_original_source_counter_signed_values_are_preserved_not_fabricated(self):
        result = consume(fixture([row(source_E1_episode=-1, original_command_counter=-1)]))
        self.assertEqual(result['groups']['moving']['N'], 1)

    def test_complete_terminal_or_unobserved_start_is_unknown(self):
        for values in ({'terminated_before_reset': True}, {'truncated_before_reset': True}, {'start_observed': False}):
            result = consume(fixture([row(**values)]))
            self.assertEqual(result['groups']['moving']['unknown'], 1)

    def test_original_fact_and_complete_kin_contradiction_unknown(self):
        result = consume(fixture([row(complete_interval_bounds_fact=False)]))
        self.assertEqual(result['groups']['moving']['unknown'], 1)

    def test_partial_end_keeps_original_reason_and_flags(self):
        result = consume(fixture([row(natural_complete_nonterminal_interval=False, complete_interval_bounds_fact=False,
                                      end_reason='original_reset', truncated_before_reset=True,
                                      original_terminal_reason_time_out=True)]))
        self.assertEqual(result['groups']['moving']['end_reasons']['original_reset'], 1)
        self.assertEqual(result['original_terminal_reason_true_counts']['original_terminal_reason_time_out'], 1)

    def test_route_rows_are_not_skill_denominator(self):
        route = dict(source_SHA=SHA, record_type='same_episode_original_catalog_route', env_id=0,
                     observed_nonterminal_catalog_goal_fact=True)
        result = consume(fixture([route, row()]))
        self.assertEqual(result['groups']['moving']['N'], 1)
        self.assertEqual(result['raw_rows']['ignored_record_types']['same_episode_original_catalog_route'], 1)

    def test_duplicate_UID_invalidates_prior_not_first_success_preferred(self):
        result = consume(fixture([row(), row(original_kinematic_bounds_met=False, complete_interval_bounds_fact=False)]))
        self.assertEqual(result['groups']['moving']['N'], 0)
        self.assertEqual(result['groups']['moving']['unknown'], 2)
        self.assertEqual(result['UID_provenance']['duplicate_rows'], 1)

    def test_separate_episode_or_segment_not_stitched_or_deduplicated(self):
        result = consume(fixture([row(), row(episode_uid=1), row(same_UID_segment=1)]))
        self.assertEqual(result['groups']['moving']['N'], 3)
        self.assertEqual(result['UID_provenance']['duplicate_rows'], 0)

    def test_bad_tick_span_is_unknown_not_repaired(self):
        result = consume(fixture([row(last_physics_tick=9)]))
        self.assertEqual(result['groups']['moving']['unknown'], 1)


class IntegrityTests(unittest.TestCase):
    def test_drop_count_not_allocated_to_standing_or_moving(self):
        result = consume(fixture([row()], dropped=4))
        self.assertEqual(result['groups']['moving']['rate'], 1.)
        self.assertEqual(result['dropped_rows'], 4)
        self.assertIsNone(result['drops_moving_standing_allocation'])
        self.assertIsNone(result['groups']['moving']['all_original_complete_population_rate'])

    def test_missing_case_binding_all_unknown(self):
        result = consume(fixture([row()]), case_metadata=None)
        self.assertEqual(result['groups']['moving']['unknown'], 1)
        self.assertFalse(result['grading_integrity_verified'])

    def test_wrong_header_or_row_model_source_not_graded(self):
        value = fixture([row(source_SHA='b' * 64)])
        result = consume(value)
        self.assertEqual(result['groups']['moving']['unknown'], 1)
        value = fixture([row()]); value['schema']['source_model_SHA'] = 'b' * 64
        value['schema_raw'] = c._encoded(value['schema'])
        value['producer']['schema_SHA'] = hashlib.sha256(value['schema_raw']).hexdigest()
        result = consume(value)
        self.assertFalse(result['grading_integrity_verified'])

    def test_wrong_group_or_role_case_not_graded(self):
        for key, bad in (('group_id', 'OTHER'), ('role', 'E3')):
            value = fixture([row()]); value['final'][key] = bad
            self.assertEqual(consume(value)['groups']['moving']['N'], 0)

    def test_producer_raw_hash_mismatch_suppresses_verified_rates(self):
        value = fixture([row()]); value['producer']['SHA'] = 'b' * 64
        result = consume(value)
        self.assertEqual(result['groups']['moving']['N'], 1)
        self.assertIsNone(result['groups']['moving']['rate'])
        self.assertFalse(result['grading_integrity_verified'])

    def test_schema_hash_mismatch_suppresses_rates(self):
        value = fixture([row()]); value['producer']['schema_SHA'] = 'b' * 64
        self.assertIsNone(consume(value)['groups']['moving']['rate'])

    def test_nested_bool_rows_by_schema_is_not_integer_one(self):
        value = fixture([row()]); value['producer']['rows_by_schema'] = [True]
        self.assertFalse(consume(value)['grading_integrity_verified'])

    def test_original_event_pooled_mismatch_detected_without_drops(self):
        value = fixture([row()]); value['final']['skill']['original_RM70_interval_route_facts']['events']['natural_complete_intervals'] = 2
        self.assertFalse(consume(value)['grading_integrity_verified'])

    def test_missing_finish_metadata_keeps_observed_n_N_but_not_attested_rate(self):
        result = consume(fixture([row()]), producer=None)
        self.assertEqual((result['groups']['moving']['n'], result['groups']['moving']['N']), (1, 1))
        self.assertIsNone(result['groups']['moving']['rate'])
        self.assertFalse(result['grading_integrity_verified'])
        self.assertFalse(result['all_original_complete_population_coverage_verified'])
        self.assertIsNone(result['dropped_rows'])

    def test_missing_exact_schema_bytes_keeps_attestation_gap(self):
        result = consume(fixture([row()]), schema_raw=None)
        self.assertEqual(result['groups']['moving']['N'], 1)
        self.assertIsNone(result['groups']['moving']['rate'])
        self.assertIn('exact_schema_bytes_unavailable', result['metadata_evidence_gaps'])

    def test_one_binary_pass_no_seek_or_read_all(self):
        class Once(io.BytesIO):
            def seek(self, *a): raise AssertionError('no seek')
            def read(self, *a): raise AssertionError('no read-all')
        value = fixture([row()])
        result = c.stream_consume(Once(value['raw']), schema=value['schema'], schema_raw=value['schema_raw'],
                                 producer=value['producer'], case_metadata=value['final'], expected_role='W35',
                                 expected_source_sha=SHA, expected_group_id='OWN_SYNTHETIC_GROUP')
        self.assertEqual(result['raw_rows']['SHA256'], hashlib.sha256(value['raw']).hexdigest())

    def test_duplicate_schema_keys_and_bool_schema_id_rejected(self):
        with self.assertRaises(c.ConsumerError): c._loads(b'{"a":1,"a":2}')
        value = fixture([row()]); value['schema']['schemas'][0]['schema_id'] = True
        with self.assertRaises(c.ConsumerError): consume(value)

    def test_nonfinite_JSON_and_malformed_positional_are_unknown(self):
        value = fixture([]); value['raw'] = b'[true,[]]\n[0,[NaN]]\n'
        value['producer'].update(bytes=len(value['raw']), rows=2, SHA=hashlib.sha256(value['raw']).hexdigest(), attempted_rows=2,
                                 retained_total_bytes=len(value['raw']) + len(value['schema_raw']))
        result = consume(value)
        self.assertEqual(result['groups']['unknown_standing']['unknown'], 2)
        self.assertFalse(result['grading_integrity_verified'])

    def test_missing_record_type_is_unknown(self):
        value = row(); del value['record_type']
        result = consume(fixture([value]))
        self.assertEqual(result['groups']['unknown_standing']['unknown'], 1)

    def test_overlong_line_drained_once_and_hash_preserved(self):
        value = fixture([]); value['raw'] = b'x' * 220 + b'\n'
        with patch.object(c, 'MAX_LINE', 32):
            result = consume(value, producer=None)
        self.assertEqual(result['raw_rows']['lines'], 1)
        self.assertEqual(result['raw_rows']['SHA256'], hashlib.sha256(value['raw']).hexdigest())
        self.assertEqual(result['format_error_counts']['line_too_long'], 1)

    def test_wilson_is_descriptive_and_n0_null(self):
        self.assertIsNone(c.wilson95(0, 0))
        low, high = c.wilson95(1, 1)
        self.assertLess(low, 1.); self.assertEqual(high, 1.)


class CLISourceTests(unittest.TestCase):
    def own_case(self):
        directory = HERE / 'CPU_SYNTHETIC_CASES_V1'; directory.mkdir(exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix='own_new_', dir=directory))
        value = fixture([row(), row(2, standing=True, original_kinematic_bounds_met=False, complete_interval_bounds_fact=False)])
        data, schema = root / c.DATA_NAME, root / c.SCHEMA_NAME
        value['producer'].update(path=str(data), schema_path=str(schema))
        data.write_bytes(value['raw']); schema.write_bytes(value['schema_raw'])
        (root / 'FINAL.json').write_bytes(c._encoded(value['final']))
        return root

    def arguments(self, root):
        return ['--input', str(root / c.DATA_NAME), '--case-root', str(root), '--expected-role', 'W35',
                '--expected-source-sha', SHA, '--expected-group', 'OWN_SYNTHETIC_GROUP', '--output', str(root / 'NEW_GRADE.json')]

    def test_CLI_new_own_synthetic_positional_case(self):
        root = self.own_case()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()): rc = c.main(self.arguments(root))
        self.assertEqual(rc, 0)
        result = json.loads((root / 'NEW_GRADE.json').read_text('utf8'))
        self.assertTrue(result['all_original_complete_population_coverage_verified'])
        self.assertEqual(result['input_binding']['data_opens'], 1)
        self.assertEqual(result['groups']['moving']['n'], 1)
        self.assertEqual(result['groups']['standing']['false'], 1)

    def test_CLI_no_overwrite_and_wrong_group_before_raw_open(self):
        root = self.own_case(); args = self.arguments(root)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(c.main(args), 0)
            self.assertEqual(c.main(args), 2)
        root = self.own_case(); args = self.arguments(root); args[args.index('OWN_SYNTHETIC_GROUP')] = 'WRONG'
        with patch.object(c, 'stream_consume', side_effect=AssertionError('raw must not be opened for wrong group')):
            with redirect_stderr(io.StringIO()): self.assertEqual(c.main(args), 2)

    def test_CLI_input_outside_explicit_own_case_is_blocked_before_consume(self):
        root, other = self.own_case(), self.own_case()
        args = self.arguments(root); args[args.index('--input') + 1] = str(other / c.DATA_NAME)
        with patch.object(c, 'stream_consume', side_effect=AssertionError('outside case must not be consumed')):
            with redirect_stderr(io.StringIO()): self.assertEqual(c.main(args), 2)

    def test_exact_original_source_bytes_and_line_evidence(self):
        for name, pin in c.SOURCE_PINS.items():
            raw = (SOURCE_ROOT / name).read_bytes()
            self.assertEqual(len(raw), pin['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), pin['SHA256'])
        original = (SOURCE_ROOT / 'rm70_intervals227.py').read_text('utf8')
        self.assertIn('self.stand[ids]=cmd.is_standing_env[ids]', original)
        self.assertIn('complete=lookup[ids]&self.known[ids]&~self.term[ids]&~self.timeout[ids]', original)
        self.assertIn('complete_interval_bounds_fact=complete&kin', original)
        self.assertIn("self.rows.append(dict(**extra,**{k:v[i] for k,v in cpu.items()}))", original)

    def test_consumer_imports_stdlib_only_and_has_no_model_or_runtime_import(self):
        tree = ast.parse((HERE / 'w35_original_row_split_consumer_v1.py').read_text('utf8'))
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        self.assertFalse(set(imports).intersection({'torch', 'numpy', 'isaaclab', 'isaacsim', 'rm70_intervals227', 'positional_rows227'}))


if __name__ == '__main__':
    start = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = dict(kind='OWN_SYNTHETIC_STDLIB_ONLY_W35_ORIGINAL_ROW_SPLIT_V1', tests=result.testsRun,
                   passed=result.wasSuccessful(), failures=len(result.failures), errors=len(result.errors),
                   seconds=time.perf_counter() - start, actual_JSONL_files_read=0, original_PT_NPZ_files_read=0,
                   SDK_Torch_GPU_native_resource_account_operations=0, original_observer_or_eval_files_changed=False)
    (HERE / 'CPU_TEST_RESULTS_V1.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
