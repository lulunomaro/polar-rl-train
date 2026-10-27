"""Complete UNUSED entry source after retained V1 no-op anchor error."""
from pathlib import Path
import ast,json,hashlib,traceback
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;OLD=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/code'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,text):
 ast.parse(text)
 with (D/name).open('x',encoding='utf8',newline='\n') as f:f.write(text)
def change(text,old,new):
 assert text.count(old)==1,old;return text.replace(old,new)
try:
 source=(D/'derive_from_actual_R2_source_once.py').read_text('utf8')
 start=source.index("entry=(OLD/");end=source.index("write('native88C_frozen_single_sdk_entry_unused_once.py',entry)")+len("write('native88C_frozen_single_sdk_entry_unused_once.py',entry)")
 segment=source[start:end].replace('entry=change(entry," if q[\'execution_backend\']==\'target72\':", " if q[\'execution_backend\']==\'target72\':")\n','')
 exec(compile(segment,'reviewed_source_entry_derivation','exec'),globals())
 for p in D.glob('*.py'):ast.parse(p.read_bytes())
 checks=dict(environment_AST_exact=ast.dump(next(n for n in ast.parse((OLD/'native87R5_eval_environment_v1.py').read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='environment'))==ast.dump(next(n for n in ast.parse((D/'native88C_eval_environment_v1.py').read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='environment')),
 own_PID_guard_byteexact=(OLD/'native87R5_own_pid_out_guard_v1.py').read_bytes()==(D/'native88C_own_pid_out_guard_v1.py').read_bytes())
 assert all(checks.values())
 with (D/'SOURCE_DERIVATION_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,checks=checks,old_source_pins={str(p):H(p) for p in OLD.glob('*.py')},
  generated_entry_SHA=H(D/'native88C_frozen_single_sdk_entry_unused_once.py'),V1_original_error_and_partial_retained=True,actual_entry_model_SDK_or_GPU_executed=False),f,indent=2)
 print(json.dumps(dict(passed=True,entry_generated_unused=True)))
except BaseException:
 with (D/'DERIVATION_V2_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),source_generation_only=True),f,indent=2)
 raise
