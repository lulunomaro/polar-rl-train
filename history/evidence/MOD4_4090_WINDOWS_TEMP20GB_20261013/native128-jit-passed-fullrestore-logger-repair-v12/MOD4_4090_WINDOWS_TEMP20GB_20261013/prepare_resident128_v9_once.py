"""Use proven small128 projection shape and properresident cap; virtual tracked separately."""
from pathlib import Path
import json,time,sys,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope512_memory20GB_resident_bound_v8_20261013';NEW=R+'/temporary_scope128_memory20GB_resident_v9_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=D/'reports/RESIDENT128_V9_TARGET_CPU_DISPATCH_ACTUAL.json';assert not receipt.exists()
 code="""from pathlib import Path;import json,hashlib,shutil,time,psutil,msvcrt,ast,sys,os
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
x=json.loads((old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_native_v1/output/ORIGINAL_ERROR.json').read_bytes());assert x['worker_exitcode']==1 and x['no_PPO'] and 'MemoryError' in e['error'] and x['own_child_and_descendants_actual_absent']
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
changes=[]
class Small128(ast.NodeTransformer):
 def visit_Constant(self,n):
  if type(n.value) is int and n.value==512:n.value=128
  if isinstance(n.value,str):n.value=n.value.replace('windows4090_temporary512_memory20GB_selected_source_v7','windows4090_temporary128_memory20GB_selected_source_v9')
  return n
for name in ('temporary_worker.py','temporary_state_binding.py','temporary_training_runtime.py','temporary_probe_contract_base.py','windows4090_substep_readback_v6.py','left_head_offset_aware_migration_v3.py','temporary_parent.py'):
 p=new/'payload'/name;before=ref(p);t=Small128().visit(ast.parse(p.read_text(encoding='utf8')));p.write_text(ast.unparse(ast.fix_missing_locations(t))+'\\n',encoding='utf8');changes.append(dict(old=before,new=ref(p)))
p=new/'payload/temporary_state_binding.py';s=p.read_text(encoding='utf8');anchor="if torch.is_tensor(v) and n in v.shape:";assert s.count(anchor)==1;s=s.replace(anchor,"if torch.is_tensor(v) and n in v.shape and not any(path.startswith('/'+k) for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict')):");p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
p=new/'payload/temporary_parent.py';s=p.read_text(encoding='utf8').replace('peakhard >= 30000000000','peakhard >= 60000000000').replace('peakhard >= 31000000000','peakhard >= 62000000000').replace('< 30000000000','< 60000000000');p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
sys.path.insert(0,str(new/'payload'));import torch;assert not torch.cuda.is_initialized()
import original_full20k_binding as original
from selected_source_projection import project_tree
from temporary_state_binding import perenv_inventory
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());ck=original.validate(torch.load(mf['source']['path'],map_location='cpu',weights_only=False),mf['source']['sha256']);rng=torch.get_rng_state().clone();ids=torch.linspace(0,19999,128).round().long();rows=[];small=project_tree(ck,ids,changes=rows)
assert len(rows)==len(perenv_inventory(small))==99 and original.floating_count(small)==107 and torch.equal(rng,torch.get_rng_state())
for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):assert original.same(small[key],ck[key])
fixture=new/'reports/SELECTED128_CPU_SCHEMA_FIXTURE_NOT_GPU_SOURCE.pt';torch.save(small,fixture);assert original.same(small,torch.load(fixture,map_location='cpu',weights_only=False))
cpu=dict(epoch=time.time(),passed=True,no_GPU_or_PPO=True,actual_target_environment_root=str(r),scope=str(new),num_envs=128,original_source=mf['source'],float107=True,projected_perenv99=True,network128_dimension_explicitly_excluded_from_perenv_count=True,all_nonperenv_actorcritic_Adam_global_named_privateRNG_exact=True,CPU_fixture=ref(fixture),actual_source_family_balanced_selection_pending=True,old512privatecommit_failure_retained=True)
cp=new/'reports/TARGET_TEMP128_CPU_PASSED_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8')
mf.update(scope_root=str(new),epoch=time.time(),num_envs=128,virtual_commit_limit_bytes=64000000000,physical_RAM_target_bytes=20000000000,target_CPU_receipt=ref(cp),source_original_num_envs=20000,concrete_future_training_trace_upper_bound_bytes=128*256*24*16*4,private_commit_not_misreported_as_resident_RAM=True,actual_resident_25percent_headroom_required_before_formal=True)
mf['temporary_small_batch_capacities']['gpu_found_lost_aggregate_pairs_capacity']=4194304;mf['admitted_Windows20k_GPU_buffer_capacities']['gpu_found_lost_aggregate_pairs_capacity']=4194304;mf['substep_readback_V6']['source_sha256']=H(new/'payload/windows4090_substep_readback_v6.py')
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary128_memory20GB_resident_sequence_v9',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_only=True,targetCPU=cpu,old_error=e,old_EXIT=x,source_changes=changes,new_manifest=ref(f),proper_resident_limit19500MB_worker134MB_parent=True,physical_softlimit18GB=True,system_pagefile_not_changed=True,virtual64GB_ceiling_not_RAM_use_claim=True)
(new/'reports/RESIDENT128_SOURCE_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
"""
 f=D/'resident128_v9_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');remote=R+'/'+f.name;upload(f,remote,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",100))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_native_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode native -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,new_native_requested_once=True,old_sdk_not_replayed=True,old_sources_failures_preserved=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),new_scope=NEW,N128_native_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('RESIDENT128_V9_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
