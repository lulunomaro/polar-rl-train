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
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and task['kind']=='E1_CANONICAL_ACTUAL_CPU_FOUR_LEAF_ONCE_V1'
 assert task['canonical'] in ('CURB141','SLOPE135')
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
  actual=dict(original_iteration=int(ck['iter']),original_LR=ck['optimizer_state_dict']['param_groups'][0]['lr'],original_17Adam_step=actualAdam[0],original_STD6=ck['actor_state_dict']['distribution.std_param'].tolist(),actor_tensor_count=len(ck['actor_state_dict']),critic_tensor_count=len(ck['critic_state_dict']),actor_first_shape=list(ck['actor_state_dict']['mlp.0.weight'].shape),critic_first_shape=list(ck['critic_state_dict']['mlp.0.weight'].shape),original_topkeys=list(ck),tensor_leaf_count=len(tensors),original_CUDA16byte_rng_count=len(rng16),original_CUDA16byte_rng_byteindex=rng16)
  report=dict(kind='E1_CANONICAL_ACTUAL_FOUR_LEAF_CPU_PASS_NO_GPU',passed=True,canonical=task['canonical'],purpose=task['purpose'],original_source=dict(path=str(source),bytes=len(raw),SHA=sourceSHA),new_typed_source=dict(path=str(newpath),bytes=len(newraw),SHA=newSHA),actual_source_metadata=actual,migration_function_receipt=migration,all_original_fields_after_reverse_literal_tensor_dtype_shape_exact=True,own_typed_roundtrip_real_IO_and_decode_exact=True,new_checkpoint_topkeys_same_no_undeclared_clock_kind_added=True,CUDA16byte_rng_bytes_preserved_not_CPUrestoredCUDA=True,CPU_globalRNG_unchanged=True,CUDA_initialized=False,counts=count,actor_forward_optimizer_or_SDK_or_budget_operations=0,actual_fullrestore_or_skill_graduation=False)
  put('CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',report);print(json.dumps(dict(passed=True,canonical=task['canonical'],actual_source_metadata=actual,new_typed_source=report['new_typed_source'],counts=count),indent=2))
 except BaseException:
  put('CPU_FOUR_LEAF_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),counts=count,no_auto_source_reload=True,SDK_GPU_budget_operations=0));raise
if __name__=='__main__':main()
