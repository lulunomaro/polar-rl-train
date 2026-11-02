"""Prepare NEWvariant CPUonce producer from earlier actualtested mechanism.
No PT/runtime imports here; actualRoot/schema audit occurs from samefuturecache.
"""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;T=B.parent;old=T/'E1_actual_qualification_v1/cpu_four_leaf_typed_once_v1.py';s=old.read_text(encoding='utf-8')
s=s.replace("task['kind']=='E1_CANONICAL_ACTUAL_CPU_FOUR_LEAF_ONCE_V1'","task['kind']=='E1_EXPLICIT_VARIANT_ACTUAL_CPU_FOUR_LEAF_ONCE_V1'",1).replace("task['canonical'] in ('CURB141','SLOPE135')","task['canonical'] in ('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50')",1)
anchor="  actual=dict(original_iteration="
extra='''  # Actualcomplete root/nestedschema from SAME decodedCPUdict; no re-read.
  owner=json.loads((B/'SOURCE_OWNER_MAP.json').read_bytes());expected=set(owner['source_derived_rootkey_inventory']);rootdiff=dict(actual_only=sorted(set(ck)-expected),source_derived_only=sorted(expected-set(ck)),actual_count=len(ck),source_derived_count=len(expected))
  schema=[]
  def schema_walk(v,path=''):
   typ=type(v).__module__+'.'+type(v).__qualname__
   if torch.is_tensor(v):schema.append(dict(path=path,kind='tensor',type=typ,dtype=str(v.dtype),shape=list(v.shape),device=str(v.device)))
   elif isinstance(v,dict):
    schema.append(dict(path=path,kind='dict',type=typ,keys=[str(k) for k in v],key_types={str(k):type(k).__name__ for k in v}))
    for k,x in v.items():schema_walk(x,path+'/'+str(k))
   elif isinstance(v,(tuple,list)):
    schema.append(dict(path=path,kind='sequence',type=typ,length=len(v)))
    for k,x in enumerate(v):schema_walk(x,path+'/'+str(k))
   elif typ.startswith('numpy') and hasattr(v,'shape'):schema.append(dict(path=path,kind='numpy',type=typ,shape=list(v.shape),dtype=str(v.dtype)))
   else:schema.append(dict(path=path,kind='scalar',type=typ,value=v))
  schema_walk(ck)
  unknown=[dict(path='/'+k,type=type(ck[k]).__module__+'.'+type(ck[k]).__qualname__,producer_reference='UNMAPPED_ACTIVE_OWNER_PENDING_NOT_DROPPED',physical_or_RNG_application='UNKNOWN_NOT_INFERRED_FROM_PASSTHROUGH') for k in rootdiff['actual_only']]
  if task['canonical']=='CURB_PROTECTED878':
   historical=ck['distributed_rank_contract'];assert historical['rank']==0 and historical['world_size']==3 and historical['global_envs']==60000 and historical['per_rank_envs']==20000
   known={'world_size','rank','task','per_rank_envs','global_envs','source_SHA','explicit_source_stream_fork_after_strict_restore'};extra_fields=set(historical)-known;extra_schema=dict(distributed_rank_contract=historical,extra_unknown_fields=sorted(extra_fields),meaning='ONLYrank0complete20kshard. Historicalworld3/60k contractbytes preserved, no NCCL/merge/fork/no all60k restored claim')
  else:
   historical=ck['independent_expert_scope_state'];known={'centers','kind','origin','original_private_RNG_draws_unchanged','target'}
   if task['canonical']=='CURB_INDEPENDENT113':known.add('reset_direction')
   extra_fields=set(historical)-known;extra_schema=dict(scope_fields=list(historical),extra_unknown_fields=sorted(extra_fields),task_contract=ck['independent_expert_task_contract'],tensor_shapes={k:list(v.shape) for k,v in historical.items() if torch.is_tensor(v)},tensor_dtypes={k:str(v.dtype) for k,v in historical.items() if torch.is_tensor(v)},reset_direction_original_preserved='reset_direction' in historical)
  unknown.extend(dict(path='/'+('distributed_rank_contract' if task['canonical']=='CURB_PROTECTED878' else 'independent_expert_scope_state')+'/'+k,type='Seeactualschema',producer_reference='Knownproducerdict has unexpectedextra',physical_or_RNG_application='UNKNOWN') for k in sorted(extra_fields))
  owner_audit=dict(actual_rootkey_diff=rootdiff,known_variant_extra_schema=extra_schema,unmapped_root_or_known_extra_fields=unknown,complete_nested_schema=schema,remaining_builtin_nested_loadowner_review='LOCALsource ASTagainstthiscompleteactualschema required beforefutureSDK',GPU_permission=False,passthrough_only_not_physical_application=True)
  put('CPU_COMPLETE_ROOT_AND_NESTED_SCHEMA_OWNER_AUDIT.json',owner_audit)
'''
assert s.count(anchor)==1;s=s.replace(anchor,extra+anchor,1)
s=s.replace("actual_source_metadata=actual,migration_function_receipt=migration","actual_source_metadata=actual,actual_rootkey_diff=rootdiff,known_variant_extra_schema=extra_schema,unmapped_root_or_extra_owner=unknown,nested_schema_report='CPU_COMPLETE_ROOT_AND_NESTED_SCHEMA_OWNER_AUDIT.json',migration_function_receipt=migration",1)
s=s.replace("kind='E1_CANONICAL_ACTUAL_FOUR_LEAF_CPU_PASS_NO_GPU'","kind='E1_EXPLICIT_VARIANT_ACTUAL_FOUR_LEAF_CPU_PASS_NO_GPU'",1)
s=s.replace("actual_source_metadata=actual,new_typed_source=report['new_typed_source'],counts=count","actual_source_metadata={k:v for k,v in actual.items() if k!='original_CUDA16byte_rng_byteindex'},new_typed_source=report['new_typed_source'],rootkey_diff=rootdiff,unknown_owner=unknown,counts=count",1)
ast.parse(s)
with (B/'cpu_variant_four_leaf_schema_audit_once_v1.py').open('x',encoding='utf-8') as f:f.write(s)
print('Prepared new CPUonly variantworker with root/fullnested schema audit; no model I/O')
