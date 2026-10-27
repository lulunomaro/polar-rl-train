"""Exact reviewed reader primitives with native88 source-config extension only."""
from pathlib import Path
import ast,sys,hashlib,io,json,math,traceback
from dataclasses import dataclass,asdict
from native88_closing_protocol_v1 import BOOTSTRAP_SHA,require
SOURCE_SHA=BOOTSTRAP_SHA # Original reader name: only the normal86 shared witness.

def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())

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

def native_modules(s,pins,seed):
 import torch
 ns=pins.extract('source/supermimic_wheel_leg_v3/learner.py',('SuperMimicConfig',),dict(dataclass=dataclass))
 config=pins.extract('source/native_own_fudan88_gas400_training_v2.py',('config_for',),dict(SuperMimicConfig=ns['SuperMimicConfig']))['config_for'](seed)
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
  summaries[opt_name]=validate_native_optimizer(module,s[opt_name],betas)
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

def validate_native_optimizer(module,state,betas):
    import torch
    optimizer=torch.optim.Adam(module.parameters(),lr=2e-4,betas=betas);optimizer.load_state_dict(state)
    parameters=list(module.parameters());require(len(optimizer.state)==len(parameters)>0,'native optimizer incomplete')
    require(all(tuple(g['betas'])==betas for g in optimizer.param_groups),'native optimizer betas changed')
    steps=[]
    for p in parameters:
        value=optimizer.state[p];require({'step','exp_avg','exp_avg_sq'}<=set(value),'native Adam moments missing')
        require(value['exp_avg'].shape==value['exp_avg_sq'].shape==p.shape and value['exp_avg'].dtype==value['exp_avg_sq'].dtype==p.dtype,'native moment shape/dtype')
        require(int(value['step'])>0,'native optimizer positive completed step');steps.append(int(value['step']))
    return dict(passed=True,state_count=len(steps),min_step=min(steps),max_step=max(steps),betas=list(betas))
