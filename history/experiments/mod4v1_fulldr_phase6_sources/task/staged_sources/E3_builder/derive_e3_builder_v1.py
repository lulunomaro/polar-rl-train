"""E3 source-only derivation from generic string/manifest scaffold, NOT E2 env."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent;STAGED=HERE.parent
s=(STAGED/'E2_builder/build_e2_mod4v1_sources_v5.py').read_text(encoding='utf-8')
s=s.replace('E2','E3').replace('e2_','e3_').replace('_e2','_e3').replace('/e2/','/e3/')
s=s.replace('OWN_E3_H1_KIND','OWN_E2_H1_KIND')  # original E3 production variable name

def change(a,b):
 global s
 if a not in s:raise ValueError('Missing E3 source derivation anchor: '+a[:150])
 s=s.replace(a,b)

s=s.replace('42822','43090').replace('42823','43091').replace('859300','866060').replace('14615089','14715029').replace('.00022500000000000002','.0002562890625000001')
s=s.replace('b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1','1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8')
s=s.replace('MOD4_E3_PPO50_GAS400_2610v93','MOD4_E3_PPO50_GAS400_2610v97').replace('final_valid_update92.pt','final_valid_update87.pt').replace('prior_new_PPO_updates=92','prior_new_PPO_updates=87')
s=s.replace('MOD4V1_E3_SELECTED43090_FULLD0D7_WORLD_SIGNED4_V1','MOD4V1_E3_SELECTED43090_FULLD0D7_RECOVERY13_V1')
change("read(prep/'E3_COMPLETE_INSTALL_MANIFEST_V1.json','0e27157ce13a88748504c02a5702b7d6027ca14ca3224e4c6d4d5bcbe52175fd')", "read(night/'E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1/E3_COMPLETE_INSTALL_MANIFEST_V1.json','04e88211fa685523c3a9a0bd074ac69a5618baf55ffea67c1eab93f7bc436023')")
change("source('train_E3_full_resume_v1.py')", "source('train_E3_fullstate_v1.py')")
change("root/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/reports/E3_93_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'", "night/'TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1/reports/E3_97_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'")
s=s.replace('d741414f54c22bff910541560e3af689f0c36afa507fb416e7beb7dd632468bb','b9f5af6b1677ed6835ede170a38822f618e695e3f11fda5e6492a9c7282883bf')
s=s.replace('e3_command_checkpoint_v1.py','e3_fullstate_checkpoint_v1.py')
s=s.replace('from e3_h1_flat_environment_v1 import E3H1FlatEnv as Mod4Env','from e3_recovery_runtime_v1 import RecoveryEnv as Mod4Env')
s=s.replace('E3_WORLD_MOVING_SIGNED4','E3_PUBLIC_RECOVERY')
s=s.replace('from e3_fullstate_checkpoint_v1 import install_e3_save_contract','from e3_fullstate_checkpoint_v1 import install as install_chassis_pd_save_contract')
s=s.replace("SOURCE_SHA='5b5d1ee88bf9f56f865378d82d9f8864fa5ec2859f636c9b33b07558323d7f6e'", "SOURCE_SHA='59fa03e6e4d3ecf81153707082840df0347f6504508dd1a413dda7b714db6b75'")
s=s.replace('E3_83B90_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt','E3_86B89_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt')
s=s.replace("entry=mod/'train_E3_full_resume_v1.py'", "entry=mod/'train_E3_fullstate_v1.py'")
s=s.replace("worker.replace('==42731','==43090').replace('{857460}','{866060}').replace('857460+20*updates','866060+20*updates')", "worker.replace('==43004','==43090').replace('{864320}','{866060}').replace('864320+20*updates','866060+20*updates')")
s=s.replace('ITER, ADAM, PRIOR_UPDATES = 43090, 866060, 92','ITER, ADAM, PRIOR_UPDATES = 43090, 866060, 87')
s=s.replace('E3_MOD4V1_WORLD_MOVING_SIGNED4','E3_MOD4V1_RECOVERY13').replace('original_E3_world_moving_signed4','original_E3_public_recovery13')
s=s.replace('E3_WORLD_MOVING_SIGNED4_NOT_H1jump_NOT_RM70','E3_RECOVERY13_NOT_E0_H1jump_RM70')
s=s.replace('historical_E3_world_signed4_reset_command_and_DR_scope_exactly_reused','historical_E3_recovery13_phase_bank_reward_RNG_scope_exactly_reused').replace('historical_E3_world_signed4_scope_reuse_receipt_SHA','historical_E3_recovery13_scope_reuse_receipt_SHA')
# Carry unchanged ORIGINAL E3 phase/environment/cache, not an E2/E0 substitute.
a="    health=replace(health0,"
assert a in s
s=s.replace(a,"    for unchanged_name in ('e3_recovery_runtime_v1.py','e3_public_recovery_phase_v1.py','e3_reset_bank_cache_v1.py'):\n        original_E3=source(unchanged_name);emit(P+unchanged_name,original_E3)\n"+a,1)
# Provenance references are this E3 derivation and original authoritative E3 rows.
a=s.index("    template,template_ref=read(");b=s.index("    history=[]",a)
s=s[:a]+"    template,template_ref=read(STAGED/'E2_builder/build_e2_mod4v1_sources_v5.py');driver,driver_ref=read(HERE/'derive_e3_builder_v1.py');refs.extend([template_ref,driver_ref])\n    launcher_row=rows['lib/zonglin2_app_launcher.py'];original_launcher,original_launcher_ref=read(Path(launcher_row['local_path']),launcher_row['SHA']);refs.append(original_launcher_ref)\n"+s[b:]
# E3 owner plans are NOT an added gate. Preserve actual97 code; record unknowns.
a="    files['SOURCE_DIFF.patch']="
assert a in s
s=s.replace(a,"    files['E3_FROZEN97_SCOPE_AND_GAPS.json']=J(dict(actual_producer_manifest=install_ref,environment='original_e3_recovery_runtime_v1.RecoveryEnv',recipe_count=13,recovery_bank_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',recovery_bank_bytes=32022178,original_fixed_recovery_pose=34,original_phase_reward_private_command_RNG_retained=True,producer_effort_owner_field='UNDEFINED_OR_UNKNOWN_NOT_ADDED',historical_unimplemented_owner_plan_not_a_new_admission_gate=True,new_coverage_not_claimed=True,fullskill_and_complete_SuperMimic_gap_preserved=True,E3_PT_or_SDK_executed=False))\n"+a,1)
# Replace inherited E2 README entirely with the E3 original protocol description.
a=s.index("    files['README.md']=b'''");b=s.index("    generator=Path(__file__)",a)
s=s[:a]+'''    files['README.md']=b"""# E3 selected1cd -> MOD4v1 source-only overlay

