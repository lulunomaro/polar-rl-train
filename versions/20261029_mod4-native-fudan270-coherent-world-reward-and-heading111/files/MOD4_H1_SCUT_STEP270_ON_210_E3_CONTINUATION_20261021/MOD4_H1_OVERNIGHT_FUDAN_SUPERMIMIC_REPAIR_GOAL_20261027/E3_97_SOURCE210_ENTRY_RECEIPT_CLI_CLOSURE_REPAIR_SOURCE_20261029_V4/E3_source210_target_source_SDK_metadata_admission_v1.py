"""New target metadata admission; pins qualified formal CPU witness, never loads PT."""
from pathlib import Path
import argparse,ast,hashlib,importlib.metadata as md,importlib.util,json,math,os,sys,time,traceback
MODEL_SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',required=True,type=Path);a=p.parse_args();J=a.job_root.resolve();assert os.environ['CUDA_VISIBLE_DEVICES']==''
 from source210_project_launch_helpers_v1 import own_identity
 with (J/'E3_CPU_OWN_WORKER_IDENTITY.json').open('x') as f:json.dump(own_identity(os.getpid()),f,indent=2)
 m=json.loads((J/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());receipt=json.loads((J/'E3_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json').read_bytes());assert receipt['actual_postcopy_fullSHA_verified'] and receipt['job_root']==str(J)
 actual={x['relative']:x for x in receipt['files']}
 for x in m['files']:assert actual[x['relative']]['SHA']==x['SHA'] and actual[x['relative']]['bytes']==x['bytes']
 witness=J/'E3_97_QUALIFIED_FORMAL_CPU_WITNESS.json';assert H(witness)==m['qualified_formal_CPU_witness_SHA'];w=json.loads(witness.read_bytes())
 assert w['passed'] and w['model']['SHA']==MODEL_SHA and w['model']['bytes']==14715029 and w['model']['twohost_complete_SHA'] and w['model']['NEW_formal_transfer_count']==1
 assert w['whole_model_all_tensors_finite'] and w['all_critical_D1_D7_and_E3_13recipe_phase_CPU_validated'] and w['actor9_critic8_STD6_original35_38'] and w['all17_Adam_and_original_nonLR_optimizer_settings']
 assert w['new_updates']==87 and w['Adam_step']==866060 and w['stored_iteration']==43090 and w['adaptive_LR']==.0002562890625000001
 assert w['model_loads']=={'NEWformal':1,'input_source':0} and not w['new_branch_skill_qualified']
 import torch
 assert not torch.cuda.is_initialized()
 versions={name:md.version(name) for name in ('torch','rsl-rl-lib','isaacsim','isaaclab','tensordict')}
 assert versions=={'torch':'2.10.0+cu128','rsl-rl-lib':'5.0.1','isaacsim':'6.0.1.0','isaaclab':'6.1.14','tensordict':'0.14.1'}
 assert Path(sys.executable).resolve()==Path('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12').resolve()
 modules={n:importlib.util.find_spec(n).origin for n in ('torch','rsl_rl','isaacsim','isaaclab','tensordict')};assert all(modules.values())
 for r in m['RSL_sources']:
  q=Path(modules['rsl_rl']).parent/r['relative'];assert q.stat().st_size==r['bytes'] and H(q)==r['SHA']
 assert H(Path(modules['isaaclab']).parent/'utils/math.py')==m['SDK_math_SHA']
 worker=J/'evaluate_E3_adapted97_source210_frozen600_once_v1.py';tree=ast.parse(worker.read_bytes())
 cli=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Attribute) and isinstance(x.value,ast.Name) and x.value.id=='sys' and x.attr=='argv' for x in n.targets));i=next(i for i,x in enumerate(cli.elts) if isinstance(x,ast.Constant) and x.value=='--learning_rate');assert cli.elts[i+1].value=='.0002562890625000001'
 from e3_frozen_worker_call_guard_v1 import validate_frozen_worker_calls
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
 # Actual target TensorDict API validation uses only fresh CPU synthetic values.
 from tensordict import TensorDict
 from lossless_snapshot_pinned75d683 import LosslessSnapshot
 s=LosslessSnapshot(torch,3,torch.tensor([0,2]));v=TensorDict({'policy':torch.arange(6).reshape(3,2),'nested':TensorDict({'x':torch.ones(3,1)},batch_size=[3])},batch_size=[3]);out=s._snapshot(v);assert out['snapshot_batch_size']==[2] and out['entries']['policy']['value']==[[0,1],[4,5]]
 assert not torch.cuda.is_initialized()
 from original_flat_height_provider_v1 import validate_flat_height_source
 from selected_telemetry_constructor_API_fixture_v1 import run_selected_constructor_fixture
 ground_contract=json.loads((J/'GROUND_PROVIDER_SOURCE_CONTRACT.json').read_bytes());ground_proof=validate_flat_height_source(J/'runtime/isaac/mod4/mod4_task.py',ground_contract)
 constructor_proof=run_selected_constructor_fixture(J,'E3',torch)
 from e3_declared_entry_receipt_cli_contract_v1 import validate_installed_entry_contract
 entry_closure=validate_installed_entry_contract(J,m,Path(modules['isaaclab']).parent/'app/app_launcher.py')
 result=dict(passed=True,kind='MOD4_E3_ADAPTED97_SOURCE210_SOURCE_SDK_METADATA_WHOLECPU_WITNESS_V1',epoch=time.time(),source_SHA=MODEL_SHA,worker_SHA=H(worker),declared_entry_dependency_CLI_hook_receipt_contract=entry_closure,ground_provider_source_contract=ground_proof,selected_constructor_fresh_CPU_API_fixture=constructor_proof,first_native24_read_wait_maximum_seconds=360,frozen_worker_AST_call_guard=guard,versions=versions,modules=modules,qualified_formal_CPU_witness_SHA=H(witness),qualified_formal_whole_CPU_value=w,whole_CPU_witness_reused_without_PT_decode=True,model_loads_this_metadata_admission=0,target_CPU_model_restore_claimed=False,actual_CUDA_fullrestore_native24_pending=True,actual_source_SDK_and_TensorDict_synthetic_API_passed=True,actual_postcopy_binary_fullSHA_receipt=receipt['manifest_SHA'],actual_USD_gas400_composition_passed=True,gas=gas,bank74=bank,original_E3_domain='E3_PUBLIC_RECOVERY',no_W35_profile_or_native_H1_model=True,no_GPU_scene_or_optimizer_or_account_IO=True)
 with (J/'E3_TARGET_SOURCE_SDK_METADATA_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(passed=True,report_SHA=H(J/'E3_TARGET_SOURCE_SDK_METADATA_ACTUAL.json'),PT_loads=0)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=Path(sys.argv[sys.argv.index('--job-root')+1]);(p/('E3_SOURCE_SDK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc(),no_model_load_or_GPU=True),indent=2),encoding='utf8');raise
