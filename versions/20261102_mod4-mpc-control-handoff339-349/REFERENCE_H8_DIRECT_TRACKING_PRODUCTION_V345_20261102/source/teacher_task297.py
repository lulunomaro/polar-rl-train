"""Explicit reference-tracking admission; preserve original finite accounting."""
import hashlib,json,math
KIND='REFERENCE_CONDITIONED_TRACKING_BPTT_400N50_V297'
READY_KIND='REFERENCE_TRACKING297_READY'
FIRST_KIND='FIRST_ACTUAL_REFERENCE_TRACKING297'
FINAL_KIND='FINAL_ACTUAL_REFERENCE_TRACKING297'
SOURCE_SHA='4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d'
TEACHER_SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'
def sha(s):return isinstance(s,str)and len(s)==64 and all(c in'0123456789abcdef'for c in s)
def validate_task(t):
    expected=dict(kind=KIND,source_SHA=SOURCE_SHA,model_SHA=SOURCE_SHA,model_bytes=32407215,teacher_SHA=TEACHER_SHA,
        actor_obs=103,critic_obs=106,goal_dim=59,num_envs=80,source_WM_updates=7087,source_actor_Adam_step=42940,
        new_tracking_critic_Adam_step=0,max_parent_seconds=3900,save_seconds=3600,exit_headroom_seconds=300,
        policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],closure_m=.01,mimic_rad=.01,gas_nominal_N=400,
        reference_only=True,Fudan_objective_used=False,critic_same_tracking_return=True,planned_reference_tracker=True)
    for k,v in expected.items():assert t.get(k)==v,(k,t.get(k),v)
    for k in('worker_SHA','source_CPU_report_SHA','teacher_whole_CPU_receipt_SHA','carrier_CPU_receipt_SHA'):assert sha(t.get(k)),k
    assert t['reference']['SHA']=='6d28486ed94c5007a9efc1899eb5f4b1bc7757ebca980f7535628fef716a0d82'and t['reference']['bytes']==68977
    assert t['run_id'].startswith('REFERENCE_TRACKING297_');return True
def flat_go_fields(t):
    validate_task(t)
    return dict(learning_scope='reference_conditioned_tracking_BPTT',teacher_student297=True,reference_tracking297=True,
        WM_ONLY=False,FROZEN_TEACHER=True,source_model_SHA=SOURCE_SHA,teacher_SHA=TEACHER_SHA,actor_obs=103,critic_obs=106,
        goal_dim=59,num_envs=80,source_WM_updates=7087,closure_m=.01,mimic_rad=.01,Fudan_objective_used=False,
        fixed_velocity_reward_used=False,critic_same_tracking_return=True,planned_reference_tracker=True,future_actual_depth_in_H32=False)
def validate_schedule(c):
    assert set(c['experts'])=={'jump_72'}and c['scheduling_authority']=='human_requested_available_experts'
    validate_task(c['experts']['jump_72']);return True
def ready_value_SHA(v):return hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
def valid_ready(row,spec):
    try:
        validate_task(spec);q=row['closed_source_CPU'];v=q['value']
        return bool(v['passed']and v['kind']==READY_KIND and v['manifest_SHA']==spec['manifest_SHA'] and v['source_SHA']==SOURCE_SHA
            and v['source_CPU_report_SHA']==spec['source_CPU_report_SHA']and v['actual_source_migration_and_H32_CPU_passed']
            and v['admission_optimizer_steps']==0 and row['manifest_SHA']==spec['manifest_SHA']and row['key']==spec['key']
            and row['phase']=='ready'and not row['original_error']and q['SHA']==ready_value_SHA(v))
    except(KeyError,AssertionError,TypeError):return False
def validate_ready_go(g,v,spec):
    assert g['source_CPU_SHA']==ready_value_SHA(v)and g['manifest_SHA']==spec['manifest_SHA']and g['source_qualification_kind']==READY_KIND;return True
def go_identity(g,run,t):
    validate_task(t);assert g['run_id']==run==t['run_id']and g['source_SHA']==SOURCE_SHA
    assert g['save_deadline']==g['learning_started_epoch']+3600 and g['nominal_end_epoch']==g['learning_started_epoch']+3900 and g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300
    assert sha(g['source_CPU_SHA'])and sha(g['manifest_SHA'])and g['source_qualification_kind']==READY_KIND
    for k,v in flat_go_fields(t).items():assert g[k]==v,k
    return True
def validate_go(g,run,t,now):go_identity(g,run,t);assert g['learning_started_epoch']<=now<g['save_deadline'];return True
def counters(r,t,g,first):
    go_identity(g,t['run_id'],t)
    assert r['passed']and r['kind']==(FIRST_KIND if first else FINAL_KIND)and r['run_id']==t['run_id']and r['source_SHA']==SOURCE_SHA
    assert r['reference_tracking_objective'] and not r['Fudan_rewards_used'] and not r['original_JUMP_reward_unchanged']
    pi=r['actual_new_Pi_updates'];assert pi==r['actual_new_critic_updates']and(pi==1 if first else pi>0)
    assert r['actual_new_WM_updates']>0 and r['total_WM_updates']==7087+r['actual_new_WM_updates']
    assert r['actual_new_PPO_updates']==r['actual_new_STD_updates']==r['actual_frozen_teacher_updates']==0
    assert r['native24_before_first_WM_step_passed']and r['complete_three_optimizer_conversion']and r['teacher_frozen']
    count=r['new_completed_controls'];assert count>=64 and r['new_environment_transitions']==80*count and r['physics_callbacks']==8*count and r['feedback_samples']==2*count
    s=r['first_complete'if first else'final'];assert sha(s['SHA'])and s['bytes']>0
    assert s['Pi_updates']==s['critic_updates']==pi and s['complete_student_WM_three_optimizers']and s['full_student_WM_tree_finite']and s['full_Adam_norm_RNG_DR_reward_memory_saved']
    assert s['WM_Adam_step_min']==s['WM_Adam_step_max']==r['total_WM_updates']
    assert s['actor_Adam_step_min']==s['actor_Adam_step_max']==42940+pi
    assert s['critic_Adam_step_min']==s['critic_Adam_step_max']==pi and s['teacher_Adam_step']==42940
    assert s['save_epoch']>=g['learning_started_epoch'if first else'save_deadline']
    if first:
        d=r['student']['first_actual_gradient_components'];assert d['tracking_only']>0 and d['combined']>0 and all(math.isfinite(v)for v in d.values())
    assert r['student']['critic_same_tracking_return']and not r['student']['Fudan_objective_used']
    return True
def validate_first(r,t,g):return counters(r,t,g,True)
def validate_final(r,t,g):return counters(r,t,g,False)
