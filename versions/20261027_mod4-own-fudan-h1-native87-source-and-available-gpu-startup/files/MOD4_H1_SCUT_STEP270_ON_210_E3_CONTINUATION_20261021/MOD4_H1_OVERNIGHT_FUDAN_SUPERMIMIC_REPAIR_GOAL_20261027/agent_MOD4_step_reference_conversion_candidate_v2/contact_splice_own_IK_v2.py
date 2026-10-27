"""Reference-only post-contact own IK splice; no force or action injection."""
import numpy as np

def slerp(a,b,u):
    a=np.asarray(a,float);a=a/np.linalg.norm(a);b=np.asarray(b,float);b=b/np.linalg.norm(b)
    if np.dot(a,b)<0:b=-b
    dot=np.clip(np.dot(a,b),-1,1)
    if dot>.9995:
        result=a+(b-a)*u;return result/np.linalg.norm(result)
    angle=np.arccos(dot)
    return (np.sin((1-u)*angle)*a+np.sin(u*angle)*b)/np.sin(angle)

def smooth(u):return u*u*u*(10+u*(-15+6*u))

def own_wheel_centers(state,kin,quat_to_mat):
    pose=kin.forward(state[13:43],enforce_transmission=False);rotation=quat_to_mat(state[3:7])
    return np.stack([rotation@pose[n][:3,3]+state[:3] for n in kin.wheel_names])

