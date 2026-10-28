"""One W35-specific target CPU admission; no simulator scene, GPU or writer."""
from pathlib import Path
import argparse,ast,hashlib,importlib.metadata as md,importlib.util,json,math,os,sys,time,traceback

SOURCE_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
ORIGINAL_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
MANIFEST_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
KIND='MOD4_W35_ADAPTED92_NEW86_CROSSHOST_FULLSTATE_SOURCE_CPU_V1'
WORKER='evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py'
DEPENDENCIES={
 'runtime/assets/source_700N/robot.usd':(8777269,'694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'),
 'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz':(32022178,'78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83')}
def H(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def all_tensors(value,torch):
 if torch.is_tensor(value):yield value
 elif isinstance(value,dict):
  for child in value.values():yield from all_tensors(child,torch)
 elif isinstance(value,(list,tuple)):
  for child in value:yield from all_tensors(child,torch)

def validate_original_CUDA_queue_structure_CPU(queue,state):
 # Same already-validated CPU structural adapter; actual CUDA restore remains
 # in the unmodified real queue loader, never a fabricated CPU RNG substitute.
 import inspect,textwrap,torch
 module=__import__(type(queue).__module__,fromlist=['FIELDS','WIDTHS'])
 source=textwrap.dedent(inspect.getsource(type(queue).validate_state))
 old="        generator=torch.Generator(device=self.device);generator.set_state(state['rng'][key].cpu())"
 new="        value=state['rng'][key]\n        assert torch.is_tensor(value) and value.device.type=='cpu' and value.dtype==torch.uint8 and value.ndim==1 and value.numel()==16, 'Original source-specific CUDA RNG byte structure differs'"
 assert source.count(old)==1;structural=source.replace(old,new)
 scope=dict(torch=torch,FIELDS=module.FIELDS,WIDTHS=module.WIDTHS)
 exec(compile(structural,'<W35 actual queue validator: CPU structural only>','exec'),scope)
 untouched={key:value.clone() for key,value in state['rng'].items()}
 assert scope['validate_state'](queue,state) is True
 assert all(torch.equal(state['rng'][key],value) for key,value in untouched.items())
 return dict(original_validator_source_SHA=hashlib.sha256(source.encode()).hexdigest(),structural_validator_source_SHA=hashlib.sha256(structural.encode()).hexdigest(),
  CPU_fields_timestamps_lag_and_CUDA_uint8_16_structure_only=True,original_CUDA_rng_bytes_untouched=True,CPU_rng_substitution_used=False,
  actual_CUDA_generator_restore_passed=False,actual_worker_CUDA_restore_still_mandatory=True)

def validate_copy_dependency_receipt(root):
 path=root/'W35_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json';receipt=json.loads(path.read_bytes())
 assert receipt['actual_postcopy_fullSHA_verified'] is True and receipt['job_root']==str(root)
 actual={r['relative']:r for r in receipt['files']}
 for relative,(size,sha) in DEPENDENCIES.items():
  item=actual[relative];assert item['bytes']==size and item['SHA']==sha
  p=root/relative;assert p.is_file() and p.stat().st_size==size
 return dict(path=str(path),SHA=H(path),actual_postcopy_fullSHA_reused=True,binaries_not_rehashed_in_this_CPU_reader=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--job-root',required=True,type=Path);args=parser.parse_args();root=args.job_root.resolve()
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 report=root/'W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json';assert not report.exists()
 runtime=root/'runtime';mod=runtime/'isaac/mod4';source=root/'source/W35_ADAPTED92_FINAL78.pt'
 manifest=root/'original_run_manifest.json';assert H(source)==SOURCE_SHA and H(manifest)==MANIFEST_SHA
 original=json.loads(manifest.read_bytes());assert original['num_envs']==20000
 env=original['env'];assert env['RM_KEEP_STD']=='1' and env['RM_PHYSICS_DT_S']=='0.0025' and env['RM_SOLVER_POS']=='32' and env['RM_SOLVER_VEL']=='4'
 dependency=validate_copy_dependency_receipt(root)
 import torch,numpy as np
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();ck=torch.load(source,map_location='cpu',weights_only=False)
 assert ck['iter']==32336 and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8
 assert ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 assert len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={648360}
 assert ck['optimizer_state_dict']['param_groups'][0]['lr']==.00011390625000000003
 assert ck['PPO50_gas400_adaptation']['original_source_SHA']==ORIGINAL_SHA and ck['PPO50_gas400_adaptation']['target_population']==20000
 assert ck['PPO50_gas400_new_updates']==78 and ck['PPO50_gas400_clock']==dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)
 assert ck['spring_pressure_recipe']['nominal_stiffness_N_m']==2000 and ck['physical_action_delay_state']['control_us']==20000
 tensors=list(all_tensors(ck,torch));assert all(x.device.type=='cpu' for x in tensors) and all(torch.isfinite(x).all() for x in tensors if x.is_floating_point())
 sys.path[:0]=[str(mod),str(runtime)]
 from action_delay_physics_queue import PhysicsActionQueue
 queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue_proof=validate_original_CUDA_queue_structure_CPU(queue,ck['physical_action_delay_state'])
 from spring_pressure_checkpoint import validate_saved_pressure
 from gas_damping_checkpoint import validate_saved_damping
 from chassis_pd_checkpoint import validate_saved_chassis_pd
 validate_saved_pressure(ck['spring_pressure_state'],20000);validate_saved_damping(ck['gas_damping_state'],20000);validate_saved_chassis_pd(ck['chassis_PD_state'],20000)
 from g3_terrain_checkpoint import validate as validate_g3
 from retention_command_state import validate as validate_command,PROFILE
 validate_g3(ck['E1_terrain_state'],20000);validate_command(ck['E1_retained_flat_command_state'],20000)
 assert ck['E1_retained_flat_command_state']['rng_device_type']=='cuda' and ck['E1_current_command_profile']==PROFILE
 assert ck['E1_terrain_state']['G3_profile_sha256']==H(mod/'g3_cad_profile.json')
 # Exact used W35 pose/footprint integrity, never the E0 flat74 assumption.
 from W35_gas400_exact_selected_reset_compatibility_v2 import require_W35_exact_four_scalar_asset,verify_original_W35_selected_bank
 metadata=mod/'MOD4_RESET_COLLISION_BANK.json';meta=json.loads(metadata.read_bytes())
 asset=require_W35_exact_four_scalar_asset(meta,metadata,runtime/'assets/robot.usd',runtime/'assets/import_contract.json')
 with np.load(mod/'MOD4_RESET_COLLISION_BANK.npz',allow_pickle=False) as bank:
  pick=int(np.argmin(abs(bank['root_height']-.25)));selected=verify_original_W35_selected_bank(bank,pick)
 assert selected['selected_pose_index']==34
 from physics_clock import validate_clock
 assert validate_clock(.0025)['decimation']==8
 worker=root/WORKER;worker_tree=ast.parse(worker.read_bytes())
 cli=next(n.value for n in ast.walk(worker_tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='sys' and t.attr=='argv' for t in n.targets))
 lr_index=next(i for i,n in enumerate(cli.elts) if isinstance(n,ast.Constant) and n.value=='--learning_rate')
 assert cli.elts[lr_index+1].value=='.00011390625000000003'
 # Actual installed USD CPU composition; no AppLauncher or physics scene.
 from pxr import Usd,UsdPhysics
 stage=Usd.Stage.Open(str(runtime/'assets/robot.usd'));assert stage;gas=[]
 for name in ('left_gas_slide','right_gas_slide'):
  prim=stage.GetPrimAtPath('/Robot/joints/'+name);assert prim and prim.IsA(UsdPhysics.PrismaticJoint)
  joint=UsdPhysics.PrismaticJoint(prim);drive=UsdPhysics.DriveAPI.Get(prim,'linear')
  item=dict(name=name,lower=float(joint.GetLowerLimitAttr().Get()),upper=float(joint.GetUpperLimitAttr().Get()),stiffness=float(drive.GetStiffnessAttr().Get()),damping=float(drive.GetDampingAttr().Get()))
  assert math.isclose(item['lower'],-.0267046843609,rel_tol=0,abs_tol=1e-8) and math.isclose(item['upper'],.020639440248416612,rel_tol=0,abs_tol=1e-8)
  assert item['stiffness']==2000 and item['damping']==3;gas.append(item)
 versions={}
 for name in ('torch','rsl-rl-lib','isaacsim','isaaclab'):
  try:versions[name]=md.version(name)
  except md.PackageNotFoundError:versions[name]=None
 modules={name:(importlib.util.find_spec(name).origin if importlib.util.find_spec(name) else None) for name in ('torch','rsl_rl','isaaclab','isaacsim')};assert all(modules.values())
 copy_root=Path(os.environ['MOD4_PROVEN_CLONE_ROOT']).resolve()
 assert versions=={'torch':'2.10.0+cu128','rsl-rl-lib':'5.0.1','isaacsim':'6.0.1.0','isaaclab':'6.1.14'} and all(Path(x).resolve().is_relative_to(copy_root) for x in modules.values())
 installed=json.loads((root/'W35_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());rsl=Path(modules['rsl_rl']).parent;lab=Path(modules['isaaclab']).parent
 for item in installed['RSL_sources']:assert (rsl/item['relative']).stat().st_size==item['bytes'] and H(rsl/item['relative'])==item['SHA']
 assert H(lab/'utils/math.py')==installed['SDK_math_SHA']
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 value=dict(kind=KIND,attempt_id='W35_ADAPTED92_NEW86_TARGET_INITIAL_WHOLE_CPU_20261029_V1',epoch=time.time(),passed=True,source_SHA=SOURCE_SHA,original_source_SHA=ORIGINAL_SHA,
  original_run_manifest_SHA=MANIFEST_SHA,worker_SHA=H(worker),executable=sys.executable,versions=versions,modules=modules,
  actor35_critic38_original_STD_17Adam_LR=True,constructor_LR_literal_matches_original_optimizer=.00011390625000000003,
  original20k_D1_D7_and_CUDA_rng_codec_retained=True,source_tensors=len(tensors),all_source_cpu_finite=True,
  W35_G3_saved_terrain_structure_valid=True,W35_retained_flat_command_structure_valid=True,actual_command_CUDA_rng_restore_pending=True,
  queue20ms_fields_CPU_structurally_valid=True,queue_structure_proof=queue_proof,
  W35_exact_asset_compatibility=asset,W35_nearest250_selected_bank=selected,binary_dependency_install_receipt=dependency,
  actual_USD_gas400_composition_passed=True,gas_CPU_composed=gas,actual_W35_mesh_GPU_identity_pending=True,
  no_GPU_scene_native_or_PPO_or_account_write=True,actual_CUDA_fullrestore_pending=True,not_skill_qualification=True,
  WM_transition_data_collection_executed=False)
 with report.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(report=str(report),SHA=H(report),passed=True,actual_CUDA_fullrestore_pending=True)))
if __name__=='__main__':
 try:main()
 except Exception:
  argv=sys.argv;root=Path(argv[argv.index('--job-root')+1]) if '--job-root' in argv else Path(__file__).resolve().parent
  p=root/('W35_SOURCE_SDK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  p.write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_GO_or_GPU=True),indent=2),encoding='utf8');raise
