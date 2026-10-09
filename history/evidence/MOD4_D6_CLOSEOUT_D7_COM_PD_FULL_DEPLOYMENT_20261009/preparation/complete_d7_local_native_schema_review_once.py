"""Continue local build after an actual result-assignment reader mismatch; once."""
from pathlib import Path
import json,ast,hashlib,shutil,time
PREP=Path(__file__).resolve().parent;OLD=PREP.parent/'MOD4_D6_FULL_CONTRACT_20261009';D=PREP.parent/'MOD4_D7_FULL_CONTRACT_20261009';R=D/'reports'
assert not (R/'LOCAL_D7_BUILD.json').exists() and not (D/'native_d7_chassis_pd_probe.py').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'));f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
new=[str(p.relative_to(D)).replace('\\','/') for p in (D/'isaac/mod4').glob('*.py') if str(p.relative_to(D)).replace('\\','/') not in f]
def put(n,t):
 p=D/n;assert not p.exists();ast.parse(t);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf8');new.append(n)
raw=(PREP/'prepare_d7_combined_contract_once.py').read_text();tail="t=(OLD/'native_d6_gas_probe.py')"+raw.split("t=(OLD/'native_d6_gas_probe.py')",1)[1]
tail=tail.replace('gas_damping_audit=env._gas_damping.audit()',"report['gas_damping_audit']=env._gas_damping.audit()")
tail=tail.replace('chassis_PD_audit=env.chassis_pd_audit(),',"report['chassis_PD_audit']=env.chassis_pd_audit();")
exec(tail,globals())
