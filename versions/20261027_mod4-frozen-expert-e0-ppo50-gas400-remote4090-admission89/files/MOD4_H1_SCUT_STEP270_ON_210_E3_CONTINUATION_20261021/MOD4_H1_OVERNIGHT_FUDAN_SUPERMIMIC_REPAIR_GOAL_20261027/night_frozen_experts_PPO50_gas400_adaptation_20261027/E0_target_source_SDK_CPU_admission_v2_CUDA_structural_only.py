"""Installed remote CPU admission for the one E0 fork; no GO, GPU scene or writer."""
from pathlib import Path
import argparse, hashlib, importlib.metadata as md, importlib.util, json, math, os, sys, time, traceback

SOURCE_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'
ORIGINAL_SHA='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'
MANIFEST_SHA='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1'
KIND='MOD4_E0_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1'
def H(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def all_tensors(value,torch):
 if torch.is_tensor(value):yield value
 elif isinstance(value,dict):
  for child in value.values():yield from all_tensors(child,torch)
 elif isinstance(value,(list,tuple)):
  for child in value:yield from all_tensors(child,torch)

def validate_original_CUDA_queue_structure_CPU(queue,state):
 # Keep all existing queue field/timestamp/lag checks. Omit ONLY the attempt
 # to load a saved CUDA RNG codec into a CPUGenerator. Do not substitute
 # fabricated CPU RNG bytes and do not claim actual CUDA restore here.
 import inspect,textwrap,hashlib
 import torch
 module=__import__(type(queue).__module__,fromlist=['FIELDS','WIDTHS'])
 source=textwrap.dedent(inspect.getsource(type(queue).validate_state))
 old="        generator=torch.Generator(device=self.device);generator.set_state(state['rng'][key].cpu())"
 new="        value=state['rng'][key]\n        assert torch.is_tensor(value) and value.device.type=='cpu' and value.dtype==torch.uint8 and value.ndim==1 and value.numel()==16, 'Original source-specific CUDA RNG byte structure differs'"
 assert source.count(old)==1
 structural=source.replace(old,new)
 scope=dict(torch=torch,FIELDS=module.FIELDS,WIDTHS=module.WIDTHS)
 exec(compile(structural,'<actual queue validator: CPU structural only>','exec'),scope)
 untouched={key:value.clone() for key,value in state['rng'].items()}
 assert scope['validate_state'](queue,state) is True
 assert all(torch.equal(state['rng'][key],value) for key,value in untouched.items())
 return dict(validator_scope='CPU queue fields/timestamps/lag and original CUDA uint8[16] byte structure only',
             original_validator_source_SHA=hashlib.sha256(source.encode()).hexdigest(),
             structural_validator_source_SHA=hashlib.sha256(structural.encode()).hexdigest(),
             original_CUDA_rng_bytes_untouched=True,CPU_generator_set_state_not_called=True,
             CPU_rng_substitution_used=False,actual_CUDA_generator_restore_passed=False,
             actual_worker_CUDA_restore_still_mandatory=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',required=True,type=Path);a=p.parse_args();root=a.job_root.resolve()
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 report=root/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';assert not report.exists()
 runtime=root/'runtime';mod=runtime/'isaac/mod4';source=root/'source/E0_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt';manifest=root/'original_run_manifest.json'
 assert H(source)==SOURCE_SHA and H(manifest)==MANIFEST_SHA
 original=json.loads(manifest.read_bytes());assert original['num_envs']==20000
 env=original['env'];assert env['RM_KEEP_STD']=='1' and env['RM_PHYSICS_DT_S']=='0.0025' and env['RM_SOLVER_POS']=='32' and env['RM_SOLVER_VEL']=='4'
 import torch
 torch.set_num_threads(2);cpu_rng=torch.get_rng_state().clone();ck=torch.load(source,map_location='cpu',weights_only=False)
 assert ck['iter']==31903 and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8
 assert ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 assert len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={639560}
 assert ck['optimizer_state_dict']['param_groups'][0]['lr']==.00038443359375000017
 assert ck['spring_pressure_state']['n']==20000 and ck['spring_pressure_recipe']['nominal_stiffness_N_m']==2000
 assert ck['physical_action_delay_state']['control_us']==20000
 assert ck['PPO50_gas400_adaptation']['original_source_SHA']==ORIGINAL_SHA and ck['PPO50_gas400_adaptation']['target_population']==20000
 tensors=list(all_tensors(ck,torch));assert all(x.device.type=='cpu' for x in tensors) and all(torch.isfinite(x).all() for x in tensors if x.is_floating_point())
 sys.path[:0]=[str(mod),str(runtime)]
 from action_delay_physics_queue import PhysicsActionQueue
 queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue_structure_proof=validate_original_CUDA_queue_structure_CPU(queue,ck['physical_action_delay_state'])
 from spring_pressure_checkpoint import validate_saved_pressure
 from gas_damping_checkpoint import validate_saved_damping
 from chassis_pd_checkpoint import validate_saved_chassis_pd
 validate_saved_pressure(ck['spring_pressure_state'],20000);validate_saved_damping(ck['gas_damping_state'],20000);validate_saved_chassis_pd(ck['chassis_PD_state'],20000)
 from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
 reset=check_runtime_source(mod);assert reset['passed']
 from physics_clock import validate_clock
 assert validate_clock(.0025)['decimation']==8
 # Parse the new tiny USD layer with the actual installed USD CPU bindings.
 from pxr import Usd,UsdPhysics
 stage=Usd.Stage.Open(str(runtime/'assets/robot.usd'));assert stage
 gas=[]
 for name in ('left_gas_slide','right_gas_slide'):
  prim=stage.GetPrimAtPath('/Robot/joints/'+name);assert prim and prim.IsA(UsdPhysics.PrismaticJoint)
  joint=UsdPhysics.PrismaticJoint(prim);drive=UsdPhysics.DriveAPI.Get(prim,'linear')
  row=dict(name=name,lower=float(joint.GetLowerLimitAttr().Get()),upper=float(joint.GetUpperLimitAttr().Get()),stiffness=float(drive.GetStiffnessAttr().Get()),damping=float(drive.GetDampingAttr().Get()))
  assert math.isclose(row['lower'],-.0267046843609,rel_tol=0,abs_tol=1e-8) and math.isclose(row['upper'],.020639440248416612,rel_tol=0,abs_tol=1e-8)
  assert row['stiffness']==2000 and row['damping']==3;gas.append(row)
 # Version/API evidence comes from this installed interpreter. No sim/app import.
 versions={}
 for name in ('torch','rsl-rl-lib','isaacsim','isaaclab'):
  try:versions[name]=md.version(name)
  except md.PackageNotFoundError:versions[name]=None
 modules={name:(importlib.util.find_spec(name).origin if importlib.util.find_spec(name) else None) for name in ('torch','rsl_rl','isaaclab','isaacsim')}
 assert all(modules.values())
 assert torch.equal(cpu_rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 value=dict(kind=KIND,attempt_id='E0_TARGET_SOURCE_SDK_CPU_20261027_V1',epoch=time.time(),passed=True,source_SHA=SOURCE_SHA,
            original_source_SHA=ORIGINAL_SHA,original_run_manifest_SHA=MANIFEST_SHA,worker_SHA=H(root/'E0_PPO50_gas400_finite_worker_v1.py'),
            executable=sys.executable,versions=versions,modules=modules,actor35_critic38_original_STD_17Adam_LR=True,
            original20k_D1_D7_and_CUDA_rng_codec_retained=True,source_tensors=len(tensors),all_source_cpu_finite=True,
            queue20ms_fields_CPU_structurally_valid=True,queue_structure_proof=queue_structure_proof,admission_reader_version='V2_CUDA_structural_only',reset_bank_source_CPU=reset,actual_USD_gas400_composition_passed=True,gas_CPU_composed=gas,
            no_GPU_scene_or_native_or_PPO_or_account_write=True,actual_CUDA_fullrestore_pending=True,not_skill_qualification=True)
 with report.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(report=str(report),SHA=H(report),kind=KIND,passed=True,actual_CUDA_fullrestore_pending=True)))
if __name__=='__main__':
 try:main()
 except Exception:
  args=sys.argv;root=Path(args[args.index('--job-root')+1]) if '--job-root' in args else Path(__file__).resolve().parent
  error=root/('E0_SOURCE_SDK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  error.write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_GO_or_GPU=True),indent=2),encoding='utf8');raise
