"""Fresh104 E3 evaluator preparation; actual source reset/phase CPU, no target dispatch."""
from pathlib import Path
import ast,os,sys,time,json,hashlib,shutil,zipfile,types,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017';K=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017';A=K/'e2_closed112_frozen_prepared_v10/payload';S=M/'payload/recovery/job0/runtime/isaac/mod4';E=B/'e3_closed85_frozen_prepared_v1';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
ADAPTER='''"""Actual per-environment public0/3 source actor; no hidden phase supplied to actor."""
from pathlib import Path
import numpy as np,torch,time
from tensordict import TensorDict
from recovery_closed85_single35_public03_perenv_CPU_v2 import Single35,EXPECTED
def build_retention_single(vec,path,device):
 from frozen_history_policy import DecisionHistoryVec
 from e3_native_witness_v1 import CONTEXT,cpu
 before=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state(device).clone();c=Single35(path,vec.num_envs,device)
 assert c.exact() and torch.equal(before,torch.get_rng_state()) and torch.equal(cuda,torch.cuda.get_rng_state(device))
 CONTEXT['save']('E3_FROZEN_SOURCE_ACTUAL.json',dict(source_SHA=EXPECTED,source_path=str(path),actor9_including_STD_initial_exact=True,construction_RNG_unchanged=True,critic_optimizer_gate_not_loaded_to_GPU=True,no_PPO=True,fresh104_not_source20000_fullstate_restore=True))
 wrapped=DecisionHistoryVec(vec,'A0');get=wrapped.get_observations;step0=wrapped.step;rows=[];timing=[];start=[None]
 def observed():
  if c.pending is None:torch.cuda.synchronize(device);start[0]=time.perf_counter()
  p=c.begin(int(wrapped.env.common_step_counter),lambda:get()['policy'],wrapped.env.recovery.mode())
  assert not p['shared_obs'][:,:3].any()
  wrapped.env._retention_native_witness.obs=cpu(p['shared_obs'])
  return TensorDict(dict(policy=p['shared_obs']),batch_size=[vec.num_envs])
 def policy(obs):
  assert c.pending is not None and torch.equal(obs['policy'],c.pending['shared_obs'])
  result=c.pending['raw_action'];wrapped.env._retention_native_witness.raw_action=cpu(result)
  torch.cuda.synchronize(device);timing.append((time.perf_counter()-start[0])*1000);rows.append({k:cpu(v) for k,v in c.pending.items()});return result
 def step(action):
  assert c.pending is not None and torch.equal(action,c.pending['raw_action'])
  result=step0(action);actual=wrapped.env._retention_native_witness.rows[-1]
  c.finish(torch.as_tensor(actual['processed_action'],device=device),torch.as_tensor(actual['terminated']|actual['truncated'],device=device));return result
 class Observer:
  def audit(self):
   import hashlib
   assert c.controls==c.calls==len(rows)==len(timing) and c.pending is None and c.exact()
   p=Path(CONTEXT['output_dir'])/'E3_SINGLE_FULL_CONTROL_ACTUAL.npz';assert not p.exists();np.savez_compressed(p,**{k:np.stack([r[k] for r in rows]) for k in rows[0]},inference_chain_wall_ms=np.asarray(timing))
   out=dict(source_SHA=EXPECTED,actor9_STD_initial_final_literalexact=True,controls=c.controls,provider_calls=c.calls,public_modes_0_or3_actual_perenv=True,whole6_clip6_previous_actual6_selectedreset=True,no_PPO=True,optimizer_updates=0,raw=dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()),host_latency_not_board_deadline=True)
   CONTEXT['save']('E3_SINGLE_POLICY_CONTROL_ACTUAL.json',out);return out
 wrapped.get_observations=observed;wrapped.step=step
 return wrapped,policy,Observer()
'''
ENV_CREATE='''
def create_observed_env(args,cfg):
 from e3_recovery_runtime_v1 import RecoveryEnv,configure
 from isaaclab.sensors import ContactSensorCfg
 assert cfg.sim.dt==.0025 and cfg.decimation==4 and cfg.scene.num_envs==104
 configure(cfg);cfg.scene.full_robot_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/.*',update_period=0.0,history_length=1,track_air_time=False)
 CONTEXT['declared_eval_integrity_guard']=declared_config(cfg)
 e=RecoveryEnv(cfg=cfg);CONTEXT['env']=e
 actual=dict(mimic=float(e.termination_manager.get_term_cfg('mimic').params['threshold']),closure=float(e.termination_manager.get_term_cfg('closure').params['threshold']),physics_dt=float(e.cfg.sim.dt),decimation=int(e.cfg.decimation),episode_seconds=float(e.cfg.episode_length_s),num_envs=int(e.num_envs))
 assert actual['mimic']==.01 and actual['closure']==.002 and actual['episode_seconds']>=15 and actual['num_envs']==104
 CONTEXT['actual_eval_integrity_guard']=actual;CONTEXT['save']('ACTUAL_RUNTIME_CONFIG_READBACK.json',dict(actual=actual,declared=CONTEXT['declared_eval_integrity_guard']))
 e._retention_native_witness=Witness(e,args)
 # The original source scene-update wrapper captures each actual post-physics frame.
 # Extend its existing witness indices to all104; actor inputs/reset/rewards are unchanged.
 e.e3_witness=torch.arange(e.num_envs,device=e.device);e.e3_capture=True
 old_update=e.scene.update;w=e._retention_native_witness
 def observed_update(dt):
  before=len(w.sub);old_update(dt)
  if not w.active:return
  assert len(w.sub)==before+1 and len(e.e3_physical)==1
  raw=e.e3_physical.pop();w.sub[-1].update({'E3_'+k:cpu(v) for k,v in raw.items()})
  for k,v in w.sub[-1].items():
   if np.asarray(v).dtype.kind in 'fc':assert np.isfinite(v).all(),('E3 physical nonfinite',k)
  assert float(np.max(abs(w.sub[-1]['E3_all31_force'][:,e.e3_wheels]-w.sub[-1]['E3_wheel_raw'])))<=.1
 e.scene.update=observed_update
 old_compute=e.termination_manager.compute
 def observed_termination(*a,**k):
  value=old_compute(*a,**k)
  if w.active:
   assert e.e3_frame is not None
   w.phase.update({'E3_'+key:cpu(v) for key,v in e.e3_frame.items()});e.e3_frame=None
  return value
 e.termination_manager.compute=observed_termination
 return e

def build_observed_frozen_policy(vec,path,device):
 from e3_retention_single_adapter_v1 import build_retention_single
 assert CONTEXT['router_mode']=='single_eval'
 return build_retention_single(vec,path,device)

def finalize_observer(env,result):env._retention_native_witness.finish(result)
'''
RUN='''"""Frozen original recovery public-request/pose recipe; no learning."""
from pathlib import Path
import json,torch,numpy as np,hashlib,time
from e3_native_witness_v1 import CONTEXT,create_observed_env,build_observed_frozen_policy,finalize_observer,SMALL_EVAL_CAPACITY,tensor,cpu
@torch.inference_mode()
def run_recovery(args):
 import mod4_task as task
 from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
 torch.manual_seed(args.seed);cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=104;cfg.sim.device=args.device;cfg.sim.enable_scene_query_support=True
 for k,v in SMALL_EVAL_CAPACITY.items():setattr(cfg.sim.physics,k,v)
 cfg.scene.wheel_contact_scut.filter_prim_paths_expr=['/World/ground/geometry/mesh'];cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim=64
 env=create_observed_env(args,cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.0);vec,policy,observer=build_observed_frozen_policy(vec,args.checkpoint,env.device)
 env.reset();env.e3_reset_enabled=True;env.place_declared_fall(torch.arange(104,device=env.device));env.publish()
 phase=env.recovery;assert torch.equal(phase.recipe,torch.arange(104,device=env.device)%13) and not phase.age.any()
 CONTEXT['save']('E3_FRESH104_EXPLICIT_LEGAL_FALL_RESET_ACTUAL.json',dict(reset=env.e3_reset_receipt,recipe=cpu(phase.recipe).tolist(),public_modes=cpu(phase.mode()).tolist(),fresh104_DR_draws_not_restored20k=True,actual_q30=cpu(env.scene['robot'].data.joint_pos).tolist(),actual_root13=cpu(env.scene['robot'].data.root_state_w).tolist(),body_names=env.e3_body_names,contact_names=env.e3_contact_names,authored34_shapes=env.e3_shapes,sourcegeometry_not_cookedShapeLocal=True))
 for tick in range(args.steps):
  env.publish();assert not env.command_manager.get_term('twist').command.any()
  action=policy(vec.get_observations());vec.step(action)
 w=env._retention_native_witness;rows=w.rows
 # These are original source-event diagnostics, not an invented graduation gate.
 events=np.stack([r['E3_event_delta'] for r in rows]);first_failure=np.full(104,args.steps,dtype=np.int64)
 for tick,r in enumerate(rows):first_failure=np.where((first_failure==args.steps)&(r['terminated']|r['truncated']),tick,first_failure)
 result=dict(case_id=args.case_id,source_SHA=args.checkpoint_sha,steps=args.steps,callbacks=4*args.steps,recipe_ids=cpu(phase.recipe).tolist(),original_source_event_delta_sum=events.sum(0).tolist(),first_ordinary_or_truncation_step=first_failure.tolist(),skill_qualification_claimed=False,no_PPO=True,frozen_architecture_audit=observer.audit(),physical_saved_every_callback=True,actual_new_recipe_not_source20k_restore=True)
 finalize_observer(env,result);return result
'''
def main():
 assert not E.exists();E.mkdir();shutil.copytree(A,Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pt'))
 C=Q/'frozen_shared/runtime/isaac/mod4';copies=[]
 for name in ('e3_recovery_runtime_v1.py','e3_public_recovery_phase_v1.py','h1_fullstate_environment_v1.py','h1_public_request_phase_v1.py','h1_authored_full_collider_plane_reference_v1.py','spin_commands.py','directional_spin_runtime.py'):
  before=H(C/name) if (C/name).is_file() else None;shutil.copy2(S/name,C/name);copies.append(dict(relative=str((C/name).relative_to(Q)),source=str(S/name),source_SHA=H(S/name),previous_frozen_SHA=before))
 # All actual plant/runtime files are retained. These exact imports restore the E3
 # source command audit; the signed4-owned E2 audit is not used for the zero command.
 components=O/'E3_closed85_frozen_actual_public03_perenv_CPU_v2'
 for name in ('recovery_closed85_source_guard_v1.py','recovery_closed85_single35_public03_perenv_CPU_v2.py'):shutil.copy2(components/name,Q/name)
 p=Q/'source/E3_closed85.pt';shutil.copy2(M/'actual_closed_final_models/recovery/final_valid_update85.pt',p);assert H(p)=='8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208'
 write(Q/'e3_retention_single_adapter_v1.py',ADAPTER);write(Q/'e3_frozen_recovery_loop_v1.py',RUN)
 old=(A/'retention_native_witness_v8.py').read_text('utf8');old=old[:old.index('\ndef create_observed_env(')]+ENV_CREATE
 old=old.replace('from e2_closed112_source_guard_CPU_v1 import validate_E2_source','from recovery_closed85_source_guard_v1 import validate_E3_source').replace('validate_E2_source(source)','validate_E3_source(source)');write(Q/'e3_native_witness_v1.py',old)
 query=(A/'retention_plane_reference_v8.py').read_text('utf8');assert query.count('((80,2),(88,2))')==1;query=query.replace('((80,2),(88,2))','((80,2),(88,2),(104,2))');write(Q/'e3_plane_reference_104_v1.py',query)
 p2=Q/'e3_native_witness_v1.py';text=p2.read_text('utf8').replace('from retention_plane_reference_v8 import plane_query_actual as new_reference','from e3_plane_reference_104_v1 import plane_query_actual as new_reference');p2.write_text(text,encoding='utf8',newline='\n')
 worker=(A/'e2_frozen_worker_v10.py').read_text('utf8').replace('E2_CLOSED112','E3_CLOSED85').replace('MANIFEST_V10','MANIFEST_V1').replace('SIGNED4_FROZEN_V10','PUBLIC03_FROZEN_V1').replace("choices=['world']","choices=['recovery']").replace('a.num_envs==88','a.num_envs==104').replace('from e2_closed112_source_guard_CPU_v1 import validate_E2_source','from recovery_closed85_source_guard_v1 import validate_E3_source').replace('validate_E2_source(source)','validate_E3_source(source)').replace('from retention_native_witness_v8 import CONTEXT','from e3_native_witness_v1 import CONTEXT').replace('from retention_world_native_v8 import run_world','from e3_frozen_recovery_loop_v1 import run_recovery').replace('run_world(a)','run_recovery(a)');write(Q/'e3_frozen_worker_v1.py',worker)
 parent=(A/'e2_frozen_parent_v10.py').read_text('utf8').replace('e2_frozen_worker_v10.py','e3_frozen_worker_v1.py').replace('E2_CLOSED112_FROZEN_COMPLETE_MANIFEST_V10.json','E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V1.json');write(Q/'e3_frozen_parent_v1.py',parent)
 sys.path[:0]=[str(Q),str(C)];from recovery_closed85_source_guard_v1 import validate_E3_source;from recovery_closed85_single35_public03_perenv_CPU_v2 import Single35;from e3_public_recovery_phase_v1 import RecoveryPhase
 rng=torch.get_rng_state().clone();ck=torch.load(p,map_location='cpu',weights_only=False);validate_E3_source(ck);actor=Single35(p,104,'cpu');assert actor.exact()
 phase=RecoveryPhase(104,'cpu');assert phase.mode().tolist().count(0)==8 and phase.mode().tolist().count(3)==96
 # Execute the unmodified source fall-placement function with a CPU robot sink.
 tree=ast.parse((S/'e3_recovery_runtime_v1.py').read_text('utf8'));klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RecoveryEnv');fun=next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name=='place_declared_fall');ns=dict(torch=torch,np=np,Path=Path,__file__=str(S/'e3_recovery_runtime_v1.py'),tensor=lambda x:x);exec(compile(ast.Module(body=[fun],type_ignores=[]),'original_source_fall_CPU','exec'),ns)
 bank=np.load(S/'MOD4_RESET_COLLISION_BANK.npz');robot=types.SimpleNamespace(joint_names=list(bank['joint_names']),data=types.SimpleNamespace(root_state_w=torch.zeros(104,13)))
 def joint(q,qd,env_ids):robot.q=q.clone();robot.qd=qd.clone()
 def root(v,env_ids):robot.data.root_state_w[env_ids]=v
 robot.write_joint_state_to_sim=joint;robot.write_root_state_to_sim=root
 class Scene(dict):pass
 scene=Scene(robot=robot);scene.env_origins=torch.zeros(104,3);e=types.SimpleNamespace(scene=scene,recovery=phase,device='cpu',publish=lambda:None);ns['place_declared_fall'](e,torch.arange(104));root=robot.data.root_state_w
 assert root.shape==(104,13) and robot.q.shape==(104,30) and not root[:,7:].any() and not robot.qd.any() and not phase.age.any()
 assert torch.allclose(root[:,3:7].norm(dim=-1),torch.ones(104),atol=1e-7) and root[:,2].min()>0
 for i in range(13):assert (phase.recipe==i).sum()==8
 # Actual mode mixed vectors, once provider, previous actual6 and selected reset.
 last=torch.zeros(104,6);x=torch.zeros(104,35);x[:,28:]=torch.nn.functional.one_hot(phase.mode(),7);calls=[0]
 def provider():calls[0]+=1;return x
 pending=actor.begin(0,provider,phase.mode());assert actor.begin(0,provider,phase.mode()) is pending and calls==[1];ended=torch.arange(104)%17==0;actor.finish(pending['clipped_action'],ended);assert actor.exact()
 for _ in range(300):phase.begin();phase.update(torch.full((104,),-1.),torch.zeros(104),torch.zeros(104))
 assert not phase.mode().any();ids=torch.tensor([1,3]);phase.reset(ids,torch.ones(2));assert phase.mode().tolist().count(3)==2
 x=torch.zeros(104,35);x[:,22:28]=actor.last;x[:,28:]=torch.nn.functional.one_hot(phase.mode(),7);pending=actor.begin(1,lambda:x,phase.mode());actor.finish(pending['clipped_action'],torch.zeros(104,dtype=torch.bool));assert actor.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 recipe=dict(version=1,source_SHA=H(p),source_Adam657660=True,num_envs=104,seed=20260928,DR_profile='white_v3',recipe_ids=(torch.arange(104)%13).tolist(),per_recipe_count=8,public_mode3_controls_per_rescue_episode=300,normal_recipe12_public0=True,zero_twist_command=True,original_source_fall_function_SHA=hashlib.sha256(ast.dump(fun).encode()).hexdigest(),reset_bank_SHA=H(S/'MOD4_RESET_COLLISION_BANK.npz'),native120_before_full1500_and_independent_allrow_CPU=True,no_skill_threshold_invented_or_pass_claimed=True)
 write(Q/'E3_CLOSED85_PUBLIC03_FROZEN_RECIPE_V1.json',json.dumps(recipe,indent=2))
 original=json.loads((M/'payload/recovery/job0/original_run_manifest.json').read_bytes())['env'];env={k:v for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')};env.update(RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0')
 rows=[]
 for path in sorted(q for q in Q.rglob('*') if q.is_file() and '__pycache__' not in q.parts):
  if path.suffix=='.py':ast.parse(path.read_text('utf8'))
  rows.append(dict(relative=path.relative_to(Q).as_posix(),bytes=path.stat().st_size,SHA=H(path)))
 mf=Q/'E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V1.json';manifest=dict(version=1,source=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)),source_relative='source/E3_closed85.pt',source_guard='recovery_closed85_source_guard_v1.py',recipe=recipe,env=env,files=rows,package_files_v8=[dict(relative=r['relative'],bytes=r['bytes'],sha256=r['SHA']) for r in rows],fresh104_not_source20000_fullstate_restore=True)
 write(mf,json.dumps(manifest,indent=2));bundle=E/'E3_CLOSED85_COMPLETE_FROZEN_PAYLOAD_V1.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for row in rows:z.write(Q/row['relative'],row['relative'])
  z.write(mf,mf.name)
 out=dict(epoch=time.time(),passed_complete_package_and_original_fall_phase_actor_CPU_only=True,manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),files=len(rows),recipe=recipe,exact_source_overlay_copies=copies,original_plant_and_bank_reused=True,actual_original_fall_CPU_root13=root.tolist(),legal_bank_q30=robot.q.tolist(),mode_initial_8normal96rescue_then_after300_104normal_then_two_selectedreset_rescue=True,once_provider_actual_feedback_last6_clip6_actor9STD_sourceexact=True,RNG_unchanged0CUDA0optimizer=True,query104_shape_only_extension_original1e6_comparison_unchanged=True,read_only_extra_all104_body31_contact34_geometry_captured_eachphysical_if_actual_dispatched=True,no_target249_upload_or_Task_or_native_or_skill_result_yet=True,actual_native120_CPU_exit_lockfree_then_unused_full1500_required=True,source_old_engineering_FP32_vs_authoredFP64_limits_not_erased=True)
 with (R/'E3_CLOSED85_FULL104_PUBLIC03_FROZEN_PACKAGE_ORIGINAL_RESET_PHASE_ACTOR_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(E3_complete_CPU_package=True,files=len(rows),bytes=bundle.stat().st_size,no_GPU_dispatch=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E3_FULL_FROZEN_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_dispatch=True),f,indent=2)
  raise
