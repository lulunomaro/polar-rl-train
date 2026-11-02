"""One independently consumed actualCPU source purpose; NO CUDA RNG restore/SDK.
Exactly one original byte/SHA/CPUdecode, only4leaf, full inverseexact; NEWtyped
PT + real ownroundtrip. Externalreceipt only; no new checkpoint metadata keys.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,time,traceback

def main():
 p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();task=json.loads(a.task.read_bytes());B=a.task.parent
 def put(n,v):
  with (B/n).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and task['kind']=='E1_EXPLICIT_VARIANT_ACTUAL_CPU_FOUR_LEAF_ONCE_V1'
 assert task['canonical'] in ('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50')
 put('CPU_PURPOSE_CONSUMED.json',dict(pid=os.getpid(),epoch=time.time(),purpose=task['purpose'],original_source_path=task['source_path'],original_expected_SHA=task['source_SHA'],original_byte_reads_planned=1,original_hash_planned=1,original_CPUdecode_planned=1,CUDA_or_SDK_or_GPU_or_budget=False))
 count=dict(original_byte_reads=0,original_SHA=0,original_CPUdecodes=0,own_roundtrip_byte_reads=0,own_roundtrip_decodes=0)
 try:
  import torch
  torch.set_num_threads(2);assert not torch.cuda.is_initialized();cpu_rng=torch.get_rng_state().clone()
  from e1_four_leaf_migration_v1 import migrate_complete_source,reverse_four_leaf_view,FOUR_PATHS,leaf
  source=Path(task['source_path'])
  with source.open('rb') as f:raw=f.read();count['original_byte_reads']+=1
  sourceSHA=hashlib.sha256(raw).hexdigest();count['original_SHA']+=1
  assert sourceSHA==task['source_SHA'] and len(raw)==task['source_bytes']
  ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);count['original_CPUdecodes']+=1
  def exact(a,b):
   if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.device.type==b.device.type=='cpu' and torch.equal(a,b)
   if isinstance(a,dict):return isinstance(b,type(a)) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
   if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
   if type(a).__module__.startswith('numpy') and hasattr(a,'shape'):
    import numpy as np
    return type(a)is type(b) and a.shape==b.shape and a.dtype==b.dtype and bool(np.array_equal(a,b))
   return type(a)is type(b) and a==b
  def tensor_leaves(v,path=''):
   if torch.is_tensor(v):yield path,v
   elif isinstance(v,dict):
    for k,z in v.items():yield from tensor_leaves(z,path+'/'+str(k))
   elif isinstance(v,(tuple,list)):
    for i,z in enumerate(v):yield from tensor_leaves(z,path+'/'+str(i))
  tensors=list(tensor_leaves(ck));assert all(t.device.type=='cpu' and bool(torch.isfinite(t).all()) for _,t in tensors)
  actualAdam=sorted({int(s['step']) for s in ck['optimizer_state_dict']['state'].values()});assert len(actualAdam)==1 and len(ck['optimizer_state_dict']['state'])==17
  before={path:leaf(ck,path) for path in FOUR_PATHS};typed,migration=migrate_complete_source(ck,role=task['role']);inverse=reverse_four_leaf_view(typed,before);assert exact(inverse,ck)
  assert set(typed)==set(ck) and typed['actor_state_dict'] is ck['actor_state_dict'] and typed['critic_state_dict'] is ck['critic_state_dict'] and typed['optimizer_state_dict'] is ck['optimizer_state_dict']
  rng16=[dict(path=path,numel=t.numel(),dtype=str(t.dtype),byte_SHA=hashlib.sha256(t.contiguous().numpy().tobytes()).hexdigest(),CPU_decoded_bytes_not_CUDA_restored=True) for path,t in tensors if t.dtype==torch.uint8 and t.numel()==16]
  buf=io.BytesIO();torch.save(typed,buf);newraw=buf.getvalue();newSHA=hashlib.sha256(newraw).hexdigest();newpath=B/(task['canonical']+'_FULL20K_TYPED50HZ400N_FOURLEAF_NO_NEW_KEYS.pt')
  with newpath.open('xb') as f:f.write(newraw)
  with newpath.open('rb') as f:own=f.read();count['own_roundtrip_byte_reads']+=1
  assert own==newraw;roundtrip=torch.load(io.BytesIO(own),map_location='cpu',weights_only=False);count['own_roundtrip_decodes']+=1;assert exact(typed,roundtrip)
  assert exact(reverse_four_leaf_view(roundtrip,before),ck) and torch.equal(cpu_rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
  # Actualcomplete root/nestedschema from SAME decodedCPUdict; no re-read.
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
  actual=dict(original_iteration=int(ck['iter']),original_LR=ck['optimizer_state_dict']['param_groups'][0]['lr'],original_17Adam_step=actualAdam[0],original_STD6=ck['actor_state_dict']['distribution.std_param'].tolist(),actor_tensor_count=len(ck['actor_state_dict']),critic_tensor_count=len(ck['critic_state_dict']),actor_first_shape=list(ck['actor_state_dict']['mlp.0.weight'].shape),critic_first_shape=list(ck['critic_state_dict']['mlp.0.weight'].shape),original_topkeys=list(ck),tensor_leaf_count=len(tensors),original_CUDA16byte_rng_count=len(rng16),original_CUDA16byte_rng_byteindex=rng16)
  report=dict(kind='E1_EXPLICIT_VARIANT_ACTUAL_FOUR_LEAF_CPU_PASS_NO_GPU',passed=True,canonical=task['canonical'],purpose=task['purpose'],original_source=dict(path=str(source),bytes=len(raw),SHA=sourceSHA),new_typed_source=dict(path=str(newpath),bytes=len(newraw),SHA=newSHA),actual_source_metadata=actual,actual_rootkey_diff=rootdiff,known_variant_extra_schema=extra_schema,unmapped_root_or_extra_owner=unknown,nested_schema_report='CPU_COMPLETE_ROOT_AND_NESTED_SCHEMA_OWNER_AUDIT.json',migration_function_receipt=migration,all_original_fields_after_reverse_literal_tensor_dtype_shape_exact=True,own_typed_roundtrip_real_IO_and_decode_exact=True,new_checkpoint_topkeys_same_no_undeclared_clock_kind_added=True,CUDA16byte_rng_bytes_preserved_not_CPUrestoredCUDA=True,CPU_globalRNG_unchanged=True,CUDA_initialized=False,counts=count,actor_forward_optimizer_or_SDK_or_budget_operations=0,actual_fullrestore_or_skill_graduation=False)
  put('CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',report);print(json.dumps(dict(passed=True,canonical=task['canonical'],actual_source_metadata={k:v for k,v in actual.items() if k!='original_CUDA16byte_rng_byteindex'},new_typed_source=report['new_typed_source'],rootkey_diff=rootdiff,unknown_owner=unknown,counts=count),indent=2))
 except BaseException:
  put('CPU_FOUR_LEAF_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),counts=count,no_auto_source_reload=True,SDK_GPU_budget_operations=0));raise
if __name__=='__main__':main()
