"""Bounded NumPy reference conversion; geometric proposal, never plant evidence."""
from dataclasses import dataclass
import numpy as np

def require(v,message):
    if not v:raise ValueError(message)

def build_recorded_kinematics(contract,geometry,kin_class,transform,quat_to_mat):
    """Original FK class, recorded authored frames only. AxisX is pinned exporter convention."""
    by_child={v['child']:dict(v,name=k) for k,v in contract['joints'].items()}
    joints=[]
    for child in geometry['body_names'][1:]:
        row=by_child[child];limits=row['limits_si']
        joints.append(dict(name=row['name'],parent=row['parent'],child=child,
            T0=transform(np.asarray(row['local_pos0']),quat_to_mat(row['local_rot0'])),
            T1inv=np.linalg.inv(transform(np.asarray(row['local_pos1']),quat_to_mat(row['local_rot1']))),
            kind='Prismatic' if row['type']=='slide' else 'Revolute',axis=0,
            lower=-np.inf if limits is None else limits[0],upper=np.inf if limits is None else limits[1]))
    names={r['name']:r for r in joints}
    mimics=[dict(name=k,reference=v['reference_joint'],gearing=v['gearing'],offset=v['offset'],
                 child=names[k]['child'],reference_child=names[v['reference_joint']]['child']) for k,v in contract['mimics'].items()]
    closures=[dict(name=k,parent=v['body0'],child=v['body1'],
         T0=transform(np.asarray(v['anchor0_m']),np.eye(3)),T1=transform(np.asarray(v['anchor1_m']),np.eye(3))) for k,v in contract['closures'].items()]
    points=[]
    for wheel in ('left_wheel','right_wheel'):
        s=[s for s in geometry['shapes'] if s['body']==wheel]
        require(len(s)==1 and s[0]['type']=='Mesh','one recorded wheel collider required')
        s=s[0];points.append(np.asarray(s['points'])@np.asarray(s['linear_body_from_shape']).T+np.asarray(s['origin_body_m']))
    return kin_class(geometry['body_names'],joints,closures,mimics,contract['training_window']['input_difference_min_rad'],points,
        dict(actual_own_wheel_collision_radius_m=max(abs(points[0][:,2])),nominal_spawn_height_m=contract['spawn_height_m'],
             provenance='existing authored-frame contract plus extracted collision JSON; no USD/mesh asset reread'))

def wheel_bounds(states,kin,quat_to_mat):
    require(states.ndim==2 and states.shape[1]==73 and np.isfinite(states).all(),'finite packed73 required')
    lows=[];highs=[];closure=[]
    for state in states:
        poses=kin.forward(state[13:43],enforce_transmission=False);rotation=quat_to_mat(state[3:7])
        vertices=[]
        for name,points in zip(kin.wheel_names,kin.wheel_points):
            p=poses[name];vertices.append((rotation@(p[:3,:3]@points.T+p[:3,3,None])).T+state[:3])
        lows.append([p.min(0) for p in vertices]);highs.append([p.max(0) for p in vertices])
        closure.append(np.linalg.norm(kin.closure_vectors(poses),axis=-1).max())
    return np.asarray(lows),np.asarray(highs),np.asarray(closure)

def ranges(ages,mask):
    selected=np.asarray(ages)[mask].astype(int)
    if not len(selected):return []
    result=[];start=previous=selected[0]
    for value in selected[1:]:
        if value!=previous+1:result.append([int(start),int(previous)]);start=value
        previous=value
    result.append([int(start),int(previous)]);return result

def command_path(ages,*,vx=.8,onset=100,end=180):
    age=np.asarray(ages);t=np.clip((age-onset)*.01,0,(end-onset)*.01)
    return vx*t

