"""Source-only binding and tiny closure-schema negatives; no model or torch import."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,time,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
HISTORY=L/'night_frozen_experts_PPO50_gas400_adaptation_20261027'
N=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))
def emit(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 assert not (HERE/'E0_89D_INPUT_WITNESS_BINDINGS_v1.json').exists()
 metadata=HISTORY/'reports/E0_W35_ORIGINAL_CHECKPOINT_CPU_METADATA_V1.json'
 original=json.loads(metadata.read_bytes())['sources']['E0']
 producer=HISTORY/'reports/ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_ACTUAL_V1.json'
 migration=json.loads(producer.read_bytes())['sources']['E0'];assert migration['new_source']['SHA']=='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'
 base=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/reports/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'
 assert H(base)=='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c'
 cpu=json.loads(base.read_bytes());assert cpu['passed']
 first=N/'reports/E0_FIRST_ACTUAL_4090_PPO_V5_FULLRESTORE_CLOCK_GAS400_RETURNED_ACTUAL.json'
 fv=json.loads(first.read_bytes());assert fv['passed_first_PPO'] and fv['actual_restore_and_24control_clock_gas_readback']
 runtime=HISTORY/'E0_runtime50_gas400_candidate_v1/isaac/mod4'
 adapter=HISTORY/'E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py'
 dependencies=[metadata,producer,base,first,adapter,N/'reports/E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json']
 for name in ('action_delay_physics_queue.py','feedback_delay_checkpoint.py','feedback_delay_mild.py','spring_pressure_checkpoint.py',
  'gas_damping_checkpoint.py','chassis_pd_checkpoint.py','chassis_com_component.py','explicit_pd_component.py'):
  dependencies.append(runtime/name)
 binding=dict(schema='mod4.E0.89D.new_formal_FINAL.initialCPU.saved_witness_bindings.v1',epoch=time.time(),
  original_metadata=original['metadata'],original_optimizer_param_group=original['optimizer_summary']['param_groups'][0],
  adaptation_original_provenance=migration['original'],base_source_CPU=row(base),first_PPO=row(first),queue_CPU_adapter=row(adapter),
  runtime_mod_path=str(runtime),base_reset_bank_evidence=cpu['reset_bank_source_CPU'],frozen_small_dependencies=[row(p) for p in dependencies],
  source_producer=row(producer),original_metadata_snapshot=row(metadata),
  metadata_summary_is_not_a_full_hidden_tensor_fingerprint=True,input_model_not_reopened=True,no_normal86_witness_read=True,
  normal_PPO_weights_STD_factors_and_rng_may_evolve=True,whole_NEW_final_initial_CPU_read_pending=True)
 emit('E0_89D_INPUT_WITNESS_BINDINGS_v1.json',binding)
 p=HERE/'review_NEW_E0_89D_formal_FINAL_initial_CPU_once_v1.py';ast.parse(p.read_bytes())
 spec=importlib.util.spec_from_file_location('E0_FINAL_reviewer_source_tiny_schema',p);reviewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(reviewer)
 go=fv['go'];n=2;remote=reviewer.REMOTE+'/e0/adaptation/final_valid_update2.pt'
 final=dict(path=remote,new_updates=n,Adam_step=639600,bytes=123,SHA='a'*64)
 terminal=dict(terminal_all_own_children_waited=True,returncode=0,original_error=False,errors=[],actual_exit=dict(actual_waited=True,returncode=0))
 v=dict(actual_normal_finite_ending_returned=True,actual_finite_transport_returned=True,canonical_None=True,all_original_locks_free=True,
  owner_exit=dict(original_cost_settled=True),owner_cohort_final=dict(original_cost_settled=True,go=dict(e0=go),rows=dict(e0=terminal)),terminal=terminal,
  unique_original_segment=dict(owner_parent_pid=go['original_owner_pid'],experts=dict(e0=dict(started_epoch=go['learning_started_epoch'],actual_returncode=0,duration_bound_passed=True,charged_seconds=100.25)),charged_expert_seconds=100.25),
  original_fee_seconds=100.25,closed_remaining_snapshot=100000.,own_process_out_or_nonexecuting_zombie=[dict(pid=x['pid'],original_out=True) for x in fv['snapshot']['known_own_processes']],
  formal=dict(passed=True,source_SHA=reviewer.SOURCE_SHA,original_frozen_label_unchanged=True,new_branch_skill_qualified=False,final=final),
  published_complete_FINAL_model=dict(twohost_fullSHA_verified=True,source_stat_before_after_unchanged=True,original_producer=final,path=remote,SHA='a'*64,bytes=123,local_path=str(reviewer.MODEL)))
 reviewer.closure_gate(v,fv,reviewer.MODEL);negative={}
 changes=[('partial_no_published_FINAL',lambda x:x.update(published_complete_FINAL_model=None)),
  ('worker_original_error',lambda x:x['terminal'].update(original_error=True)),
  ('terminal_nonzero',lambda x:x['terminal'].update(returncode=1)),
  ('duration_over_original3900',lambda x:x['unique_original_segment']['experts']['e0'].update(charged_seconds=3900.1)),
  ('unverified_twohost_SHA',lambda x:x['published_complete_FINAL_model'].update(twohost_fullSHA_verified=False))]
 for name,change in changes:
  bad=copy.deepcopy(v);change(bad)
  try:reviewer.closure_gate(bad,fv,reviewer.MODEL)
  except (AssertionError,TypeError,KeyError) as e:negative[name]=dict(type=type(e).__name__,message=str(e))
  else:raise AssertionError(name+' accepted')
 emit('E0_FINAL_REVIEWER_SOURCE_AND_TINY_SCHEMA_ACTUAL_V1.json',dict(epoch=time.time(),passed=True,reviewer=row(p),
  synthetic_complete_schema_accepted=True,negative_rejections=negative,no_actual_FINAL_receipt_or_model_was_read=True,
  no_torch_Actor_SDK_GPU_remote_or_ledger_import_or_IO=True,no_input_PT_or_normal86_read=True,actual_model_review_pending=True,
  Git_status='ordinary_supplement_existing89trial_pending_root'))
 print(json.dumps(dict(passed=True,reviewer_SHA=H(p),bindings_SHA=H(HERE/'E0_89D_INPUT_WITNESS_BINDINGS_v1.json'),negative_cases=len(negative),source_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  emit('SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_model_GPU_remote_read=True));raise
