"""One-shot NEW v2 source/index authoring; reads only small sealed Python/JSON."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
OLD = PROJECT / 'source_stage_a1_microbatch_eval_v1' / 'stage_a1_microbatch_eval_v1.py'
OLD_INDEX = PROJECT / 'source_frozen_eval_microbatch_parent_v1' / 'MICROBATCH_STAGE_INDEX_V1.json'
BASE = PROJECT / 'source_resume_runtime_v2' / 'resume_runtime_contracts_v3.py'
H = lambda raw: hashlib.sha256(raw).hexdigest()
DEP_PIN = (22337, 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7')

DEPENDENCY_FUNCTION = '''def verify_close_dependency_imports(app_source, base_source):
    """Real full-module imports, no stubs or SDK instance/close calls."""
    app_source, base_source = Path(app_source), Path(base_source)
    receipts = {}
    for label, path, pin, extra in (
        ('contracts', base_source, DEPENDENCY_PIN, set()),
        ('AppV6', app_source, APP_CLOSE_PIN, {'resume_runtime_contracts_v3'})):
        raw = path.read_bytes()
        need((len(raw), H(raw)) == pin, 'close dependency source pin differs: ' + label)
        parsed = ast.parse(raw)
        roots = set()
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import): roots.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: roots.add(node.module.split('.')[0])
        need(roots <= set(sys.stdlib_module_names) | {'__future__'} | extra,
             'unexpected non-stdlib close dependency import: ' + label)
        receipts[label] = dict(path=str(path), bytes=len(raw), SHA256=H(raw), import_roots=sorted(roots),
                               full_original_module=True, AST_cropped_or_stubbed=False)
    names = ('app_close_semantics_v5', 'resume_runtime_contracts_v3')
    before = {name: sys.modules.get(name) for name in names}
    try:
        for name in names: sys.modules.pop(name, None)
        base_spec = importlib.util.find_spec('resume_runtime_contracts_v3')
        need(base_spec is not None and Path(base_spec.origin).resolve() == base_source.resolve(),
             'real base dependency must resolve in the actual source/stage root')
        base = importlib.import_module('resume_runtime_contracts_v3')
        need(Path(base.__file__).resolve() == base_source.resolve(), 'actual contracts import origin differs')
        app_spec = importlib.util.spec_from_file_location('app_close_semantics_v5', app_source)
        app = importlib.util.module_from_spec(app_spec)
        sys.modules['app_close_semantics_v5'] = app
        app_spec.loader.exec_module(app)  # Entire unchanged helper, including its real import at line 23.
        need(app._base is base and base.FINAL_KIND == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
             and callable(base.evaluate_waited_worker), 'helper must bind real complete contracts module')
        need(app.SOURCE_CODE_VERSION == 'V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES', 'actual AppV6 version differs')
        need(not any(name in sys.modules for name in ('torch', 'isaacsim', 'omni')), 'dependency check imported native package')
        return dict(kind='REAL_COMPLETE_APP_V6_CONTRACTS_IMPORT_CHECK_V2', passed=True,
                    modules=receipts, helper_base_is_actual_imported_contracts=True,
                    model_C_lock_SDK_GPU_operations=0, actual_SimulationApp_binding=None,
                    actual_close_or_wait_performed=False)
    finally:
        for name, old in before.items():
            if old is None: sys.modules.pop(name, None)
            else: sys.modules[name] = old


'''


def once(text, before, after):
    assert text.count(before) == 1, ('literal uniqueness', before[:100], text.count(before))
    return text.replace(before, after, 1)


def main():
    old_raw, index_raw, base_raw = OLD.read_bytes(), OLD_INDEX.read_bytes(), BASE.read_bytes()
    assert (len(old_raw), H(old_raw)) == (29335, 'dff8143d2464f82f720497ddfe4c241cfd4846e938a9f975962defdaac8c893b')
    assert (len(index_raw), H(index_raw)) == (4529, '42e4714c8adf4361351e052d4006f863452fbad557343cc22f9dbad21951beaf')
    assert (len(base_raw), H(base_raw)) == DEP_PIN
    old_index = json.loads(index_raw)
    index = dict(kind='SOURCE_ONLY_14_MAPPINGS_MICROBATCH_CLOSE_DEPENDENCY_V2_NOT_INSTALLED',
        original_thirteen_index=dict(path=str(OLD_INDEX), bytes=len(index_raw), SHA256=H(index_raw)),
        entries=old_index['entries'] + [dict(path=str(BASE), relative='resume_runtime_contracts_v3.py',
                                            bytes=len(base_raw), SHA256=H(base_raw))],
        original_thirteen_entries_unchanged=True, original_runtime_requires_thirteen_as_subset_unchanged=True,
        new_dependency_only=True, keep_all_other_original_static_dependencies_and_worker_files=True,
        source_admission=False)
    assert index['entries'][:13] == old_index['entries']
    encoded = (json.dumps(index, indent=2) + '\n').encode()
    text = old_raw.decode().replace('\r\n', '\n')
    text = once(text, 'import io\n', 'import io\nimport importlib.util\n')
    text = once(text, "INDEX_PIN = (4529, '42e4714c8adf4361351e052d4006f863452fbad557343cc22f9dbad21951beaf')",
        'INDEX_PIN = ' + repr((len(encoded), H(encoded))))
    text = once(text, "'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py'}",
        "'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py', 'resume_runtime_contracts_v3.py'}")
    text = once(text, "POSE_SHA = '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f'",
        "POSE_SHA = '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f'\nDEPENDENCY_PIN = " + repr(DEP_PIN) +
        "\nAPP_CLOSE_PIN = (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39')")
    text = text.replace('sealed thirteen-mapping index pin differs', 'sealed fourteen-mapping index pin differs')
    text = once(text, 'SOURCE_ONLY_13_MAPPINGS_NEW_MICROBATCH_NOT_INSTALLED', index['kind'])
    text = once(text, "len(entries) == 13, 'exact thirteen mappings required'", "len(entries) == 14, 'exact fourteen mappings required'")
    text = once(text, 'all thirteen installed aliases required once', 'original thirteen plus one close dependency required once')
    text = once(text, 'def metadata_validate(root, *, plan_bytes=None):', DEPENDENCY_FUNCTION + 'def metadata_validate(root, *, plan_bytes=None):')
    text = once(text, "watched = ('a1_frozen_eval_runtime_v2', 'frozen_eval_microbatch_runtime_v1')",
        "watched = ('a1_frozen_eval_runtime_v2', 'frozen_eval_microbatch_runtime_v1', 'app_close_semantics_v5', 'resume_runtime_contracts_v3')")
    text = once(text, '        with contextlib.redirect_stdout(output):\n',
        "        dependency = verify_close_dependency_imports(\n            root / ('app_close_semantics_v6.py' if plan_bytes is not None else 'app_close_semantics_v5.py'),\n            root / 'resume_runtime_contracts_v3.py')\n        with contextlib.redirect_stdout(output):\n")
    text = once(text, "result.update(model_path_resolve='LEXICAL_METADATA_ONLY_NO_LSTAT'",
        "result.update(dependency_completeness=dependency, model_path_resolve='LEXICAL_METADATA_ONLY_NO_LSTAT'")
    for old in ('SOURCE_MICROBATCH_PREFLIGHT_ONLY_NO_ADMISSION_V1', 'STAGE_BEGIN_MICROBATCH_V1',
                'STAGED_STATIC_FILES_MICROBATCH_V1', 'SOURCE_MICROBATCH_STAGE_COMPLETE_NOT_DISPATCH_V1',
                'STAGE_COMPLETE_MICROBATCH_V1', 'STAGE_ERROR_MICROBATCH_V1'):
        text = text.replace(old, old[:-2] + 'V2')
    text = once(text, 'Stdlib ONLY: preflight or one NEW E3/W35 frozen-eval source stage. NEVER dispatch.',
        'V2 stdlib ONLY: original thirteen plus complete close dependency; one NEW stage, NEVER dispatch.')
    ast.parse(text); compile(text, 'stage_a1_microbatch_eval_v2.py', 'exec')
    old_functions = {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(old_raw).body if isinstance(n, ast.FunctionDef)}
    new_functions = {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    changed = [name for name in old_functions if old_functions[name] != new_functions[name]]
    assert set(changed) == {'source_mappings', 'metadata_validate', 'preflight_summary', 'stage'}
    outputs = {'MICROBATCH_STAGE_INDEX_V2.json': encoded, 'stage_a1_microbatch_eval_v2.py': text.encode(),
        'V2_DELTA_SOURCE_AUTHORING_RECEIPT.json': (json.dumps(dict(
            original_V1_PIN=[len(old_raw), H(old_raw)], original_thirteen_index_PIN=[len(index_raw), H(index_raw)],
            new_index_PIN=[len(encoded), H(encoded)], dependency_PIN=list(DEP_PIN),
            changed_original_functions=changed, original_thirteen_entries_unchanged=True,
            all_other_original_functions_AST_identical=True, native_operations=0), indent=2) + '\n').encode()}
    for name, data in outputs.items():
        with (HERE / name).open('xb') as stream: stream.write(data)
    print(json.dumps({name: dict(bytes=len(raw), SHA256=H(raw)) for name, raw in outputs.items()}, indent=2))


if __name__ == '__main__': main()
