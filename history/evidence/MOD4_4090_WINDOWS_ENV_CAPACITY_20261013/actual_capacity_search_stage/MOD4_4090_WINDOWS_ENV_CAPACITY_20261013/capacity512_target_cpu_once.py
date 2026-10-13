from pathlib import Path;import json,hashlib,time,psutil,msvcrt,shutil,zipfile,ast,sys
r=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013');old=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope128_memory20GB_logger_ready_v12_20261013');new=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_own128_expanded_benchmark_v1_20261013');N=512
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
f=json.loads((old/'attempts/temporary2048_train_v1/output/WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json').read_bytes());x=json.loads((old/'attempts/temporary2048_train_v1/EXIT_RECEIPT.json').read_bytes());released=json.loads((old/'SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json').read_bytes());assert f['passed'] and x['passed'] and released['all_own_descendants_actual_absent'] and released['OSlock_released']
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
source=Path(f['latest']['path']);assert H(source)=='f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3' and f['actual_updates']==121
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as z:z.seek(0);msvcrt.locking(z.fileno(),msvcrt.LK_NBLCK,1);z.seek(0);msvcrt.locking(z.fileno(),msvcrt.LK_UNLCK,1)
package=r/'CAPACITY_COMPONENTS_TEMPLATE_V1.zip';assert H(package)=='6a72a3bad1ee745a0349ff7b628b31ab39487683a44637e8f753bc3527fec7ca';assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');(new/'payload').mkdir();(new/'reports').mkdir();(new/'attempts').mkdir()
with zipfile.ZipFile(package) as z:
 for name in z.namelist():assert Path(name).name==name;z.extract(name,new/'payload')
class EnvCount(ast.NodeTransformer):
 def visit_keyword(self,node):
  if node.arg in ('actor_hidden_dims','critic_hidden_dims'):return node
  return self.generic_visit(node)
 def visit_Constant(self,node):
  if type(node.value)is int and node.value==128:node.value=N
  return node
for name in ('temporary_worker.py','temporary_training_runtime.py','temporary_probe_contract_base.py','windows4090_substep_readback_v6.py','left_head_offset_aware_migration_v3.py','temporary_parent.py'):
 p=new/'payload'/name;t=EnvCount().visit(ast.parse(p.read_text(encoding='utf8')));p.write_text(ast.unparse(ast.fix_missing_locations(t))+'\n',encoding='utf8');compile(p.read_text(encoding='utf8'),str(p),'exec')
p=new/'payload/temporary_state_binding.py';t=ast.parse(p.read_text(encoding='utf8'))
for node in t.body:
 if isinstance(node,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='N' for v in node.targets):node.value=ast.Constant(N)
p.write_text(ast.unparse(ast.fix_missing_locations(t))+'\n',encoding='utf8')
sys.path.insert(0,str(new/'payload'));import torch;assert not torch.cuda.is_initialized();import expanded_source_projection as ex
candidate,CPU=ex.materialize(source,expected_source_sha='f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3',target_n=N,output_dir=new/'reports/CPU_ACTUAL_FULLSOURCE_EXPANSION')
import temporary_state_binding as binding
ck=torch.load(candidate,map_location='cpu',weights_only=False);binding.validate(ck,H(candidate));assert ex.floating_count(ck)==107 and len(binding.perenv_inventory(ck))==99
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),num_envs=N,source=ref(source),max_formal_updates=4,capacity_benchmark_only=True,production_weights_discarded=True,planned_production_source='Own prePPO fullrestore, never benchmark-trained weights',parent128_final=ref(source),explicit_slot_replication_from_complete_current_own128=True,concrete_future_training_trace_upper_bound_bytes=N*256*24*16*4)
mf['temporary_small_batch_capacities']['gpu_found_lost_aggregate_pairs_capacity']=8388608 if N<=512 else 16777216;mf['admitted_Windows20k_GPU_buffer_capacities']=dict(mf['temporary_small_batch_capacities'])
# Current cfg has eleven fields: preserve all non-overridden actual defaults.
previous=json.loads((old/'attempts/temporary2048_fullrestore_v1/output/WINDOWS4090_ORIGINAL_CAPACITY_IDENTITY.json').read_bytes())['actual_new_Windows20k_cfg'];previous.update(mf['temporary_small_batch_capacities']);mf['admitted_Windows20k_GPU_buffer_capacities']=previous
CPU.update(passed=True,source_actual_parent_EXIT=x,new_target_num_envs=N,old_source107_and99_verified=True,source_actorcritic_Adam_not_spliced=True,old_V12_untouched=True)
cp=new/'reports/TARGET_EXPANDED_CAPACITY_CPU_ACTUAL.json';cp.write_text(json.dumps(CPU,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp);mf['substep_readback_V6']['source_sha256']=H(new/'payload/windows4090_substep_readback_v6.py')
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
q=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';q.write_text(json.dumps(mf,indent=2),encoding='utf8');lease=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';lease.write_text(json.dumps(dict(epoch=time.time(),case_id='capacity512_own128_expanded_benchmark_v1_20261013',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(q),human20GB_environment_search_authorized=True),indent=2),encoding='utf8')
print(json.dumps(dict(epoch=time.time(),passed_target_CPU_only=True,num_envs=N,source=ref(source),candidateCPU=ref(candidate),proof=ref(cp),new_manifest=ref(q),parent_final_actual_checked=True,no_GPU_pass_inferred=True)))
