"""One locked original 51-point gate; retain failure without changing hypothesis."""
from pathlib import Path
import hashlib,json,shutil,sys
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lock=json.loads((D/'SOURCE_LOCK.json').read_bytes())
assert sha(D/'METHOD.json')==lock['method_SHA']and sha(D/'ARCHITECTURE.md')==lock['architecture_SHA']
for x in lock['sources']:assert sha(Path(x['path']))==x['SHA']
A=D/'attempt001';A.mkdir(exist_ok=False)
files=['ARCHITECTURE.md','METHOD.json','SOURCE_LOCK.json','freeze_sources.py','freeze_001.log','fk_limits.py','run_limits_001.py']
for n in files:shutil.copy2(D/n,A/n)
pre=dict(kind='ORIGINAL_SYMMETRIC_HYPOTHESIS_PREEXEC_ONLY_LIMIT_GATE',files=[dict(path=n,SHA=sha(D/n))for n in files],old_sources=len(lock['sources']),physics_calls=0)
with(A/'PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(pre,f,indent=2)
from fk_limits import PublicFK
v=PublicFK().offset_grid(-.10,.10,51)
v.update(attempt='001',status='LIMIT_GATE_PASS'if v['limits_gate_pass']else'NOT_READY_DOMAIN',prototype_implemented=False,entry_not_built=True)
with(A/'LIMITS_RESULT.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:v[k]for k in ['attempt','status','offsets','violating_offset_count','FK_failures','math_gate_pass','limits_gate_pass','max_common_rotation_error_m','max_delta_error_rad','model_boots','forward_calls','integrator_calls','physics_module_imported']},indent=2))
print('RESULT_SHA='+sha(A/'LIMITS_RESULT.json'))
sys.exit(0 if v['limits_gate_pass']and v['math_gate_pass']else 1)
