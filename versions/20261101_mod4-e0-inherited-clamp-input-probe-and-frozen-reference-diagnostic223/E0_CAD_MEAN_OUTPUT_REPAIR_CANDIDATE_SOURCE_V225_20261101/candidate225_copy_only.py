"""UNSELECTED copy-only candidate; frozen originals are never written here.

On states where the old left crank mean is projected to the CAD lower stop,
canonicalize its mean head to the hip head plus that stop offset. This removes
an unnecessary raw tail while preserving the SAME-INPUT mean position target.
Last-action observations and sampled behavior may change: physical standing,
walking and jump regression is mandatory before learning. No reward edits.
"""
import copy

ORDER=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin']

def repair_copy(state,proof,optimizer_parameter_ID_by_actor_key,*,allow_synthetic=False):
    if proof.get('synthetic_fixture_only'):
        if not allow_synthetic:raise ValueError('Synthetic geometry cannot admit a real checkpoint')
    elif not(proof.get('actual_original_action_term_verified')and proof.get('actual_SDK_source_SHA')):
        raise ValueError('Fresh actual action-term/default-offset/optimizer-binding proof required')
    if proof.get('source_model_SHA')not in ('a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a','e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538'):
        raise ValueError('Unexpected source model')
    if proof.get('policy_order')!=ORDER or proof.get('leg_scales')!=[.5]*4:
        raise ValueError('Actual action order and four equal original scales required')
    offsets=proof.get('leg_default_offsets');diff=proof.get('diff_min')
    if not isinstance(offsets,list)or len(offsets)!=4 or not isinstance(diff,(float,int)):
        raise ValueError('Actual default offsets and original CAD lower bound required')
    keys=('mlp.6.weight','mlp.6.bias','distribution.std_param')
    if set(optimizer_parameter_ID_by_actor_key)!=set(keys):raise ValueError('Exact optimizer parameter identity mapping required')
    opt=state['optimizer_state_dict'];ids=optimizer_parameter_ID_by_actor_key
    if any(ids[k]not in opt['state']for k in keys)or len(set(ids.values()))!=3:raise ValueError('Missing/ambiguous optimizer slots')
    actor=state['actor_state_dict'];w,b,s=(actor[k]for k in keys)
    if tuple(w.shape)!=(6,64)or tuple(b.shape)!=(6,)or tuple(s.shape)!=(6,):raise ValueError('Unexpected actor shape')
    if float(s[2])<=0:raise ValueError('Homologous right-crank learned STD must be positive')
    delta=(offsets[1]-offsets[0]+float(diff))/.5
    result=copy.deepcopy(state);a=result['actor_state_dict']
    a[keys[0]][0].copy_(w[1]);a[keys[1]][0].copy_(b[1]+delta)
    #Explicit candidate delta:use same source's homologous right-crank STD.
    #This changes the sampled distribution;it is not claimed behavior-exact.
    a[keys[2]][0].copy_(s[2])
    for key in keys:
        old=opt['state'][ids[key]];new=result['optimizer_state_dict']['state'][ids[key]]
        from_row=2 if key==keys[2]else 1
        for moment in ('exp_avg','exp_avg_sq','max_exp_avg_sq'):
            if moment in old:
                if tuple(old[moment].shape)!=tuple(actor[key].shape):raise ValueError('Unexpected optimizer moment shape')
                new[moment][0].copy_(old[moment][from_row])
    result['candidate225_repair_metadata']=dict(status='UNSELECTED_PENDING_ACTUAL_BINDING_AND_PHYSICAL_REGRESSION',
        source_model_SHA=proof['source_model_SHA'],left_crank_mean_head='copy hip output row plus actual CAD offset',
        left_crank_STD='copy same source right-crank STD;explicit new distribution delta',
        source_17Adam_steps_and_LR_preserved=True,only_affected_optimizer_rows_transformed=True,
        other5_heads_trunk_critic_unchanged=True,reward_physics_guards_unchanged=True,
        same_input_mean_target_equivalence_is_conditional=True,rollout_or_sampled_equivalence_claim=False,
        required_before_learning=['Actual SDK action defaults/scales/CAD and optimizer identity proof','New copy qualification','Standing and forward/reverse walking regression','Original plane jump regression'])
    return result
