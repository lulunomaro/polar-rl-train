"""E3 actual97 read-only evaluation control, gated by its completed fresh80."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
pairs=[('evaluate_e2_b3_native24_no_update_v1.py','evaluate_e3_1cd_native24_no_update_v1.py'),('supervise_e2_b3_no_update_v1.py','supervise_e3_1cd_no_update_v1.py'),('collect_b3_no_update_v1.py','collect_1cd_no_update_v1.py'),('prepare_dispatch_b3_no_update_once.py','prepare_dispatch_1cd_no_update_once.py')]
for old,new in pairs:
 text=(ROOT/'E2_actual_fullrestore_native24'/old).read_text(encoding='utf-8').replace('E2','E3').replace('e2_','e3_').replace('_e2','_e3').replace('/e2/','/e3/').replace('B3','1CD').replace('b3_','1cd_').replace('_b3','_1cd')
 text=text.replace('OWN_E3_H1_KIND','OWN_E2_H1_KIND').replace('E3_WORLD_MOVING_SIGNED4','E3_PUBLIC_RECOVERY')
 text=text.replace('b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1','1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8')
 text=text.replace('MOD4_E3_PPO50_GAS400_2610v93','MOD4_E3_PPO50_GAS400_2610v97').replace('final_valid_update92.pt','final_valid_update87.pt')
 text=text.replace('14615089','14715029').replace('42822','43090').replace('859300','866060').replace('.00022500000000000002','.0002562890625000001')
 text=text.replace('MOD4V1_E3_FRESH80_FULLDR_20261102_023610_1793558170021229000','MOD4V1_E3_FRESH80_FULLDR_20261102_030504_1793559904510076900')
 if old.startswith('evaluate_'):
  text=text.replace('E3_COMMAND_RESUME_STARTUP_VERIFIED.json','E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json')
  a="            command_proof=json.loads(receipts['E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json'].read_bytes());assert command_proof['source_has_E3_command_state']\n            command=source['E3_moving4_command_state'];assert command['kind']=='E3_PUBLIC_RECOVERY' and command['moving_yaw_cap']==4.\n            assert len(command['tensors'])==9 and all(v.shape[0]==20000 for v in command['tensors'].values())\n            term=env.command_manager.get_term('twist');assert type(term).__module__=='e3_directional_spin_runtime_v1' and term._dt==.02"
  b="            phase_proof=json.loads(receipts['E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json'].read_bytes());assert phase_proof['source_had_E3']\n            phase=source['E3_public_recovery_state']['phase'];assert len(phase['tensors'])==7 and all(v.shape[0]==20000 for v in phase['tensors'].values())\n            term=env.command_manager.get_term('twist');assert type(env).__module__=='e3_recovery_runtime_v1' and term._dt==.02\n            assert env.e3_reset_enabled and not env.recovery.age.any() and env._e3_fixed_reset_cache.pick==34\n            assert env._e3_fixed_reset_cache.source_sha=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'\n            assert env.recovery.recipe.shape==(20000,) and set(env.recovery.recipe.tolist())==set(range(13))"
  assert a in text;text=text.replace(a,b)
  text=text.replace('E3_world_signed4_nine_tensor_private_mode_RNG_restored=True','E3_recovery13_phase7_private_command_RNG_restored=True,original_declared_fall_publish_after_ONE_reset=True,producer_effort_owner_field="UNDEFINED_OR_UNKNOWN_NO_NEW_GATE"')
 ast.parse(text)
 with (HERE/new).open('x',encoding='utf-8') as f:f.write(text)
print(json.dumps({'E3_new_eval_only_sources':[new for old,new in pairs],'gate':'Fresh80 actualPASS and original locks released REQUIRED','source_PT_reads_by_derivation':0},indent=2))
