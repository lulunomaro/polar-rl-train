"""ExplicitMOCK: fakeTensor/fakeTorch/fakeenv+onefakeReset. NO real PT/Torch/GPU."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,time,traceback,types
B=Path(__file__).resolve().parent;T=B.parent.parent

def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
class FakeTensor:
 def __init__(self,shape,label,device='MOCK_CPU'):self.shape=shape;self.label=label;self.device=device
 def detach(self):return self
 def clone(self):return FakeTensor(self.shape,self.label,self.device)
 def to(self,*,device):return FakeTensor(self.shape,self.label,device)
class FakeTorch:
 def is_tensor(self,v):return isinstance(v,FakeTensor)
 def arange(self,n,*,device):return tuple(range(n))
def exact(a,b):
 if isinstance(a,FakeTensor):return isinstance(b,FakeTensor) and a.shape==b.shape and a.label==b.label
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return type(a)is type(b) and a==b

def main():
 fixture=load('explicit_canonical_mock_fixture',T/'staged_sources/E1_40050_BUILDER_V1/test_four_leaf_migration_MOCK_v1.py').fixture;rows=[]
 oldAxis=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016\train_payload\independent_expert_axis_v1.py').read_bytes();oldtree=ast.parse(oldAxis);oldwriter=next(n for n in ast.walk(oldtree) if isinstance(n,ast.FunctionDef) and n.name=='write')
 for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');rt=root/'runtime/isaac/mod4';role='E1_SLOPE' if name.startswith('SLOPE') else 'E1_CURB';migration=load('e1_pure_MOCK_'+name,rt/'e1_four_leaf_migration_v1.py');extra=load('extra_MOCK_'+name,rt/'variant_extra_state_runtime_v2.py');source=fixture(role);source['UNKNOWN_NESTED_ROOT']={'unknown_original_leaf':'MOCK_RETAIN_NESTED','known_current_leaf':0}
  if name=='CURB_PROTECTED878':source['distributed_rank_contract']=dict(rank=0,world_size=3,per_rank_envs=20000,global_envs=60000,task='E1_CURB20_original_entry',source_SHA='MOCK_G3_NOT_REAL_SHA',explicit_source_stream_fork_after_strict_restore=True,UNKNOWN_CONTRACT_EXTRA='MOCK_RETAIN')
  else:
   kind='CURB20' if name=='CURB_INDEPENDENT113' else 'SLOPE5';state=dict(centers=FakeTensor((20000,2),'MOCK_CENTERS'),target=FakeTensor((20000,),'MOCK_TARGET'),origin=FakeTensor((20000,2),'MOCK_ORIGIN'),kind=kind,original_private_RNG_draws_unchanged=True,UNKNOWN_AXIS_EXTRA=FakeTensor((16,),'MOCK_UNKNOWN_SAVED_RNG_BYTES_NOT_GENERATOR'))
   if name=='CURB_INDEPENDENT113':state['reset_direction']=FakeTensor((20000,),'MOCK_ORIGINAL_SAVED_RESET_DIRECTION_NOT_RECOMPUTED')
   source['independent_expert_scope_state']=state;source['independent_expert_task_contract']=dict(kind=kind,GPU_UUID='MOCK_HISTORICAL_GPU_NOT_FUTUREBINDING',UNKNOWN_TASK_EXTRA='MOCK_RETAIN')
  typed,receipt=migration.migrate_complete_source(source,role=role);assert all(typed[k] is source[k] for k in extra.required_extra_keys(name));original={path:migration.leaf(source,path) for path in migration.FOUR_PATHS};inverse=migration.reverse_four_leaf_view(typed,original);assert migration.assert_only_four_paths(source,inverse,reverse=True)
  env=types.SimpleNamespace(device='MOCK_GPU_NOT_REAL_GPU',num_envs=20000,reset_calls=0,writer_calls=0);torch=FakeTorch()
  def writer_installer(e,t):
   def write(ids):assert len(ids)==20000;e.writer_calls+=1
   return write
  before=extra.restore_extra_before_original_reset(env,typed,variant=name,torch_module=torch,writer_installer=writer_installer)
  # Symbolicloweroriginalhelper ONEreset; not actualSDK/state qualification.
  env.reset_calls+=1
  after=extra.finish_extra_after_original_reset(env,typed,variant=name,torch_module=torch,exact=exact);assert env.reset_calls==1 and env.writer_calls==int(name=='CURB_INDEPENDENT113')
  current_generated=dict(typed);current_generated.pop('UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP');current_generated['UNKNOWN_NESTED_ROOT']={'known_current_leaf':1}
  for key in extra.required_extra_keys(name):current_generated.pop(key)
  saved=extra.merge_extra_into_own_save(current_generated,env,variant=name);assert saved['UNKNOWN_NESTED_ROOT']=={'unknown_original_leaf':'MOCK_RETAIN_NESTED','known_current_leaf':1};assert set(saved)==set(typed) and exact({k:saved[k] for k in extra.required_extra_keys(name)},{k:source[k] for k in extra.required_extra_keys(name)}) and saved['UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP'] is typed['UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP']
  newwriter=next(n for n in ast.walk(ast.parse((rt/'variant_extra_state_runtime_v2.py').read_bytes())) if isinstance(n,ast.FunctionDef) and n.name=='write');assert ast.dump(oldwriter,include_attributes=False)==ast.dump(newwriter,include_attributes=False)
  negatives=[]
  bad=dict(typed);bad.pop(extra.required_extra_keys(name)[0])
  try:extra.restore_extra_before_original_reset(env,bad,variant=name,torch_module=torch,writer_installer=writer_installer)
  except ValueError:negatives.append('missing_OWN_extra_not_silently_ignored')
  else:raise AssertionError('Expectedmissingextra error')
  if name=='CURB_PROTECTED878':
   bad=copy.deepcopy(typed);bad['distributed_rank_contract']['rank']=1
  else:
   bad=copy.deepcopy(typed);bad['independent_expert_scope_state']['centers']=FakeTensor((80,2),'MOCK_WRONG_SLICE')
  try:extra.restore_extra_before_original_reset(env,bad,variant=name,torch_module=torch,writer_installer=writer_installer)
  except ValueError:negatives.append('wronghistoricalrank_or20k_slice_not_accepted')
  else:raise AssertionError('Expectedinvalidvariant error')
  rows.append(dict(variant=name,passed=True,MOCK_ONLY_NOT_ACTUAL_PT_OR_GPU=True,pure_fourleaf_receipt=receipt,extra_before=before,extra_after=after,source_extra_keyobjects_unchanged_by_fourleaf=True,new_save_missingroot_and_nestedunknown_retained_currentknownwins=True,original_Curb_axis_writer_AST_exact=True,negative_cases=negatives,symbolic_reset_calls=1,physical_or_RNG_calls=0,real_torch_or_sourcePT_operations=0))
 out=B/'THREE_VARIANT_FOURLEAF_EXTRA_RESTORE_SAVE_MOCK_PROOF_V2.json'
 with out.open('x',encoding='utf-8') as f:json.dump(dict(kind='THREE_VARIANT_SOURCE_ONLY_EXPLICIT_FAKE_MOCK_PROOF',passed=True,rows=rows,no_actual_PT_or_Torch_SDK_SSH_GPU_operations=True),f,indent=2)
 print(json.dumps(dict(report=str(out),MOCK_ONLY=True,variants=3,negative_cases=6,real_PT_SDK_operations=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('VARIANT_MOCK_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),MOCK_ONLY=True,PT_SDK_operations=0),f,indent=2)
  raise
