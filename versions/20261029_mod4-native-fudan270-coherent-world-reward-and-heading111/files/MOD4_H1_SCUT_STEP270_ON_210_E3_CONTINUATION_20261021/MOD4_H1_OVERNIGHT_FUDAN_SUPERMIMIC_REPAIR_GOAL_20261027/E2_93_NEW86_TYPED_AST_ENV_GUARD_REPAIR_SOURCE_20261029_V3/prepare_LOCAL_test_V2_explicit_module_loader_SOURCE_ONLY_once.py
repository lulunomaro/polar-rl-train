from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
old=B/'test_actual_target_CPU_AST_section_on_selected_worker_SOURCE_ONLY_once.py';raw=old.read_bytes();text=raw.decode();guard=B/'e2_frozen_worker_call_guard_v3.py';sha=hashlib.sha256(guard.read_bytes()).hexdigest()
a='from e2_frozen_worker_call_guard_v3 import validate_frozen_worker_calls,DECLARED_ENV_CALL'
b="""import importlib.util
_guard_path=Path(__file__).resolve().parent/'e2_frozen_worker_call_guard_v3.py'
assert hashlib.sha256(_guard_path.read_bytes()).hexdigest()==EXPECTED_GUARD_SHA
_spec=importlib.util.spec_from_file_location('e2_frozen_worker_call_guard_v3',_guard_path)
_module=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=_module;_spec.loader.exec_module(_module)
validate_frozen_worker_calls=_module.validate_frozen_worker_calls;DECLARED_ENV_CALL=_module.DECLARED_ENV_CALL""".replace('EXPECTED_GUARD_SHA',repr(sha))
assert text.count(a)==1;text=text.replace(a,b);ast.parse(text)
with (B/'test_actual_target_CPU_AST_section_on_selected_worker_SOURCE_ONLY_once_v2_explicit_loader.py').open('xb') as f:f.write(text.encode())
with (B/'reports/V1_LOCAL_TEST_IMPORT_ORIGINAL_ERROR_BEFORE_GUARD_ACTUAL.json').open('x') as f:json.dump(dict(passed=False,returncode=1,phase='top-level test import before actual target CPU guard statements',original_error='ModuleNotFoundError: No module named e2_frozen_worker_call_guard_v3',source=str(old),source_SHA=hashlib.sha256(raw).hexdigest(),new_test_only_fix='Explicit absolute path/SHA importlib preload into sys.modules; target CPU/worker/guard unchanged',additional_unexecuted_shell_preparation_error='PowerShell -c nested quoted string caused SyntaxError unterminated string literal; no new file was written, subsequent missing-file exit2. Replaced by this literal source preparation script.',no_model_SDK_remote_or_GPU=True),f,indent=2)
print('Prepared explicit-loader CPU source test V2; original V1 retained')
