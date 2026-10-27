"""UNUSED formal native2 closing review. Each FINAL one initial CPU load.

New purpose: one shared load of qualified normal86 H1 solely to prove both
native FINAL frozen PPO cores remain literal-exact. No actor/WM forward/physics.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,ast,hashlib,importlib,importlib.util,io,json,math,os,time,traceback
from dataclasses import asdict,dataclass
from native87R5_closing_protocol_v1 import KEYS,SOURCE_SHA,require,validate_detached,validate_fees,validate_actual_GO_binding,native_window,optional_phase
from native87R5_event_curve_summary_v1 import read_curve

def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(R,name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def exact(a,b):
 import torch
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a.cpu(),b.cpu())
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a) is type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return type(a) is type(b) and a==b
def finite(x):
 import torch
 if torch.is_tensor(x):require(bool(torch.isfinite(x).all()),'nonfinite FINAL tensor')
 elif isinstance(x,dict):
  for value in x.values():finite(value)
 elif isinstance(x,(list,tuple)):
  for value in x:finite(value)
 elif isinstance(x,float):require(math.isfinite(x),'nonfinite FINAL scalar')

class OneInitialLoadPool:
 def __init__(self,reader=None,loader=None):
  self.reader=reader or (lambda p:Path(p).read_bytes());self.loader=loader;self.attempted=set();self.cache={};self.records=[]
 def load(self,path,SHA,role):
  if SHA in self.cache:return self.cache[SHA]
  require(SHA not in self.attempted,'initial read already consumed; no reload after error')
  self.attempted.add(SHA);row=dict(role=role,path=str(path),producer_SHA=SHA,initial_load_attempted=True,completed=False);self.records.append(row)
  try:
   raw=self.reader(path);require(hashlib.sha256(raw).hexdigest()==SHA,'collected FINAL initial-read full SHA mismatch')
   if self.loader is None:
    import torch
    value=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False)
   else:value=self.loader(raw)
   self.cache[SHA]=value;row.update(completed=True,initial_full_SHA_verified=True);return value
  except BaseException:row['original_error']=traceback.format_exc();raise
 def load_qualified_shared_source(self,path,expected_bytes):
  require(SOURCE_SHA not in self.attempted,'shared qualified source read already consumed')
  path=Path(path);require(path.is_file() and not path.is_symlink() and path.stat().st_size==expected_bytes==16868635,'qualified source exact path/stat required')
  self.attempted.add(SOURCE_SHA);row=dict(role='shared_closed86_H1_frozen_bootstrap_new_native87R5_FINAL_qualification',path=str(path),
   producer_SHA=SOURCE_SHA,producer_bytes=expected_bytes,producer_SHA_already_formally_qualified_not_rehashed=True,
   initial_load_attempted=True,completed=False);self.records.append(row)
  try:
   import torch
   value=torch.load(path,map_location='cpu',weights_only=False)
   require('UniSuperMimic_H1_test' not in value,'shared source must be qualified normal H1, never old native86')
   self.cache[SOURCE_SHA]=value;row['completed']=True;return value
  except BaseException:row['original_error']=traceback.format_exc();raise

class PinnedSource:
 """Read Python/JSON source only; never load a checkpoint inside a validator."""
 def __init__(self,B,spec):
  self.B=Path(B).resolve();m=self.B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';require(H(m)==spec['manifest_SHA'],'prepared manifest bytes changed')
  self.rows={r['relative']:r for r in read(m)['files']};self.extracted=[]
  actual={p.relative_to(self.B).as_posix() for p in self.B.rglob('*.py')}
  expected={k for k in self.rows if k.endswith('.py')};require(actual==expected,'exact Python inventory differs')
  for relative in expected:self.raw(relative)
 def raw(self,relative):
  p=self.B/relative;r=self.rows[relative]
  require(p.resolve().is_relative_to(self.B) and not p.is_symlink() and p.is_file(),'review source path containment')
  raw=p.read_bytes();require(len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['SHA'],'review source byte pin differs '+relative);return raw
 def extract(self,relative,names,namespace=None):
  t=ast.parse(self.raw(relative));selected=[]
  for node in t.body:
   named=isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names
   assigned=isinstance(node,ast.Assign) and any(isinstance(v,ast.Name) and v.id in names for v in node.targets)
   if named or assigned:selected.append(node)
  found={node.name for node in selected if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
  found|={v.id for node in selected if isinstance(node,ast.Assign) for v in node.targets if isinstance(v,ast.Name)}
  require(set(names)<=found,'pure source definitions missing '+relative)
  ns={} if namespace is None else dict(namespace)
  exec(compile(ast.Module(body=selected,type_ignores=[]),relative,'exec'),ns)
  self.extracted.append(dict(relative=relative,names=list(names),exact_AST_SHA=hashlib.sha256(ast.dump(ast.Module(body=selected,type_ignores=[])).encode()).hexdigest()))
  return ns

def original_physical_state(s,pins,n=4096):
 import torch
 base='job0/runtime/isaac/mod4/'
 st=s['sensor_DR_state'];require(st['version']==1 and st['n']==n and st['profile']=='noise_bias_mild_v1','saved sensor population/profile')
 require(st['bias'].shape==(n,4) and st['episode'].shape==(n,) and st['episode'].dtype==torch.long,'saved sensor shape')
 channels=dict(base_ang_vel=3,projected_gravity=3,leg_pos=4,leg_vel=4,wheel_vel=2)
 require(set(st['noise_rng'])==set(channels) and set(st['cache'])<=set(channels),'saved original sensor channel schema')
 for k,(tick,noise) in st['cache'].items():require(tick.shape==(n,) and noise.shape==(n,channels[k]),'saved sensor cache shape')
 def rng(value):require(torch.is_tensor(value) and value.dtype==torch.uint8 and value.ndim==1 and value.numel()>0,'saved private RNG byte schema')
 rng(st['bias_rng'])
 for value in st['noise_rng'].values():rng(value)
 global_rng=s['sensor_global_rng_state'];rng(global_rng['cpu']);require(bool(global_rng['cuda']),'saved global CUDA RNG bytes missing')
 for value in global_rng['cuda']:rng(value)
 for group in ('sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):
  require(isinstance(s[group],dict) and s[group],'original named private RNG group missing')
  for value in s[group].values():rng(value)
 widths=pins.extract(base+'feedback_delay_mild.py',('WIDTHS',))['WIDTHS']
 v=pins.extract(base+'feedback_delay_checkpoint.py',('validate_delay_state',),dict(torch=torch,WIDTHS=widths))
 v['validate_delay_state'](type('Schema',(),dict(n=n,enabled=True))(),s['feedback_delay_state'])
 q=pins.extract(base+'action_delay_physics_queue.py',('WIDTHS','FIELDS','PhysicsActionQueue'),dict(torch=torch))['PhysicsActionQueue'](n,'cpu',0)
 saved=s['physical_action_delay_state']
 for value in saved['rng'].values():rng(value)
 # Preserve CUDA bytes and check original queue schema using CPU generator
 # formats, matching the original saved-state CPU validator. No CUDA restore.
 q.validate_state(dict(saved,rng={k:g.get_state() for k,g in q.rng.items()}))
 v=pins.extract(base+'spring_pressure_checkpoint.py',('validate_saved_pressure',),dict(torch=torch));v['validate_saved_pressure'](s['spring_pressure_state'],n)
 profile=pins.extract(base+'gas_damping_factor.py',('PROFILE',))['PROFILE']
 v=pins.extract(base+'gas_damping_checkpoint.py',('validate_saved_damping',),dict(torch=torch,PROFILE=profile));v['validate_saved_damping'](s['gas_damping_state'],n)
 com=pins.extract(base+'chassis_com_component.py',('PROFILE',))['PROFILE'];pd=pins.extract(base+'explicit_pd_component.py',('PROFILE',))['PROFILE']
 v=pins.extract(base+'chassis_pd_checkpoint.py',('validate_saved_chassis_pd',),dict(torch=torch,COM_PROFILE=com,PD_PROFILE=pd));v['validate_saved_chassis_pd'](s['chassis_PD_state'],n)
 v=pins.extract('h1_step270_fullstate_checkpoint_candidate_uninstalled.py',('validate_new_phase',),dict(torch=torch))
 require(s['H1_step270_task_state']['version']==270,'saved task version270')
 v['validate_new_phase'](s['H1_step270_task_state']['phase'],n)
 task=s['H1_step270_task_state'];fields=pins.extract('h1_step270_fullstate_checkpoint_candidate_uninstalled.py',('COMMAND_FIELDS',))['COMMAND_FIELDS']
 require(set(task['external_command'])==set(fields) and task['private_command_mode_rng'].dtype==torch.uint8,'original task command/RNG missing')
 for value in task['external_command'].values():require(value.shape[0]==n,'saved command population not4096')
 require(s['H1_step270_runtime_contract']['original_D0_D7_STD_optimizer_save_chain_retained'] is True,'original save chain declaration absent')
 return dict(passed=True,saved_population=n,phase_version=270,original_D3_D4_D5_D6_D7_validator_AST_exact=True,
  original_D0_D2_named_RNG_and_feedback_groups_retained=True,
  CUDA_rng_bytes_schema_only_no_CPU_emulation_of_CUDA_restore=True,not_PhysX_exact_resume=True)

def frozen_bootstrap(s,bootstrap):
 require(len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8,'whole frozen PPO actor9/critic8 missing')
 require(tuple(s['actor_state_dict']['distribution.std_param'].shape)==(6,),'frozen six STD missing')
 require(len(s['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={832460},'frozen17Adam832460 differs')
 for name in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
  require(exact(s[name],bootstrap[name]),'frozen normal86 H1 core changed '+name)
 return dict(passed=True,source_SHA=SOURCE_SHA,Adam=832460,actor9_critic8_STD6_17Adam_all_state_literal_exact=True,
             native_not_normal_PPO_source=True,native_PPO20Adam_rule_applied=False)

def validate_native_optimizer(module,state,lr,betas):
 import torch
 optimizer=torch.optim.Adam(module.parameters(),lr=lr,betas=betas);optimizer.load_state_dict(state)
 parameters=list(module.parameters());require(len(optimizer.state)==len(parameters)>0,'native optimizer incomplete parameter state')
 steps=[]
 for parameter in parameters:
  value=optimizer.state[parameter]
  require({'step','exp_avg','exp_avg_sq'}<=set(value),'native Adam moments missing')
  require(value['exp_avg'].shape==value['exp_avg_sq'].shape==parameter.shape and int(value['step'])>0,'native optimizer moment shape/positive step')
  steps.append(int(value['step']))
 return dict(state_count=len(steps),min_step=min(steps),max_step=max(steps),strict_parameter_shapes=True)

def native_modules(s,pins,seed):
 import torch
 ns=pins.extract('source/supermimic_wheel_leg_v3/learner.py',('SuperMimicConfig',),dict(dataclass=dataclass))
 config=pins.extract('source/native_own_fudan87_training.py',('config_for',),dict(SuperMimicConfig=ns['SuperMimicConfig']))['config_for'](seed)
 args=asdict(config);require(exact(s['args'],args),'full actual native configuration differs from pinned config_for')
 # All package Python bytes were verified above. Construct CPU modules solely
 # for strict state/optimizer schema loading; no module forward is called.
 sys.path[:0]=[str(pins.B/'source'),str(pins.B/'source/sm_deps')]
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
 from supermimic_wheel_leg_v3.networks import Policy,Critic
 wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)
 pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=args['policy_hidden'])
 critic=Critic(73+54+31+7+1460,hidden=args['critic_hidden'])
 require(wm.in_dim==167 and wm.out_dim==126,'new native WM dimensions')
 summaries={}
 for model_name,opt_name,module,betas in (('wm','opt_wm',wm,(.9,.999)),('pi','opt_pi',pi,(.9,.95)),('critic','opt_v',critic,(.9,.999))):
  module.load_state_dict(s[model_name],strict=True)
  summaries[opt_name]=validate_native_optimizer(module,s[opt_name],args['lr'],betas)
 require(type(s['iteration']) is int and s['iteration']>0 and s['sim_steps']>0,'new native counters not positive')
 return dict(passed=True,full_config_exact=True,WM_Pi_Critic_strict_CPU_state_load=True,three_optimizers=summaries,
             no_actor_or_WM_forward=True,no_native20Adam_rule=True)

def role_terminal(receipt,key):
 a=receipt['authority72'];node=receipt['nodes'][key];row=a['cohort']['rows'][key];original=node['node_terminal']['row']
 require(node['all_selected_target_processes_actual_out'] and node['node_exit']['actual_all_own_children_waited'] and node['node_exit']['validation_fcntl_released_if_acquired'] and all(x['actual_fcntl_free'] for x in node['locks']),'actual node allout/locks missing')
 require(row['final']==original['final'] and row['returncode']==original['returncode'],'owner/node terminal differs')
 require(row['terminal_all_own_children_waited'] and row['returncode']==0 and not row['original_error'] and not row['errors'],'original native terminal failed')
 require(row['final'] and row['final']['passed'] is True,'rc0 is not a complete passed FINAL')
 return row['final']

def review_role(s,bootstrap,commit,spec,collected,pins,out,run_id,event_curve=None):
 import torch
 finite(s);progress=native_window(commit)
 ns=pins.extract('source/native_finalization_own_v3.py',('REQUIRED_ORIGINAL_GROUPS','REQUIRED_NATIVE_GROUPS','NATIVE_CONTRACT','PublicationError','assert_finite','verify_native'),dict(torch=torch,math=math))
 ns['verify_native'](s,s['UniSuperMimic_publication'])
 require(exact(s['UniSuperMimic_test_contract'],ns['NATIVE_CONTRACT']),'NATIVE_CONTRACT exact types/values differ')
 pub=s['UniSuperMimic_publication'];native=s['UniSuperMimic_H1_test'];producer=pub['producer'];formal=commit['final']
 require(pub['native_iteration']==native['iteration']==formal['updates']==collected['updates'],'native iteration/source FINAL mismatch')
 require(pub['history_shape']==[4096,10,86] and pub['episode_step_shape']==[4096],'new4096 history/episode dimensions')
 for name in ('world_updates','policy_updates','run_token','save_token','producer'):require(pub[name]==formal[name],'fresh publication differs '+name)
 require(pub['world_updates']>0 and pub['policy_updates']>0,'new native WM/Pi progress required')
 require(producer['bridge_source_SHA']==pins.rows['source/native_own_fudan87_training.py']['SHA'] and producer['finalization_source_SHA']==pins.rows['source/native_finalization_own_v3.py']['SHA'],'producer code pins differ')
 require(producer['bootstrap_task_source_SHA']==SOURCE_SHA and producer['bootstrap_Adam']==832460 and producer['native_architecture_fresh'] is True and producer['method']=='MOD4_own_Fudan_native_v3','fresh method/bootstrap provenance')
 require(producer['reference_artifact_SHA']==spec['reference_artifact_SHA'],'reference binding differs')
 objective=out/'NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json';require(H(objective)==producer['runtime_objective_contract_SHA'],'actual runtime objective SHA differs')
 objective_value=read(objective);pre=read(out/'NATIVE87_ACTUAL_GPU_PRECONTROL_ADMISSION.json')
 require(pre['actual_GPU_runtime_readback_passed'] is True and pre['before_first_native_physical_control_and_Pi'] is True and pre['actual_environment_count']==4096,'actual precontrol new plant evidence missing')
 require(pre['source_SHA']==SOURCE_SHA and pre['actual_reference_SHA']==spec['reference_artifact_SHA'],'actual source/reference binding')
 require(pre['actual_static_context_dim']==31 and pre['actual_dynamic_aux_dim']==54 and pre['packed_state_dim']==127 and pre['actor_obs_dim']==86 and pre['goal_frame_dim']==146,'actual new native dimensions')
 require(pre['actual_physics_dt']==.0025 and pre['actual_control_dt']==.01 and pre['actual_solver']==[1,32,4],'original physical clock/solver')
 expected=read(pins.B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json')['expected_runtime_joint_names']
 require(pre['actual_joint_names']==expected and len(set(expected))==30 and len(pre['actual_body_names'])==31,'actual runtime30/31 order')
 require(objective_value['actual_leg_encoder_joint_names']==pre['actual_leg_encoder_names'] and len(pre['actual_leg_encoder_names'])==4,'actual encoder order/objective binding')
 require(objective_value['packed_state']==127 and objective_value['dynamic_aux']==54 and objective_value['static_xi']==31 and objective_value['actor_observation']==86 and objective_value['goal_frame']==146,'actual objective schema')
 require(pre['actual_source_policy_bootstrap']['policy_actor9_critic8_STD6_17Adam832460_exact'] is True and pre['actual_source_policy_bootstrap']['old20k_environmental_state_restored'] is False and pre['legacy_native86_model_or_optimizer_loaded'] is False,'actual fresh bootstrap scope')
 require(pre['actual_source_policy_bootstrap']['actual_component_populations4096'] is True and pre['actual_source_policy_bootstrap']['physical_episode_fresh'] is True,'actual component populations/new episode')
 plant=read(out/'NATIVE87_ACTUAL_BEFORE_FIRST_CONTROL_ADMISSION.json')
 require(plant['passed'] is True and plant['actual_environment_count']==4096 and plant['actual_fresh_D0_D7_backend_readback_passed'] is True
  and plant['actual_DR_audit']['actual_parameters_pass'] is True and plant['before_first_control_and_Pi'] is True
  and plant['source20k_environment_state_not_restored'] is True,'actual original DR/backend before-control receipt missing')
 physical=original_physical_state(s,pins);frozen=frozen_bootstrap(s,bootstrap);modules=native_modules(native,pins,spec['seed'])
 try:phase=read(out/'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json')
 except FileNotFoundError:phase=None
 except Exception as exc:phase=dict(optional_reader_error=type(exc).__name__+': '+str(exc))
 curve=event_curve if event_curve is not None else read_curve(out/'ACTUAL_H1_CONVERGENCE_CURVE.jsonl',formal.get('original_H1_events'))
 return dict(passed=True,key=spec['key'],seed=spec['seed'],final=collected,source_SHA=SOURCE_SHA,
  native_progress=progress,native_fullstate_finite=True,NATIVE_CONTRACT_strict_type_and_values=True,
  frozen_bootstrap=frozen,native_modules=modules,original_physical_state=physical,actual_GPU_precontrol=pre,original_DR_precontrol=plant,
  source_extracted_validator_lineage=pins.extracted,optional_phase=optional_phase(phase),event_curve=curve,
  all_native_outputs_not_normal_H1_E2_or_recovery_production_sources=True,not_270mm_skill_graduation=True)

def eligible_formal_R5_roles(receipt):
 eligible=[];errors={}
 for key in KEYS:
  try:
   commit=role_terminal(receipt,key);native_window(commit)
   rows=receipt['native_H1_method_fullstate'][key]
   require(len(rows)==1 and rows[0]['formal_manifest_passed'] is True and rows[0]['twohost_complete_SHA'] is True,'no formal complete new R5 FINAL')
   require(rows[0]['SHA']==commit['final']['SHA'],'formal FINAL SHA metadata differs')
   eligible.append(key)
  except Exception:errors[key]=traceback.format_exc()
 return eligible,errors

def validate_R5_source_CPU_evidence(envelope):
 value=envelope['value'];ingress=value['actual_SDK_tensor_ingress_CPU']
 require(value['actual_observation_manager_API_source_CPU_passed'] is True and value['expected_actual_SDK_observation_manager_SHA']=='de7c9b2c6b6e0bdb431a0574727982feebe72142ebf41b1140dce624b932d6b8','R5 actual observation API source evidence absent')
 require(value['actual_SDK_tensor_ingress_CPU_passed'] is True and ingress['passed'] is True and ingress['fixture_only'] is True,'R5 installed-source/proxy CPU evidence absent')
 require(ingress['actual_GPU_runtime_readback_passed'] is False and ingress['actual_SDK_instance_or_scene_created'] is False,'source CPU must not claim actual GPU or scene')
 require(ingress['actual_bridge_constructor_current_init_state_selected_reset_checked'] is True,'real bridge proxy ingress CPU path not checked')
 for key,field,SHA in [('base','expected_actual_SDK_base_articulation_data_SHA','677d500672162d9bdc04b417c726b0d61edc839e0396cb3faf15316fbca28067'),('physx','expected_actual_SDK_physx_articulation_data_SHA','43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff')]:
  require(value[field]==ingress['actual_source_SHA_checks'][key]['SHA']==SHA,'R5 actual base/PhysX SDK source binding differs')
 return True

def main():
 os.environ['CUDA_VISIBLE_DEVICES']=''
 p=argparse.ArgumentParser();p.add_argument('--stage',required=True);args=p.parse_args();N=Path(args.stage).resolve();R=N/'reports'
 q=read(R/'AVAILABLE_TWO_NATIVE87R5_SOURCE_PREPARED_ACTUAL.json');detached=read(R/'AVAILABLE_TWO_NATIVE87R5_ACTUAL_OWNER_NODES_DETACHED.json');validate_detached(detached)
 receipt=read(R/'H1_NATIVE87R5_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')
 require(receipt['actual_finite_transport_returned'] is True and receipt['run_id']==detached['run_id'],'actual closing transport/run incomplete')
 require(q['roots']==detached['roots'] and q['owner_root']==detached['owner_root'],'actual R5 prepared/detached roots differ')
 for key in KEYS:
  require({k:v for k,v in detached['specs'][key].items() if k!='preinstalled_CPU_proof_SHA'}==q['specs'][key],'actual R5 detached source spec differs')
 validate_actual_GO_binding(receipt['authority72']['cohort']['go'],detached)
 require(set(receipt['native_H1_method_fullstate'])==set(KEYS) and receipt['active_keys']==list(KEYS),'exact two-native collected models')
 eligible,metadata_errors=eligible_formal_R5_roles(receipt)
 if not eligible:
  put(R,'H1_NATIVE87R5_NO_FORMAL_FINAL_CPU_METADATA_ACTUAL.json',dict(epoch=time.time(),passed=False,
   errors=metadata_errors,no_formal_new_R5_FINAL=True,no_checkpoint_or_bootstrap_model_read=True,
   original_canonical_cost_settled=receipt['original_canonical_cost_settled'],old_R3_R4_FINALs_never_opened=True))
  return False
 intent=dict(epoch=time.time(),purpose='native87R5 FINAL frozen bootstrap qualification',run_id=detached['run_id'],
   qualified_normal86_H1_shared_initial_load_count=1,each_new_FINAL_initial_load_count=1,
   source_producer_SHA=SOURCE_SHA,source_expected_bytes=16868635,no_source_SHA_rehash_requested=True,
   no_actor_or_WM_forward_no_GPU_no_old_native86_no_raw=True,no_rearm_or_second_load_after_error=True)
 put(R,'H1_NATIVE87R5_FINAL_REVIEW_INTENT_ACTUAL.json',intent);put(R,'H1_NATIVE87R5_FINAL_REVIEW_ENTRY_CONSUMED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,intent=intent))
 import torch
 torch.set_num_threads(2);pool=OneInitialLoadPool();models={};errors={};fees=None;bootstrap=None;curves={}
 try:fees=validate_fees(receipt['authority72'],receipt['authority72']['cohort']['go'],detached['owner_identity'])
 except BaseException:
  errors['original_fees']=traceback.format_exc();put(R,'H1_NATIVE87R5_ORIGINAL_FEE_CPU_ERROR_ACTUAL.json',dict(error=errors['original_fees'],original_flags_not_repaired=True))
 source=N.parent/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/current_baseline_closed_models/h1/model_update138.pt'
 try:
  qualified=read(Path(q['payloads']['h1'])/'native_source_metadata/QUALIFIED_CLOSED86_H1_POLICY_SOURCE_ACTUAL.json')
  require(qualified['passed'] and qualified['value']['final']['SHA']==SOURCE_SHA and qualified['value']['Adam']==832460,'saved formal source qualification differs')
  bootstrap=pool.load_qualified_shared_source(source,16868635)
 except BaseException:errors['shared_source']=traceback.format_exc();put(R,'H1_NATIVE87R5_SHARED_SOURCE_CPU_ORIGINAL_ERROR_ACTUAL.json',dict(error=errors['shared_source'],new_purpose=intent,no_second_load=True))
 cpu=read(R/'AVAILABLE_TWO_NATIVE87R5_ACTUAL_SOURCE_CPU_RETURNED_ACTUAL.json');seen_final=set()
 for key in KEYS:
  out=N/'current_native87R5_closed_text'/key/'job0/production'
  node_final=((receipt.get('nodes',{}).get(key,{}).get('node_terminal') or {}).get('row') or {}).get('final') or {}
  curves[key]=read_curve(out/'ACTUAL_H1_CONVERGENCE_CURVE.jsonl',(node_final.get('final') or {}).get('original_H1_events'))
  try:
   spec=detached['specs'][key];pins=PinnedSource(q['payloads'][key],spec)
   sys.path.insert(0,str(pins.B));protocol=importlib.import_module('native87_protocol_v1')
   require(protocol.native87_valid_ready(dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=cpu['results'][key]['ready_envelope'],original_error=False),spec),'actual R5 source SDK CPU evidence differs')
   require(H(Path(protocol.__file__))==pins.rows['native87_protocol_v1.py']['SHA'],'imported source protocol differs from this exact payload')
   validate_R5_source_CPU_evidence(cpu['results'][key]['ready_envelope'])
   commit=role_terminal(receipt,key);rows=receipt['native_H1_method_fullstate'][key];require(len(rows)==1,'exactly one formal complete FINAL required')
   final=rows[0];require(final['formal_manifest_passed'] is True and final['twohost_complete_SHA'] is True and final['SHA']==commit['final']['SHA'],'formal FINAL/two-host SHA incomplete')
   require(final['SHA'] not in seen_final and final['SHA']!=SOURCE_SHA,'distinct native seed publication required');seen_final.add(final['SHA'])
   path=Path(final['local_path']).resolve();require(path.is_relative_to((N/'current_native87R5_method_fullstate'/key/'formal').resolve()),'collected native FINAL path containment')
   s=pool.load(path,final['SHA'],key+'_native_FINAL')
   require(bootstrap is not None,'shared frozen-core source qualification unavailable; loaded FINAL is not reread')
   value=review_role(s,bootstrap,commit,spec,final,pins,out,detached['run_id'],curves[key])
   value['original_actual_role_cost_unmodified']=receipt['authority72']['original_segment']['experts'][key]
   models[key]=value;curves[key]=value['event_curve']
   put(R,'H1_NATIVE87R5_HEALTHY_'+key.upper()+'_INITIAL_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,value=value,independent_healthy_role_only=True,not_overall_pass=True))
  except BaseException:
   errors[key]=traceback.format_exc();put(R,'H1_NATIVE87R5_'+key.upper()+'_CLOSE_CPU_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=errors[key],other_healthy_roles_retained=True,no_second_initial_load=True))
 require(not torch.cuda.is_initialized(),'CPU reviewer initialized CUDA')
 passed=set(models)==set(KEYS) and fees is not None and not errors
 result=dict(schema='mod4.native87R5.two_native_typed_close_CPU.v1',epoch=time.time(),passed=passed,models=models,errors=errors,original_fees=fees,
   original_canonical_cost_settled=receipt['original_canonical_cost_settled'],initial_model_load_records=pool.records,
   source_qualification_purpose=intent,all_outputs_native_not_normal_production_sources=True,CUDA_initialized=False,
   no_query_or_replay_or_extra_policy_forward=True,not_physical_skill_graduation=True)
 put(R,'H1_NATIVE87R5_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',result)
 put(R,'H1_NATIVE87R5_EVENT_CURVE_TEXT_SUMMARY_ACTUAL.json',dict(epoch=time.time(),curves=curves,diagnostic_errors=errors,not_model_or_skill_gate=True))
 lines=['R5 native closing event summary; actual completed controls x4096, not iterations x24.']
 for key,value in curves.items():
  latest=value.get('latest_complete_snapshot') or {};lines.append(key+': '+json.dumps(dict(diagnostic_passed=value['diagnostic_passed'],complete_controls=latest.get('control'),environment_control_transitions=(latest.get('control',0)*4096),events=latest.get('counts'),intervals=value['event_increment_intervals']),allow_nan=False))
 with (R/'H1_NATIVE87R5_EVENT_CURVE_TEXT_SUMMARY_ACTUAL.txt').open('x',encoding='utf8') as f:f.write('\n'.join(lines)+'\n')
 print(json.dumps(dict(passed=passed,healthy_native=list(models),errors=list(errors),initial_load_records=pool.records)))
 return passed
if __name__=='__main__':
 try:sys.exit(0 if main() else 1)
 except SystemExit:raise
 except BaseException:
  stage=Path(sys.argv[sys.argv.index('--stage')+1]);put(stage/'reports','H1_NATIVE87R5_REVIEW_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_second_initial_model_load=True));raise
