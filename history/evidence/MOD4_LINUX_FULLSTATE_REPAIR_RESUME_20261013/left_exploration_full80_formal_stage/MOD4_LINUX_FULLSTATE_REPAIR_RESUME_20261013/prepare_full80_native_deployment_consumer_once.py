"""Prepare only the new120-control full80 native consumer; old deployments are never imported."""
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent
P=W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014'
old=W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014/deploy_reference17b_frozen1500_unique_once.py'
s=old.read_text()
s=s.replace('MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014','MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014')
s=s.replace('native3060_Linux20k_final_bodypos_worldpos_reference1500_v1','native3060_Linux20k_final_full80_native120_v1')
s=s.replace('MOD4_Linux20kFinalReference_20261014_Frozen1500_v1','MOD4_Linux20kFinalFull80_20261014_Native120_v1')
s=s.replace("pack=json.loads((R/'REFERENCE17B_ACTUAL_SOURCE_PACKAGE_SHA.json').read_bytes())","prep=json.loads((R/'FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').read_bytes());pack=prep['package']")
s=s.replace("CPU=json.loads((R/'REFERENCE17B_SOURCE_FROZEN_CPU_PREPARED_ACTUAL.json').read_bytes())","CPU=prep")
s=s.replace('REFERENCE17B_FROZEN3060_V1_SOURCE_PACKAGE.zip','FULL80_NATIVE_SOURCE_V1.zip')
s=s.replace('paired_direct3060_reference17b_v1.py','paired_full80_native_v1.py').replace('run_direct3060_reference17b_parent_v1.py','run_full80_native_parent_v1.py')
s=s.replace('steps=1500,num_envs=8','steps=120,num_envs=80').replace('not_80env_production_qualification=True','native120_only_not_full15s_or_qualification=True')
s=s.replace('demand_reference17b1500_parent_launcher_unique_once.py','demand_full80_native120_parent_launcher_unique_once.py')
q=P/'deploy_full80_native120_unique_once.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
print(str(q))