Worker worker_mod4v1_e3.py --mode train --num-envs20000 --run-id ACTUAL --out NEW_JOB/production. Trainer runtime/isaac/mod4/train_mod4v1_e3.py is derived ONLY from original97 train_E3_fullstate_v1 and RecoveryEnv, not E0/H1/W35 environment.

Actual97 complete manifest04e88211... and selected CPUb9f5af6... pin source1cd/14715029/43090/866060/LR.0002562890625000001/prior87. Original E3_PUBLIC_RECOVERY shared variable OWN_E2_H1_KIND remains intentional. Source-cache original D0-D7 plus E3_public_recovery_state/phase/private command RNG, ONE original sensor reset, then original declared-fall placement/publish/age0 are preserved. No fake PhysX exact resume.

Unchanged original RecoveryPhase has13 recipes, original 7 state tensors and original reward masks/upright progress/stable credit/age progression. RecoveryEnv still uses original E3ResetBankCache: bank78af9fa4.../32022178, original joint permutation/q30/fixedpick34, all25200 original points and13 rotations/cache mutation guards. Base flat133/filter74 random reset is a SEPARATE original helper, not a replacement for recovery resets. No raw NPZ/PT is opened by generation.

New2c/bae first import, explicit closure.01m and mimic.01rad/cfg.sim.physics; unchanged solver2.5ms/TGS32,4,50/100Hz, learned STD17Adam/fixedSI/original hardware envelope/reward. New nominal guard wraps the complete original restore. Old517 four-scalar base-bank admission is replaced by exact3body DIFF plus original range witnesses. D6=original gas damping, not all joint friction/hardware coverage.

Original producer has no specifically defined standalone effort-owner field in this join. That remains UNDEFINED/UNKNOWN; no new owner coverage is invented and later unimplemented owner plans are NOT a new admission gate. Preserve actual97 motor/control code and all historic fullskill/SuperMimic gaps. Static success is NOT E3 adaptation or graduation.

ROOT must install complete actual97 manifest runtime/lib/train-deploy/SOURCE_FREEZE/original manifests/bank dependencies into a NEW job before overlay, and provide fresh actual sourceSDK/asset/resource/privateEX/shared-finite/current original owner/budget/Ready/TaskGO. This generator creates NO Task/GO/actual pass. Source PT is metadata only; the runtime cache later allows one physical selected byte/hash/decode with original logical callers and own roundtrips.

Old source labels remain historical. New saved iteration labels start43091, saved iter43090+newupdates/Adam866060+20*newupdates, without an extra optimizer step. Original misleading Native34 receipt filename has24 controls; do not interpret it as34 or extend the protocol. Original freeze/error/reader history remains intact. Parent owns actual execution/independent skill evaluation and Git archival.
"""
'''+s[b:]
ast.parse(s)
out=HERE/'build_e3_mod4v1_sources_v1.py'
with out.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'generator':str(out),'source_only_no_E3_PT_SDK':True,'original97_RecoveryEnv_and13recipe_not_substituted':True},indent=2))
