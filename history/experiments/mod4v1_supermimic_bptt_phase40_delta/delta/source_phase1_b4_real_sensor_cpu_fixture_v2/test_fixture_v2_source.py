"""Five NEW narrow SOURCE checks; never import/execute either CPU fixture."""
import ast
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
PINS = json.loads((HERE / 'SOURCE_PINS.json').read_text(encoding='utf-8'))
OLD = Path(PINS['V1_frozen_source']['directory'])
A = b"self.templates = {k: t.arange(80 * w, dtype=t.float64, device='cpu').reshape(80, w) * .001"
B = b"self.templates = {k: t.arange(80 * w, dtype=t.float32, device='cpu').reshape(80, w) * .001"
C = b"assert envelope['original_dtype'] == str(source.dtype) == 'torch.float64'"
D = b"assert envelope['original_dtype'] == str(source.dtype) == 'torch.float32'"


def info(path):
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def differences(left, right, path='Module'):
    if type(left) is not type(right):
        return [(path, left, right)]
    if isinstance(left, ast.AST):
        result = []
        for name, value in ast.iter_fields(left):
            result.extend(differences(value, getattr(right, name), path + '.' + name))
        return result
    if isinstance(left, list):
        if len(left) != len(right):
            return [(path, left, right)]
        result = []
        for i, (a, b) in enumerate(zip(left, right)):
            result.extend(differences(a, b, path + '[' + str(i) + ']'))
        return result
    return [] if left == right else [(path, left, right)]


