"""Five NEW SOURCE-only checks: AST/compile/full-file pins; NO fixture or injected module import."""
from pathlib import Path
import ast
import hashlib
import json
import unittest

HERE = Path(__file__).resolve().parent
R = HERE.parent
RUNTIME = dict(queue='discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_physics_queue.py',
    actuation='source_phase1_actuation_clock_scope_v2/actuation_tap_v2.py',
    codec='source_phase1_typed_capture_codec_v1/typed_capture_codec.py',
    observer='source_phase1_typed_native_capture_v1/phase1_capture_observer.py',
    field='source_phase1_passive_sensor_capture_v4/field_snapshot.py',
    contract='source_phase1_typed_native_capture_v1/phase1_capture_contract.py')
SEALS = {
    'source_phase1_typed_native_capture_v1/SOURCE_SEAL.json':'f92384f7943d27a4d588316cfba129011ca47851571ff252040df4c740424966',
    'source_phase1_actuation_clock_scope_v2/SOURCE_SEAL.json':'105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b',
    'source_phase1_typed_capture_codec_v1/SOURCE_SEAL.json':'2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219',
    'source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json':'81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3'}
EXPECTED = dict(queue='a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8',
    actuation='ec10b09b77548c560611e641d685e2cee029c9778ff8c8852a8bf070243bd95d',
    codec='77c007fb0b17088b54bb0c115913159c7a9bf99f50f29a0b203dea483f0d1ee4',
    observer='944c6e0cbc91e881c8c205bc78ee3b1aecf8ade877b7b97711dd6acebe93569e',
    contract='cc85300dfe62fbb33bb7c072b2adbc40d865c08ac45df663425ca658bd74e0a3')
REFERENCES = ['source_phase1_c2_real_cpu_fixture_v1/real_cpu_fixture_c2.py',
              'source_phase1_c2_real_cpu_fixture_v1/c2_cpu_fixture_wrapper.py']


def identity(path):
    raw = path.read_bytes()
    return dict(path=path.as_posix(), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def build_pins():
    sources = {key: identity(R/name) for key, name in RUNTIME.items()}
    seals = {name: identity(R/name) for name in SEALS}
    for name, expected in SEALS.items(): assert seals[name]['sha256'] == expected
    for key, expected in EXPECTED.items(): assert sources[key]['sha256'] == expected
    field = json.loads((R/'source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json').read_bytes())['files']['field_snapshot.py']
    assert (sources['field']['bytes'], sources['field']['sha256']) == (field['bytes'], field['sha256'])
    index = json.loads((R/'source_phase1_typed_native_capture_v1/CAPTURE_SOURCE_INDEX.json').read_bytes())
    row = index['all_actuation_original_sources'][RUNTIME['queue']]
    assert (sources['queue']['bytes'], sources['queue']['sha256']) == (row['bytes'], row['sha256'])
    return dict(kind='TYPED_C2_CPU_FIXTURE_SOURCE_PINS_V1', runtime_sources=sources,
                readonly_upstream_seals=seals, design_references=[identity(R/name) for name in REFERENCES],
                full_module_injection_only=True, actual_runtime_execution=False)


class SourceOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (HERE/'typed_c2_cpu_fixture.py').read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.text)
        cls.fn = next(n for n in cls.tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_fixture')
        cls.calls = [n for n in ast.walk(cls.fn) if isinstance(n, ast.Call)]

    def test_01_full_original_source_pins(self):
        pins = build_pins()
        self.assertEqual(pins, json.loads((HERE/'SOURCE_PINS.json').read_bytes()))
        self.assertEqual(pins['runtime_sources']['queue']['bytes'], 8511)
        for row in pins['runtime_sources'].values():
            compile(Path(row['path']).read_text(encoding='utf-8'), row['path'], 'exec', dont_inherit=True)
        self.assertEqual(len(pins['runtime_sources']), 6)

    def test_02_small_compile_and_exact_injection_signature(self):
        self.assertTrue(150 <= len(self.text.splitlines()) <= 220)
        self.assertEqual([a.arg for a in self.fn.args.args], ['torch_module','PhysicsActionQueue','actuation_module','codec_module','observer_module','field_module'])
        self.assertEqual(self.fn.args.defaults, [])
        compile(self.tree, str(HERE/'typed_c2_cpu_fixture.py'), 'exec', dont_inherit=True)
        imports = [n for n in ast.walk(self.tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertEqual(sorted((n.module if isinstance(n, ast.ImportFrom) else n.names[0].name) for n in imports), ['hashlib','json','pathlib','random'])
        self.assertFalse(any(isinstance(n, ast.If) and '__name__' in ast.unparse(n.test) for n in self.tree.body))

    def test_03_full_functions_not_old_suites_or_sdk_gate(self):
        attrs = {n.func.attr for n in self.calls if isinstance(n.func, ast.Attribute)}
        self.assertTrue({'install_actuation_tap','WindowRetention','add','report','typed_c2_event','validate_owned','materialize','FieldSnapshot','state_dict','drain','close'} <= attrs)
        names = {n.func.id for n in self.calls if isinstance(n.func, ast.Name)}
        self.assertIn('PhysicsActionQueue', names)
        self.assertFalse({'eval','exec','compile','__import__'} & names)
        self.assertNotIn('verify_actuation_binding', self.text)
        for old in ('run_c2_cpu_fixture(', 'derived_fixture.run_fixture', 'real_cpu_fixture_c2', 'import torch', 'importlib', 'set_rng_state', 'set_default_dtype'):
            self.assertNotIn(old, self.text)

    def test_04_declared_known_group_ownership_and_fixed_loop(self):
        for text in ('range(64)', "'legs': 2, 'wheels': 1", "t.tensor([78, 79]", "'lag_steps'", "2**53 + 7", "same-tick submit", "same-tick apply", "envelope['values'] is value", '.data_ptr()', '._version', "allowed_roles=('QUEUE_GROUP_FULL',)", 'set(c2.QUEUE_FIELDS)', 'view(torch.uint8)', 'random.getstate()', 't.get_rng_state()', 'retained_owned'):
            self.assertIn(text, self.text)
        observer = ast.parse((R/RUNTIME['observer']).read_text(encoding='utf-8'))
        adopt = next(n for n in observer.body if isinstance(n, ast.FunctionDef) and n.name == 'adopt_queue_owned')
        tensor_ops = {n.func.attr for n in ast.walk(adopt) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertFalse({'clone','detach','index_select','float','double','to','cpu'} & tensor_ops)

    def test_05_explicit_unknown_clocks_shapes_errors_and_serde(self):
        for text in ("om.stored_clock(tapped)", "'sim_time_us' not in", "['control_slot'] == 'UNKNOWN'", "typed['tick'] == raw['tick']", "'NON_TERM_SETTER'", "'SAME_ASSET_TERM_APPLY_CONTEXT'", "typed['args'][0]['values'] == 'UNKNOWN'", "typed['setter']['joint_ids']['values'] == 'UNKNOWN'", "!= 'ENV_IDS_FULL'", 'exception_identity', 'id(errors[-1])', 'except cm.CaptureError:', 'except ValueError:', 'exc is fault', '[0, 1, 62, 63]', 'UNKNOWN_UNRETAINED', 'json.loads(text) == wire', 'type(v) is int', 'type(v) is bool'):
            self.assertIn(text, self.text)
        self.assertNotIn("sim_time_us=", self.text)
        self.assertLess(self.text.index("tap.close()['restored']"), self.text.index('wire = codec.materialize('))