def analyze_geometry(ages,states,kin,quat_to_mat,*,edge=.35,height=.27,depth=.8,half_width=.6,vx=.8,root_x_path=None):
    ages=np.asarray(ages);rawlo,rawhi,closure=wheel_bounds(states,kin,quat_to_mat)
    translated=states.copy();translated[:,0]=command_path(ages,vx=vx) if root_x_path is None else root_x_path;translated[:,1]=0
    lo,hi,_=wheel_bounds(translated,kin,quat_to_mat)
    both_clear=(lo[:,:,2]>=height).all(-1)
    fully_inside=((lo[:,:,0]>=edge)&(hi[:,:,0]<=edge+depth)&(lo[:,:,1]>=-half_width)&(hi[:,:,1]<=half_width)).all(-1)
    apex=int(np.argmax(rawlo[:,:,2].min(-1)))
    descending=np.arange(len(ages))>apex
    jointwindow=both_clear&fully_inside&descending
    elapsed=(ages-100)*.01
    localrear=rawlo[:,:,0].min(-1)-states[:,0]
    required=np.where(elapsed>0,(edge-localrear)/np.maximum(elapsed,1e-12),np.inf)
    # Diagnostic lower bound only: command is a target, not a hard physical velocity limit.
    active=both_clear&descending&(elapsed>0)
    result=dict(apex_age=int(ages[apex]),wheel_bottom_peak_m=float(rawlo[:,:,2].min(-1).max()),
      clearance_ge270_age_ranges=ranges(ages,both_clear),descending_clear_age_ranges=ranges(ages,both_clear&descending),
      complete_footprint_inside_at_command08_age_ranges=ranges(ages,fully_inside),
      descending_clear_and_complete_inside_age_ranges=ranges(ages,jointwindow),
      command_vx_m_s=vx,request_age=[100,179],path_kind='ideal_original_command_tracking' if root_x_path is None else 'new_own_task_goal_physical_command_unchanged',
      command_path_assumption='No measured motion claim; new goal is not an actuator command',
      required_constant_vx_from_age100_min_m_s=float(required[active].min()) if active.any() else None,
      from_rest_constant_accel_lower_bound_min_m_s2=float((2*(edge-localrear[active])/elapsed[active]**2).min()) if active.any() else None,
      max_closure_error_m=float(closure.max()),source_contact_used_as_own_contact=False,
      rows=[dict(age=int(f),original_bottom_left_right_m=rawlo[i,:,2].tolist(),original_local_footprint_x_minmax=[rawlo[i,:,0].tolist(),rawhi[i,:,0].tolist()],
          command_root_x_m=float(translated[i,0]),command_footprint_x_minmax=[lo[i,:,0].tolist(),hi[i,:,0].tolist()],
          both_bottom_ge270=bool(both_clear[i]),complete_inside=bool(fully_inside[i]),descending=bool(descending[i]),
          required_constant_vx_m_s=None if not np.isfinite(required[i]) else float(required[i])) for i,f in enumerate(ages)])
    return result,translated,jointwindow,apex

@dataclass
class OwnStepReference:
    ages:np.ndarray
    states:np.ndarray
    masks:np.ndarray
    phases:np.ndarray
    metadata:dict

    def target_bundle(self,ages):
        ages=np.asarray(ages)
        require(np.isfinite(ages).all() and (ages>=self.ages[0]).all() and (ages<=self.ages[-1]).all(),'reference age outside explicit clip')
        indices=np.searchsorted(self.ages,ages)
        require(np.array_equal(self.ages[indices],ages),'integer control ages required')
        s=self.states[indices];m=self.masks[indices]
        return dict(packed73=s,mask73=m,root_xyz=s[...,:3],root_quaternion_wxyz=s[...,3:7],root_velocity=s[...,7:10],
                    joint_q30=s[...,13:43],joint_qd30=s[...,43:73],phase=self.phases[indices],source_contact_is_own_contact=False)

    def future10_goal(self,ages):
        a=np.asarray(ages);bundle=self.target_bundle(a[...,None]+np.arange(10))
        return dict(goal=bundle['packed73']*bundle['mask73'],mask=bundle['mask73'],phase=bundle['phase'])

    def objective_error(self,states,ages):
        b=self.target_bundle(ages)
        require(np.asarray(states).shape==b['packed73'].shape,'same named packed state shape required')
        # Diagnostic target consistency, not a new training reward or SO3 loss.
        return ((states-b['packed73'])**2*b['mask73']).sum(-1)

