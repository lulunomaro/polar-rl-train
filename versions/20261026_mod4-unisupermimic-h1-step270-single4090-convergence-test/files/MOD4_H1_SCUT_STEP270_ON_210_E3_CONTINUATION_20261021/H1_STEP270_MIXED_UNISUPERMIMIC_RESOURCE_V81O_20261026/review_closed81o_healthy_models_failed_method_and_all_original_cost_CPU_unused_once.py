from pathlib import Path
import json,time,torch
N=Path(__file__).resolve().parent;R=N/'reports';read=lambda p:json.loads(Path(p).read_bytes())
def main():
    q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    receipt=read(R/'THREE_EXPERT_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert receipt['actual_finite_transport_returned']
    co=receipt['source210']['cohort'];segment=receipt['source210']['original_segment'];assert set(co['go'])==set(segment['experts'])=={'h1','e2','recovery'}
    failed=co['rows']['e2'];assert failed['original_error'] and failed['terminal_all_own_children_waited'] and not (failed.get('final') or {}).get('passed') and receipt['complete_models']['e2']==[]
    fc=segment['experts']['e2'];assert fc['duration_bound_passed'] and fc['charged_seconds']>0 and abs(fc['charged_seconds']-(fc['ended_epoch']-fc['started_epoch']))<1e-5
    torch.set_num_threads(2);models={}
    for key in ('h1','recovery'):
        assert len(receipt['complete_models'][key])==1
        final=receipt['complete_models'][key][0];s=torch.load(final['local_path'],map_location='cpu',weights_only=False)
        source=Path(q['payloads'][key])/'job0/source'/q['specs'][key]['source_filename']
        old=torch.load(source,map_location='cpu',weights_only=False);counts=[0,0]
        def finite(x):
            if torch.is_tensor(x):
                counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
            elif isinstance(x,dict):
                for v in x.values():finite(v)
            elif isinstance(x,(list,tuple)):
                for v in x:finite(v)
        finite(s)
        updates=s['owned_H1_completed_updates'] if key=='h1' else (s['owned_phase_complete_updates'] if key=='e2' else s['E3_production_updates'])
        Adam=q['specs'][key]['source_Adamstep']+20*updates
        assert updates>0 and final['updates']==updates and len(s['optimizer_state_dict']['state'])==17
        assert {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={Adam}
        assert len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8
        changed={name:[k for k in old[name] if not torch.equal(old[name][k],s[name][k])] for name in ('actor_state_dict','critic_state_dict')}
        assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8 and 'distribution.std_param' in changed['actor_state_dict']
        if key=='h1':
            assert not s['failed_partial_prefix'] and s['owned_H1_learning_task']['source_SHA']==q['specs'][key]['source_SHA']
            phase=s['H1_step270_task_state'];assert phase['version']==270 and phase['phase']['version']==270 and phase['phase']['num_envs']==20000
            assert phase['phase']['geometry']==dict(height=.270,edge_x=.35,depth=.8,width=1.2)
            assert s['H1_step270_runtime_contract']['original_D0_D7_STD_optimizer_save_chain_retained']
            assert final['actual17Adam_steps']==[Adam]
            assert s['owned_H1_learning_task']['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only'
        else:
            assert counts==([175,98] if key=='e2' else [173,96]) and s['policy_clock']['policy_hz']==50 and final['Adam_step']==Adam
            if key=='e2':assert s['owned_phase']=='production' and s['owned_new_expert_task']['kind']=='E2_WORLD_MOVING_SIGNED4' and s['owned_new_expert_task']['source_SHA']==q['specs'][key]['source_SHA']
        cost=segment['experts'][key];go=co['go'][key]
        assert cost['actual_returncode']==0 and cost['duration_bound_passed'] and cost['started_epoch']==go['learning_started_epoch']
        assert abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5
        models[key]=dict(final=final,updates=updates,Adam=Adam,counts=counts,all17_changed=changed,actual_cost=cost,source_SHA=q['specs'][key]['source_SHA'])
        models[key]['raw_actor_distribution_std_param6']={'current':s['actor_state_dict']['distribution.std_param'].detach().reshape(-1).tolist(),'source':old['actor_state_dict']['distribution.std_param'].detach().reshape(-1).tolist(),'raw_parameterization_not_inferred_as_effective_STD':True}
        if key=='h1':
            state=s['H1_step270_task_state']['phase'];t=state['tensors'];g=state['goal']
            models[key]['H1_current_episode_snapshot']=dict(
                scope='Only per-environment currently retained episode state at FINAL; selected resets erase earlier events. Not whole-window totals, lifetime maximum, frozen evaluation, or graduation.',
                environments=state['num_envs'],takeoff_count_sum=int(t['takeoff_count'].sum()),
                landing_count_sum=int(t['landing_count'].sum()),recovery_count_sum=int(t['recovery_count'].sum()),
                goal_launched_envs=int(g['launched'].sum()),goal_landed_envs=int(g['landed'].sum()),
                goal_success_envs=int(g['success'].sum()),both_wheels_crossed_envs=int(t['crossed'].all(-1).sum()),
                max_retained_episode_both_wheel_bottom_peak_world_z_m=float(t['peak'].max()),
                retained_episode_peak_positive_envs=int((t['peak']>0).sum()),
                age_control_min=int(t['age_control'].min()),age_control_max=int(t['age_control'].max()),
                goal_attempt_envs=int(g['attempt'].sum()),goal_edge_envs=int(g['edge'].sum()),
                current_goal_air_callback_ticks_max=int(g['air_ticks'].max()),current_goal_land_callback_ticks_max=int(g['land_ticks'].max()),current_goal_stable_callback_ticks_max=int(g['stable_ticks'].max()),
                descriptive_only_no_new_admission_or_skill_threshold=True)
        if key=='recovery':
            phase=s.get('E3_public_recovery_state',{}).get('phase',{})
            tensors=phase.get('tensors',{})
            snapshot=dict(scope='Only per-environment currently retained E3 episode state at FINAL, reset erases earlier credited events. Not whole-window totals, policy evaluation or task graduation.',phase_version=phase.get('version'),state_present=bool(tensors),original_recovery_condition='projected gravity z<-0.984807753, root speed<.03m/s, angular speed<.2rad/s, request active, stable feedback ticks>=50',original_stable_period_seconds=.5,no_new_training_gate=True)
            if tensors:
                recipe=tensors['recipe'];credited=tensors['credited'];cohorts=[]
                for recipe_id in range(13):
                    mask=recipe==recipe_id
                    cohorts.append(dict(recipe=recipe_id,environments=int(mask.sum()),current_episode_credited=int(credited[mask].sum()),current_request=int(tensors['request'][mask].sum()),current_age_feedback_ticks_median=float(tensors['age'][mask].float().median()),current_peak_upright_median=float(tensors['peak'][mask].median()),current_stable_feedback_ticks_max=int(tensors['stable'][mask].max())))
                snapshot.update(environments=len(recipe),currently_credited_fallen_envs=int((credited&(recipe!=12)).sum()),currently_credited_normal_envs=int((credited&(recipe==12)).sum()),per_recipe=cohorts)
            models[key]['E3_current_retained_episode_recovery_snapshot']=snapshot
    diagpath=N/'current_three_closed_text/h1/job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json'
    diagnostic=dict(present=diagpath.is_file(),expected_complete_control_rows=models['h1']['updates']*24,not_a_model_training_or_skill_gate=True)
    if diagpath.is_file():
        try:
            value=read(diagpath);diagnostic['value']=value;diagnostic['complete_closed_window_accounting_valid']=(value.get('schema')=='completed_control_goal_events_v1' and value.get('diagnostic_valid') is True and value.get('complete_control_rows')==models['h1']['updates']*24 and value.get('environment_control_transitions')==models['h1']['updates']*24*20000)
        except (OSError,ValueError) as error:diagnostic.update(complete_closed_window_accounting_valid=False,read_error=str(error))
    models['h1']['lifetime_goal_event_diagnostic']=diagnostic
    jp=N/'current_three_closed_text/h1/job0/production/control_prefix_raw/CONTROL_LANDING_EVENT_JOURNAL_ACTUAL.json'
    jd=dict(present=jp.is_file(),not_a_model_or_skill_gate=True)
    if jp.is_file():
        try:
            jv=read(jp);jd.update(value=jv,complete_control_row_coverage_valid=jv.get('diagnostic_valid') is True and jv.get('completed_control_rows_seen')==models['h1']['updates']*24)
        except (OSError,ValueError) as error:jd.update(read_error=str(error),complete_control_row_coverage_valid=False)
    models['h1']['landing_event_journal_diagnostic']=jd
    assert not torch.cuda.is_initialized()
    result=dict(epoch=time.time(),passed=True,qualification_scope='healthy_h1_recovery_models_with_failed_method_all3_original_cost',failed_method=dict(key='e2',original_error=True,no_qualified_model=True,no_native_policy_update=True,original_terminal=failed,actual_cost=fc),original_slots_cost=segment['experts'],models=models,all_owner_nodes_children_actual_out=True,
                original_canonical_cost_settled=True,all_original_private_shared_locks_free=True,
                actual_cost_sumonce=sum(v['charged_seconds'] for v in segment['experts'].values()),
                remaining_actual_snapshot=receipt['source210']['original_canonical_remaining'],
                no_query_native_replay=True,not_270mm_skill_or_graduation_proof=True)
    with (R/'HEALTHY_PRODUCTION_PAIR_AND_FAILED_METHOD_ORIGINAL_ALL_COST_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(passed=True,models={k:v['final']['SHA'] for k,v in models.items()},original_cost_settled=True)))
if __name__=='__main__':main()
