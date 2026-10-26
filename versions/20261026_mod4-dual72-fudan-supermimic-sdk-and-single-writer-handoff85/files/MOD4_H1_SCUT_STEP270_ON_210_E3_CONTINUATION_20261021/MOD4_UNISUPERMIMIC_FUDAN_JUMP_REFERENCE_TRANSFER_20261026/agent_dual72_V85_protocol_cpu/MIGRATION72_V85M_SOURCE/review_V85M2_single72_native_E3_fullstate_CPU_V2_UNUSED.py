from pathlib import Path
import json,time,torch,sys
N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N));read=lambda p:json.loads(Path(p).read_bytes())

def review_new_native_method(receipt,q,co,segment):
    import hashlib,importlib.util
    rows=receipt['native_H1_method_fullstate'];terminal=co['rows']['e2'];cost=segment['experts']['e2']
    base=dict(present=False,original_terminal=terminal,actual_cost=cost,not_production_H1_or_E2_source=True,not_frozen_skill_graduation=True)
    assert cost['duration_bound_passed'] and 0<cost['charged_seconds']<=3900
    if not rows:
        assert not (terminal.get('final') or {}).get('passed'),'Passed terminal checkpoint was not collected; preserve collection failure'
        return dict(base,no_qualified_native_model=True,rc0_is_not_success=True)
    assert len(rows)==1 and terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors']
    final=rows[0];commit=terminal['final'];assert commit['passed'] and commit['trace_persisted'] and final['twohost_complete_SHA'] and final['SHA']==commit['final']['SHA']
    spec=q['specs']['e2'];s=torch.load(final['local_path'],map_location='cpu',weights_only=False)
    bootstrap=Path(q['payloads']['e2'])/'job0/source'/spec['source_filename'];old=torch.load(bootstrap,map_location='cpu',weights_only=False)
    expected=s['UniSuperMimic_publication'];producer=expected['producer'];pins=spec['candidate_pins']
    assert producer['bridge_source_SHA']==pins['bridge_source_SHA'] and producer['finalization_source_SHA']==pins['finalization_source_SHA']
    assert producer['bootstrap_task_source_SHA']==spec['source_SHA'] and producer['reference_artifact_SHA']==spec['reference_artifact_SHA']
    assert producer['adapter_CPU_report_SHA']==spec['adapter_CPU_report_SHA'] and producer['objective_contract_SHA']==spec['objective_contract_SHA']
    runtime_order=read(N/'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json')
    assert runtime_order['actual_runtime_order_readback'] and runtime_order['complete_named_permutation'] and runtime_order['before_first_physical_step_and_Pi']
    assert runtime_order['reference_artifact_SHA']==spec['reference_artifact_SHA'] and producer['runtime_objective_contract_SHA']==runtime_order['runtime_objective_contract_SHA']
    runtime_contract_path=N/'current_three_closed_text/e2/job0/production'/spec['objective_contract_runtime_basename']
    assert hashlib.sha256(runtime_contract_path.read_bytes()).hexdigest()==producer['runtime_objective_contract_SHA']
    from mixed84_protocol_v1 import validate_objective_contract
    runtime_contract=read(runtime_contract_path);validate_objective_contract(runtime_contract);assert runtime_contract['provider_execution_scope']=='runtime_actual_SDK_named_mapping_required' and runtime_contract['reference_metadata']['sdk_joint_order_verified'] is True
    for name in ('run_token','save_token'):assert expected[name]==commit['final'][name]
    module_path=Path(q['payloads']['e2'])/'source/native_finalization_v1.py'
    assert hashlib.sha256(module_path.read_bytes()).hexdigest()==pins['finalization_source_SHA']
    module_spec=importlib.util.spec_from_file_location('new_native_finalization_verified_source',module_path);module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    module.verify_native(s,expected)
    def exact(a,b):
        if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
        if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
        if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
        return type(a)==type(b) and a==b
    for name in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[name],old[name]),'Frozen83B PPO bootstrap changed: '+name
    assert {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={829700}
    native=s['UniSuperMimic_H1_test'];assert native['iteration']==commit['final']['updates']>0
    assert commit['final']['world_updates']>0 and commit['final']['policy_updates']>0
    assert all(name in native for name in ('wm','pi','critic','opt_wm','opt_pi','opt_v'))
    return dict(base,present=True,final=final,producer=producer,bootstrap_frozen_Adam829700=True,world_updates=commit['final']['world_updates'],policy_updates=commit['final']['policy_updates'],native_fullstate_CPU_verified=True)

def main():
    q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    receipt=read(R/'V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_RETURNED_ACTUAL.json');assert receipt['actual_finite_transport_returned']
    co=receipt['authority72']['cohort'];segment=receipt['authority72']['original_segment'];assert set(co['go'])==set(segment['experts'])=={'e2','recovery'}
    torch.set_num_threads(2);models={}
    for key in ('recovery',):
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
    assert not torch.cuda.is_initialized()
    native=review_new_native_method(receipt,q,co,segment)
    assert set(models)=={'recovery'}
    result=dict(epoch=time.time(),passed=True,qualification_scope='normal83B_E3_and_separate_Fudan_native_H1_method_H1_PPO_deferred',models=models,native_method=native,normal_E2_83B_preserved_paused=dict(SHA='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f',Adam=857460),all_owner_nodes_children_actual_out=True,
                original_canonical_cost_settled=True,all_original_private_shared_locks_free=True,
                actual_cost_sumonce=sum(v['charged_seconds'] for v in segment['experts'].values()),
                remaining_actual_snapshot=receipt['authority72']['original_canonical_remaining'],
                no_query_native_replay=True,not_270mm_skill_or_graduation_proof=True)
    with (R/'V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(passed=True,models={k:v['final']['SHA'] for k,v in models.items()},original_cost_settled=True)))
if __name__=='__main__':main()
