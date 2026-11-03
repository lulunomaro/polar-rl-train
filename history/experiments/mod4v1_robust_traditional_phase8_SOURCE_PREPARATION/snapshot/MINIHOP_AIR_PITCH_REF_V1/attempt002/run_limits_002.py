"""One new-domain 51 point gate before prototype implementation; no third try."""
from pathlib import Path
import hashlib,json,shutil,sys
D=Path(__file__).resolve().parent;T=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((D/'SOURCE_LOCK.json').read_bytes());assert sha(D/'METHOD.json')==s['method_SHA']and sha(D/'ARCHITECTURE.md')==s['architecture_SHA']
assert sha(T/'fk_limits.py')==s['unchanged_shared_FK_SHA']
for x in s['sources']:assert sha(Path(x['path']))==x['SHA']
assert not(D/'controller.py').exists()
A=D/'limits_preexec';A.mkdir(exist_ok=False)
for n in ['ARCHITECTURE.md','METHOD.json','SOURCE_LOCK.json','run_limits_002.py']:shutil.copy2(D/n,A/n)
shutil.copy2(T/'fk_limits.py',A/'fk_limits.py')
with(A/'PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(dict(files=[dict(path=p.name,SHA=sha(p))for p in A.iterdir()if p.is_file()and p.name!='PREEXEC.json']),f,indent=2)
sys.path.insert(0,str(T));from fk_limits import PublicFK
v=PublicFK().offset_grid(-.10,.03,51)
v.update(attempt='002',status='PRECODE_DOMAIN_GATE_PASS'if v['limits_gate_pass']and v['math_gate_pass']else'NOT_READY_DOMAIN',prototype_not_yet_implemented=True)
with(D/'LIMITS_RESULT.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:v[k]for k in ['attempt','status','offsets','violating_offset_count','FK_failures','math_gate_pass','limits_gate_pass','max_common_rotation_error_m','max_delta_error_rad','model_boots','forward_calls','integrator_calls','physics_module_imported']},indent=2))
print('MIN_HIP_MARGIN='+str(v['minimum_joint_margins']['left_hip']))
print('RESULT_SHA='+sha(D/'LIMITS_RESULT.json'))
sys.exit(0 if v['limits_gate_pass']and v['math_gate_pass']else 1)
