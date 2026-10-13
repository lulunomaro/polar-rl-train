"""New immutable candidate, own final128 source; only then unique GPU lease."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope128_memory20GB_logger_ready_v12_20261013'
PARENT_SHA='f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 n=int(sys.argv[1]);assert n in (640,768)
 case='capacity'+str(n)+'_own128_expanded_benchmark_v5_20261013';new=R+'/'+case
 receipt=D/'reports'/('CAPACITY_'+str(n)+'_TARGET_CPU_DISPATCH_ACTUAL.json');assert not receipt.exists()
 package=D/'CAPACITY_COMPONENTS_TEMPLATE_V5_OWN_STOP.zip';remote=R+'/'+package.name
 upload(package,remote,60)
 code="""from pathlib import Path;import json,hashlib,time,psutil,msvcrt,shutil,zipfile,ast,sys
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+new+"""');N="""+str(n)+"""
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
f=json.loads((old/'attempts/temporary2048_train_v1/output/WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json').read_bytes());x=json.loads((old/'attempts/temporary2048_train_v1/EXIT_RECEIPT.json').read_bytes());released=json.loads((old/'SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json').read_bytes());assert f['passed'] and x['passed'] and released['all_own_descendants_actual_absent'] and released['OSlock_released']
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
source=Path(f['latest']['path']);assert H(source)=='"""+PARENT_SHA+"""' and f['actual_updates']==121
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as z:z.seek(0);msvcrt.locking(z.fileno(),msvcrt.LK_NBLCK,1);z.seek(0);msvcrt.locking(z.fileno(),msvcrt.LK_UNLCK,1)
package=r/'CAPACITY_COMPONENTS_TEMPLATE_V5_OWN_STOP.zip';assert H(package)=='"""+H(package)+"""';assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');(new/'payload').mkdir();(new/'reports').mkdir();(new/'attempts').mkdir()
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
 p=new/'payload'/name;t=EnvCount().visit(ast.parse(p.read_text(encoding='utf8')));p.write_text(ast.unparse(ast.fix_missing_locations(t))+'\\n',encoding='utf8');compile(p.read_text(encoding='utf8'),str(p),'exec')
p=new/'payload/temporary_state_binding.py';t=ast.parse(p.read_text(encoding='utf8'))
for node in t.body:
 if isinstance(node,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='N' for v in node.targets):node.value=ast.Constant(N)
p.write_text(ast.unparse(ast.fix_missing_locations(t))+'\\n',encoding='utf8')
sys.path.insert(0,str(new/'payload'));import torch;assert not torch.cuda.is_initialized();import expanded_source_projection as ex
candidate,CPU=ex.materialize(source,expected_source_sha='"""+PARENT_SHA+"""',target_n=N,output_dir=new/'reports/CPU_ACTUAL_FULLSOURCE_EXPANSION')
import temporary_state_binding as binding
ck=torch.load(candidate,map_location='cpu',weights_only=False);binding.validate(ck,H(candidate));assert ex.floating_count(ck)==107 and len(binding.perenv_inventory(ck))==99
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),num_envs=N,source=ref(source),max_formal_updates=4,capacity_benchmark_only=True,production_weights_discarded=True,planned_production_source='Own prePPO fullrestore, never benchmark-trained weights',parent128_final=ref(source),explicit_slot_replication_from_complete_current_own128=True,concrete_future_training_trace_upper_bound_bytes=N*256*24*16*4)
mf['temporary_small_batch_capacities']['gpu_found_lost_aggregate_pairs_capacity']=8388608 if N<=512 else 16777216;mf['temporary_small_batch_capacities']['gpu_collision_stack_size']=268435456;mf['admitted_Windows20k_GPU_buffer_capacities']=dict(mf['temporary_small_batch_capacities'])
# Current cfg has eleven fields: preserve all non-overridden actual defaults.
previous=json.loads((old/'attempts/temporary2048_fullrestore_v1/output/WINDOWS4090_ORIGINAL_CAPACITY_IDENTITY.json').read_bytes())['actual_new_Windows20k_cfg'];previous.update(mf['temporary_small_batch_capacities']);mf['admitted_Windows20k_GPU_buffer_capacities']=previous
CPU.update(passed=True,source_actual_parent_EXIT=x,new_target_num_envs=N,old_source107_and99_verified=True,source_actorcritic_Adam_not_spliced=True,old_V12_untouched=True)
cp=new/'reports/TARGET_EXPANDED_CAPACITY_CPU_ACTUAL.json';cp.write_text(json.dumps(CPU,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp);mf['substep_readback_V6']['source_sha256']=H(new/'payload/windows4090_substep_readback_v6.py')
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
q=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';q.write_text(json.dumps(mf,indent=2),encoding='utf8');lease=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';lease.write_text(json.dumps(dict(epoch=time.time(),case_id='"""+case+"""',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(q),human20GB_environment_search_authorized=True),indent=2),encoding='utf8')
print(json.dumps(dict(epoch=time.time(),passed_target_CPU_only=True,num_envs=N,source=ref(source),candidateCPU=ref(candidate),proof=ref(cp),new_manifest=ref(q),parent_final_actual_checked=True,no_GPU_pass_inferred=True)))
"""
 p=D/('capacity'+str(n)+'_target_cpu_once.py');assert not p.exists();p.write_text(code,encoding='utf8');compile(code,str(p),'exec');upload(p,R+'/'+p.name,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+R+'/'+p.name+"'",100))
 ps="& '"+new+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+new+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+new+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+new+"/attempts/temporary2048_native_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+new+"/runtime2048' -StageMode native -TrainSeconds 900 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,native_fullrestore_fullPPO4_sequence_requested_once=True,sharedGPU_lease_only_one=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),num_envs=n,new_scope=new)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('CAPACITY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_before_any_continuation=True),indent=2),encoding='utf8');raise
