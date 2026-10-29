"""New target metadata admission; pins qualified formal CPU witness, never loads PT."""
from pathlib import Path
import argparse,ast,hashlib,importlib.metadata as md,importlib.util,json,math,os,sys,time,traceback
MODEL_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',required=True,type=Path);a=p.parse_args();J=a.job_root.resolve();assert os.environ['CUDA_VISIBLE_DEVICES']==''
 from project_clone_launch_helpers_v1 import own_identity
 with (J/'E0_CPU_OWN_WORKER_IDENTITY.json').open('x') as f:json.dump(own_identity(os.getpid()),f,indent=2)
 m=json.loads((J/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json').read_bytes());receipt=json.loads((J/'E0_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json').read_bytes());assert receipt['actual_postcopy_fullSHA_verified'] and receipt['job_root']==str(J)
 actual={x['relative']:x for x in receipt['files']}
 for x in m['files']:assert actual[x['relative']]['SHA']==x['SHA'] and actual[x['relative']]['bytes']==x['bytes']
 witness=J/'E0_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json';assert H(witness)==m['qualified_formal_CPU_witness_SHA'];w=json.loads(witness.read_bytes())
 assert w['passed'] and w['model']['SHA']==MODEL_SHA and w['model']['bytes']==14031973 and w['model']['producer_twohost_fullSHA_verified']
 r=w['review'];assert w['new_updates']==82 and r['all_whole_model_tensors_finite'] and r['actor9_critic8_STD6_actor35_critic38'] and r['D1_D7_factors_and_rng_CPU_structure_passed']
 assert r['Adam_states']==17 and r['Adam_step']==641200 and r['stored_RSL_iteration']==31984 and r['final_adaptive_optimizer_LR']==.00038443359375000017
 import torch
 assert not torch.cuda.is_initialized()
 versions={name:md.version(name) for name in ('torch','rsl-rl-lib','isaacsim','isaaclab','tensordict')}
 assert versions=={'torch':'2.10.0+cu128','rsl-rl-lib':'5.0.1','isaacsim':'6.0.1.0','isaaclab':'6.1.14','tensordict':'0.14.1'}
 D=Path(os.environ['MOD4_PROVEN_CLONE_ROOT']).resolve();modules={n:importlib.util.find_spec(n).origin for n in ('torch','rsl_rl','isaacsim','isaaclab','tensordict')};assert all(Path(x).resolve().is_relative_to(D) for x in modules.values())
 for r in m['RSL_sources']:
  q=Path(modules['rsl_rl']).parent/r['relative'];assert q.stat().st_size==r['bytes'] and H(q)==r['SHA']
 assert H(Path(modules['isaaclab']).parent/'utils/math.py')==m['SDK_math_SHA']
 worker=J/'evaluate_E0_adapted82_new86_frozen1000_once_v2_early.py';tree=ast.parse(worker.read_bytes())
 cli=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Attribute) and isinstance(x.value,ast.Name) and x.value.id=='sys' and x.attr=='argv' for x in n.targets));i=next(i for i,x in enumerate(cli.elts) if isinstance(x,ast.Constant) and x.value=='--learning_rate');assert cli.elts[i+1].value=='.00038443359375000017'
 from e0_frozen_worker_call_guard_v1 import validate_frozen_worker_calls
 guard=validate_frozen_worker_calls(tree)
 mod=J/'runtime/isaac/mod4';sys.path[:0]=[str(mod),str(J/'runtime')]
 from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
 bank=check_runtime_source(mod);assert bank['passed'] and bank['pose_ranges']['original_height_filter_selected_poses']==74
 from pxr import Usd,UsdPhysics
 stage=Usd.Stage.Open(str(J/'runtime/assets/robot.usd'));assert stage;gas=[]
 for n in ('left_gas_slide','right_gas_slide'):
  prim=stage.GetPrimAtPath('/Robot/joints/'+n);assert prim and prim.IsA(UsdPhysics.PrismaticJoint);q=UsdPhysics.PrismaticJoint(prim);d=UsdPhysics.DriveAPI.Get(prim,'linear')
  r=dict(name=n,lower=float(q.GetLowerLimitAttr().Get()),upper=float(q.GetUpperLimitAttr().Get()),stiffness=float(d.GetStiffnessAttr().Get()),damping=float(d.GetDampingAttr().Get()))
  assert math.isclose(r['lower'],-.0267046843609,abs_tol=1e-8,rel_tol=0) and math.isclose(r['upper'],.020639440248416612,abs_tol=1e-8,rel_tol=0) and r['stiffness']==2000 and r['damping']==3;gas.append(r)
 prior_path=J/'E0_PREVIOUS_SAMEHOST_FULL1000_WITNESS.json';assert H(prior_path)==m['samehost_V1_witness_SHA'];prior=json.loads(prior_path.read_bytes());pv=prior['original_terminal'];pr=pv['result']
 assert prior['source_SHA']==MODEL_SHA and prior['old_job']=='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_LONG_COMMAND_20261029v1/e0' and prior['source_GPU_case_complete'] and not prior['original_errors'] and not prior['integrity']
 assert pv['actual_worker_waited'] and pv['returncode']==0 and pv['private_EX_released'] and pv['passed_frozen_execution'] and pr['controls']==1000 and pr['num_envs']==20000 and pr['core_actor_critic_STD_norm_optimizer_literal_unchanged'] and pr['all17_Adam_steps']==641200 and pr['actual_LR_unchanged']==.00038443359375000017
 from E0_actual_target_method_lifecycle_CPU_fixture_v2 import run_fixture
 command_file=Path(modules['isaaclab']).parent/'managers/command_manager.py';velocity_file=Path(modules['isaaclab']).parent/'envs/mdp/commands/velocity_command.py'
 command_raw=command_file.read_bytes();velocity_raw=velocity_file.read_bytes()
 early_API=run_fixture(J,torch,command_raw,velocity_raw,J/'CPU_E0_ACTUAL_TARGET_METHOD_LIFECYCLE')
 assert early_API['passed'] and not torch.cuda.is_initialized()
 # Actual target TensorDict API validation uses only fresh CPU synthetic values.
 from tensordict import TensorDict
 from lossless_snapshot_pinned75d683 import LosslessSnapshot
 s=LosslessSnapshot(torch,3,torch.tensor([0,2]));v=TensorDict({'policy':torch.arange(6).reshape(3,2),'nested':TensorDict({'x':torch.ones(3,1)},batch_size=[3])},batch_size=[3]);out=s._snapshot(v);assert out['snapshot_batch_size']==[2] and out['entries']['policy']['value']==[[0,1],[4,5]]
 assert not torch.cuda.is_initialized()
 from original_flat_height_provider_v1 import validate_flat_height_source
 from selected_telemetry_constructor_API_fixture_v1 import run_selected_constructor_fixture
 ground_contract=json.loads((J/'GROUND_PROVIDER_SOURCE_CONTRACT.json').read_bytes());ground_proof=validate_flat_height_source(J/'runtime/isaac/mod4/mod4_task.py',ground_contract)
 constructor_proof=run_selected_constructor_fixture(J,'E0',torch)
 from e0_declared_entry_receipt_cli_contract_v1 import validate_installed_entry_contract
 entry_proof=validate_installed_entry_contract(J,m,Path(modules['isaaclab']).parent/'app/app_launcher.py')
 result=dict(passed=True,kind='MOD4_E0_ADAPTED82_NEW86_EARLY_SOURCE_SDK_METADATA_WHOLECPU_WITNESS_V2',epoch=time.time(),source_SHA=MODEL_SHA,worker_SHA=H(worker),ground_provider_source_contract=ground_proof,selected_constructor_fresh_CPU_API_fixture=constructor_proof,actual_target_CommandTerm_method_AST_passed=True,actual_target_method_CPU_lifecycle=early_API,actual_target_method_CPU_lifecycle_helper_SHA=H(J/"e0_early_original_resample_passthrough_observer_v1.py"),actual_command_source_path=str(command_file),actual_command_source_SHA=H(command_file),actual_velocity_source_path=str(velocity_file),actual_velocity_source_SHA=H(velocity_file),samehost_qualified_V1_case_witness_SHA=H(prior_path),declared_entry_CLI_hook_receipt_dependency_closure=entry_proof,first_native24_read_wait_maximum_seconds=360,frozen_worker_AST_call_guard=guard,versions=versions,modules=modules,qualified_formal_CPU_witness_SHA=H(witness),qualified_formal_whole_CPU_value=w,whole_CPU_witness_reused_without_PT_decode=True,model_loads_this_metadata_admission=0,target_CPU_model_restore_claimed=False,actual_CUDA_fullrestore_native24_pending=True,actual_source_SDK_and_TensorDict_synthetic_API_passed=True,actual_postcopy_binary_fullSHA_receipt=receipt['manifest_SHA'],actual_USD_gas400_composition_passed=True,gas=gas,bank74=bank,original_E0_domain='E0_DIRECTIONAL_SPIN_V1',no_E2_W35_profile_or_native_H1_model=True,no_GPU_scene_or_optimizer_or_account_IO=True)
 with (J/'E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(passed=True,report_SHA=H(J/'E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json'),PT_loads=0)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=Path(sys.argv[sys.argv.index('--job-root')+1]);(p/('E0_SOURCE_SDK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc(),no_model_load_or_GPU=True),indent=2),encoding='utf8');raise
