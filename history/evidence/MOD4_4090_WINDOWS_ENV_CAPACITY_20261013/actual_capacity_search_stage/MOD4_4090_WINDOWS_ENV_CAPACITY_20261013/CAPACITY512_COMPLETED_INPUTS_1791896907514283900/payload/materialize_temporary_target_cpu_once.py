"""Fresh CPU target from actual frozen V6a, explicit temporary2048 state fixture."""
from pathlib import Path
import json,shutil,hashlib,os,time,ast,sys,copy,traceback
R=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013')
S=R/'training_scope_full20k_left_repair_audited_v6a_20261013'
T=R/'temporary_scope2048_memory20GB_left_repair_20261013'
P=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=H(p))
def fresh(p,v):
 with Path(p).open('xb') as f:f.write(json.dumps(v,indent=2).encode());f.flush();os.fsync(f.fileno())
def main():
 assert not T.exists();T.mkdir();(T/'reports').mkdir();(T/'attempts').mkdir()
 prior=json.loads((S/'reports/TARGET_FULL20K_CPU_PASSED_ACTUAL.json').read_bytes());assert prior['passed'] and prior['floating_tensors']==107 and prior['perenv_fields']==99
 for row in prior['sourcefreeze_files']:assert H(row['path'])==row['sha256'],row['path']
 shutil.copytree(S/'runtime20k',T/'runtime2048');shutil.copytree(P,T/'payload')
 C=T/'runtime2048/isaac/mod4';entry=C/'wave50_entry_runtime_v2.py';before=ref(entry)
 t=ast.parse(entry.read_text(encoding='utf8'));f=next(x for x in t.body if isinstance(x,ast.FunctionDef) and x.name=='reset_entry_xy')
 f.body[0:0]=ast.parse("if hasattr(env,'_local_projection_reset_xy'):\n from selected_source_projection import selected_entry\n return selected_entry(env,ids)").body
 entry.write_text(ast.unparse(ast.fix_missing_locations(t))+'\n',encoding='utf8')
 sys.path.insert(0,str(T/'payload'));import torch
 assert not torch.cuda.is_initialized()
 import original_full20k_binding as old
 from selected_source_projection import project_tree
 ck=old.validate(torch.load(prior['source']['path'],map_location='cpu',weights_only=False),prior['source']['sha256'])
 rng=torch.get_rng_state().clone();ids=torch.linspace(0,19999,2048).round().long();changes=[];candidate=project_tree(ck,ids,changes=changes)
 assert len(changes)==99 and old.floating_count(candidate)==107 and torch.equal(rng,torch.get_rng_state())
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):assert old.same(ck[key],candidate[key]),key
 for key in old.IDENTITY_STATES:assert candidate[key]['num_envs']==2048
 fixture=T/'reports/SELECTED2048_CPU_SCHEMA_FIXTURE_NOT_GPU_SOURCE.pt';torch.save(candidate,fixture)
 assert old.same(candidate,torch.load(fixture,map_location='cpu',weights_only=False))
 # Replay-free actual target CPU source and independent storage checks.
 for key in ('actor_state_dict','critic_state_dict'):
  for k,v in ck[key].items():assert candidate[key][k].data_ptr()!=v.data_ptr()
 cpu=dict(epoch=time.time(),passed=True,no_GPU_or_PPO=True,actual_target_environment_root=str(R),scope=str(T),num_envs=2048,original_source=prior['source'],finite_floating107=True,perenv_fields_projected99=True,CPU_fixture_linear_ids_not_actual_family_selection=True,actual_GPU_family_balanced_selection_pending=True,all_globalnamed_private_CPUCUDA_source_state_bytes_preserved_CPU=True,independent_storage=True,no_RNG_in_CPU_projection=True,CPU_fixture=ref(fixture),projection_fields=changes,entry_overlay=dict(old=before,new=ref(entry),selected_source_entry_only=True),whole_full20k_parent_scope_not_changed=True)
 fresh(T/'reports/TARGET_TEMP2048_CPU_PASSED_ACTUAL.json',cpu)
 original=json.loads((S/'prepared/windows20k_left_repair_audited_v6a_sdk10_v1/SDK10_STAGE_MANIFEST_PREPARED_NOT_GRANTED.json').read_bytes())
 sourcefreeze=[ref(p) for base in (T/'runtime2048',T/'payload') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
 manifest=dict(original,epoch=time.time(),scope_root=str(T),num_envs=2048,approved_for_new_Windows4090_scope=True,root_review_actual={'GPU_lease_explicitly_granted':True,'human_new20GB_temporary_scope_authorization':True},sourcefreeze_files=sourcefreeze,target_CPU_receipt=ref(T/'reports/TARGET_TEMP2048_CPU_PASSED_ACTUAL.json'),max_formal_updates=256,temporary_small_batch_capacities=dict(gpu_max_rigid_contact_count=2**21,gpu_max_rigid_patch_count=2**17,gpu_found_lost_pairs_capacity=2**19,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**21),requested_memory_limit_bytes=20000000000,soft_RSS_save_stop_bytes=18000000000,temporary_branch_not_full20k_training=True,initial_family_selection_pending_actual_GPU=True,first_formal_seconds=3600)
 caps=dict(manifest['admitted_Windows20k_GPU_buffer_capacities']);caps.update(manifest['temporary_small_batch_capacities']);manifest['admitted_Windows20k_GPU_buffer_capacities']=caps
 manifest['substep_readback_V6']['source_sha256']=H(T/'payload/windows4090_substep_readback_v6.py')
 manifest['resource_guards']=dict(durable_free_bytes=6000000000,RAM_available_bytes=22000000000,GPU_free_bytes=8000000000)
 manifest['resource_guard_reference']=dict(scope='new temporary2048 20GB hardjob commit ceiling +18GB RSS softstop; full20k guards retained unchanged',actual_peak_required_before_formal=True)
 fresh(T/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json',manifest)
 print(json.dumps(dict(passed=True,scope=str(T),targetCPU=cpu,manifest=ref(T/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json'),GPU_started=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if T.exists():fresh(T/'reports/TARGET_TEMP_CPU_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True))
  raise
