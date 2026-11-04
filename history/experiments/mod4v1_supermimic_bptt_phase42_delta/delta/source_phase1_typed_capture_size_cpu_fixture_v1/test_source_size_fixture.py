"""Five NEW AST/ownScalar checks only; no old fixture/module/Torch execution."""
from pathlib import Path
import ast
import hashlib
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
API = runpy.run_path(str(HERE / 'size_fixture.py'))  # Complete NEW stdlib-only module.


def run_checks():
    results = []
    source = (HERE / 'size_fixture.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    assert len(source.splitlines()) <= 150
    imports = [n.module if isinstance(n, ast.ImportFrom) else n.names[0].name
               for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert set(imports) == {'pathlib', 'hashlib', 'json', 'random', 'sys'}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not attrs & {'settrace', 'clone', 'astype', 'manual_seed', 'set_rng_state', 'setstate', 'cuda'}
    locals_reads = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr == 'f_locals']
    assert len(locals_reads) == 1 and "frame.f_locals.get('wire')" in source
    assert source.count('sys.setprofile(') == 2 and 'finally:\n        sys.setprofile(prior)' in source
    for name in ('b4_run', 'c2_run'):
        assert sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
                   for n in ast.walk(tree)) == 1
    results.append('AST_150_LINES_STDLIB_TARGETED_PROFILE_AND_TWO_SINGLE_CALLS')

    value = {'unknown': 'UNKNOWN', 'unicode': '雪', 'int64': 2**60 + 7, 'bool': [True, False],
             'ids': [0, 79], 'finite_float': [-0.0, 0.1, 1e20]}
    for style in ('producer', 'raw', 'canonical'):
        options = dict(ensure_ascii=True, allow_nan=False, sort_keys=style != 'producer')
        if style == 'producer': options['indent'] = 2
        if style == 'canonical': options['separators'] = (',', ':')
        raw = json.dumps(value, **options).encode('utf-8')
        stat = API['_json_stat'](value, style)
        assert stat['bytes'] == len(raw) and stat['SHA256'] == hashlib.sha256(raw).hexdigest()
        assert not raw.endswith(b'\n') and json.loads(raw) == value
    try:
        API['_json_stat']({'invalid': float('nan')})
    except ValueError:
        pass
    else:
        raise AssertionError('stdlib nonfinite JSON gate was lost')
    results.append('OWN_SCALAR_EXACT_JSON_ENCODING_UNICODE_INT_BOOL_NO_LF')

    sensor = {'full_report': value, 'controls': ['OWN_SCALAR'] * 64}
    c2 = {'windows': {'first': [value], 'last': [value], 'middle': 'UNKNOWN'}, 'original_exception_events': [value]}
    scaffold = {'case': {'actuation': {'unavailable_binding': 'UNKNOWN'}, 'setup': 'UNKNOWN'},
                'terminal': {'role': 'OWN_SCALAR', 'returncode': 'UNKNOWN'}, 'group': {'cost': 'UNKNOWN'}}
    before = json.dumps([sensor, c2, scaffold], sort_keys=True)
    case = dict(scaffold['case'], sensor=sensor)
    case['actuation'] = dict(case['actuation'], **c2)
    group = dict(scaffold['group'], terminal=[dict(scaffold['terminal'], data=case)])
    measured = API['_pack'](sensor, c2, scaffold)
    assert measured == {'CASE': API['_json_stat'](case), 'GROUP': API['_json_stat'](group)}
    assert measured['GROUP']['bytes'] > measured['CASE']['bytes']
    assert before == json.dumps([sensor, c2, scaffold], sort_keys=True)
    results.append('OWN_SCALAR_PARENT_TERMINAL_DATA_EMBEDDING_ALL_FIELDS_UNCHANGED')

    report = dict(control_ledger=dict(requested_controls=64, recorded_controls=64,
                  all_controls_observed=True, normal_channel_records=640), metadata_retention_complete=True)
    calls, returned_wire = {'b4': 0, 'c2': 0}, {'OWN_SCALAR_C2': value}
    def finish(item):
        return item
    def unrelated():
        wire = {'DO_NOT_CAPTURE_UNRELATED_LOCALS': True}
        return wire
    def b4_success():
        calls['b4'] += 1
        unrelated(); finish({'control_ledger': {}}); finish(report); finish(dict(report, later=True))
        return {'status': 'PASS'}
    def c2_success():
        calls['c2'] += 1
        wire = returned_wire
        unrelated()
        return {'controls': 64, 'kind': 'OWN_SCALAR_NOT_OLD_FIXTURE'}
    prior = sys.getprofile()
    captured = API['_collect'](b4_success, (), {}, c2_success, (), {}, finish.__code__)
    assert captured[0] is report and captured[1] is returned_wire and captured[4]
    assert calls == {'b4': 1, 'c2': 1} and sys.getprofile() is prior
    results.append('OWN_SCALAR_PROFILE_FIRST_COMPLETE_RETURN_REFERENCES_RESTORED')

    error = RuntimeError('OWN_SCALAR_ORIGINAL_EXCEPTION')
    def fails():
        raise error
    for first, second in ((fails, c2_success), (b4_success, fails)):
        try:
            API['_collect'](first, (), {}, second, (), {}, finish.__code__)
        except RuntimeError as actual:
            assert actual is error and sys.getprofile() is prior
        else:
            raise AssertionError('ownScalar original exception was replaced')
    results.append('OWN_SCALAR_PROFILE_EXCEPTION_IDENTITY_AND_FINALLY_RESTORE')
    assert len(results) == 5
    return dict(kind='SIZE_FIXTURE_AST_OWN_SCALAR_CHECKS_V1', status='PASS', cases=results,
                tests=5, failures=0, errors=0, old_fixtures_executed=0, Torch_imported=False,
                actual_CPU_B4_C2_executed=False, native=False, Gate1='UNKNOWN', stage2_GO=False)
