"""UNUSED: one of one fixed fresh N1 frozen qualified88C/400N attempt.

No training entry main, runner, optimizer, learner, WM, or historical env restore.
Requires a NEW eval-owned runtime copy and closed qualified88C formal model.
Root must bind/install this source and keep the sole72 authority guard alive.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,sys,time,traceback,ast,importlib.util,importlib.metadata
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from native88C_frozen_acceptance_contract_v1 import SEEDS,CANONICAL,GPU_BACKENDS,require,validate_eval_binding,select_source
from native88C_eval_environment_v1 import bind_private_job_root,environment
from native88C_frozen_acceptance_driver_v1 import make_frozen_policy,run_single_case,termination_cache_contract
def H(path):
 d=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):d.update(chunk)
 return d.hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def put(root,name,value):
 with (Path(root)/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def contained(root,relative):
 p=(Path(root)/relative).resolve();require(p.is_relative_to(Path(root).resolve()),'path escaped private eval runtime');return p
def validate_evidence(q,base):
 values={}
 for key,row in q['evidence_pins'].items():
  p=contained(base,row['eval_relative']);require(H(p)==row['SHA'],'copied original evidence SHA differs: '+key);values[key]=read(p)
 selected=select_source(values['cpu'],values['collection'],{k.removeprefix('events_'):v for k,v in values.items() if k.startswith('events_')})
 require(selected['selected_key']==q['selected_key'] and selected['selection_scope']==q['selection_scope'],'predeclared source choice differs')
 final=selected['source']['final'];require(final['SHA']==q['source_model']['SHA'] and final['bytes']==q['source_model']['bytes'],'formal qualified native model differs')
 producer=final['producer']
 require(producer['initial_native_source']==q['native_parent_source'] and producer['bootstrap_task_source_SHA']=='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394','native R5 parent and normal86 witness distinct')
 require(producer['runtime_objective_contract_SHA']==q['objective_contract_SHA'] and producer['gas400_parameter_source_contract_SHA']==q['gas400_parameter_source_contract_SHA'] and producer['actual_gas400_asset_composition_report_SHA']==q['actual_gas400_asset_composition_report_SHA'],'typed native88C objective/gas recipe pins')
 require(values['collection']['run_id']==q['source_run_id'],'source run differs')
 require(q['original_owner_locks']==values['collection']['authority72']['original_locks'],'original authority lock evidence differs')
 from native88C_own_pid_out_guard_v1 import records_from_evidence
 require(q['known_qualified_own_processes']==records_from_evidence(values),'recorded own PID/create source differs')
 slot='recovery' if q['execution_backend']=='target72' else 'h1'
 require(q['selected_GPU_original_locks']==[r['path'] for r in values['collection']['nodes'][slot]['locks']],'selected original GPU lock/lease set differs')
 return selected,values
def validate_runtime(q,B):
 require(B.is_relative_to(Path(q['eval_root']).resolve()) and B!=Path(q['eval_root']).resolve(),'runtime must be a new eval-root child')
 for root in q['qualified_training_roots'].values():require(not B.is_relative_to(Path(root).resolve()),'qualified training runtime is read-only')
 expected={row['relative']:row for row in q['runtime_files']}
 require(len(expected)==len(q['runtime_files']),'duplicate runtime inventory')
 for relative,row in expected.items():
  p=contained(B,relative);require(p.suffix.lower() not in ('.pt','.pth','.npz'),'evaluation runtime must not include historical model/raw')
  require(p.is_file() and p.stat().st_size==row['bytes'] and H(p)==row['SHA'],'exact runtime source/asset inventory differs: '+relative)
 actual={p.relative_to(B).as_posix() for p in B.rglob('*.py')}
 require(actual=={r for r in expected if r.endswith('.py')},'unapproved or absent Python in new runtime')
 require(read(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json')==q['runtime_source_contract'],'exact C training source contract changed')
 tree=ast.parse((B/'source/native88_gas400_migration_v1.py').read_bytes());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NATIVE_CONTRACT' for t in n.targets));scope={}
 exec(compile(ast.Module(body=[node],type_ignores=[]),'pinned_native_output_contract','exec'),scope)
 require(scope['NATIVE_CONTRACT']==q['native_output_contract'],'new native88 output contract source differs')
 return True
def validate_installed_sources(q):
 c=q['runtime_source_contract'];sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
 versions={}
 for name in ('isaaclab','rsl-rl-lib','torch'):
  try:versions[name]=importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError:versions[name]='not_registered_distribution'
 require(versions==c['expected_installed_versions'],'fresh installed SDK/RSL/torch versions')
 require(H(sdk/'utils/math.py')==c['expected_actual_SDK_math_SHA'],'fresh actual SDK math source')
 for row in c['expected_actual_RSL_sources']:
  path=contained(rsl,row['relative']);require(path.stat().st_size==row['bytes'] and H(path)==row['SHA'],'fresh actual RSL source')
 return dict(passed=True,versions=versions,no_scene_or_model_created=True)

class Authority:
 def __init__(self,q,out):self.q=q;self.out=out;self.handles=[];self.raw=None
 def enter(self):
  import fcntl
  if self.q['execution_backend']=='target72':
   paths=[str(Path(CANONICAL).parent/name) for name in ('native_floor_supervisor.lock','autonomy_controller.lock')]
   # Must be copied from the actually closed owner report, never substitute a new lock.
   expected=[r['path'] for r in self.q['original_owner_locks']]
   require(paths==expected,'original authority lock paths differ')
   for p in paths:
    h=open(p,'rb+');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);self.handles.append(h)
   self.raw=Path(CANONICAL).read_bytes();c=json.loads(self.raw)
   require(c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026','sole72 still active')
   require(c['remaining_training_seconds']>86412.86069250107 and c['budget_mode']=='finite_original_limits_restored_after_single4090_return' and c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[],'original authority floor/mode/extensions')
  else:
   row=self.q['external72_readonly_guard'];p=contained(self.q['eval_root'],row['eval_relative']);require(H(p)==row['SHA'],'external72 guard ready receipt changed')
   self.external=read(p);require(self.external['kind']=='native88C_readonly72_eval_guard' and self.external['canonical']==CANONICAL and self.external['read_only'] is True,'actual72 readonly holder required')
   require(self.external['original_owner_locks']==self.q['original_owner_locks'],'external guard original locks differ')
   require(self.q['external72_guard_parent_keeps_live_stdin_and_requires_waited_exit_proof'] is True,'root finite live-holder/exit binding required; ready receipt alone insufficient')
   # Source210 never opens the retired local canonical or the72 canonical path.
  self.check()
 def check(self):
  if self.raw is not None:require(Path(CANONICAL).read_bytes()==self.raw,'sole72 canonical bytes changed during frozen case')
  else:require(time.time()+30<self.external['expires_epoch'],'external72 guard expired or insufficient headroom')
 def close(self):
  try:
   self.check();put(self.out,'READONLY_AUTHORITY_CASE_EXIT.json',dict(passed=True,canonical_unchanged=self.raw is not None,canonical_SHA=hashlib.sha256(self.raw).hexdigest() if self.raw is not None else self.external['canonical_SHA'],external72_parent_exit_proof_required=self.raw is None,no_account_write=True,no_canonical_copy=True))
  finally:
   for h in reversed(self.handles):h.close()
def resource_admission(q,out):
 import fcntl,psutil,shutil,subprocess
 handles=[]
 try:
  for p in q['selected_GPU_original_locks']:
   h=open(p,'rb+');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);handles.append(h)
  row=subprocess.check_output(['nvidia-smi','-i',q['GPU_UUID'],'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',')
  require(row[0].strip()==q['GPU_UUID'] and '4090' in row[1] and int(row[2])>15669,'fresh selected original GPU resource floor')
  users=subprocess.check_output(['nvidia-smi','-i',q['GPU_UUID'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
  require(q['GPU_UUID'] not in users,'selected GPU has an existing compute user; leave it untouched')
  require(psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(out).free>25*1024**3,'original frozen replay RAM/storage headroom')
  from native88C_own_pid_out_guard_v1 import assert_recorded_own_out
  assert_recorded_own_out(q['known_qualified_own_processes'],psutil.Process,psutil.NoSuchProcess,execution_backend=q['execution_backend'])
  return handles
 except BaseException:
  for h in reversed(handles):h.close()
  raise
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--binding',required=True);parser.add_argument('--seed',required=True,type=int,choices=SEEDS);args=parser.parse_args()
 q=read(args.binding);validate_eval_binding(q);base=Path(q['eval_root']).resolve();B=Path(q['runtime_root']).resolve();J=B/'job0';out=base/('seed_'+str(args.seed))
 require(base.is_dir() and not out.exists(),'new predeclared consumed seed namespace required');out.mkdir()
 put(out,'ENTRY_CONSUMED_BEFORE_APP_OR_MODEL.json',dict(purpose=q['purpose'],seed=args.seed,epoch=time.time(),no_retry=True))
 app=None;env=None;resources=[];authority=Authority(q,out);entered=False
 try:
  require(Path(args.binding).resolve().is_relative_to(base),'binding must be in new eval root')
  require(len(q['eval_code_pins'])>=5,'complete eval entry/helper pins required')
  for name,SHA in q['eval_code_pins'].items():require(H(contained(HERE,name))==SHA,'eval Python source differs: '+name)
  require(set(p.name for p in HERE.glob('*.py'))==set(q['eval_code_pins']),'unapproved eval Python module')
  selected,evidence=validate_evidence(q,base);validate_runtime(q,B)
  authority.enter();entered=True;resources=resource_admission(q,out)
  source=contained(base,q['model_eval_relative']);require(source.stat().st_size==q['source_model']['bytes'] and H(source)==q['source_model']['SHA'],'copied formal native model differs')
  for key in list(os.environ):
   if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
  original=read(J/'original_run_manifest.json')['env'];os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
  bind_private_job_root(out/'private');os.environ.update(environment({'GPU_UUID':q['GPU_UUID']}))
  os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_KEEP_STD='1',RM_RESCUE_STOP_FILE=str(out/'UNUSED_STOP_FILE.json'),OWN_E2_H1_KIND='FROZEN_NATIVE88C_SINGLE_ATTEMPT')
  sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4'),str(HERE)]
  put(out,'FRESH_INSTALLED_SOURCE_BEFORE_APP_ACTUAL.json',validate_installed_sources(q))
  import runpy
  entry=J/'runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py'
  sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed',str(args.seed),'--steps_per_env','24','--init_checkpoint',str(source),'--log_root',str(out/'UNUSED_training_logs')]
  ns=runpy.run_path(str(entry),run_name='native88C_frozen_N1_configuration_only');app=ns['app']
  import h1_scut_fudan_jump_reward_v1 as scut,h1_step270_sdk_runtime_candidate as terrain
  original_rewards=scut.configure;scut.configure=lambda c:terrain.configure_rewards(c,original_rewards)
  original_cfg=ns['Mod4EnvCfg'];factory=ns['build_env']
  def cfg():
   c=original_cfg();c.scene.num_envs=1;c.seed=args.seed;c.episode_length_s=5.;c.sim.device='cuda:0'
   require(float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01,'original reset contract')
   c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};return c
  factory.__globals__.update(Mod4Env=terrain.H1Step270Env,Mod4EnvCfg=cfg)
  env=factory();vec=ns['RslRlVecEnvWrapper'](env,clip_actions=6.)
  import torch,inspect
  from types import SimpleNamespace
  import mod4_task as task
  from actual_DR_memory_getter_v1 import RuntimeOrderBinding,indices,tensor
  from native_wheel_leg_bridge_v4 import NativeWheelLegBridge
  from native87_encoder_actual_sdk_adapter_v1 import actual_encoder_joint_names
  from own_step_differentiable_objective_v2 import build_own_step_mdp,OwnStepDifferentiableMdpV2
  from gas400_sdk_admission_candidate_v1 import check_actual_new_gas
  from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
  from supermimic_wheel_leg_v3.networks import Policy
  from supermimic_wheel_leg_v3.geometry import unflatten_state
  props=env.cfg.scene.robot.spawn.articulation_props
  require(env.num_envs==1 and not env.h1_capture and env._sim_step_counter==0 and not bool(env.h1_phase.age_control.any()),'actual fresh N1 before first control')
  require(env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4 and env.cfg.episode_length_s==5. and float(vec.clip_actions)==6.,'actual original N1 clock/timeout/action clip')
  require(props.solver_position_iteration_count==32 and props.solver_velocity_iteration_count==4 and env.cfg.sim.physics.solver_type==1,'actual original TGS32/4')
  require(terrain.GEOMETRY==dict(height=.270,edge_x=.35,depth=.8,width=1.2),'original step270 physical geometry')
  require(env._physics_action_delay.queue.control_us==10000,'original action delay control period')
  robot=env.scene['robot'];names=tuple(robot.joint_names);body=tuple(robot.body_names)
  require(list(names)==q['runtime_source_contract']['expected_runtime_joint_names'] and len(body)==31,'actual source/runtime30order31body')
  audit=env._mild_dr.audit();require(audit['actual_parameters_pass'] is True,'actual fresh N1 DR backend')
  components=[c.state_dict() for c in [env._sensor_mild,env._physics_action_delay,env._spring_pressure,env._gas_damping,env._chassis_com,env._explicit_pd]]
  require(all(c.get('n',c.get('num_envs'))==1 for c in components),'actual fresh N1 D0-D7 populations; no source4096 restore')
  closure=torch.stack(list(task.closure_errors(env).values())).amax(0);mimic=torch.stack(list(task.mimic_errors(env).values())).amax(0)
  require(bool(torch.isfinite(closure).all()) and bool(torch.isfinite(mimic).all()) and float(closure.max())<=.002 and float(mimic.max())<=.01,'original per-env initial closure/mimic reset admission')
  def group(key):return tuple(names[i] for i in indices(robot.actuators[key].joint_indices,30))
  binding=RuntimeOrderBinding(body,names,group('legs'),group('wheels'),group('gas_springs'),int(env._mild_dr.materials.shape[1]))
  ref=contained(B,q['reference_relative']);require(H(ref)==q['reference_SHA'],'original own reference SHA')
  encoder=actual_encoder_joint_names(env,names);geo=contained(B,q['own_geometry_relative']);require(H(geo)==q['own_geometry_SHA'],'own C wheel geometry source')
  mdp=build_own_step_mdp(read(J/'assets/import_contract.json'),read(geo),read(ref),names,encoder,device=env.device,order_scope='actual_SDK_readback')
  require(type(mdp) is OwnStepDifferentiableMdpV2 and json.loads(json.dumps(mdp.contract_manifest()))==q['objective_contract'],'actual C own-wheel V2 semantics/order')
  require(hashlib.sha256(json.dumps(mdp.contract_manifest(),indent=2).encode()).hexdigest()==q['objective_contract_SHA'],'actual unchanged objective contract SHA')
  capture=env._integrated_contact;require(list(capture.sensor.body_names)==['left_wheel','right_wheel'] and tuple(capture.history.shape)==(1,3,2,3),'original named contact history18')
  bank_source=check_runtime_source(J/'runtime/isaac/mod4');gas_actual=check_actual_new_gas(env,expected_joint_names=list(names),tensor=tensor,require_active_preload=False)
  require(env._rescue_reset_bank[0].shape==(74,30) and env._rescue_reset_q.shape==(1,30),'actual original400N first reset cache/write path')
  bridge=NativeWheelLegBridge(SimpleNamespace(env=vec),SimpleNamespace(frame=None),mdp,binding,lambda:None)
  state,xi=bridge.current();require(state.shape==(1,127) and xi.shape==(1,31),'actual new bridge/static dimensions')
  # Fresh check of actual installed source, after SDK App establishes extension imports.
  term_path=inspect.getsourcefile(type(env.termination_manager));require(term_path is not None,'actual termination source unavailable')
  term=termination_cache_contract(term_path)
  observation_path=inspect.getsourcefile(type(env.observation_manager));require(H(observation_path)=='de7c9b2c6b6e0bdb431a0574727982feebe72142ebf41b1140dce624b932d6b8','actual encoder SDK source differs')
  expected_data={'677d500672162d9bdc04b417c726b0d61edc839e0396cb3faf15316fbca28067','43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff'}
  actual_data={}
  for cls in type(robot.data).__mro__:
   path=inspect.getsourcefile(cls) if cls.__module__!='builtins' else None
   if path and Path(path).is_file():actual_data[path]=H(path)
  require(expected_data.issubset(set(actual_data.values())),'actual base/PhysX SDK data source differs or MRO source unavailable')
  put(out,'ACTUAL_FRESH_N1_SDK_BEFORE_FORWARD_ADMISSION.json',dict(passed=True,num_envs=1,seed=args.seed,actual_order=list(names),actual_body_names=list(body),actual_encoder_order=list(encoder),actual_static_dim=31,actual_packed_dim=127,actual_D0_D7_backend=audit,termination_cache=term,actual_data_MRO_source_SHAs=actual_data,original_physics_success_unchanged=True,no_native_forward_yet=True,source4096_or20k_environment_state_not_restored=True,original_first_reset_completed=True,reset_bank_exact_compatibility_source_CPU=bank_source,actual_new400N_gas_readback=gas_actual,ownwheel_V2_objective=q['objective_contract']))
  # One initial deserialization of the NEW qualified FINAL per case. No whole
  # source model, old native86, optimizer, learner or WM object is constructed.
  saved=torch.load(source,map_location='cpu',weights_only=False)
  publication=saved['UniSuperMimic_publication'];formal=q['source_model']
  require(publication['world_updates']==formal['world_updates'] and publication['policy_updates']==formal['policy_updates'] and publication['native_iteration']==formal['updates'],'formal native publication counter binding')
  producer=publication['producer'];require(producer['bootstrap_task_source_SHA']=='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394' and producer['initial_native_source']==q['native_parent_source'] and producer['reference_artifact_SHA']==q['reference_SHA'],'C model/native R5 parent/normal86 witness/reference binding')
  require(producer['runtime_objective_contract_SHA']==q['objective_contract_SHA'] and producer['gas400_parameter_source_contract_SHA']==q['gas400_parameter_source_contract_SHA'] and producer['actual_gas400_asset_composition_report_SHA']==q['actual_gas400_asset_composition_report_SHA'],'C actual objective/400N source recipe')
  pi=make_frozen_policy(saved,Policy,env.device,expected_native_contract=q['native_output_contract']);del saved
  put(out,'ACTUAL_RENDER_GEOMETRY.json',dict(body_names=list(body),shapes=env.h1_shapes,geometry=terrain.GEOMETRY,source_asset=str(J/'assets/robot.usd')))
  result=run_single_case(vec,bridge,pi,unflatten_state,tensor,out/'episode',seed=args.seed,source_identity=dict(model=q['source_model'],selected_key=q['selected_key'],selection_scope=q['selection_scope'],source_run_id=q['source_run_id']),term_contract=term,authority_check=authority.check)
  authority.check();put(out,'FROZEN_SINGLE_CASE_FUNCTION_RETURNED_ACTUAL.json',dict(passed=True,result=result,one_fixed_episode_only=True,not_skill_graduation=True))
 except BaseException:
  put(out,'PRIMARY_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True));raise
 finally:
  if env is not None:
   try:env.close()
   except BaseException:put(out,'ENV_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  if entered:
   try:authority.close()
   except BaseException:put(out,'AUTHORITY_EXIT_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
  for h in reversed(resources):h.close()
  if app is not None:
   # Primary case/error receipts are durable before Kit may terminate Python.
   app.close()
if __name__=='__main__':main()
