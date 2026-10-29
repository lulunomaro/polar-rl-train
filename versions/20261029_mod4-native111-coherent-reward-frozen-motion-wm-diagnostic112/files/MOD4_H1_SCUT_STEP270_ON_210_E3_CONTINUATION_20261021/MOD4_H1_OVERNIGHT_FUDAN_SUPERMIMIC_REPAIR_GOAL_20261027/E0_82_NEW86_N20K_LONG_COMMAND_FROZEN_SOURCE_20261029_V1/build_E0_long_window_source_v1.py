"""LOCAL text-only derivation; never opens policy/NPZ/USD or calls SDK/network."""
from pathlib import Path
import ast,hashlib,json,re
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
E2=L/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4'
E3=L/'E3_97_SOURCE210_ENTRY_RECEIPT_CLI_CLOSURE_REPAIR_SOURCE_20261029_V4'
OLD=L/'E0_210_N20K_MEAN_FROZEN_REGRESSION_SOURCE_V1'
M=json.loads((OLD/'E0_FROZEN_CASE_COMPLETE_INPUT_MANIFEST_V2.json').read_bytes())
MODEL='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
OLDMODEL='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
LR='.00038443359375000017';OLDLR='.00022500000000000002'
STAGE='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_LONG_COMMAND_20261029v1/e0'
OLDSTAGE='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v4/e2'
files={
'evaluate_E2_adapted93_new86_frozen900_once_v1.py':'evaluate_E0_adapted82_new86_frozen1000_once_v1.py',
'detached_E2_new86_frozen_profile_supervisor_once_v1.py':'detached_E0_new86_frozen_profile_supervisor_once_v1.py',
'E2_new86_target_source_SDK_metadata_admission_v1.py':'E0_new86_target_source_SDK_metadata_admission_v1.py',
'remote_E2_new86_profile_install_and_detach_v4_originalHeight.py':'remote_E0_new86_long_command_install_and_detach_v1.py',
'upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v4_originalHeight.py':'upload_admit_detach_NEW86_E0_final82_long_command_secure_stdin_UNUSED_once_v1.py',
'e2_profile_domain_telemetry_v1.py':'e0_long_command_domain_telemetry_v1.py',
'e2_original_profile_catalog_candidate_v1.py':'e0_original_profile_catalog_v1.py',
'e2_frozen_worker_call_guard_v3.py':'e0_frozen_worker_call_guard_v1.py',
'E2_frozen_actual_receipts_readonly_CODE_v4.py':'E0_frozen_actual_receipts_readonly_CODE_v1.py',
'run_E2_new86_readonly_secure_stdin_v4.py':'run_E0_new86_readonly_secure_stdin_v1.py',
'read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v4.py':'read_E0_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py',
'collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v4.py':'collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v1.py',
'FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V4.json':'FROZEN_E0_82_NEW86_LONG_COMMAND_SOURCE_INDEX_V1.json',
'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json':'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',
'E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json':'E0_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json',
}
changes=[]
def H(raw):return hashlib.sha256(raw).hexdigest()
def write(n,s):
 raw=s.encode() if isinstance(s,str) else s
 with (B/n).open('xb') as f:f.write(raw)
def sub(s,a,b):
 assert a in s,a
 return s.replace(a,b)
