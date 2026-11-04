"""Five own SOURCE/AST/config/memory-stream cases; never call application.main or the old14 suite."""
from pathlib import Path
import ast
import copy
import io
import json
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import typed_science_cache_apply_v1 as app


class MemoryPath:
    """An owned synthetic bytes stream, not a filesystem path or capture artifact."""
    def __init__(self, raw):
        self.raw, self.opens, self.limit = raw, 0, None
    def open(self, mode):
        assert mode == 'rb'
        self.opens += 1
        owner = self
        class Stream(io.BytesIO):
            def read(self, maximum):
                owner.limit = maximum
                return super().read(maximum)
        return Stream(self.raw)


def state():
    return dict(cache={}, proof={}, counts={a: dict(read=0, hash=0, decode=0) for a in app.ALIASES})


def pin(raw):
    return dict(bytes=len(raw), SHA256=app.sha(raw))


class SourceCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(Path(app.__file__).read_text(encoding='utf-8'))
        source = Path(__file__).resolve().parent.parent/'source_phase1_typed_native_capture_v1/CAPTURE_SOURCE_INDEX.json'
        raw = source.read_bytes()
        assert (len(raw), app.sha(raw)) == (148229, '92da4a44ca9b7b6246c82d4dd281b73fa176bc1bdfbac981aa3403e43d7873d8')
        index = json.loads(raw)
        rows = index['bootstrap_original_sources']+index['original17']+index['new_sources']+index['dependency_sources']+[index['producer_abi']]
        cls.rows = sorted([dict(relative=r['install_relative'], bytes=r['bytes'], SHA256=r['SHA256']) for r in rows], key=lambda r:r['relative'])
        assert len(cls.rows) == 34 and app.canonical(cls.rows) == app.MANIFEST34

    def config(self):
        group = 'MOD4V1_TYPED_SYNTHETIC_CONFIG_ONLY'
        life = {key: dict(kind='SYNTHETIC_CONFIG_NOT_ACTUAL_METADATA') for key in app.REQUIRED_LIFE}
        life['app_close_binding'] = dict(fast_shutdown=True)
        life['app_fast_intent'] = dict(kind='SYNTHETIC_PRESENT_ONLY_NOT_A_REAL_FAST_INTENT')
        life['parent_exit_scope'].update(all_own_children_waited=True, original_single_GPU_private_EX_released=True,
            original_global_finite_EX_released=True, child_waits=[dict(role='E3', actual_waited=True, returncode=0)], errors=[])
        life['outer_parent_wait'].update(actual_parent_p_wait_returned=True, returncode=0, controller_errors=[])
        life['source_grade'].update(passed_closed_capture_execution=True, errors=[],
            external_settlement_reference='UNKNOWN_SYNTHETIC_OPTIONAL_FIELD_NOT_PROMOTED')
        task = dict(group_id=group, role='E3', controls=64, fixture='SYNTHETIC_CONFIG_ONLY')
        proofs = {}
        for alias, document in dict(life, task=task).items():
            raw = json.dumps(document, allow_nan=False).encode()
            proofs[alias] = dict(original_bytes=len(raw), original_SHA256=app.sha(raw), decoded_canonical_SHA256=app.canonical(document))
        expected = {a: pin(b'{"synthetic_only":true}') for a in app.ALIASES}
        info = {relative: dict(status='READ', read_count=1, whole_JSON_read=True, **expected[a]) for a,relative in app.ALIASES.items()}
        root = str(app.B/'tasks'/group)
        return dict(kind='PARENT_NEW_TYPED_SCIENCE_CACHE_CONFIG_V1', qualified_closed_execution=True,
            new_functional_purpose='OWN_TYPED_CACHE_SCIENCE_AFTER_CLOSED', new_purpose_reference='SYNTHETIC_TEST_REFERENCE_NOT_QUALIFICATION',
            independent_source_qualification_reference='SYNTHETIC_TEST_REFERENCE_NOT_SOURCE_AUTHENTICATION', root=root, group_id=group,
            analysis_root='/synthetic-analysis-only', OUTPUT='/synthetic-analysis-only/TYPED_SCIENCE_CACHE_RESULT_V1.json', role='E3', controls=64,
            qualified_closed_scope=dict(root=root, group_id=group, passed_closed_capture_execution=True, errors=[], missing_metadata=[]),
            task=task, lifecycle=life, expected_whole_files=expected, file_metadata=info, actual_source_hashes=copy.deepcopy(self.rows),
            provenance=dict(whole_documents=proofs))

    def test_01_AST_fresh_normal_imports_one_consumer_no_launcher_or_payload_export(self):
        self.assertIsNone(app.CONFIG)
        self.assertEqual(app.STATUS, 'SOURCE_READY_FOR_PARENT_NEW_PURPOSE_ONLY')
        imports = {alias.name for n in ast.walk(self.tree) if isinstance(n, ast.Import) for alias in n.names}
        self.assertEqual(imports, {'hashlib', 'json', 'sys', 'capture_evidence_verifier_v1', 'typed_capture_consumer'})
        attrs = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        self.assertEqual(sum(n.func.attr == 'verify_typed_capture' for n in attrs), 1)
        self.assertEqual(sum(n.func.attr == 'write' for n in attrs), 1)
        self.assertEqual(sorted(n.args[0].value for n in attrs if n.func.attr == 'open'), ['rb', 'x'])
        self.assertFalse(any(n.func.attr in {'Popen','exec_command','replace','rename','mkdir','addaudithook','write_bytes','write_text'} for n in attrs))
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'exec','eval','compile'} for n in ast.walk(self.tree)))
        main = next(n for n in self.tree.body if isinstance(n,ast.FunctionDef) and n.name == 'main')
        self.assertEqual(main.body[1].value.func.id, 'validate_config')
        text = ast.unparse(main)
        self.assertIn('group_final=group', text)
        self.assertNotIn('str(error)', text)
        self.assertNotIn('traceback', text)
        self.assertIn("exception_type=type(error).__name__", text)
        self.assertEqual(len(Path(app.__file__).read_text(encoding='utf-8').splitlines()) <= 140, True)

    def test_02_concrete_config_and_optional_UNKNOWN_stay_unchanged_no_main(self):
        c = self.config(); before = app.canonical(c)
        root, analysis = app.validate_config(c)
        self.assertEqual(str(root), c['root'])
        self.assertEqual(str(analysis), c['analysis_root'])
        self.assertEqual(app.canonical(c), before)
        self.assertEqual(c['lifecycle']['source_grade']['external_settlement_reference'], 'UNKNOWN_SYNTHETIC_OPTIONAL_FIELD_NOT_PROMOTED')
        self.assertNotIn('group_final', c['lifecycle'])
        c['controls'] = c['task']['controls'] = 128
        raw = json.dumps(c['task']).encode()
        c['provenance']['whole_documents']['task'] = dict(original_bytes=len(raw), original_SHA256=app.sha(raw), decoded_canonical_SHA256=app.canonical(c['task']))
        app.validate_config(c)
        missing = self.config(); del missing['lifecycle']['source_grade']['external_settlement_reference']
        grade = missing['lifecycle']['source_grade']; raw = json.dumps(grade).encode()
        missing['provenance']['whole_documents']['source_grade'] = dict(original_bytes=len(raw), original_SHA256=app.sha(raw), decoded_canonical_SHA256=app.canonical(grade))
        app.validate_config(missing)
        self.assertNotIn('external_settlement_reference', grade)  # Absence stays absent, not UNKNOWN or truth.

    def test_03_paths_types_actual_metadata_full34_and_missing_are_fail_closed(self):
        variants = [('root','/unrelated/tasks/wrong'), ('controls',True), ('role','W35'), ('OUTPUT','/outside/RESULT.json')]
        for key, value in variants:
            c = self.config(); c[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): app.validate_config(c)
        c = self.config(); c['expected_whole_files']['worker_final']['bytes'] = app.MAXIMUM+1
        with self.assertRaises(ValueError): app.validate_config(c)
        c = self.config(); c['file_metadata']['cases/E3/FINAL.json']['SHA256'] = '0'*64
        with self.assertRaises(ValueError): app.validate_config(c)
        c = self.config(); c['actual_source_hashes'].pop()
        with self.assertRaises(ValueError): app.validate_config(c)
        c = self.config(); del c['lifecycle']['app_fast_intent']
        with self.assertRaises(KeyError): app.validate_config(c)
        c = self.config(); c['provenance']['whole_documents']['task']['decoded_canonical_SHA256'] = 'UNKNOWN'
        with self.assertRaises(ValueError): app.validate_config(c)
        c = self.config(); c['lifecycle']['group_final'] = {'projected': True}
        with self.assertRaises(ValueError): app.validate_config(c)

    def test_04_memory_only_read_hash_decode_once_and_same_object_cache(self):
        raw = b'{ "value":3, "synthetic_owned":"not actual trace" }'
        memory, s = MemoryPath(raw), state()
        first = app.read_once('worker_final', memory, pin(raw), s, app.canonical)
        again = app.read_once('worker_final', memory, pin(raw), s, app.canonical)
        self.assertIs(first, again)
        self.assertEqual(memory.opens, 1)
        self.assertEqual(memory.limit, 64*1024*1024+1)
        self.assertEqual(s['counts']['worker_final'], dict(read=1, hash=1, decode=1))
        self.assertEqual(s['proof']['worker_final']['original_SHA256'], app.sha(raw))
        self.assertEqual(s['proof']['worker_final']['decoded_canonical_SHA256'], app.canonical(first))
        self.assertNotEqual(app.sha(raw), app.canonical(first))
        canonical_raw = json.dumps(first, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        self.assertEqual(app.sha(canonical_raw), app.canonical(first))  # Distinct definitions can legitimately coincide.
        self.assertEqual(s['counts']['group_final'], dict(read=0, hash=0, decode=0))

    def test_05_memory_corruption_no_retry_no_decode_fallback_no_consumer_execution(self):
        for raw, expected, counts in [(b'{"x":1}', pin(b'{"x":2}'), dict(read=1, hash=1, decode=0)),
                                      (b'{', pin(b'{'), dict(read=1, hash=1, decode=1)),
                                      (b'[]', pin(b'[]'), dict(read=1, hash=1, decode=1)),
                                      (b'{"x":NaN}', pin(b'{"x":NaN}'), dict(read=1, hash=1, decode=1))]:
            memory, s = MemoryPath(raw), state()
            with self.subTest(raw=raw), self.assertRaises(ValueError): app.read_once('worker_final', memory, expected, s, app.canonical)
            with self.assertRaises(ValueError): app.read_once('worker_final', memory, expected, s, app.canonical)
            self.assertEqual(memory.opens, 1)
            self.assertEqual(s['counts']['worker_final'], counts)
            self.assertNotIn('worker_final', s['cache'])
        self.assertNotIn('typed_capture_consumer', sys.modules)
        self.assertNotIn('capture_evidence_verifier_v1', sys.modules)
        self.assertNotIn('torch', sys.modules)


if __name__ == '__main__': unittest.main(verbosity=2)