def generate_contact_splice(ages,source_states,forward_x,mask73,kin,quat_to_mat,angular_velocity_world,
                            bounds_function,reference_class,*,contact_controls=20,platform_height=.27,
                            edge=.35,platform_depth=.8,own_spawn_height=.337742301121,row_sink=None):
    ages=np.asarray(ages);source_states=np.asarray(source_states)
    if not 10<=contact_controls<=25:raise ValueError('contact transition must be 0.10..0.25s')
    output=source_states.copy();output[:,0]=forward_x;output[:,1]=0
    lo,hi,_=bounds_function(output,kin,quat_to_mat)
    minimum=lo[:,:,2].min(-1);apex=int(np.argmax(minimum))
    crossings=np.where((minimum[:-1]>=platform_height)&(minimum[1:]<platform_height)&(np.arange(len(ages)-1)>=apex))[0]
    if not len(crossings):raise ValueError('No descending own-wheel platform-height intersection')
    before=int(crossings[0]);touch=before+1
    if touch+contact_controls>=len(ages):raise ValueError('Reference does not contain full post-contact transition')
    # Event intersection between two original descending samples. Never reset q to0.
    def interpolate(u):
        state=(1-u)*output[before]+u*output[touch]
        state[3:7]=slerp(output[before,3:7],output[touch,3:7],u)
        return state
    lower=0.;upper=1.
    for _ in range(26):
        middle=(lower+upper)/2;state=interpolate(middle)
        low,_,_=bounds_function(state[None],kin,quat_to_mat)
        if low[0,:,2].min()>=platform_height:lower=middle
        else:upper=middle
    entry=interpolate(lower)
    # X is the new own reference at this control; not a physical command change.
    entry[0]=forward_x[touch]
    entry_low,entry_high,_=bounds_function(entry[None],kin,quat_to_mat)
    if not ((entry_low[0,:,0]>=edge)&(entry_high[0,:,0]<=edge+platform_depth)).all():raise ValueError('First own platform touch before full wheel footprint crossing')
    if not ((entry_low[0,:,1]>=-.6)&(entry_high[0,:,1]<=.6)).all():raise ValueError('First touch outside platform lateral footprint')
    centers0=own_wheel_centers(entry,kin,quat_to_mat)
    neutral_q=np.zeros(30);neutral_poses=kin.forward(neutral_q,enforce_transmission=False)
    neutral_centers=np.stack([neutral_poses[n][:3,3] for n in kin.wheel_names])
    radius=float(kin.source_metadata['actual_own_wheel_collision_radius_m'])
    target_end_z=own_spawn_height+platform_height
    output[touch]=entry;seed=entry[13:43].copy();rows=[];end=touch+contact_controls
    for i in range(touch,end+1):
        u=(i-touch)/contact_controls;blend=smooth(u)
        state=output[i].copy();state[3:7]=slerp(entry[3:7],np.array([1.,0,0,0]),blend)
        state[2]=(1-blend)*entry[2]+blend*target_end_z
        offset0=centers0-entry[:3]
        centers=state[:3]+(1-blend)*offset0+blend*neutral_centers
        centers[:,2]=(1-blend)*centers0[:,2]+blend*(platform_height+radius)
        rotation=quat_to_mat(state[3:7]);corrections=[];fit=None
        for correction in range(5):
            target=(rotation.T@(centers-state[:3]).T).T
            fit=kin.solve(target,seed,max_iterations=40) # original bounded closed-chain IK and tolerances
            if fit.status!='STATIC_KINEMATIC_FIT':
                raise ValueError(dict(reason='ORIGINAL_OWN_IK_FAILED',age=int(ages[i]),correction=correction,result=fit.summary(),target=target.tolist()))
            state[13:43]=fit.joint_pos30;seed=fit.joint_pos30.copy()
            low,high,closure=bounds_function(state[None],kin,quat_to_mat)
            penetration=np.maximum(platform_height-low[0,:,2],0)
            if penetration.max()<=1e-7:break
            # The original center-fit tolerance is1mm. A bounded geometric target
            # correction larger than that tolerance avoids accepting a stale seed
            # within tolerance while its collider remains below the platform.
            adjust=np.where(penetration>1e-7,np.maximum(penetration+.00005,.0011),0)
            centers[:,2]+=adjust;corrections.append(adjust.tolist())
        if (low[0,:,2]<platform_height-1e-7).any():raise ValueError(dict(reason='BOUNDED_FLOOR_CORRECTION_FAILED',age=int(ages[i])))
        if not ((low[0,:,0]>=edge)&(high[0,:,0]<=edge+platform_depth)).all():raise ValueError(dict(reason='CONTACT_FOOTPRINT_LEAVES_PLATFORM',age=int(ages[i])))
        output[i]=state
        rows.append(dict(age=int(ages[i]),u=float(u),root_z_m=float(state[2]),bottom_left_right_m=low[0,:,2].tolist(),
            target_world_center_z_m=centers[:,2].tolist(),actual_world_center_z_m=own_wheel_centers(state,kin,quat_to_mat)[:,2].tolist(),
            closure_max_m=float(closure[0]),IK=fit.summary(),bounded_floor_target_corrections_m=corrections))
        if row_sink is not None:row_sink(rows[-1])
    for i in range(end+1,len(ages)):
        output[i]=output[end];output[i,0]=forward_x[i]
    # Preserve source-air Z/Vz, q/dq, R/omega literally. Only new own XY travel differs.
    output[:,7]=np.gradient(output[:,0],.01)
    output[:,8]=np.gradient(output[:,1],.01)
    root_velocity=np.gradient(output[:,:3],.01,axis=0)
    qvelocity=np.gradient(output[:,13:43],.01,axis=0)
    omega=angular_velocity_world(output[:,3:7],ages*.01)
    output[touch:,7:10]=root_velocity[touch:]
    output[touch:,43:73]=qvelocity[touch:]
    output[touch:,10:13]=omega[touch:]
    lows,highs,closure=bounds_function(output,kin,quat_to_mat)
    if closure.max()>.002:raise ValueError('Original2mm closure bound failed after splice')
    original_columns=np.r_[2:7,9:73]
    if not np.array_equal(output[:touch,original_columns],source_states[:touch,original_columns]):raise ValueError('Original source-air geometry/vertical dynamics modified')
    phase=np.where(ages<100,'pre_request',np.where(np.arange(len(ages))<=apex,'jump_ascent',
            np.where(np.arange(len(ages))<touch,'jump_descent',np.where(np.arange(len(ages))<end,'own_contact_transition','own_platform_support_recovery'))))
    masks=np.broadcast_to(mask73,(len(ages),73)).copy();masks[:,:3]=True;masks[:,7:10]=True
    metadata=dict(reference_role='new_own_MOD4_step_goal_from_Fudan_air_segment_plus_own_postcontact_IK',
        source_air_Z_R_q_vertical_velocity_angular_velocity_qd_literal_preserved_before_touch=True,
        own_forward_goal_differs_from_physical_command=True,physical_command_vx_m_s=.8,
        first_touch_age=int(ages[touch]),first_touch_between_original_ages=[int(ages[before]),int(ages[touch])],
        first_touch_interpolation_fraction=float(lower),contact_transition_controls=contact_controls,
        support_age=int(ages[end]),support_root_z_m=target_end_z,own_spawn_height_m=own_spawn_height,
        initial_touch_not_neutral=True,entry_all_joint_abs_max=float(abs(entry[13:43]).max()),
        entry_masked_joint_abs_max=float(abs(entry[13:43][np.asarray(mask73[13:43],bool)]).max()),
        first_touch_bottom_left_right_m=entry_low[0,:,2].tolist(),
        final_joint_abs_max=float(abs(output[end,13:43]).max()),
        final_masked_joint_abs_max=float(abs(output[end,13:43][np.asarray(mask73[13:43],bool)]).max()),
        final_center_height_error_to_platform_plus_radius_m=(own_wheel_centers(output[end],kin,quat_to_mat)[:,2]-(platform_height+radius)).tolist(),
        original_wheel_center_IK_tolerance_m=.001,closure_max_m=float(closure.max()),
        min_postcontact_wheel_bottom_m=float(lows[touch:,:,2].min()),no_airborne_plus270mm_height=True,
        dynamic_actuation_contact_force_and_success='pending_not_tested',source_contact_used_as_own_contact=False,
        full_body_nonpenetration='pending',unidentified_spin_targets_remain_masked=True,
        contact_floor_correction='Bounded per-wheel geometric target adjustment; not measured contact or physical force')
    return reference_class(ages,output,masks,phase,metadata),rows
