from pathlib import Path
import ast,json,time
H=Path(__file__).resolve().parent;T=H.parent;N=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
s=(P/'review_three_expert_complete_models_original_cost_CPU_V5_unused_once.py').read_text('utf8').replace('import json,time,torch','import json,time,torch,traceback',1).replace("for key in ('h1','e2','recovery'):","for key in ('h1','recovery'):",1)
s=s.replace("finite(s)\n        updates=", "finite(s)\n        if key=='h1':bootstrap_H1=old\n        updates=",1)
native='''    native=dict(present=bool(receipt['complete_models']['e2']),not_production_expert_source=True,not_frozen_skill_or_causal_PPO_speed_comparison=True)
    if native['present']:
        try:
            assert len(receipt['complete_models']['e2'])==1
            final=receipt['complete_models']['e2'][0];state=torch.load(final['local_path'],map_location='cpu',weights_only=False)
            counts=[0,0];finite(state)
            contract=state['UniSuperMimic_test_contract'];method=state['UniSuperMimic_H1_test']
            assert contract['state_joints']==30 and contract['actions']==6 and contract['obs_dim']==128 and contract['goal_dim']==73 and contract['original_physics_and_success_unchanged'] and contract['original_RSL_core_frozen_bootstrap_only'] and contract['not_production_expert_source']
            assert method['iteration']==final['updates'] and final['world_updates']>0 and final['policy_updates']>0
            for name in ('actor_state_dict','critic_state_dict'):
                assert set(state[name])==set(bootstrap_H1[name]) and all(torch.equal(v,bootstrap_H1[name][k]) for k,v in state[name].items())
            assert {int(v['step']) for v in state['optimizer_state_dict']['state'].values()}=={q['specs']['e2']['source_Adamstep']}
            optimizers={}
            for name in ('opt_wm','opt_pi','opt_v'):
                values=method[name]['state'];assert values;steps=[int(v['step']) for v in values.values()]
                optimizers[name]=dict(parameter_states=len(values),min_step=min(steps),max_step=max(steps))
            assert optimizers['opt_wm']['max_step']==final['world_updates'] and optimizers['opt_pi']['max_step']==final['policy_updates'] and optimizers['opt_v']['max_step']>0
            for name in ('wm','pi','critic'):assert method[name] and all(torch.isfinite(v).all() for v in method[name].values() if torch.is_tensor(v))
            cost=segment['experts']['e2'];go=co['go']['e2'];assert cost['actual_returncode']==0 and cost['duration_bound_passed'] and cost['started_epoch']==go['learning_started_epoch'] and abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5
            native.update(passed_native_fullfinite_CPU=True,final=final,finite_tensor_counts=counts,iteration=method['iteration'],world_updates=final['world_updates'],policy_updates=final['policy_updates'],sim_steps=method['sim_steps'],optimizers=optimizers,original_bootstrap_actor_critic_STD_Adam_frozen_exact=True,actual_cost=cost,original_H1_events=final['original_H1_events'],method_model_names={k:len(method[k]) for k in ('wm','pi','critic')})
        except BaseException:
            native.update(passed_native_fullfinite_CPU=False,original_error=traceback.format_exc(),healthy_production_model_checks_retained=True)
    else:
        native.update(passed_native_fullfinite_CPU=False,original_terminal=co['rows']['e2'],original_cost=segment['experts']['e2'],no_missing_FINAL_promoted=True)
'''
s=s.replace("    diagpath=N/'current_three_closed_text/",native+"    diagpath=N/'current_three_closed_text/",1)
s=s.replace("result=dict(epoch=time.time(),passed=True,models=models,","result=dict(epoch=time.time(),passed=True,qualification_scope='production_h1_recovery_pair_and_separate_native_method_diagnostic',models=models,native_method=native,original_slots_cost=segment['experts'],",1)
s=s.replace("'THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'","'PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json'",1)
out=N/'review_closed82q_production_pair_and_native_fullstate_CPU_unused_once.py';assert not out.exists();ast.parse(s);out.write_text(s,'utf8')
analysis='''from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;R=N/'reports';read=lambda p:json.loads(Path(p).read_bytes())
proof=read(R/'PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
path=N/'current_three_closed_text/e2/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl';rows=[]
if path.is_file():
 for i,line in enumerate(path.read_text('utf8').splitlines(),1):
  if line.strip():rows.append(dict(read_line=i,**json.loads(line)))
native=proof['native_method'];curves=[]
for row in rows:
 value=row['events'];assert value['diagnostic_valid'] and value['complete_control_rows']==row['completed_control_rows'] and value['environment_control_transitions']==row['environment_transitions']
 curves.append(dict(GO_elapsed_s=row['GO_elapsed_s'],environment_transitions=row['environment_transitions'],native_iteration=row['native_iteration'],world_updates=row['world_updates'],policy_updates=row['policy_updates'],events=value['events'],leading_edge_cross_events=value['both_leading_edges_cross_event_count'],world_model_losses=row['wm_last'],policy_losses=row['policy_last']))
for a,b in zip(curves,curves[1:]):assert a['GO_elapsed_s']<=b['GO_elapsed_s'] and a['environment_transitions']<=b['environment_transitions'] and a['policy_updates']<=b['policy_updates']
milestones={}
for name in ('takeoff_count','landing_count','recovery_count'):
 first=next((i for i,r in enumerate(curves) if r['events'][name]>0),None)
 milestones[name]=dict(first_positive_curve_row_elapsed_s=(curves[first]['GO_elapsed_s'] if first is not None else None),previous_logged_zero_elapsed_s=(curves[first-1]['GO_elapsed_s'] if first is not None and first>0 else None),event_time_is_interval_censored_by_curve_frequency=True)
result=dict(epoch=time.time(),actual_closed_window=True,native_fullfinite_passed=native.get('passed_native_fullfinite_CPU',False),native_final=native.get('final'),actual_method_original_cost=proof['original_slots_cost']['e2'],curve_rows=curves,first_logged_event_time_brackets=milestones,original_H1_final_completed_control_events=native.get('original_H1_events'),source_actor_fresh128_history10_goal73_versus_pretrained_PPO35_not_matched=True,world_model_loss_not_step_success=True,success_requires_original_270mm_dualwheel_platform_contact_and200stable_callbacks=True,counts_are_stochastic_completed_controls_not_frozen_policy_success_rate=True,elapsed_includes_original_GO_initialization_and_warmup=True,no_PPO_speed_multiplier_or_graduation_claim=True)
with (R/'ACTUAL_NATIVE_H1_CLOSED_WINDOW_CONVERGENCE_TIME_AND_EVENTS_CPU_SUMMARY.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(native_fullfinite=result['native_fullfinite_passed'],curve_rows=len(curves),events=result['original_H1_final_completed_control_events'],original_method_fee=result['actual_method_original_cost']['charged_seconds'])))
'''
out=N/'summarize_closed82q_native_H1_true_events_vs_time_CPU_unused_once.py';assert not out.exists();ast.parse(analysis);out.write_text(analysis,'utf8')
with (N/'reports/NATIVE_FULLSTATE_REVIEW_AND_CONVERGENCE_CURVE_CPU_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_only_readers=True,normal_H1_E3_full17Adamx20_and_actorSTDcritic_change_checks_retained=True,native_actor_world_critic_optimizer_finite_step_checks_separate=True,original_PPO_bootstrap_frozen_not_falsely_20Adam_per_native_iteration=True,single_initial_load_each_FINAL_no_production_source_reread_for_native_bootstrap=True,true_events_vs_GO_time_and_transitions_not_model_loss=True,original_physical_success_and_frozen_evaluation_distinction_retained=True,no_remote_GPU_or_checkpoint_load_yet=True),f,indent=2)
print(json.dumps(dict(prepared_closed_native_CPU_review=True,no_model_read_yet=True)))