def convert(s):
 for a,b in files.items():s=s.replace(a,b)
 s=s.replace(OLDSTAGE,STAGE).replace(OLDMODEL,MODEL)
 # Tokens with separators only: NEVER replace E2 inside NATIVE24 or a SHA.
 s=s.replace('e2_','e0_').replace('E2_93','E0_82').replace('E2_ADAPTED93','E0_ADAPTED82').replace('E2_ADAPTED93_FINAL92','E0_ADAPTED89D_FINAL82')
 s=s.replace('E2_ADAPTED93_FINAL92.pt','E0_ADAPTED89D_FINAL82.pt').replace('E2_ADAPTED93','E0_ADAPTED82')
 s=s.replace('E2_ADAPTED82_FINAL92.pt','E0_ADAPTED89D_FINAL82.pt')
 s=s.replace('E2_','E0_').replace('_E2','_E0').replace('E2Panel','E0Panel').replace('E2Book','E0Book')
 s=s.replace('E2_WORLD_MOVING_SIGNED4','E0_DIRECTIONAL_SPIN_V1').replace('E0_WORLD_MOVING_SIGNED4','E0_DIRECTIONAL_SPIN_V1')
 s=s.replace('859300','641200').replace('42822','31984').replace(OLDLR,LR).replace('14615089','14031973')
 s=s.replace('MOD4_E0_ADAPTED93','MOD4_E0_ADAPTED82').replace('source/E0_ADAPTED93_FINAL92.pt','source/E0_ADAPTED89D_FINAL82.pt')
 s=s.replace('E2 V4','E0 V1').replace('E2 V2','E0 V1').replace("'E2'","'E0'")
 # Only selected evaluation controls, NOT 900s normal eligibility/read wait.
 for a,b in [("['controls']==900","['controls']==1000"),('controls=900','controls=1000'),('requested_controls=900','requested_controls=1000'),('range(900)','range(1000)'),('completed<900','completed<1000'),("get('controls')==900","get('controls')==1000"),("get('requested_controls')==900","get('requested_controls')==1000"),("get('steady_controls')==800","get('steady_controls')==900"),('requested900_controls_100warm_800steady_complete','requested1000_controls_100warm_900steady_complete')]:s=s.replace(a,b)
 return s
shared=('project_clone_launch_helpers_v1.py','lossless_snapshot_pinned75d683.py','original_flat_height_provider_v1.py','GROUND_PROVIDER_SOURCE_CONTRACT.json')
for n in shared:write(n,(E2/n).read_bytes())
for old,new in files.items():
 if not old.endswith('.py'):continue
 src=(E2/old).read_bytes();s=convert(src.decode('utf8'));write(new,s)
 changes.append(dict(source=str(E2/old),source_SHA=H(src),target=new,target_SHA=H(s.encode()),derivation='bounded text template; special E0 deltas follow, not a runtime proof'))
