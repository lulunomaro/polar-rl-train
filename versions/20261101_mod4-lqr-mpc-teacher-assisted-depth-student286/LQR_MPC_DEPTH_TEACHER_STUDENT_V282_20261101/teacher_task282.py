"""Task and receipt fields for the new teacher-assisted student window."""
import hashlib,json
KIND='LQR_MPC_REFERENCE_DEPTH_SUPERMIMIC_400N50_V282'
READY_KIND='LQR_MPC_REFERENCE_DEPTH_STUDENT282_READY'
FIRST_KIND='FIRST_ACTUAL_TEACHER_DEPTH_STUDENT282'
FINAL_KIND='FINAL_ACTUAL_TEACHER_DEPTH_STUDENT282'
SOURCE_SHA='cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b'
TEACHER_SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'

def validate_task(t):
    for k,v in dict(kind=KIND,source_SHA=SOURCE_SHA,teacher_SHA=TEACHER_SHA,
        model_SHA=SOURCE_SHA,model_bytes=31985705,num_envs=80,actor_obs=44,critic_obs=47,
        source_WM_updates=4719,max_parent_seconds=3900,exit_headroom_seconds=300,
        closure_m=.01,mimic_rad=.01,policy_hz=50,feedback_hz=100,physics_dt=.0025,
        TGS=[32,4],gas_nominal_N=400,reference_only=True,literal_reward_unchanged=True).items():
        assert t.get(k)==v,(k,t.get(k),v)
    for k in ('worker_SHA','carrier_CPU_receipt_SHA','source_CPU_report_SHA'):
        assert isinstance(t.get(k),str) and len(t[k])==64,k
    return True

def flat_go_fields(t):
    validate_task(t)
    return dict(learning_scope='teacher_assisted_depth_SuperMimic',teacher_student282=True,
        WM_ONLY=False,FROZEN_TEACHER=True,source_model_SHA=SOURCE_SHA,teacher_SHA=TEACHER_SHA,
        actor_obs=44,critic_obs=47,source_WM_updates=4719,num_envs=80,closure_m=.01,
        mimic_rad=.01,original_Fudan19_methods_16weights_unchanged=True,
        future_actual_depth_in_H32=False,reference_state_supervision=True)

def validate_schedule(c):
    assert set(c['experts'])=={'jump_72'} and c['scheduling_authority']=='human_requested_available_experts'
    validate_task(c['experts']['jump_72']);return True

def valid_ready(row,spec):
    try:
        validate_task(spec);q=row['closed_source_CPU'];v=q['value']
        return bool(v['passed'] and v['kind']==READY_KIND and v['manifest_SHA']==spec['manifest_SHA']
            and v['source_SHA']==SOURCE_SHA and v['source_CPU_report_SHA']==spec['source_CPU_report_SHA']
            and row['manifest_SHA']==spec['manifest_SHA'] and not row['original_error']
            and q['SHA']==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest())
    except (KeyError,AssertionError,TypeError):return False

def validate_go(g,run,t,now):
    validate_task(t);assert g['run_id']==run==t['run_id'] and g['source_SHA']==SOURCE_SHA
    assert g['save_deadline']==g['learning_started_epoch']+3600 and g['max_parent_seconds']==3900
    assert g['learning_started_epoch']<=now<g['save_deadline']
    for k,v in flat_go_fields(t).items():assert g[k]==v,k
    return True

def validate_first(r,t,g):
    assert r['passed'] and r['kind']==FIRST_KIND and r['run_id']==t['run_id']
    assert r['actual_new_Pi_updates']==r['actual_new_critic_updates']==1
    assert r['student']['first_actual_gradient_components']['combined']>0
    assert r['native24_before_first_WM_step_passed']
    assert r['first_complete']['Pi_updates']==1 and r['first_complete']['complete_student_WM_three_optimizers']
    assert r['original_JUMP_reward_unchanged']
    return True
