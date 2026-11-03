"""Eight stdlib metadata/toy/AST checks. No target module is imported or run."""
import ast
from collections import deque
import copy
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
PINS = json.loads((HERE / 'SOURCE_PINS.json').read_text(encoding='utf-8'))
SCHEMA = json.loads((HERE / 'schema_example.json').read_text(encoding='utf-8'))


def definitions(raw):
    found = {}
    def walk(node, prefix=''):
        for child in getattr(node, 'body', []):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                found[name] = child
                walk(child, name + '.')
    walk(ast.parse(raw.decode('utf-8')))
    return found


def source(key):
    return Path(PINS['sources'][key]['path']).read_bytes()


def envelopes(value):
    if isinstance(value, dict):
        if value.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1':
            yield value
        else:
            for item in value.values():
                yield from envelopes(item)
    elif isinstance(value, list):
        for item in value:
            yield from envelopes(item)


def toy_semantic_select(role, original_shape, values, rows):
    """Lists only: illustrates semantic-role selection, NOT a tensor adapter."""
    if role == 'ENV_ROWS_WITNESS':
        if original_shape[0] != 80 or len(rows) > 8:
            raise ValueError('toy witness shape/cap')
        return [values[i] for i in rows]
    if role == 'ENV_IDS_FULL':
        if len(values) > 80:
            raise ValueError('toy ids cap')
        return list(values)
    if role == 'TERMINAL_BOOL_FULL':
        if original_shape != [80] or any(type(x) is not bool for x in values):
            raise ValueError('toy terminal shape/dtype')
        return list(values)
    raise ValueError('unknown semantic role stays UNKNOWN, no shape inference')


