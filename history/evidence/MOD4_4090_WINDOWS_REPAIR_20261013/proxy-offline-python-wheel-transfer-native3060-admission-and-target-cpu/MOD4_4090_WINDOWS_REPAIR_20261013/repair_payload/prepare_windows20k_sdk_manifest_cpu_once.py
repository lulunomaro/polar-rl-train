"""CPU-only draft of SDK10 stage manifest/lease; root review must grant GPU.

The draft always has approved_GPU_scope=false.  Real budget/cost/resource inputs
may be supplied by the root; otherwise missing references are explicit pending.
This tool never fills future PASSED receipts or invents guard/extension values.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, sys, time, traceback
from materialize_windows20k_target_cpu_once import ENVIRONMENT_ROOT,SCOPE_NAME,H,ref,fresh_json

def checked_ref(row):
 assert set(row)>={'path','sha256'} and Path(row['path']).is_absolute()
 assert H(row['path'])==row['sha256'],'explicit input SHA mismatch'
 return json.loads(Path(row['path']).read_bytes())
def fieldpath(tree,path):
 for key in path:tree=tree[key]
 return tree
def budget_reference(config):
 """Root provides actual schema paths, values are read from original evidence."""
 b=config['budget_original_saved_reference'];source=checked_ref(b)
 conservative=config.get('budget_mode')=='actual_saved_applied_7_records_conservative_walltime_bound'
 if conservative:
  six=checked_ref(config['sixth_budget_applied_reference'])
  assert six['applied_once'] and six['authorized_before']==468000 and six['authorized_after']==828000 and six['added_seconds']==360000 and six['old_segments_and_other_fields_exact']
  assert source['applied_once'] and source['extension_id']=='USER_ADD100H_20261011_7TH'
  assert source['authorized_before']==six['authorized_after']==828000 and source['authorized_after']==1188000 and source['added_seconds']==360000 and source['extension_records']==7
  assert source['old_six_extensions_unchanged'] and source['charged_unchanged'] and source['completed_segments_unchanged']
  assert config['original_initial_base_seconds_root_reviewed']==36000
  authorized=source['authorized_after'];base=36000;remaining=source['remaining_seconds'];ext=None
  assert 0<=remaining<=authorized and source['epoch']<=time.time()
 else:
  mapping=config['budget_schema_paths'];authorized=fieldpath(source,mapping['authorized_seconds']);base=fieldpath(source,mapping['base_seconds']);extensions=fieldpath(source,mapping['extensions'])
  assert type(authorized) in (int,float) and authorized==1188000 and base==36000
  ext=[fieldpath(row,mapping['each_extension_seconds']) for row in extensions]
  assert len(ext)==7 and sum(ext)+base==authorized and all(type(x) in (int,float) and x>0 for x in ext)
  remaining=fieldpath(source,mapping['remaining_snapshot_seconds']);assert type(remaining) in (int,float) and 0<=remaining<=authorized
 index=config['pending_parent_cost_index'];costs=checked_ref(index);rows=fieldpath(costs,config['pending_cost_schema_paths']['rows']);seen=set();pending=[]
 for row in rows:
  keys=config['pending_cost_schema_paths'];identity=fieldpath(row,keys['unique_segment_identity']);assert identity not in seen;seen.add(identity)
  accounted=fieldpath(row,keys['already_accounted_original_canonical']);assert type(accounted) is bool
  noPPO=fieldpath(row,keys['no_PPO_cost_excluded']);assert type(noPPO) is bool
  exitref=fieldpath(row,keys['parent_EXIT_reference']);actual=checked_ref(exitref)
  duration=fieldpath(actual,keys['actual_parent_EXIT_seconds']);assert type(duration) in (int,float) and duration>=0
  classification=fieldpath(row,keys['classification']);assert classification in ('actual_PPO','failed_learning_startup','CPU_SDK_native_fullrestore_noPPO')
  assert noPPO==(classification=='CPU_SDK_native_fullrestore_noPPO')
  if not accounted and not noPPO:pending.append(dict(unique_segment_identity=identity,seconds=duration,parent_EXIT_reference=exitref,classification=classification))
 out=dict(authorized_seconds=authorized,base_seconds=base,extension_seconds=ext,remaining_snapshot_seconds=remaining,pending_unique_actual_parent_cost_seconds=sum(x['seconds'] for x in pending),pending_actual_parent_segments=pending,actual_original_saved_reference=b,pending_parent_cost_index=index,canonical_reconciliation_pending=True,new_budget_authority=False,no_canonical_copy_write_refund_or_recharge=True)
 if conservative:
  # One canonical controller is exclusive. Even deducting every elapsed wall
  # second is a lower planning bound; it is not the actual charged ledger.
  assert all(checked_ref(x['parent_EXIT_reference'])['epoch']-x['seconds']>=source['epoch'] for x in pending),'pending costs outside covered interval require an independent deduction'
  out.update(extension_records_count=source['extension_records'],aggregate_extension_seconds=authorized-base,individual_extension_record_values_not_reconstructed=True,sixth_budget_applied_reference=config['sixth_budget_applied_reference'],planning_mode='conservative_all_walltime_since_actual_saved_snapshot_lower_bound',snapshot_epoch=source['epoch'],snapshot_is_not_current_live_remaining=True,pending_cost_interval_already_covered_by_elapsed_walltime=True,no_second_subtraction_of_covered_localcost=True,prepared_conservative_remaining_lower_bound_seconds=max(0.,remaining-(time.time()-source['epoch'])),lower_bound_not_actual_charged_or_new_budget=True)
 return out
def resources(config):
 source=checked_ref(config['resource_guard_review']);paths=config['resource_guard_schema_paths']
 passed=fieldpath(source,paths['planning_passed']);assert passed is True
 values={k:fieldpath(source,paths[k]) for k in ('durable_free_bytes','RAM_available_bytes','GPU_free_bytes')}
 assert all(type(v) is int and v>0 for v in values.values())
 # These are approved requirements from evidence, not current-free snapshots.
 assert fieldpath(source,paths['values_are_guard_requirements_not_available_snapshots']) is True
 return values
def saved_readonly_budget_config(scope,B):
 D=scope/'repair_payload/admission_reference_data';portable=json.loads((D/'PENDING_PARENT_COST_PORTABLE_SOURCE_INDEX.json').read_bytes());rows=[]
 for row in portable['rows']:
  r=dict(row);r['parent_EXIT_reference']=ref(D/row['parent_EXIT_filename']);rows.append(r)
 path=B/'ACTUAL_PARENT_COST_INDEX_RELOCATED_EVIDENCE_ONLY.json'
 fresh_json(path,dict(epoch=time.time(),rows=rows,original_portable_index=ref(D/'PENDING_PARENT_COST_PORTABLE_SOURCE_INDEX.json'),unique_cost_seconds=portable['total_actual_parent_pendingcost_seconds'],canonical_pending_not_written=True))
 return dict(budget_mode='actual_saved_applied_7_records_conservative_walltime_bound',budget_original_saved_reference=ref(D/'BUDGET_APPLIED_7TH_ORIGINAL.json'),sixth_budget_applied_reference=ref(D/'BUDGET_APPLIED_6TH_ORIGINAL.json'),original_initial_base_seconds_root_reviewed=36000,pending_parent_cost_index=ref(path),pending_cost_schema_paths={'rows':['rows'],'unique_segment_identity':['unique_segment_identity'],'already_accounted_original_canonical':['already_accounted_original_canonical'],'no_PPO_cost_excluded':['no_PPO_cost_excluded'],'parent_EXIT_reference':['parent_EXIT_reference'],'actual_parent_EXIT_seconds':['wall_seconds'],'classification':['classification']})
def prepare(root,case,config_path=None):
 scope=root/SCOPE_NAME;reports=scope/'reports';receipt=reports/'TARGET_FULL20K_CPU_PASSED_ACTUAL.json';cpu=json.loads(receipt.read_bytes())
 assert cpu['passed'] and cpu['no_GPU_or_PPO'] and cpu['actual_target_environment_root']==str(root)
 assert cpu['floating_tensors']==107 and cpu['perenv_fields']==99 and cpu['all107finite_and99full20k_unprojected']
 assert cpu['future_GPU_API_offsets_restore_probe_and_PPO_pending']
 assert re.fullmatch(r'windows20k_left_repair_sdk10_v[1-9][0-9]*',case),'new precise SDK10 case identity only'
 B=scope/'prepared'/case;assert not B.exists(),'draft consumed; inspect original result instead of overwriting';B.mkdir()
 manifest=dict(epoch=time.time(),approved_for_new_Windows4090_scope=False,root_review_actual={'GPU_lease_explicitly_granted':False,'review_and_real_resources_pending':True},environment_root=str(root),scope_root=str(scope),shared_gpu_lock=str(root/'WINDOWS4090_GPU_EXCLUSIVE.lock'),num_envs=20000,seed=20260928,source=cpu['source'],source_environment=cpu['source_environment'],sourcefreeze_files=cpu['sourcefreeze_files'],approved_ABI_metadata_bindings=cpu['approved_ABI_metadata_bindings'],admitted_leg_offsets=[0.,0.,0.,0.],actual_GPU_allenv_action_API_offsets_and_default_q_exact_still_required=True,admitted_Windows20k_GPU_buffer_capacities=cpu['assembly']['actual_new_SDK_default_capacity11'],actual_capacity_source=cpu['assembly']['capacity_source'],old_Linux_effective_capacity_equivalence_unproven=True,target_CPU_receipt=ref(receipt),required_stage_receipts={'fullrestore':[],'train':[]},original005_budget_reference=None,resource_guards=None,resource_guard_reference=None,pending_inputs=[],source_first_exact_then_one_left_migration=True,no_local128_projection_or_91d_splice=True,no_future_PASSED_or_GPU_lease_inferred=True)
 readonly_budget=saved_readonly_budget_config(scope,B)
 manifest['original005_budget_reference']=budget_reference(readonly_budget)
 if config_path:
  config=json.loads(Path(config_path).read_bytes());assert config['actual_environment_root']==str(root)
  if 'budget_original_saved_reference' not in config:config={**readonly_budget,**config}
  manifest['original005_budget_reference']=budget_reference(config);manifest['resource_guards']=resources(config);manifest['resource_guard_reference']=config['resource_guard_review'];manifest['actual_root_input_config']=ref(config_path)
  installation=checked_ref(config['installation_ready_receipt']);assert fieldpath(installation,config['installation_schema_paths']['passed']) is True
  manifest['installation_ready_receipt']=config['installation_ready_receipt'];manifest['installation_GPU_initialization_not_claimed']=True
 else:manifest['pending_inputs']=['actual_approved20k_guard_requirements','actual_Torch_Sim_Lab_installation_ready_receipt','root_explicit_GPU_lease_review']
 path=B/'SDK10_STAGE_MANIFEST_PREPARED_NOT_GRANTED.json';fresh_json(path,manifest)
 P=scope/'repair_payload';lease=dict(epoch=time.time(),case_id=case,environment_root=str(root),scope_root=str(scope),shared_gpu_lock=str(root/'WINDOWS4090_GPU_EXCLUSIVE.lock'),mode='sdk',approved_GPU_scope=False,attempt_path=str(scope/'attempts'/case),python=str(root/'env/python.exe'),runtime_root=str(scope/'runtime20k'),manifest_sha256=H(path),worker_sha256=H(P/'windows4090_repair_worker.py'),parent_sha256=H(P/'run_windows4090_stage_once.py'),source_sha256=cpu['source']['sha256'],target_CPU_receipt=ref(receipt),root_review_and_actual_GPUlease_grant_required=True,one_independent_fresh_process_no_remote_oldmain=True)
 leasepath=B/'SDK10_LEASE_PREPARED_NOT_GRANTED.json';fresh_json(leasepath,lease)
 # CLI/action are reviewable; neither ScheduledTask registration nor launch occurs.
 command=[str(root/'env/python.exe'),str(P/'run_windows4090_stage_once.py'),'--lease',str(leasepath),'--manifest',str(path),'--attempt',lease['attempt_path'],'--python',lease['python'],'--runtime-root',lease['runtime_root'],'--mode','sdk','--train-seconds','3600']
 result=dict(epoch=time.time(),passed=True,CPU_draft_prepared_only=True,GPU_lease_granted=False,SDK_native_fullrestore_PPO_not_run=True,manifest=ref(path),lease=ref(leasepath),parent_argv=command,parent_module_same_as_ScheduledTask_wrapper=True,ScheduledTask_name='MOD4_Windows4090_Repair_20261013_'+case,ScheduledTask_registered_or_started=False,ScheduledTask_triggers_planned=0,no_periodic_or_boot_or_SSH_child_lifetime=True,explicit_shared_environment_OSlock=lease['shared_gpu_lock'],pending_inputs=manifest['pending_inputs'],all_large_originals_retained=True,Git_supplement_pending_root=True)
 fresh_json(B/'SDK10_MANIFEST_LEASE_CPU_PREPARED_ACTUAL.json',result);return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--environment-root',default=ENVIRONMENT_ROOT);p.add_argument('--case-id',default='windows20k_left_repair_sdk10_v1');p.add_argument('--root-input-config');a=p.parse_args();root=Path(a.environment_root).resolve();assert root==Path(ENVIRONMENT_ROOT).resolve(),'actual Windows environment only'
 try:prepare(root,a.case_id,a.root_input_config)
 except BaseException:
  d=root/SCOPE_NAME/'reports';fresh_json(d/('SDK10_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_PPO=True,prepared_not_granted=True));raise
if __name__=='__main__':main()
