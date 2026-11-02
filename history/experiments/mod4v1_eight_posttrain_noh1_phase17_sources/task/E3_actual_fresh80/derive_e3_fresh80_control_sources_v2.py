"""Reuse bounded scaffold, bind actual97 RecoveryEnv/13recipes/NPZ cache only."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
pairs=[('prepare_e2_remote_stage_once.py','prepare_e3_remote_stage_once.py'),('probe_e2_fresh80_no_pt_v1.py','probe_e3_fresh80_no_pt_v1.py'),('supervise_e2_fresh80_v1.py','supervise_e3_fresh80_v1.py'),('dispatch_e2_fresh80_v1_once.py','dispatch_e3_fresh80_v1_once.py')]
for old,new in pairs:
 text=(ROOT/'E2_actual_fresh80'/old).read_text(encoding='utf-8').replace('E2','E3').replace('e2_','e3_').replace('_e2','_e3').replace('/e2/','/e3/')
 text=text.replace('OWN_E3_H1_KIND','OWN_E2_H1_KIND').replace('E3_WORLD_MOVING_SIGNED4','E3_PUBLIC_RECOVERY')
 text=text.replace('MOD4_E3_PPO50_GAS400_2610v93','MOD4_E3_PPO50_GAS400_2610v97').replace('staged_sources/E3_MOD4V1_SOURCE_V1','staged_sources/E3_MOD4V1_SOURCE_FINAL')
 if old.startswith('probe_'):
  a="term=env.command_manager.get_term('twist');assert type(term).__module__=='e3_directional_spin_runtime_v1' and term._dt==.02"
  b="term=env.command_manager.get_term('twist');assert type(env).__module__=='e3_recovery_runtime_v1' and term._dt==.02\n        assert env._e3_fixed_reset_cache.source_sha=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83' and env._e3_fixed_reset_cache.pick==34"
  assert a in text;text=text.replace(a,b)
  a='        env.reset()  # exactly ONE explicit NEW fresh reset, not a checkpoint resume\n';assert a in text
  b=a+"        env.e3_reset_enabled=True;env.place_declared_fall(torch.arange(env.num_envs,device=env.device));assert not env.recovery.age.any();env.publish()\n        assert env.recovery.recipe.shape==(80,) and set(env.recovery.recipe.tolist())==set(range(13))\n"
  text=text.replace(a,b,1)
  text=text.replace('Original E3 WORLD_MOVING_SIGNED4 fresh80 noPT integration only','Original97 E3 RecoveryEnv/13recipe fresh80 noPT integration only')
 ast.parse(text)
 if (HERE/new).exists():
  assert new=='prepare_e3_remote_stage_once.py' and (HERE/new).read_text(encoding='utf-8')==text
  continue
 with (HERE/new).open('x',encoding='utf-8') as f:f.write(text)
print(json.dumps({'E3_new_scaffold':[new for old,new in pairs],'actual_environment':'original97 RecoveryEnv/13recipes/cache/phase, not E0/H1/E2 replacement','PT_or_SDK_started':False},indent=2))
