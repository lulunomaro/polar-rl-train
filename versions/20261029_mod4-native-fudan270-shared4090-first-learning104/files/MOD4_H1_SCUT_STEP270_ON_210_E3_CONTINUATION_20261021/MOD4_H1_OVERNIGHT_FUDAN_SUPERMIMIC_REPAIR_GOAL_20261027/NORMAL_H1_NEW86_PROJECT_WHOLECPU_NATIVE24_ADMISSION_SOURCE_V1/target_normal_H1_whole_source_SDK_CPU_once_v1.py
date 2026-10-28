"""New target purpose: one typed-model CPU load; CUDA RNG structural only."""
from pathlib import Path
import argparse,ast,hashlib,importlib.metadata as md,importlib.util,inspect,json,math,os,sys,textwrap,time,traceback,types
SOURCE='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4'
ORIGINAL='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ident():
 p=Path('/proc/self');s=(p/'stat').read_text();a=s[s.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
 return dict(pid=os.getpid(),creation=boot+int(a[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.readlink(p/'cwd'))
def leaves(v,torch):
 if torch.is_tensor(v):yield v
 elif isinstance(v,dict):
  for x in v.values():yield from leaves(x,torch)
 elif isinstance(v,(list,tuple)):
  for x in v:yield from leaves(x,torch)
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--manifest-SHA',required=True);p.add_argument('--clone-root',type=Path,required=True);a=p.parse_args();J=a.job_root.resolve();D=a.clone_root.resolve();assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 def put(n,v):
  with (J/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 put('CPU_OWN_WORKER_IDENTITY.json',ident());mf=J/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json';assert H(mf)==a.manifest_SHA;m=json.loads(mf.read_bytes())
 installed=json.loads((J/'ACTUAL_ALL_INPUT_POSTCOPY_FULLSHA_RECEIPT.json').read_bytes());assert installed['passed'] and installed['manifest_SHA']==a.manifest_SHA and installed['job_root']==str(J)
 assert installed['files']==[{k:r[k] for k in ('relative','bytes','SHA')} for r in m['files']]
 for row in m['files']:
  q=J/row['relative'];assert q.resolve().is_relative_to(J) and not q.is_symlink() and q.stat().st_size==row['bytes']
 source=J/'job0/source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt';assert H(source)==SOURCE
 versions={k:md.version(k) for k in ('torch','isaacsim','isaaclab','rsl-rl-lib')};assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}
 modules={k:importlib.util.find_spec(k).origin for k in ('torch','isaacsim','isaaclab','rsl_rl')};assert all(x and Path(x).resolve().is_relative_to(D) for x in modules.values())
 rsl=Path(modules['rsl_rl']).parent;lab=Path(modules['isaaclab']).parent
 for row in m['expected_RSL_sources']:assert (rsl/row['relative']).stat().st_size==row['bytes'] and H(rsl/row['relative'])==row['SHA']
 assert H(lab/'utils/math.py')==m['expected_SDK_math_SHA']
 import torch
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();ck=torch.load(source,map_location='cpu',weights_only=False)
 assert ck['iter']==41448 and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8
 assert ck['actor_state_dict']['distribution.std_param'].shape==(6,) and ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 assert len(ck['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={832460}
 assert ck['optimizer_state_dict']['param_groups'][0]['lr']==.00038443359375000017
 meta=ck['PPO50_gas400_adaptation'];assert meta['schema']=='mod4.normal_H1_PPO86B.original20K.PPO50_gas400.v1' and meta['original_source_SHA']==ORIGINAL and meta['original_population']==meta['target_population']==20000
 assert meta['required_public_phase_tick_increment_per_policy']==2 and meta['public_request_seconds']==[1.,1.8] and meta['original_true270_goal_geometry_unchanged']
 allvals=list(leaves(ck,torch));assert all(x.device.type=='cpu' for x in allvals) and all(bool(torch.isfinite(x).all()) for x in allvals if x.is_floating_point())
 mod=J/'job0/runtime/isaac/mod4';sys.path[:0]=[str(mod),str(J)]
 from spring_pressure_checkpoint import validate_saved_pressure,exact
 from gas_damping_checkpoint import validate_saved_damping
 from chassis_pd_checkpoint import validate_saved_chassis_pd
 validate_saved_pressure(ck['spring_pressure_state'],20000);validate_saved_damping(ck['gas_damping_state'],20000);validate_saved_chassis_pd(ck['chassis_PD_state'],20000)
 from sensor_mild_math import CHANNELS
 sensor=ck['sensor_DR_state'];assert sensor['version']==1 and sensor['n']==20000 and sensor['profile']=='noise_bias_mild_v1' and sensor['bias'].shape==(20000,4) and sensor['episode'].shape==(20000,)
 assert set(sensor['noise_rng'])==set(CHANNELS) and set(sensor['cache']).issubset(CHANNELS)
 def rng_bytes(x):assert torch.is_tensor(x) and x.dtype==torch.uint8 and x.ndim==1 and x.numel()>0
 rng_bytes(sensor['bias_rng'])
 for x in sensor['noise_rng'].values():rng_bytes(x)
 for key in ('sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):
  assert isinstance(ck[key],dict) and ck[key]
  for x in ck[key].values():rng_bytes(x)
 global_rng=ck['sensor_global_rng_state'];rng_bytes(global_rng['cpu']);assert global_rng['cpu'].numel()==rng.numel() and len(global_rng['cuda'])==1
 for x in global_rng['cuda']:rng_bytes(x)
 for key,(last,noise) in sensor['cache'].items():assert last.shape==(20000,) and noise.shape==(20000,CHANNELS[key][0])
 from feedback_delay_checkpoint import validate_delay_state
 from feedback_delay_mild import FeedbackDelay
 assert validate_delay_state(FeedbackDelay(20000,'cpu',20260928),ck['feedback_delay_state'])
 from action_delay_physics_queue import PhysicsActionQueue,FIELDS,WIDTHS
 queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);saved=ck['physical_action_delay_state'];assert saved['control_us']==ck['physical_action_delay_recipe']['control_period_us']==20000
 text=textwrap.dedent(inspect.getsource(PhysicsActionQueue.validate_state));old="        generator=torch.Generator(device=self.device);generator.set_state(state['rng'][key].cpu())"
 new="        value=state['rng'][key]\n        assert torch.is_tensor(value) and value.device.type=='cpu' and value.dtype==torch.uint8 and value.ndim==1 and value.numel()==16"
 assert text.count(old)==1;struct=text.replace(old,new);scope=dict(torch=torch,FIELDS=FIELDS,WIDTHS=WIDTHS);exec(compile(struct,'actual_queue_CPU_structure_only','exec'),scope);before={k:v.clone() for k,v in saved['rng'].items()};assert scope['validate_state'](queue,saved)
 assert all(torch.equal(saved['rng'][k],v) for k,v in before.items())
 from step270_goal_and_scut_rates_candidate import Step270Events
 tree=ast.parse((J/'h1_step270_sdk_runtime_candidate.py').read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Step270Phase');part=ast.Module(body=[cls],type_ignores=[]);ast.fix_missing_locations(part);scope=dict(torch=torch,Step270Events=Step270Events,GEOMETRY=dict(height=.270,edge_x=.35,depth=.8,width=1.2));exec(compile(part,'actual_H1_phase_CPU_state_only','exec'),scope)
 phase=scope['Step270Phase'](types.SimpleNamespace(num_envs=20000,device='cpu'));state=ck['H1_step270_task_state'];assert state['version']==270;phase.load_state_dict(state['phase']);assert exact(phase.state_dict(),state['phase'])
 assert state['private_command_mode_rng'].dtype==torch.uint8 and state['private_command_mode_rng'].ndim==1
 for x in ck['feedback_delay_state']['rng'],state['private_command_mode_rng']:rng_bytes(x)
 from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
 bank=check_runtime_source(mod);assert bank['pose_ranges']['all_poses']==133 and bank['pose_ranges']['original_height_filter_selected_poses']==74
 from physics_clock import validate_clock
 clock=validate_clock(.0025,.02);assert clock['decimation']==8 and clock['policy_hz']==50.
 assert ck['spring_pressure_recipe']['nominal_stiffness_N_m']==2000 and ck['spring_pressure_recipe']['actual_stiffness_bounds_N_m']==[1800,2200]
 from pxr import Usd,UsdPhysics
 stage=Usd.Stage.Open(str(J/'job0/assets/robot.usd'));assert stage;gas=[]
 for name in ('left_gas_slide','right_gas_slide'):
  prim=stage.GetPrimAtPath('/Robot/joints/'+name);joint=UsdPhysics.PrismaticJoint(prim);drive=UsdPhysics.DriveAPI.Get(prim,'linear');r=dict(name=name,k=float(drive.GetStiffnessAttr().Get()),damping=float(drive.GetDampingAttr().Get()),lower=float(joint.GetLowerLimitAttr().Get()),upper=float(joint.GetUpperLimitAttr().Get()))
  assert r['k']==2000 and r['damping']==3 and math.isclose(r['lower'],-.0267046843609,abs_tol=1e-8) and math.isclose(r['upper'],.020639440248416612,abs_tol=1e-8);gas.append(r)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('NORMAL_H1_TARGET_INITIAL_WHOLE_SOURCE_SDK_CPU_ACTUAL.json',dict(passed=True,kind='normal_H1_PPO86B40050_target_initial_whole_CPU_v1',epoch=time.time(),source_SHA=SOURCE,original_source_SHA=ORIGINAL,model_load_count_this_CPU_process=1,manifest_SHA=a.manifest_SHA,executable=sys.executable,versions=versions,module_origins=modules,actor35_critic38_STD6_all17Adam832460_LR_preserved=True,all_fullstate_cpu_finite=True,source_tensor_leaves=len(allvals),D1_D7_private_state_and_H1_phase_CPU_structure=True,queue_original_CUDA16byte_RNG_untouched=True,CPU_generator_substitution=False,actual_CUDA_RNG_restore_passed=False,actual_worker_CUDA_restore_mandatory=True,gas400_CPU_composition=gas,exact133pose74reset_compatibility=bank,clock=clock,new_100Hz_physical_feedback_hook_source_bound=True,actual_192callbacks_48samples_still_pending=True,no_GPU_scene_actor_optimizer_ledger_or_GO=True,skill_qualification=False))
if __name__=='__main__':
 try:main()
 except BaseException:
  args=sys.argv;J=Path(args[args.index('--job-root')+1]);p=J/('NORMAL_H1_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_GPU_or_GO=True),indent=2));raise
