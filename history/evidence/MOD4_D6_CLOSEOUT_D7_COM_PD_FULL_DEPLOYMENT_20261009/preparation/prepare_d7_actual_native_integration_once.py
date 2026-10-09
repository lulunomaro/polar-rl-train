"""Finish native/controller using the observed result assignment, no escaped source rewrite."""
from pathlib import Path
import json,ast,hashlib,shutil,time
PREP=Path(__file__).resolve().parent;OLD=PREP.parent/'MOD4_D6_FULL_CONTRACT_20261009';D=PREP.parent/'MOD4_D7_FULL_CONTRACT_20261009';R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'));f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
assert not (D/'native_d7_chassis_pd_probe.py').exists() and not (R/'LOCAL_D7_BUILD.json').exists()
new=[str(p.relative_to(D)).replace('\\','/') for p in (D/'isaac/mod4').glob('*.py') if str(p.relative_to(D)).replace('\\','/') not in f]
def put(n,t):
 p=D/n;assert not p.exists();ast.parse(t);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf8');new.append(n)
t=(OLD/'native_d6_gas_probe.py').read_text(encoding='utf8')
t=t.replace('from gas_damping_training_env import GasDampingMod4Env as Mod4Env','from chassis_pd_training_env import ChassisPDMod4Env as Mod4Env')
t=t.replace("RM_GAS_DAMPING_PROFILE='gas_damping_independent_episode_090_110_v1'","RM_GAS_DAMPING_PROFILE='gas_damping_independent_episode_090_110_v1',RM_CHASSIS_COM_PROFILE='chassis_link_local_independent_xyz_5mm_v1',RM_EXPLICIT_PD_PROFILE='explicit_motor_PD_independent_095_105_v1'")
anchor=" report['gas_damping_recipe']=env.gas_damping_recipe();report['gas_damping_audit']=env._gas_damping.audit()"
assert t.count(anchor)==1;t=t.replace(anchor,anchor+"\n report['chassis_PD_audit']=env.chassis_pd_audit()")
put('native_d7_chassis_pd_probe.py',t)
source=(PREP/'prepare_d7_combined_contract_once.py').read_text();tail="t=(OLD/'supervise_d6_gas_full_contract.py')"+source.split("t=(OLD/'supervise_d6_gas_full_contract.py')",1)[1]
exec(tail,globals())