def generate_candidate(ages,states,base_mask,kin,quat_to_mat,*,edge=.35,height=.27,depth=.8,vx=.8,root_x_path=None):
    """Keep original jump until actual own-wheel descending clearance window.

    Reject if ideal original command does not reach the platform in that window.
    A conditional C1 landing splice never raises the airborne reference by .27m.
    It blends q to the own neutral support shape and lowers root to the platform
    support height before the original descending clearance window ends.
    """
    report,translated,window,apex=analyze_geometry(ages,states,kin,quat_to_mat,edge=edge,height=height,depth=depth,vx=vx,root_x_path=root_x_path)
    failures=[];candidate=None
    ids=np.where(window)[0]
    if not len(ids):failures.append('NO_DESCENDING_CLEARANCE_AND_COMPLETE_FOOTPRINT_WINDOW_AT_ORIGINAL_COMMAND')
    else:
        begin=int(ids[0]);end=int(ids[-1])
        if end-begin<3:failures.append('LANDING_SPLICE_WINDOW_TOO_SHORT_MIN3_CONTROLS')
        else:
            support=states[0].copy();neutral_low,_,_=wheel_bounds(support[None],kin,quat_to_mat)
            support_z=support[2]+height-float(neutral_low[0,:,2].mean())
            if translated[begin,2]<support_z:failures.append('DESCENDING_START_BELOW_OWN_NEUTRAL_PLATFORM_SUPPORT_HEIGHT')
            else:
                output=translated.copy();q0=states[begin,13:43];qd0=states[begin,43:73]
                duration=(end-begin)*.01
                # Cubic Hermite endpoints preserve beginning q/qdot and finish neutral/zero.
                for i in range(begin,len(ages)):
                    u=min(1.,(i-begin)/(end-begin));a=2*u**3-3*u*u+1;b=u**3-2*u*u+u;c=-2*u**3+3*u*u
                    output[i,13:43]=a*q0+b*duration*qd0+c*support[13:43]
                    output[i,2]=a*translated[begin,2]+b*duration*states[begin,9]+c*support_z
                    # Rotation is held from the splice entry; reject unless already neutral.
                    output[i,3:7]=states[begin,3:7]
                if abs(np.dot(states[begin,3:7],support[3:7]))<1-1e-5:failures.append('ENTRY_ORIENTATION_NOT_NEUTRAL_ROTATION_SPLICE_REQUIRES_REVIEW')
                output[:,7:10]=np.gradient(output[:,:3],.01,axis=0)
                output[:,43:73]=np.gradient(output[:,13:43],.01,axis=0)
                low,high,closure=wheel_bounds(output,kin,quat_to_mat)
                if (closure>.002).any():failures.append('SPLICE_BREAKS_ORIGINAL_2MM_CLOSED_CHAIN_CONSTRAINT')
                if (low[begin:end+1,:,2]<height-1e-6).any():failures.append('SPLICE_WHEEL_PENETRATES_PLATFORM_GEOMETRY')
                if (np.diff(output[begin:end+1,2])>1e-6).any():failures.append('SPLICE_ADDS_UPWARD_FLIGHT_HEIGHT')
                if not failures:
                    mask=np.broadcast_to(base_mask,(len(ages),73)).copy();mask[:,:3]=True;mask[:,7:10]=True
                    phases=np.where(ages<100,'pre_request',np.where(np.arange(len(ages))<=apex,'jump_ascent',np.where(np.arange(len(ages))<end,'jump_descent','own_platform_support_recovery')))
                    candidate=OwnStepReference(np.asarray(ages),output,mask,phases,dict(splice_age=int(ages[begin]),support_age=int(ages[end]),
                        platform_height_m=height,edge_x_m=edge,command_vx_m_s=vx,reference_only=True,dynamic_actuation_and_actual_contact_pending=True))
    report.update(status='GEOMETRIC_REFERENCE_CANDIDATE_ONLY' if candidate is not None else 'REJECTED_NO_STEP_REFERENCE_EXPORTED',rejection_reasons=failures,
        dynamic_feasibility='pending',full_body_nonpenetration='pending',motor_limits_and_impulse='pending',own_contact_and_success='not_tested',
        no_airborne_plus270mm_translation=True,no_own_contact_from_foreign_reference=True)
    return candidate,report


def bounded_own_forward_timing(ages,states,kin,quat_to_mat,*,edge=.35,height=.27,command_vx=.8):
    """New reference GOAL only. Physical command, source clock and actions unchanged.

    Choose four descending-clear controls where root is still above own neutral
    platform support height. Reach the required rear-footprint displacement at
    the first of those controls. Cubic Hermite starts at rest and ends at the
    unchanged .8m/s command; report required speeds/accelerations without calling
    them actuator-feasible. Reject if there is no such bounded geometric window.
    """
    ages=np.asarray(ages);lo,_,_=wheel_bounds(states,kin,quat_to_mat)
    neutral=states[0:1];nlo,_,_=wheel_bounds(neutral,kin,quat_to_mat)
    support_z=states[0,2]+height-nlo[0,:,2].mean()
    apex=int(np.argmax(lo[:,:,2].min(-1)));clear=(lo[:,:,2]>=height).all(-1)
    eligible=np.where(clear&(np.arange(len(ages))>apex)&(states[:,2]>=support_z))[0]
    possible=[i for i in eligible if i+3<len(ages) and clear[i:i+4].all()]
    require(possible,'No four-control descending geometric landing-splice opportunity')
    begin=possible[-1];arrival=int(ages[begin]);duration=(arrival-100)*.01
    require(duration>0,'No positive forward travel duration')
    localrear=lo[begin,:,0].min()-states[begin,0]
    displacement=edge-localrear
    t=np.clip((ages-100)*.01,0,duration);u=t/duration
    x=(-2*u**3+3*u*u)*displacement+(u**3-u*u)*duration*command_vx
    after=ages>arrival
    x[after]=displacement+command_vx*np.clip((ages[after]-arrival)*.01,0,(180-arrival)*.01)
    vx=np.gradient(x,.01);ax=np.gradient(vx,.01)
    return x,dict(kind='new_own_task_goal_physical_command_unchanged',arrival_age=arrival,
        required_root_displacement_m=float(displacement),available_time_s=float(duration),
        required_mean_vx_m_s=float(displacement/duration),required_target_peak_vx_m_s=float(vx.max()),
        required_target_peak_abs_ax_m_s2=float(abs(ax).max()),physical_command_vx_m_s=command_vx,
        command_only_displacement_at_arrival_m=command_vx*duration,
        extra_displacement_over_command_tracking_m=float(displacement-command_vx*duration),
        support_root_z_m=float(support_z),target_x_by_age=x.tolist(),
        dynamic_motor_force_power_contact_feasibility='pending_not_tested',source_clock_and_request_unchanged=True)
