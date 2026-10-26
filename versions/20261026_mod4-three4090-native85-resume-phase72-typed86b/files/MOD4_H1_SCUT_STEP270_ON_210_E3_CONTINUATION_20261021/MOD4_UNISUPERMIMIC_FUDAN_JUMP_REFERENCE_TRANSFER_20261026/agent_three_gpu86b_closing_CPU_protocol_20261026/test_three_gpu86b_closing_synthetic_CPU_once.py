"""Synthetic gates/fees/model objects/text capture only; no SSH/PT/NPZ/GPU."""
from pathlib import Path
from copy import deepcopy
import ast,base64,hashlib,importlib.util,json,os,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;T=D.parent.parent;sys.path.insert(0,str(D))
import three_gpu86b_closing_protocol_v1 as p
import review_three_gpu86b_finals_CPU_unused_once as r
import collect_three_gpu86b_finals_actual_cost_unused_once as c
import torch
torch.set_num_threads(1)


def main():
 cases=[]
 def case(name,fn,reject=False):
  try:
   fn()
   if reject:raise AssertionError('Negative fixture unexpectedly admitted')
   cases.append(dict(name=name,passed=True,expected_rejection=False))
  except Exception as error:
   if reject and str(error)!='Negative fixture unexpectedly admitted':cases.append(dict(name=name,passed=True,expected_rejection=True,error=str(error),exception_type=type(error).__name__))
   else:cases.append(dict(name=name,passed=False,expected_rejection=reject,error=str(error),exception_type=type(error).__name__,traceback=traceback.format_exc()))
 def forbidden(*a,**k):raise AssertionError('All torch.load calls forbidden in this synthetic harness')
 torch.load=forbidden
 go={key:dict(source_SHA=p.SOURCES[key],learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,
   max_parent_seconds=3900,exit_headroom_seconds=300) for key in p.KEYS}
 go['e2'].update(native_continuation_restore_required=True,source_native_iteration=68,window_start_world_updates=680,
   window_start_policy_updates=58,bootstrap_SHA=p.SOURCES['h1'],bootstrap_Adam=829700)
 case('original900_gate_exact_boundary_positive',lambda:p.closing_gate(go,3100.))
 case('original900_gate_one_second_early_rejected',lambda:p.closing_gate(go,3099.),True)
 wrong=deepcopy(go);wrong['e2']['window_start_policy_updates']=0
 case('native_GO_cumulative_baseline_mismatch_rejected',lambda:p.closing_gate(wrong,3100.),True)
 q=dict(run_id='SYNTHETIC86B',owner_root=p.ROOT72+'/owner',owner_identity=dict(pid=123,creation=90.,root='/synthetic/cwd_not_file_root'),
   roots=dict(h1=p.ROOT210+'/h1',e2=p.ROOT72+'/e2',recovery=p.ROOT72+'/recovery'),
   specs={k:dict(key=k,source_SHA=p.SOURCES[k],execution_backend='source210' if k=='h1' else 'target72') for k in p.KEYS})
 case('owner_root_independent_from_identity_cwd_positive',lambda:p.validate_detached(q))
 wrong=deepcopy(q);wrong['owner_root']=wrong['owner_identity']['root']
 case('identity_cwd_cannot_replace_owner_file_root',lambda:p.validate_detached(wrong),True)
 wrong=deepcopy(q);wrong['specs']['h1']['token']='SYNTHETIC_ONLY'
 case('secret_field_saved_metadata_rejected',lambda:p.validate_detached(wrong),True)
 experts={key:dict(started_epoch=100.,ended_epoch=200.,charged_seconds=100.,max_parent_seconds=3900,
   actual_returncode=0,duration_bound_passed=True) for key in p.KEYS}
 authority=dict(owner_exit=dict(original_cost_settled=True),cohort=dict(original_cost_settled=True,rows={k:dict(returncode=0) for k in p.KEYS}),
   all_authority72_owner_children_actual_out=True,canonical_active_segment=None,canonical_path=p.CANONICAL,
   original_locks=[dict(actual_fcntl_free=True),dict(actual_fcntl_free=True)],original_canonical_remaining=587657.6840648651,
   original_segment=dict(owner_parent_pid=123,started_epoch=95.,experts=experts,charged_expert_seconds=300.))
 case('three_independent_original_actual_fee_sumonce_positive',lambda:p.validate_fees(authority,go,q['owner_identity']))
 for name,mutate in (
   ('false_duration',lambda x:x['original_segment']['experts']['e2'].update(duration_bound_passed=False)),
   ('fee_clamp',lambda x:x['original_segment']['experts']['h1'].update(charged_seconds=99.)),
   ('missing_slot',lambda x:x['original_segment']['experts'].pop('h1')),
   ('active_canonical',lambda x:x.update(canonical_active_segment={})),
   ('second_wrong_owner',lambda x:x['original_segment'].update(owner_parent_pid=124))):
  wrong=deepcopy(authority);mutate(wrong);before=json.dumps(wrong,sort_keys=True)
  def rejected(wrong=wrong,before=before):
   try:p.validate_fees(wrong,go,q['owner_identity'])
   finally:assert json.dumps(wrong,sort_keys=True)==before,'Original fee metadata mutated'
  case('original_fee_reject_'+name+'_without_repair',rejected,True)
 def core(Adam,value):
  actor={'distribution.std_param':torch.full((6,),float(value))};actor.update({str(i):torch.full((1,),float(value)) for i in range(8)})
  critic={str(i):torch.full((1,),float(value)) for i in range(8)}
  optimizer=dict(state={i:dict(step=torch.tensor(Adam),exp_avg=torch.zeros(1),exp_avg_sq=torch.zeros(1)) for i in range(17)},param_groups=[dict(params=list(range(17)))])
  return dict(actor_state_dict=actor,critic_state_dict=critic,optimizer_state_dict=optimizer)
 for key in ('h1','recovery'):
  s=core(p.ADAM[key]+20,1.);old=core(p.ADAM[key],0.);final=dict(updates=1)
  if key=='h1':
   s.update(owned_H1_completed_updates=1,failed_partial_prefix=False,
    owned_H1_learning_task=dict(source_SHA=p.SOURCES[key],reward_recipe_version='step270_sampled_leg_excess_v8_reward_only'),
    H1_step270_task_state=dict(version=270,phase=dict(version=270,num_envs=20000,geometry=dict(height=.270,edge_x=.35,depth=.8,width=1.2))),
    H1_step270_runtime_contract=dict(original_D0_D7_STD_optimizer_save_chain_retained=True))
   final['actual17Adam_steps']=[p.ADAM[key]+20]
  else:
   s.update(E3_production_updates=1,policy_clock=dict(policy_hz=50,physics_dt_s=.0025,decimation=8),E3_task=dict(source_SHA=p.SOURCES[key]),
    E3_public_recovery_state={},E3_reset_contract={},synthetic_other_saved_tensors=[torch.zeros(1) for _ in range(45)]+[torch.zeros(1,dtype=torch.int64) for _ in range(60)])
   final['Adam_step']=p.ADAM[key]+20
  spec=dict(source_SHA=p.SOURCES[key])
  case(key+'_normal_PPO_17Adam20_all17_changed_positive',lambda s=s,old=old,key=key,spec=spec,final=final:r.review_normal_object(s,old,key,{},spec,final))
  wrong=deepcopy(s);wrong['optimizer_state_dict']['state'][0]['step']-=1
  case(key+'_normal_bad_Adam_rejected',lambda wrong=wrong,old=old,key=key,spec=spec,final=final:r.review_normal_object(wrong,old,key,{},spec,final),True)
  wrong=deepcopy(s);wrong['actor_state_dict']['distribution.std_param']=old['actor_state_dict']['distribution.std_param'].clone()
  case(key+'_normal_unchanged_STD_rejected',lambda wrong=wrong,old=old,key=key,spec=spec,final=final:r.review_normal_object(wrong,old,key,{},spec,final),True)
 old_source=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026/payloads/e2/source/native_finalization_v1.py'
 ms=importlib.util.spec_from_file_location('closing_fixture_original_publisher',old_source);pubmod=importlib.util.module_from_spec(ms);ms.loader.exec_module(pubmod)
 bootstrap=core(829700,0.);source={key:{} for key in pubmod.REQUIRED_ORIGINAL_GROUPS};source.update(deepcopy(bootstrap))
 refs=dict(reference_artifact_SHA='0b9d642f3530ad55bd353c19918a0778378746ecc250e1f22c10c58b8c095c94',
   adapter_CPU_report_SHA='8761ebdcd7ce6a2c9e9e7a087237145a2f7e8bd641308060dc1ebc6a22d1c148',
   objective_contract_SHA='ee372360ced1fcd0eef6d4c8c7258495ecba99bcd6b0e2ad2c45a7154d6dcecd',
   runtime_objective_contract_SHA='ea471a40d99a2b990702469405209e33cea33ff474f4ede4c3322bc7d16b90f3')
 producer=dict(refs,bridge_source_SHA='b'*64,finalization_source_SHA='f'*64,continuation_source_SHA='c'*64,
   bootstrap_task_source_SHA=p.SOURCES['h1'],native_continuation_source_checkpoint_SHA=p.SOURCES['e2'],
   native_continuation_source_run_id='SOURCE85_SYNTHETIC',native_not_production_H1_or_E2_source=True)
 def opt(step):return dict(state={0:dict(step=torch.tensor(float(step)),exp_avg=torch.zeros(1),exp_avg_sq=torch.zeros(1))},param_groups=[dict(params=[0])])
 old_native=dict(iteration=68,wall_time=1.,sim_steps=100,args=dict(synthetic=True),saved_at=1.,
   wm=dict(w=torch.zeros(1)),pi=dict(w=torch.zeros(1)),critic=dict(w=torch.zeros(1)),opt_wm=opt(680),opt_pi=opt(58),opt_v=opt(232))
 source['UniSuperMimic_H1_test']=old_native
 source['UniSuperMimic_publication']=dict(world_updates=680,policy_updates=58,producer=dict(refs))
 s=deepcopy(source);native=s['UniSuperMimic_H1_test'];native.update(iteration=69,wm=dict(w=torch.ones(1)),pi=dict(w=torch.ones(1)),critic=dict(w=torch.ones(1)),opt_wm=opt(681),opt_pi=opt(59),opt_v=opt(233))
 pub=dict(native_iteration=69,world_updates=690,policy_updates=59,producer=producer,run_token='r',save_token='s',history_shape=[1,2,3],episode_step_shape=[1])
 s.update(UniSuperMimic_publication=pub,UniSuperMimic_test_contract=deepcopy(pubmod.NATIVE_CONTRACT),UniSuperMimic_obs_history=torch.zeros(1,2,3),UniSuperMimic_bridge_ep_step=torch.zeros(1,dtype=torch.int64))
 restore=dict(passed=True,source_checkpoint_SHA=p.SOURCES['e2'],restored_iteration=68,restored_world_updates=680,restored_policy_updates=58,
   all_three_native_optimizers_restored=True,new_physical_episode=True,replay_restored=False,fresh_replay_refill_steps=48)
 final=dict(updates=69,world_updates=690,policy_updates=59,producer=producer,run_token='r',save_token='s')
 commit=dict(passed=True,trace_persisted=True,primary_error=None,secondary_errors=[],final=final,
   native_continuation=dict(restore=restore,window_progress=dict(world_updates=10,policy_updates=1),no_fresh_weight_restart=True))
 spec=dict(candidate_pins=dict(bridge_source_SHA='b'*64,finalization_source_SHA='f'*64,continuation_source_SHA='c'*64),**{k:refs[k] for k in ('reference_artifact_SHA','adapter_CPU_report_SHA','objective_contract_SHA')})
 case('native68_680_58_to69_690_59_three_optimizer_frozen_bootstrap_positive',lambda:r.native_objects(s,source,bootstrap,commit,spec,final,pubmod.verify_native))
 wrong=deepcopy(commit);wrong['final']['policy_updates']=58;wrong['native_continuation']['window_progress']['policy_updates']=0
 case('native_cumulative58_is_not_new_window_positive',lambda:p.native_window(wrong),True)
 wrong=deepcopy(commit);wrong['native_continuation']['restore']['source_checkpoint_SHA']=p.SOURCES['h1']
 case('native_restore_source_cannot_be_PPO83B',lambda:p.native_window(wrong),True)
 wrong=deepcopy(s);wrong['actor_state_dict']['distribution.std_param']+=1
 case('native_bootstrap_STD_change_rejected',lambda:r.native_objects(wrong,source,bootstrap,commit,spec,final,pubmod.verify_native),True)
 wrong=deepcopy(s);wrong['UniSuperMimic_H1_test']['opt_pi']['state'][0]['step']=torch.tensor(57.)
 case('native_optimizer_source_step_regression_rejected_without20Adam_rule',lambda:r.native_objects(wrong,source,bootstrap,commit,spec,final,pubmod.verify_native),True)
 case('optional_phase_missing_is_observability_limitation',lambda:p.require(p.optional_phase(None)['model_gate'] is False,'Optional missing became gate'))
 case('optional_phase_invalid_is_observability_limitation',lambda:p.require(p.optional_phase({'reader_error':'synthetic'})['model_gate'] is False,'Optional malformed became gate'))
 phase=dict(schema='mod4.native.sampled_policy_phase_coverage.v1',diagnostic_valid=True,window_start_iteration=68,
   counts_attempted_starts_not_completed_optimizer_updates=True,not_a_training_or_model_or_skill_gate=True,
   policy_sampling_calls=2,sampled_starts=5,bands={'before50':1,'50to99':1,'100to135':1,'136to179':1,'180plus':1},imagined_horizon_intersects_request=2)
 case('optional_phase_attempted_samples_never_equal_required_completedPi',lambda:p.require(p.optional_phase(phase)['sampled_starts']==5,'Phase reader failed'))
 reads=[];loads=[];raw=b'synthetic in-memory object bytes';sha=hashlib.sha256(raw).hexdigest()
 pool=r.OneLoadPool(raw_reader=lambda path:(reads.append(path) or raw),loader=lambda value:(loads.append(value) or {'tiny':True}))
 def pool_case():
  a=pool.load('synthetic_source',sha,'H1_source');b=pool.load('same_source_bootstrap_alias',sha,'native_bootstrap')
  assert a is b and len(reads)==len(loads)==1 and pool.records[-1]['reused_in_memory']
 case('one_initial_source_load_reused_for_native_frozen_bootstrap',pool_case)
 # Exercise the exact text-only mismatch exception with tiny local synthetic
 # files. No model path is passed to capture and no transport is constructed.
 fixture=D/('synthetic_text_fixtures_'+str(time.time_ns()));(fixture/'reports').mkdir(parents=True)
 class SF:
  def get_channel(self):return self
  def settimeout(self,*args):pass
  def get(self,remote,local):Path(local).write_bytes(b'transferred synthetic mismatch')
  def close(self):pass
 class Client:
  def open_sftp(self):return SF()
 calls=[]
 def fresh_text(*args,**kwargs):
  calls.append(1);value=b'fresh synthetic text';return dict(path='synthetic',bytes=len(value),SHA=hashlib.sha256(value).hexdigest(),mtime_ns=1,base64=base64.b64encode(value).decode())
 row=dict(path='/synthetic/omni.processlifetime.log',relative='h1/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log',bytes=3,SHA=hashlib.sha256(b'old').hexdigest())
 def mismatch_case():
  texts,models=c.capture(Client(),dict(text_files=[row]),[],'h1','never_executed',fixture,fresh_text)
  assert len(calls)==1 and not models and texts[0]['one_fresh_snapshot_only']
 case('only_original_omni_log_mismatch_one_fresh_text_snapshot',mismatch_case)
 bad=dict(row,relative='h1/unexpected.log');other=fixture/'unexpected';(other/'reports').mkdir(parents=True)
 case('other_text_mismatch_rejected_original_transfer_retained',lambda:c.capture(Client(),dict(text_files=[bad]),[],'h1','never_executed',other,fresh_text),True)
 assert (other/'current_three_closed_text/h1/unexpected.log').is_file()
 for path in D.glob('*.py'):case('source_AST_'+path.name,lambda path=path:ast.parse(path.read_text('utf8')))
 def two_layers():
  collector=(D/'collect_three_gpu86b_finals_actual_cost_unused_once.py').read_text('utf8');remote=(D/'three_gpu86b_close_readonly_remote_v1.py').read_text('utf8')
  phrase="assert max(x['nominal_end_epoch'] for x in"
  assert phrase in collector and phrase in remote and 'time.monotonic()+850' in remote and 'time.monotonic()+180' in remote
  assert collector.index(phrase)<collector.index('secret=memory.recover()')
 case('two_original900_gates_before_transport_and_original850_180_waits',two_layers)
 assert not torch.cuda.is_initialized()
 result=dict(epoch=time.time(),passed=all(x['passed'] for x in cases),count=len(cases),passed_count=sum(x['passed'] for x in cases),cases=cases,
   synthetic_only=True,real_PT_NPZ_read_hash_copy=False,remote_SSH_GPU_ledger_Task_GO=False,CUDA_initialized=False,
   collector_or_actual_close_reviewer_executed=False,fixture_text_directory=str(fixture),archive='pending root phase Git archive')
 path=D/'reports'/('THREE_GPU86B_CLOSING_SYNTHETIC_CPU_ATTEMPT_'+str(time.time_ns())+'.json')
 with path.open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=result['passed'],count=result['count'],passed_count=result['passed_count'],report=str(path))))
 if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
