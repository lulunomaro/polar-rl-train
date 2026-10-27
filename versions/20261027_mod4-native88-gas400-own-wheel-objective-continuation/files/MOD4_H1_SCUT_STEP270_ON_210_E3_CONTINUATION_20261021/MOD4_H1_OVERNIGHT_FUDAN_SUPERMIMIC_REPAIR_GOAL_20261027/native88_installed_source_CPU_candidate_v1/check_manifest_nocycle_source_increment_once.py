"""Source-only regression: receipt manifest pin comes from manifest, never Task."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent
tree=ast.parse((D/'target_native88_source_sdk_cpu_v1.py').read_bytes())
n=next(x for x in ast.walk(tree) if isinstance(x,ast.DictComp) and isinstance(x.key,ast.Name) and x.key.id=='k' and any(isinstance(t,ast.Name) and t.id=='PIN_FIELDS' for g in x.generators for t in ast.walk(g.iter)))
ns=dict(PIN_FIELDS=('manifest_SHA','native88_contract_SHA'),checked=dict(manifest_SHA='a'*64),task=dict(native88_contract_SHA='b'*64))
value=eval(compile(ast.Expression(n),'receipt_pin_source','eval'),ns)
assert value==dict(manifest_SHA='a'*64,native88_contract_SHA='b'*64) and 'manifest_SHA' not in ns['task']
for f in D.glob('*.py'):ast.parse(f.read_bytes())
with (D/'MANIFEST_NOCYCLE_SOURCE_INCREMENT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=1,scope='AST pin evaluation only; no target/main/model',Task_manifest_hash_cycle_not_required=True,
 final_payload_source_pins={x:hashlib.sha256((D/x).read_bytes()).hexdigest() for x in ('native88_source_guard_v1.py','target_native88_source_sdk_cpu_v1.py','native88_installed_cpu_helpers_v1.py')}),f,indent=2)
print(json.dumps(dict(passed=True,count=1)))