class ProvenanceDesignTests(unittest.TestCase):
    def test_01_whole_source_and_complete_definition_pins(self):
        self.assertEqual(len(PINS['sources']), 22)
        definition_count = 0
        for key, row in PINS['sources'].items():
            raw = source(key)
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (row['bytes'], row['sha256']))
            if not row.get('complete_definitions'):
                continue
            nodes = definitions(raw)
            for pin in row['complete_definitions']:
                node = nodes[pin['qualname']]
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                part = b''.join(raw.splitlines(keepends=True)[start - 1:node.end_lineno])
                self.assertEqual((start, node.end_lineno), (pin['start_line'], pin['end_line']))
                self.assertEqual(hashlib.sha256(part).hexdigest(), pin['complete_source_sha256'])
                self.assertEqual(hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest(), pin['AST_sha256'])
                definition_count += 1
        self.assertEqual(definition_count, 35)
        self.assertEqual(PINS['sources']['science']['sha256'], '942a4fc5b5c77d02c86dbf815ba4b0a71f4bb0116f4738a70a0efba74c69a7d3')
        self.assertEqual(PINS['sources']['queue_diagnostic']['sha256'], 'b9a83cb124b5d202dfaaf7e10420eb8e447f5111fa34676c630ebb3762c21c07')

    def test_02_known_k80_loss_and_role_specific_full_ids(self):
        raw = source('B2')
        node = definitions(raw)['tensor_snapshot_adapter']
        text = ast.get_source_segment(raw.decode(), node)
        self.assertIn('x.shape[0] == num_envs', text)
        self.assertIn('x.index_select(0, row_ids)', text)
        witness = SCHEMA['witness_rows']
        for k in (0, 1, 79, 80):
            ids = list(range(k))
            old = ids[:8] if k == 80 else ids
            new = toy_semantic_select('ENV_IDS_FULL', [k], ids, witness)
            self.assertEqual(new, ids)
            if k == 80:
                self.assertEqual(len(old), 8)
                self.assertEqual(len(new), 80)
        self.assertEqual(toy_semantic_select('ENV_ROWS_WITNESS', [80], list(range(80)), witness), witness)
        with self.assertRaises(ValueError):
            toy_semantic_select('UNKNOWN', [80], list(range(80)), witness)
        with self.assertRaises(ValueError):
            toy_semantic_select('ENV_IDS_FULL', [81], list(range(81)), witness)

    def test_03_dtype_shape_row_mapping_survive_json(self):
        restored = json.loads(json.dumps(SCHEMA))
        self.assertEqual(restored, SCHEMA)
        tensors = list(envelopes(restored))
        self.assertGreater(len(tensors), 10)
        dtypes = set()
        for tensor in tensors:
            self.assertTrue(set(SCHEMA['required_tensor_envelope_fields']) <= set(tensor))
            self.assertEqual(tensor['evidence_level'], 'SYNTHETIC_METADATA_TOY_NOT_ACTUAL_CAPTURE')
            self.assertEqual(len(tensor['values']), tensor['retained_shape'][0])
            dtypes.add(tensor['original_dtype'])
            role = tensor['semantic_role']
            if role == 'ENV_ROWS_WITNESS':
                self.assertEqual(tensor['original_shape'][0], 80)
                self.assertEqual(tensor['retained_shape'][0], 8)
                self.assertEqual(tensor['row_mapping']['env_ids'], list(range(8)))
            elif role == 'ENV_IDS_FULL':
                self.assertIsNone(tensor['source_env_axis'])
                self.assertEqual(tensor['original_shape'], tensor['retained_shape'])
            else:
                self.assertEqual(role, 'TERMINAL_BOOL_FULL')
                self.assertEqual(tensor['original_shape'], [80])
                self.assertEqual(tensor['retained_shape'], [80])
        self.assertTrue({'torch.float16', 'torch.float32', 'torch.float64', 'torch.bfloat16', 'torch.int32', 'torch.int64', 'torch.bool'} <= dtypes)
        before = definitions(source('observer'))['materialize']
        self.assertIn('.tolist()', ast.unparse(before))
        self.assertNotIn('original_dtype', ast.unparse(before))

    def test_04_original_two_clean16_slots_not_mid_actor35(self):
        slots = SCHEMA['toy_control']['normal_slots']
        self.assertEqual([slot['slot'] for slot in slots], ['MID', 'END'])
        self.assertEqual([slot['source_clock']['physics_tick'] for slot in slots], [4, 8])
        self.assertEqual([slot['source_clock']['feedback_tick'] for slot in slots], [1, 2])
        for slot in slots:
            self.assertEqual(sum(ch['width'] for ch in slot['channels'].values()), 16)
            self.assertEqual(len(slot['channels']), 5)
            self.assertEqual(slot['channels']['base_ang_vel']['scale'], .5)
            self.assertEqual(slot['channels']['leg_vel']['scale'], .1)
            self.assertTrue(slot['source_clock']['normal_100hz_slot'])
            self.assertNotIn('actor35_original_buffer', slot)
        for key in ('mid_remaining19', 'mid_full_clean35', 'mid_actor35', 'terminal_clean35', 'initial_clean0'):
            self.assertTrue(SCHEMA['unknowns'][key].startswith('UNKNOWN'))
        self.assertEqual(SCHEMA['retention']['max_normal_channel_records'], 128 * 2 * 5)
        self.assertEqual(SCHEMA['retention']['max_clean16_witness_scalars'], 128 * 2 * 8 * 16)

    def test_05_full_flags_and_actual_callback_ids_not_witness_only(self):
        pack = SCHEMA['toy_control']['boundary_pack']
        term = pack['pre_reset']['term']
        self.assertTrue(term['values'][79])
        self.assertFalse(any(term['values'][i] for i in SCHEMA['witness_rows']))
        self.assertEqual(len(term['values']), 80)
        self.assertEqual(pack['reset']['input_ids']['values'], [79])
        self.assertEqual(pack['reset']['input_ids']['original_dtype'], 'torch.int32')
        self.assertEqual(pack['post_return']['term']['values'], term['values'])
        self.assertEqual(pack['post_return']['trunc']['values'], pack['pre_reset']['trunc']['values'])
        self.assertEqual(pack['worker_control_index'], pack['reset']['source_clock']['worker_control_index'])
        self.assertFalse(pack['event_ids_are_clock'])
        self.assertFalse(pack['pre_reset']['source_clock']['normal_100hz_slot'])
        self.assertEqual(pack['reset']['nonwitness_episode_values'], 'UNKNOWN_NOT_CAPTURED')
        absent = copy.deepcopy(pack['reset'])
        absent.update(callback_status='NOT_OBSERVED', input_ids=None)
        self.assertIsNone(absent['input_ids'])
        self.assertNotEqual(absent['input_ids'], [])
        terminal_call = ast.unparse(definitions(source('SDK_step'))['ManagerBasedRLEnv.step'])
        self.assertIn('.nonzero(as_tuple=False).squeeze(-1).int()', terminal_call)
        self.assertIn('self._reset_idx(reset_env_ids)', terminal_call)

    def test_06_independent_rings_lose_middle_edge_atomic_pack_does_not(self):
        terminal_ring = deque(maxlen=4)
        reset_ring = deque(maxlen=4)
        packs = []
        for control in range(8):
            terminal_ring.append(dict(control=control, terminal_event='t' + str(control)))
            reset = dict(control=control, reset_event='r' + str(control), ids=[79]) if control == 2 else None
            if reset is not None:
                reset_ring.append(reset)
            packs.append(dict(control=control, terminal_event='t' + str(control), reset=reset))
        self.assertEqual([item['control'] for item in terminal_ring], [4, 5, 6, 7])
        self.assertEqual([item['control'] for item in reset_ring], [2])
        self.assertFalse({item['control'] for item in terminal_ring} & {item['control'] for item in reset_ring})
        self.assertEqual(packs[2]['reset']['ids'], [79])
        self.assertEqual(packs[2]['terminal_event'], 't2')
        self.assertEqual(SCHEMA['retention']['max_boundary_packs'], 128)
        self.assertEqual(SCHEMA['retention']['other_tensors_max_rows'], 8)
        self.assertIn('UNKNOWN', SCHEMA['retention']['overflow'])

    def test_07_rng_claim_remains_limited_source_not_full_state(self):
        claim = SCHEMA['rng']
        self.assertEqual(claim['full_state_equality'], 'UNKNOWN_NOT_CAPTURED')
        self.assertEqual(claim['bias_and_delay_reset_draw_counters'], 'NOT_CAPTURED')
        self.assertEqual(claim['new_rng_or_state_calls'], 0)
        self.assertEqual(claim['new_getter_obs_reset_calls'], 0)
        feedback = definitions(source('feedback'))['feedback']
        funcs = [ast.unparse(node.func) for node in ast.walk(feedback) if isinstance(node, ast.Call)]
        self.assertEqual(funcs.count('sensor_state(env).apply'), 1)
        self.assertEqual(funcs.count('delay_state(env).apply'), 1)
        own = ast.parse(Path(__file__).read_text(encoding='utf-8'))
        imports = {node.names[0].name.split('.')[0] for node in ast.walk(own) if isinstance(node, ast.Import)}
        imports.update(node.module.split('.')[0] for node in ast.walk(own) if isinstance(node, ast.ImportFrom))
        self.assertTrue(imports <= {'ast', 'collections', 'copy', 'hashlib', 'json', 'pathlib', 'unittest'})
        self.assertFalse(SCHEMA['implemented'])
        self.assertEqual(SCHEMA['Gate1'], 'UNKNOWN')
        self.assertFalse(SCHEMA['stage2_GO'])

    def test_08_binding_dof_and_original_adapter_stats_are_separate_evidence(self):
        meta = SCHEMA['binding_metadata']
        self.assertEqual(meta['source_function'], 'verify_actuation_binding(env, api, role_source_rows)')
        self.assertEqual(meta['definition_source_key'], 'observer')
        self.assertFalse(meta['current_joint_ids_retained'])
        self.assertFalse(meta['current_sdk_setter_source_qualified'])
        self.assertEqual(meta['proposed_scalar_fields'], ['calls', 'formula_max_error', 'collect'])
        self.assertEqual(meta['statistics_evidence'], 'SOURCE_AVAILABLE_NOT_PUBLISHED_IN_A2')
        self.assertIn('values UNKNOWN', meta['joint_ids']['stored_tensor'])
        self.assertIn('known_DOF_ids', meta['strict_join_requires'])
        self.assertIn('actual_parent_scope', meta['strict_join_requires'])
        self.assertEqual(meta['observer_independent_readback'], 'UNKNOWN_NOT_CAPTURED')
        self.assertEqual(meta['external_physical_effect'], 'UNKNOWN')
        self.assertEqual(meta['C2_API'], 'UNKNOWN_NOT_ACCESSED')
        nodes = definitions(source('D4'))
        apply_text = ast.unparse(nodes['PhysicalActionDelayAdapter._wrap.apply'])
        self.assertIn('this._joint_ids', apply_text)
        self.assertIn('adapter.formula_max_error', apply_text)
        self.assertIn('adapter.calls[key] += 1', apply_text)
        self.assertLess(apply_text.index('assert error <= 1e-06'), apply_text.index('adapter.calls[key] += 1'))
        current = ast.unparse(definitions(source('observer'))['verify_actuation_binding'])
        self.assertNotIn('_joint_ids', current)
        self.assertIn('same_asset_instance_id', current)
        self.assertIn('sdk_target_writer_qualified=False', current)


if __name__ == '__main__':
    unittest.main(verbosity=2)
