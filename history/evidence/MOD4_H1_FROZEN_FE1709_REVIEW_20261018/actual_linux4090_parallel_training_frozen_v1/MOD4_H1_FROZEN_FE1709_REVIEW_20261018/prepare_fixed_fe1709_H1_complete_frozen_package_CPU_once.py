"""Pinned fe1709 H1 public0/4 frozen evaluator; fresh80, original source plant and clock."""
from pathlib import Path
import os,sys,ast,json,time,hashlib,shutil,zipfile,importlib.util,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True);A=W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017';BASE=A/'e3_closed85_frozen_prepared_v2/payload';S=A/'payload_h1_native/job0/runtime/isaac/mod4';E=B/'h1_fe1709_frozen_v1';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s if isinstance(s,str) else json.dumps(s,indent=2))
CREATE='''
def create_observed_env(args,cfg):
 from h1_takeoff_progress_environment_v2 import H1FullstateEnv
 from h1_takeoff_progress_reward_v2 import configure,isolated_actual_SDK_dt_probe
 from isaaclab.sensors import ContactSensorCfg
 assert cfg.sim.dt==.0025 and cfg.decimation==4 and cfg.scene.num_envs==80
 configure(cfg);cfg.scene.full_robot_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/.*',update_period=0.0,history_length=1,track_air_time=False)
 CONTEXT['declared_eval_integrity_guard']=declared_config(cfg)
 e=H1FullstateEnv(cfg=cfg);CONTEXT['env']=e
 actual=dict(mimic=float(e.termination_manager.get_term_cfg('mimic').params['threshold']),closure=float(e.termination_manager.get_term_cfg('closure').params['threshold']),physics_dt=float(e.cfg.sim.dt),decimation=int(e.cfg.decimation),episode_seconds=float(e.cfg.episode_length_s),num_envs=int(e.num_envs))
 assert actual['mimic']==.01 and actual['closure']==.002 and actual['episode_seconds']>=15 and actual['num_envs']==80
 CONTEXT['actual_eval_integrity_guard']=actual;CONTEXT['save']('ACTUAL_RUNTIME_CONFIG_READBACK.json',dict(actual=actual,declared=CONTEXT['declared_eval_integrity_guard']))
 CONTEXT['save']('H1_ACTUAL_SDK_REWARD_DT_READBACK.json',isolated_actual_SDK_dt_probe(e))
 e._retention_native_witness=Witness(e,args);w=e._retention_native_witness
 e.h1_witness_ids=torch.arange(e.num_envs,device=e.device);e.h1_capture=True
 update=e.scene.update
 def observed_update(dt):
  before=len(w.sub);update(dt)
  if not w.active:return
  assert len(w.sub)==before+1 and len(e.h1_physical_rows)==1
  physical=e.h1_physical_rows.pop();w.sub[-1].update({'H1_'+key:cpu(value) for key,value in physical.items()})
  for key,value in w.sub[-1].items():
   if np.asarray(value).dtype.kind in 'fc':assert np.isfinite(value).all(),('H1 physical nonfinite',key)
 e.scene.update=observed_update
 termination=e.termination_manager.compute
 def observed_termination(*args,**kwargs):
  value=termination(*args,**kwargs)
  if w.active:
   assert e.h1_control_frame is not None
   w.phase.update({'H1_'+key:cpu(value) for key,value in e.h1_control_frame.items()})
   w.phase.update({'H1_phase_'+key:cpu(value) for key,value in e.h1_phase.tensors().items()});e.h1_control_frame=None
  return value
 e.termination_manager.compute=observed_termination
 return e
def build_observed_frozen_policy(vec,path,device):
 from h1_retention_single04_adapter_v1 import build_retention_single
 assert CONTEXT['router_mode']=='single_eval'
 return build_retention_single(vec,path,device)
def finalize_observer(env,result):env._retention_native_witness.finish(result)
'''
RUN='''"""Frozen source H1 zero-twist normal100/request4-next80/normal, no learning."""
from pathlib import Path
import json,torch,numpy as np,time,sys
from h1_frozen_witness_v1 import CONTEXT,create_observed_env,build_observed_frozen_policy,finalize_observer,SMALL_EVAL_CAPACITY,cpu
@torch.inference_mode()
def run_jump(args):
 import h1_external_operator_command_v1
 sys.modules['directional_spin_runtime']=h1_external_operator_command_v1
 import mod4_task as task
 from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
 torch.manual_seed(args.seed);cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=80;cfg.sim.device=args.device;cfg.sim.enable_scene_query_support=True
 for key,value in SMALL_EVAL_CAPACITY.items():setattr(cfg.sim.physics,key,value)
 cfg.scene.wheel_contact_scut.filter_prim_paths_expr=['/World/ground/geometry/mesh'];cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim=64
 env=create_observed_env(args,cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.0);vec,policy,observer=build_observed_frozen_policy(vec,args.checkpoint,env.device)
 env.reset();env._h1_publish_external_request();assert not env.h1_phase.age_control.any() and not env._mod4_mode_bit.any()
 CONTEXT['save']('H1_FRESH80_ORIGINAL_GROUND_RESET_ACTUAL.json',dict(source_SHA=args.checkpoint_sha,fresh80_DR_not_source20000_restore=True,actual_q30=cpu(env.scene['robot'].data.joint_pos).tolist(),actual_root13=cpu(env.scene['robot'].data.root_state_w).tolist(),body_names=env.h1_body_names,contact_names=env.h1_contact_names,authored34_shapes=env.h1_shapes,sourcegeometry_not_cookedShapeLocal=True))
 for tick in range(args.steps):
  env._h1_publish_external_request();assert not env.command_manager.get_term('twist').command.any()
  action=policy(vec.get_observations());vec.step(action)
 from nominal_parameter_audit import parameter_audit
 audit=parameter_audit(env);assert audit['profile']=='white_v3' and audit['actual_parameters_pass']
 CONTEXT['save']('H1_ACTUAL_WHITE_V3_AND_DR_READBACK.json',dict(actual_parameter_audit=audit,physical_action_delay=env._physics_action_delay.audit(),chassis_PD=env.chassis_pd_audit(),sensor_recipe=env._sensor_mild.receipt(),feedback_delay=env.feedback_delay_recipe(),fresh80_DR_not_source20000_restore=True))
 result=dict(case_id=args.case_id,source_SHA=args.checkpoint_sha,seed=args.seed,profile=args.dr_profile,steps=args.steps,callbacks=4*args.steps,original_source_public100_80_clock=True,skill_qualification_claimed=False,no_PPO=True,frozen_architecture_audit=observer.audit(),physical_saved_every_callback=True,actual_fresh80_not_source20k_restore=True)
 finalize_observer(env,result);return result
'''
def main():
 assert not E.exists();torch.set_num_threads(2);rng=torch.get_rng_state().clone();E.mkdir()
 shutil.copytree(BASE,Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pt','E3_CLOSED85*','e3_*','recovery_closed85*'))
 C=Q/'frozen_shared/runtime/isaac/mod4';source_files=[]
 for name in ('h1_public_request_phase_v1.py','h1_takeoff_progress_phase_v2.py','h1_takeoff_progress_environment_v2.py','h1_takeoff_progress_reward_v2.py','h1_reward_scope_v1.py','h1_authored_full_collider_plane_reference_v1.py','h1_external_operator_command_v1.py','h1_original_directional_runtime.py'):
  shutil.copy2(S/name,C/name);source_files.append(dict(name=name,SHA=H(S/name)));assert H(C/name)==H(S/name)
 # Frozen foundation's only chassis-PD difference is the existing read-only parameter auditor.
 def methods(p):return {n.name:ast.dump(n) for c in ast.parse(p.read_text('utf8')).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
 native=methods(S/'chassis_pd_training_env.py');frozen=methods(C/'chassis_pd_training_env.py');assert native.keys()==frozen.keys() and {k for k in native if native[k]!=frozen[k]}=={'chassis_pd_audit'}
 assert H(S/'mod4_task.py')==H(C/'mod4_task.py') and H(S/'mod4_env.py')==H(C/'mod4_env.py')
 components=A/'h1_latest_closed24_frozen_public04_components_CPU_v1'
 for p in components.glob('*.py'):shutil.copy2(p,Q/p.name)
 source=Q/'source/H1_fe1709_closed24.pt';shutil.copy2(A/'actual_closed_H1_final/model_update24.pt',source);assert H(source)=='fe1709ec470aa4995e0b271947b65135d2e0bd43bec26b28316a451c5f1fa49e'
 tree=ast.parse((A/'prepare_E3_closed85_full_frozen_public03_package_CPU_once.py').read_text('utf8'))
 adapter=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ADAPTER' for t in n.targets)))
 adapter=adapter.replace('recovery_closed85_single35_public03_perenv_CPU_v2','h1_closed24_single35_public04_v1').replace('e3_native_witness_v1','h1_frozen_witness_v1').replace('wrapped.env.recovery.mode()','wrapped.env._mod4_mode_bit').replace('E3_','H1_').replace('public_modes_0_or3','public_modes_0_or4').replace('fresh104','fresh80').replace('public0/3','public0/4')
 adapter=adapter.replace('def observed():\n  if','def observed():\n  wrapped.env._h1_publish_external_request()\n  if');write(Q/'h1_retention_single04_adapter_v1.py',adapter)
 witness=(BASE/'e3_native_witness_v1.py').read_text('utf8');witness=witness[:witness.index('\ndef create_observed_env(')]+CREATE
 witness=witness.replace('e3_plane_reference_104_v1','h1_plane_reference80_v1').replace('from recovery_closed85_source_guard_v1 import validate_E3_source','from h1_closed24_source_guard_v1 import validate_H1_source').replace('validate_E3_source(source)','validate_H1_source(source)')
 write(Q/'h1_frozen_witness_v1.py',witness);shutil.copy2(BASE/'e3_plane_reference_104_v1.py',Q/'h1_plane_reference80_v1.py');write(Q/'h1_frozen_jump_loop_v1.py',RUN)
 worker=(BASE/'e3_frozen_worker_v2.py').read_text('utf8').replace('E3_CLOSED85','H1_FE1709').replace('PUBLIC03_FROZEN_V2_20261017','PUBLIC04_FROZEN_V1_20261018').replace('MANIFEST_V2','MANIFEST_V1').replace("choices=['recovery']","choices=['jump']").replace('a.num_envs==104','a.num_envs==80').replace('from recovery_closed85_source_guard_v1 import validate_E3_source','from h1_closed24_source_guard_v1 import validate_H1_source').replace('validate_E3_source(source)','validate_H1_source(source)').replace('e3_native_witness_v1','h1_frozen_witness_v1').replace('from e3_frozen_recovery_loop_v1 import run_recovery','from h1_frozen_jump_loop_v1 import run_jump').replace('run_recovery(a)','run_jump(a)')
 worker=worker.replace('Prepared isolated3060 frozen E2 case','Prepared isolated3060 frozen fixed-fe1709 H1 case');write(Q/'h1_frozen_worker_v1.py',worker)
 parent=(BASE/'e3_frozen_parent_v2.py').read_text('utf8').replace('e3_frozen_worker_v2.py','h1_frozen_worker_v1.py').replace('E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V2','H1_FE1709_FROZEN_COMPLETE_MANIFEST_V1');write(Q/'h1_frozen_parent_v1.py',parent)
 sys.path[:0]=[str(Q),str(C)];from h1_closed24_source_guard_v1 import validate_H1_source;from h1_closed24_single35_public04_v1 import Single35
 ck=torch.load(source,map_location='cpu',weights_only=False);assert validate_H1_source(ck);actor=Single35(source,80,'cpu');assert actor.exact() and not list(actor.model.parameters())
 # Verify actual worker/loop routing and guard literals, not a synthetic SDK run.
 assert "choices=['jump']" in worker and 'a.num_envs==80' in worker and 'run_jump(a)' in worker
 assert 'PUBLIC04_FROZEN_V1_20261018' in worker and 'MANIFEST_V1.json' in worker and 'run_recovery' not in worker
 assert 'cfg.scene.num_envs=80' in RUN and "env.h1_phase.age_control" in RUN and "env._mod4_mode_bit" in adapter
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 recipe=dict(source_SHA=H(source),source_Adam644660=True,source_owned24=True,num_envs=80,seed=20260928,profile='white_v3',normal100_request4_next80_then_normal_per_original_episode=True,zero_twist_original_operator_command=True,native120_then_full1500_with_independent_allrow_CPU=True,not_latest_d723_weights=True,no_source20000_state_restored_into80=True)
 write(Q/'H1_FE1709_PUBLIC04_FROZEN_RECIPE_V1.json',recipe)
 previous=json.loads((BASE/'E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V2.json').read_bytes());env=previous['env'];files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 mf=Q/'H1_FE1709_FROZEN_COMPLETE_MANIFEST_V1.json';manifest=dict(version=1,source=dict(path=str(source),bytes=source.stat().st_size,SHA=H(source)),source_relative='source/H1_fe1709_closed24.pt',source_guard='h1_closed24_source_guard_v1.py',recipe=recipe,env=env,files=files,package_files_v8=[dict(relative=r['relative'],bytes=r['bytes'],sha256=r['SHA']) for r in files],fresh80_not_source20000_restore=True)
 write(mf,manifest);bundle=E/'H1_FE1709_COMPLETE_FROZEN_PAYLOAD_V1.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for row in files:z.write(Q/row['relative'],row['relative'])
  z.write(mf,mf.name)
 out=dict(epoch=time.time(),passed_complete_payload_CPU_only=True,source=manifest['source'],manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),worker=dict(path=str(Q/'h1_frozen_worker_v1.py'),SHA=H(Q/'h1_frozen_worker_v1.py')),parent=dict(path=str(Q/'h1_frozen_parent_v1.py'),SHA=H(Q/'h1_frozen_parent_v1.py')),files=len(files),source_H1_phase_environment_reward_command_modules_exact=source_files,common_mod4_task_env_exact_to_training=True,chassis_PD_physical_methods_AST_exact_only_preexisting_readonly_audit_diff=True,original_actor9_STD_frozen_initial_exact=True,original_public04_components_302tick_28negatives_previously_passed=True,strict_prefix_query80_mimic01_COM1e5_closure002_hardware_original_foundation=True,source_seed20260928_profilewhite_v3_fresh80_not_20k_restore=True,CPU_RNG_unchanged0CUDA0optimizer=True,no249_upload_Task_or_GPU_yet=True,new_own_native_and_full_allrowCPU_pending=True)
 write(R/'H1_FE1709_COMPLETE_FROZEN_PUBLIC04_PACKAGE_CPU_PREPARED_ACTUAL.json',out)
 print(json.dumps(dict(H1_complete_frozen_CPU=True,files=len(files),package_bytes=bundle.stat().st_size,no_GPU=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:write(R/('H1_COMPLETE_FROZEN_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_SSH_Task_GPU_or_PPO=True,partial_package_preserved=True));raise