class NarrowV2SourceTests(unittest.TestCase):
    def test01_compile_only_and_exact_same_injection_API(self):
        raw = (HERE / 'cpu_fixture.py').read_bytes()
        tree = ast.parse(raw.decode('utf-8'))
        compile(tree, str(HERE / 'cpu_fixture.py'), 'exec')  # compile only; no exec
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_fixture']
        self.assertEqual(len(functions), 1)
        args = functions[0].args
        self.assertEqual([a.arg for a in args.args], ['torch_module', 'real_sensor_class', 'real_delay_class'])
        self.assertEqual([a.arg for a in args.kwonlyargs], ['codec_module', 'passive_module', 'field_module', 'dependency_module'])
        self.assertEqual(args.defaults, [])
        self.assertEqual(args.kw_defaults, [None] * 4)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        self.assertEqual(imports, ['collections', 'hashlib', 'json', 'pathlib', 'random', 'types'])
        self.assertFalse(any(isinstance(n, ast.Constant) and n.value == '__main__' for n in ast.walk(tree)))
        self.assertEqual(len(raw.splitlines()), 490)

    def test02_two_literal_full_bytes_and_two_AST_leaf_changes_only(self):
        old, new = (OLD / 'cpu_fixture.py').read_bytes(), (HERE / 'cpu_fixture.py').read_bytes()
        self.assertEqual(old.count(A), 1)
        self.assertEqual(old.count(C), 1)
        self.assertEqual(new, old.replace(A, B, 1).replace(C, D, 1))
        self.assertEqual(new.replace(B, A, 1).replace(D, C, 1), old)
        self.assertEqual(len(new), len(old))
        changed_lines = [(i, a, b) for i, (a, b) in enumerate(zip(old.splitlines(), new.splitlines()), 1) if a != b]
        self.assertEqual([i for i, _, _ in changed_lines], [115, 307])
        diff = differences(ast.parse(old.decode()), ast.parse(new.decode()))
        self.assertEqual(len(diff), 2)
        self.assertEqual([(a, b) for _, a, b in diff], [('float64', 'float32'), ('torch.float64', 'torch.float32')])
        self.assertTrue(diff[0][0].endswith('.attr'))
        self.assertTrue(diff[1][0].endswith('.value'))
        self.assertEqual(PINS['source_derivation']['fixture_change_count'], 2)

    def test03_original_sensor_dtype_support_no_production_or_RNG_patch(self):
        row = PINS['original_complete_cpu_sources']['sensor_mild_math.py']
        source = Path(row['path']).read_text(encoding='utf-8')
        tree = ast.parse(source)
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SensorCorruption')
        apply = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'apply')
        calls = [n for n in ast.walk(apply) if isinstance(n, ast.Call)]
        rand = [n for n in calls if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'torch' and n.func.attr == 'rand']
        self.assertEqual(len(rand), 1)
        self.assertEqual(rand[0].lineno, 36)
        self.assertEqual([k.arg for k in rand[0].keywords], ['device', 'generator'])
        zeros = [n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == 'zeros_like']
        self.assertEqual(len(zeros), 1)
        self.assertEqual(ast.dump(zeros[0].args[0]), "Name(id='value', ctx=Load())")
        self.assertEqual(info(Path(row['path'])), {k: row[k] for k in ('bytes', 'sha256')})
        new = ast.parse((HERE / 'cpu_fixture.py').read_text(encoding='utf-8'))
        forbidden = {'set_default_dtype', 'set_default_tensor_type', 'set_rng_state', 'manual_seed'}
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in forbidden for n in ast.walk(new)))
        self.assertEqual(sorted((n.lineno, n.attr) for n in ast.walk(new) if isinstance(n, ast.Attribute) and n.attr == 'float64'), [(119, 'float64'), (120, 'float64'), (380, 'float64'), (390, 'float64')])

    def test04_all_old_case_denominators_and_unknowns_preserved(self):
        old = json.loads((OLD / 'FIXTURE_CONTRACT.json').read_text(encoding='utf-8'))
        new = json.loads((HERE / 'FIXTURE_CONTRACT.json').read_text(encoding='utf-8'))
        for field in ('entry', 'dependency_binding', 'functional_cases_parent_only', 'outside_export', 'unknowns_preserved', 'child_actual_Torch_CPU'):
            self.assertEqual(new[field], old[field], field)
        self.assertEqual(new['software_scope'], old['software_scope'])
        self.assertEqual(new['functional_cases_parent_only']['main64']['normal_channel_records'], 640)
        self.assertEqual(new['functional_cases_parent_only']['main64']['controls_per_path'], 64)
        self.assertEqual(new['outside_export']['JSON_int64_precision_probe'], 2**60 + 7)
        failure = new['V1_failure_context']
        self.assertEqual(failure['authority'], 'PARENT_REPORTED')
        self.assertFalse(failure['report_read_by_child'])
        self.assertIsNone(failure['fixture_result'])
        self.assertFalse(failure['fixture_counts_completed_claimed'])
        self.assertFalse(failure['B4_production_or_SDK_bug_claimed'])
        self.assertIsNone(new['child_actual_Torch_CPU']['result'])
        self.assertEqual(new['runtime_result_kind_retained'], 'B4_REAL_SENSOR_DELAY_TYPED_TAP_CPU_SOFTWARE_FIXTURE_V1')
        support = new['supported_sensor_input_domain']
        self.assertEqual(support['templates_dtype'], 'torch.float32')
        self.assertFalse(support['set_default_dtype_called'])
        self.assertFalse(support['production_noise_cast_or_edit'])
        self.assertFalse(support['production_RNG_change'])

    def test05_V1_and_complete_upstream_packages_unchanged(self):
        for key in ('V1_frozen_source', 'B4', 'codec'):
            packet = PINS[key]
            directory = Path(packet['directory'])
            row = packet['seal']
            self.assertEqual(info(Path(row['path'])), {k: row[k] for k in ('bytes', 'sha256')})
            sealed = json.loads(Path(row['path']).read_text(encoding='utf-8'))
            self.assertEqual(sealed['files'], packet['files'])
            self.assertEqual(hashlib.sha256(canonical(packet['files'])).hexdigest(), packet['content_root_sha256'])
            for name, pin in packet['files'].items():
                self.assertEqual(info(directory / name), pin, key + ':' + name)
        for key in ('original_complete_cpu_sources', 'read_only_reference_sources'):
            for name, row in PINS[key].items():
                self.assertEqual(info(Path(row['path'])), {k: row[k] for k in ('bytes', 'sha256')}, name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
