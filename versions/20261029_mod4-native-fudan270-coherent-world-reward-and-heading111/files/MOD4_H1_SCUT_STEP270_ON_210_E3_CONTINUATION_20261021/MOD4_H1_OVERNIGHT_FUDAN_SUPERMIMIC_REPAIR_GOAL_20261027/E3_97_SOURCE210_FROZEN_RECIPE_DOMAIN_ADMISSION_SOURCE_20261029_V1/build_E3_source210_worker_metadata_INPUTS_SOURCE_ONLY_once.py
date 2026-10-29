"""Only source/JSON text: E3 qualified97 CPU witness plus proven bounded eval ABI."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;E2=L/'E2_93_NEW86_TYPED_AST_ENV_GUARD_REPAIR_SOURCE_20261029_V3';E3=L/'E3_97_NEW86_FROZEN_RECIPE_DOMAIN_SOURCE_PREPARATION_20261029_V1';W35=L/'W35_PROFILE_PANEL210_TENSORDICT_SNAPSHOT_REPAIR_UNUSED_SOURCE_20261029_V3'
J='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v1/e3';MODEL='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'
WORKER='evaluate_E3_adapted97_source210_frozen600_once_v1.py';CPU='E3_source210_target_source_SDK_metadata_admission_v1.py'
def H(raw):return hashlib.sha256(raw).hexdigest()
def write(n,b):
 with (B/n).open('xb') as f:f.write(b)
def put(n,v):write(n,(json.dumps(v,indent=2)+'\n').encode())
def common(text):
 for a,b in [('E2','E3'),('OWN_E3_H1_KIND','OWN_E2_H1_KIND'),('E3_WORLD_MOVING_SIGNED4','E3_PUBLIC_RECOVERY'),('b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1',MODEL),('14615089','14715029'),('859300','866060'),('42822','43090'),('.00022500000000000002','.0002562890625000001'),('E3_ADAPTED93','E3_ADAPTED97'),('E3_93_QUALIFIED','E3_97_QUALIFIED'),('FINAL92.pt','FINAL87.pt'),('E3_adapted93','E3_adapted97'),('NEW86_FROZEN_PROFILE_DOMAIN_V1','SOURCE210_FROZEN_RECIPE_DOMAIN_V1')]:text=text.replace(a,b)
 return text
def main():
 (B/'reports').mkdir(exist_ok=True)
 for n in ('e3_original_recipe_phase_catalog_v1.py','e3_recipe_domain_telemetry_v1.py'):write(n,(E3/n).read_bytes())
 write('lossless_snapshot_pinned75d683.py',(E2/'lossless_snapshot_pinned75d683.py').read_bytes())
 source=(E2/'evaluate_E2_adapted93_new86_frozen900_once_v1.py').read_bytes();worker=common(source.decode()).replace('task[\'controls\']==900',"task['controls']==600").replace('range(900)','range(600)').replace('requested_controls=900','requested_controls=600').replace('completed<900','completed<600').replace('e2_profile_domain_telemetry_v1','e3_recipe_domain_telemetry_v1').replace('E3Panel','E3Panel')
 worker=worker.replace('e3_profile_domain_telemetry_v1','e3_recipe_domain_telemetry_v1').replace('actual_target86_SDK_admission_passed','actual_source210_SDK_admission_passed').replace('GPU-90a66ae2-f536-7033-79c0-487536ae36d3','GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e')
 worker=worker.replace('E3_NEW86_CPU_ORIGINAL_WAIT_PROOF.json','E3_SOURCE210_CPU_ORIGINAL_WAIT_PROOF.json').replace('E3_TARGET_SOURCE_SDK_METADATA_ACTUAL.json','E3_TARGET_SOURCE_SDK_METADATA_ACTUAL.json').replace('E3_COMMAND_RESUME_STARTUP_VERIFIED.json','E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json')
 old="assert not cmd.manual_evaluation_mode and cmd._dt==.02 and cmd.progress_goal==.5 and cmd.pure_max==4*__import__('math').pi";assert worker.count(old)==1
 worker=worker.replace(old,"assert cmd.manual_evaluation_mode and cmd._dt==.02 and not bool(cmd.command.any())\n  assert not real.e3_capture and real._e3_fixed_reset_cache.pick==34 and real._e3_fixed_reset_cache.source_sha=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'\n  assert len(real.e3_shapes)==34 and real.recovery.recipe.shape==(20000,)")
 lines=worker.splitlines();hits=[i for i,s in enumerate(lines) if "put('ORIGINAL_E3_COMMAND_AND_TERMINATION_CRITERIA.json'" in s];assert len(hits)==1
 lines[hits[0]]="  put('ORIGINAL_E3_COMMAND_AND_TERMINATION_CRITERIA.json',dict(original_kind='E3_PUBLIC_RECOVERY',recipes=13,original_request_public100Hz_age_lt300_seconds=3,original_stable_public100Hz_ticks_ge50_seconds=.5,original_gravity_z_lt=-.984807753,original_root_speed_lt=.03,original_angular_speed_lt=.2,command3='original zero via RecoveryEnv.publish',selected_fixed_q_bank_pose=34,criterion_terms=declarations,original_soft_masks_and_reset_unmodified=True,skill_graduation=False))"
 worker='\n'.join(lines)+'\n';worker=worker.replace("assert H(source)==MODEL_SHA", "assert H(source)==MODEL_SHA")
 needle="original=read(job/'original_run_manifest.json');assert H(job/'original_run_manifest.json')==ORIGINAL_MANIFEST_SHA"
 kit="K=job/'kit_isolation';assert not K.exists();K.mkdir()\n for name in ('data','DerivedDataCache'):(K/name).mkdir()\n with (K/'data/user.config.json').open('x') as f:f.write('{}')\n os.environ['MOD4_E3_OWN_KIT_STORAGE_ROOT']=str(K)\n "+needle
 assert worker.count(needle)==1;worker=worker.replace(needle,kit)
 needle="ns=runpy.run_path(str(entry),run_name='frozen_E3_original93_restore_config')";assert worker.count(needle)==1
 worker=worker.replace(needle,"import zonglin2_app_launcher as own_launcher;assert Path(own_launcher.__file__).resolve()==job/'lib/zonglin2_app_launcher.py'\n "+needle+"\n import carb\n settings=carb.settings.get_settings();assert Path(settings.get('/UJITSO/datastore/localCachePath')).resolve()==K/'DerivedDataCache' and Path(settings.get('/app/userConfigPath')).resolve()==K/'data/user.config.json'\n assert settings.get('/physics/cooking/ujitsoCollisionCooking') is True and settings.get('/physics/cooking/ujitsoRemoteCacheEnabled') is False and settings.get('/persistent/physics/cooking/ujitsoCookingMaxProcessCount')==16\n put('ACTUAL_OWN_KIT_STORAGE_PATHS_BEFORE_ENV.json',dict(passed=True,cache=str(K/'DerivedDataCache'),user_config=str(K/'data/user.config.json'),cooking_controls_unchanged=True,no_global_cache_changed=True))")
 ast.parse(worker);write(WORKER,worker.encode())
 guard=common((E2/'e2_frozen_worker_call_guard_v3.py').read_text());ast.parse(guard);write('e3_frozen_worker_call_guard_v1.py',guard.encode())
 cpu=common((E2/'E2_new86_target_source_SDK_metadata_admission_v1.py').read_text()).replace('project_clone_launch_helpers_v1','source210_project_launch_helpers_v1').replace('evaluate_E3_adapted97_new86_frozen900_once_v1.py',WORKER).replace('all_critical_D1_D7_and_E3_command_CPU_validated','all_critical_D1_D7_and_E3_13recipe_phase_CPU_validated').replace("w['new_updates']==92","w['new_updates']==87").replace('e2_frozen_worker_call_guard_v3','e3_frozen_worker_call_guard_v1').replace('e3_frozen_worker_call_guard_v3','e3_frozen_worker_call_guard_v1')
 old="D=Path(os.environ['MOD4_PROVEN_CLONE_ROOT']).resolve();modules={n:importlib.util.find_spec(n).origin for n in ('torch','rsl_rl','isaacsim','isaaclab','tensordict')};assert all(Path(x).resolve().is_relative_to(D) for x in modules.values())";assert cpu.count(old)==1
 cpu=cpu.replace(old,"assert Path(sys.executable).resolve()==Path('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12').resolve()\n modules={n:importlib.util.find_spec(n).origin for n in ('torch','rsl_rl','isaacsim','isaaclab','tensordict')};assert all(modules.values())")
 ast.parse(cpu);write(CPU,cpu.encode())
 launcher=(W35/'zonglin2_app_launcher.py').read_bytes();new=launcher.replace(b'MOD4_W35_OWN_KIT_STORAGE_ROOT',b'MOD4_E3_OWN_KIT_STORAGE_ROOT').replace(b'/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v3/w35/kit_isolation',(J+'/kit_isolation').encode())
 assert new.replace(b'MOD4_E3_OWN_KIT_STORAGE_ROOT',b'MOD4_W35_OWN_KIT_STORAGE_ROOT').replace((J+'/kit_isolation').encode(),b'/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v3/w35/kit_isolation')==launcher;ast.parse(new);write('zonglin2_app_launcher.py',new)
 for n in ('AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py','PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py'):write(n,(W35/n).read_bytes())
 witness=L/'TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1/reports/E3_97_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json';raw=witness.read_bytes();v=json.loads(raw);assert v['passed'] and v['model']['SHA']==MODEL and v['Adam_step']==866060 and v['adaptive_LR']==.0002562890625000001;write('E3_97_QUALIFIED_FORMAL_CPU_WITNESS.json',raw)
 put('E3_SOURCE210_WORKER_METADATA_DERIVATION_PENDING_INPUT_MANIFEST.json',dict(source_only=True,target_root=J,worker=WORKER,CPU=CPU,source_model=v['model'],qualified_witness_SHA=H(raw),worker_base=str(E2/'evaluate_E2_adapted93_new86_frozen900_once_v1.py'),worker_base_SHA=H(source),worker_SHA=H(worker.encode()),CPU_SHA=H(cpu.encode()),unchanged_E3_runtime_inputs_required=True,launcher_old_SHA=H(launcher),launcher_new_SHA=H(new),launcher_inverse_exact=True,original13recipe_request3s_recoverypoint5s_not_H1_270=True,no_binary_PT_NPZ_raw_or_SDK_remote_GPU_call=True))
 print(json.dumps(dict(passed=True,worker=WORKER,CPU=CPU,model_source_SHA=MODEL,source_only=True)))
if __name__=='__main__':main()