# Worker: true E0 entry, original E0 command/DR manifest and D1-D7 only.
p=B/files['evaluate_E2_adapted93_new86_frozen900_once_v1.py'];s=p.read_text(encoding='utf8')
s=sub(s,"ORIGINAL_MANIFEST_SHA='ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f'","ORIGINAL_MANIFEST_SHA='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1'")
s=sub(s,"env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP.json'),RM_RESCUE_DEADLINE=str(deadline),RM_SPAWN_GRACE_STEPS='5',OWN_E0_H1_KIND='E0_DIRECTIONAL_SPIN_V1',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')","env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP.json'),RM_RESCUE_DEADLINE=str(deadline))")
s=sub(s,'train_E0_full_resume_v1.py','train_chassis_pd_resume_ppo.py')
s=s.replace(",'E0_COMMAND_RESUME_STARTUP_VERIFIED.json'",'')
s=sub(s,"  assert read(Path(log_dir)/'E0_COMMAND_RESUME_STARTUP_VERIFIED.json')['source_SHA']==MODEL_SHA\n",'')
s=sub(s,"witness['fingerprints']","witness['review']['new_final_tensor_fingerprints']")
s=s.replace('moving_yaw_rad_s=[-4,4]','moving_yaw_signed_abs_rad_s=[1,2]').replace('original_E2_command_bank74_reset_retained','original_E0_command_bank74_reset_retained')
s=s.replace('E2 mean','E0 mean').replace('original E2','original E0').replace('Original E2','Original E0').replace('original_E2','original_E0')
s=s.replace('graduted_skill_claim','graduated_skill_claim')
p.write_text(s,encoding='utf8',newline='\n')
# Exact worker AST env allowance follows this actual source, never blanket-update acceptance.
p=B/'e0_frozen_worker_call_guard_v1.py';s=p.read_text(encoding='utf8');a=s.index('DECLARED_ENV_CALL=');z=s.index('\n',a)
envnode=next(n for n in ast.walk(ast.parse((B/files['evaluate_E2_adapted93_new86_frozen900_once_v1.py']).read_bytes())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='env' and n.func.attr=='update')
s=s[:a]+'DECLARED_ENV_CALL='+repr(ast.unparse(envnode))+s[z:];p.write_text(s,encoding='utf8',newline='\n')
# E0 profile labels preserve true sampled signed moving 1..2rad/s.
p=B/'e0_original_profile_catalog_v1.py';s=p.read_text(encoding='utf8').replace('moving_yaw_minus4','moving_yaw_negative_abs1_to2').replace('moving_yaw_plus4','moving_yaw_positive_abs1_to2').replace('E2_WORLD_MOVING_SIGNED4','E0_DIRECTIONAL_SPIN_V1').replace('E2 command','E0 command');p.write_text(s,encoding='utf8',newline='\n')
# E0 has no E2 native capture extension; original ChassisPD env is the API.
p=B/'e0_long_command_domain_telemetry_v1.py';s=p.read_text(encoding='utf8');s=sub(s,'        assert not e._own_native_capture\n','');s=s.replace('original_E2','original_E0').replace('E2-specific','E0-specific').replace('E2_WORLD_MOVING_SIGNED4','E0_DIRECTIONAL_SPIN_V1');p.write_text(s,encoding='utf8',newline='\n')
# CPU witness uses its ACTUAL nested E0 review schema, no fabricated E2 field aliases.
p=B/'E0_new86_target_source_SDK_metadata_admission_v1.py';s=p.read_text(encoding='utf8');start=s.index(" assert w['passed']");end=s.index(' import torch',start)
s=s[:start]+''' assert w['passed'] and w['model']['SHA']==MODEL_SHA and w['model']['bytes']==14031973 and w['model']['producer_twohost_fullSHA_verified']
 r=w['review'];assert w['new_updates']==82 and r['all_whole_model_tensors_finite'] and r['actor9_critic8_STD6_actor35_critic38'] and r['D1_D7_factors_and_rng_CPU_structure_passed']
 assert r['Adam_states17']==17 and r['Adam_step']==641200 and r['stored_RSL_iteration']==31984 and r['final_adaptive_optimizer_LR']==.00038443359375000017
''' + s[end:]
s=s.replace('original_E2_domain','original_E0_domain').replace('no_W35_profile_or_native_H1_model','no_E2_W35_profile_or_native_H1_model')
p.write_text(s,encoding='utf8',newline='\n')
# Explicit small proof: elapsed source facts, population proposal rejected by strict restore.
term=L/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4/reports/E2_V4_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json';v=json.loads(term.read_bytes())
sup=v['original_terminal']['supervisor']['creation'];end=v['original_terminal']['epoch'];first=max(r['value']['epoch'] for r in v['restore']['D1_D7_original_CUDA_restore_receipts'])
proof=dict(kind='E0_longcase_population_clock_and_saved_throughput_source_design_v1',only_saved_JSON_and_source_reads=True,E2_source=str(term),E2_source_SHA=H(term.read_bytes()),E2_20k900_elapsed_sup_to_terminal=end-sup,E2_startup_to_fullrestore_s=first-sup,E2_900_loop_and_exit_s=end-first,E2_linear_1000_loop_and_startup_estimate_s=first-sup+(end-first)*1000/900,estimate_not_guarantee=True,W35_20k906_wall_limited1680_fact=True,rejected_designs=[dict(num_envs=4096,controls=2000,seconds=40,status='NOT_SELECTED',reason='Original D1-D7 saved num_envs and all per-env arrays strictly bind20k; no projection or guard relaxation authorized'),dict(num_envs=20000,controls=2000,seconds=40,status='NOT_SELECTED',reason='Uncertain throughput against unchanged1680 worker/1800 supervisor; no promise full40s')],selected=dict(num_envs=20000,controls=1000,seconds=20,warmup=100,steady=900,maximum_worker_seconds=1680,supervisor1800=True,original_episode_seconds=20,original_resampling_seconds=[12,16],initial_instance_left_censored=True,observed_resample_reset_lifecycle=True,complete_instance_count_may_be_zero=True,missing_exposure_pending=True,no_full_skill_or_20k_40s_claim=True))
write('SOURCE_DESIGN_AND_REJECTED_POPULATION_PROPOSALS.json',json.dumps(proof,indent=2))
write('TEMPLATE_SOURCE_DERIVATION_REFERENCE.json',json.dumps(dict(files=changes,original_manifest=str(OLD/'E0_FROZEN_CASE_COMPLETE_INPUT_MANIFEST_V2.json'),no_model_or_binary_read=True),indent=2))
print(json.dumps(dict(passed_source_generation_only=True,files=len(changes),throughput_estimate_s=proof['E2_linear_1000_loop_and_startup_estimate_s'])))
