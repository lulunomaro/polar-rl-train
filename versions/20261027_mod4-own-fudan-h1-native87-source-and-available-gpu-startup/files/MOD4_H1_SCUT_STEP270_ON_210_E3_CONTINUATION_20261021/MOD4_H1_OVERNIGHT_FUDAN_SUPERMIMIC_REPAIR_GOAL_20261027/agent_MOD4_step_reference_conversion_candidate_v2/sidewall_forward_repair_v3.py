"""Existing own FK only: reject early wall strike, repair reference XY timing."""
import numpy as np

def wall_report(ages,states,kin,quat_to_mat,bounds_function,edge=.35,height=.27):
    lo,hi,closure=bounds_function(states,kin,quat_to_mat)
    result=[]
    for k,name in enumerate(kin.wheel_names):
        front=hi[:,k,0]>=edge;cross=np.where(front)[0]
        straddle=front&(lo[:,k,0]<edge)
        violation=straddle&(lo[:,k,2]<height-1e-9)
        result.append(dict(wheel=name,first_front_cross_age=int(ages[cross[0]]) if len(cross) else None,
            straddling_ages=ages[straddle].tolist(),violating_ages=ages[violation].tolist(),
            min_bottom_during_straddle_m=float(lo[straddle,k,2].min()) if straddle.any() else None,
            min_platform_clearance_during_straddle_m=float((lo[straddle,k,2]-height).min()) if straddle.any() else None))
    return dict(passed=all(not r['violating_ages'] for r in result),wheels=result,
        footprint_and_bottom_from_existing_own_FK=True,no_IK_or_physics=True,closure_max_m=float(closure.max())),lo,hi

def hermite(t,start,end,x0,x1,v0,v1):
    duration=(end-start)*.01;u=np.clip((t-start)*.01/duration,0,1)
    return (2*u**3-3*u*u+1)*x0+(u**3-2*u*u+u)*duration*v0+(-2*u**3+3*u*u)*x1+(u**3-u*u)*duration*v1

def repair_delayed_approach(ages,states,kin,quat_to_mat,bounds_function,*,arrival_age=141,edge=.35,height=.27):
    ages=np.asarray(ages);old,lo,hi=wall_report(ages,states,kin,quat_to_mat,bounds_function,edge,height)
    if old['passed']:return states.copy(),dict(changed=False,original_report=old)
    bothclear=(lo[:,:,2]>=height).all(-1);eligible=np.where(bothclear&(ages>=100)&(ages<arrival_age))[0]
    if not len(eligible):raise ValueError('No both-wheel clearance before required arrival; delayed approach unavailable')
    release=int(eligible[0]);release_age=int(ages[release]);arrival=int(np.where(ages==arrival_age)[0][0])
    before=(ages>=100)&(ages<release_age)
    localfront=hi[:,:,0]-states[:,None,0]
    forbidden=lo[:,:,2]<height
    limits=np.where(forbidden,edge-localfront,np.inf)
    approach_x=float(limits[before].min())-.001 # explicit 1mm reference approach clearance, not a runtime health gate
    arrival_x=float(states[arrival,0])
    if not (0<approach_x<arrival_x):raise ValueError('No bounded monotone approach knot')
    x=states[:,0].copy()
    first=(ages>=100)&(ages<=release_age);second=(ages>release_age)&(ages<=arrival_age)
    x[first]=hermite(ages[first],100,release_age,0,approach_x,0,.8)
    x[second]=hermite(ages[second],release_age,arrival_age,approach_x,arrival_x,.8,.8)
    if (np.diff(x[ages<=arrival_age])<-1e-9).any():raise ValueError('Delayed approach reverses own forward goal')
    output=states.copy();output[:,0]=x;output[:,7]=np.gradient(x,.01)
    report,_,_=wall_report(ages,output,kin,quat_to_mat,bounds_function,edge,height)
    if not report['passed']:raise ValueError(dict(reason='DELAYED_APPROACH_STILL_HITS_SIDEWALL',report=report))
    vx=np.gradient(x,.01);ax=np.gradient(vx,.01)
    return output,dict(changed=True,original_report=old,repaired_report=report,
        release_age=release_age,approach_x_m=approach_x,arrival_age=arrival_age,arrival_x_m=arrival_x,
        peak_target_vx_m_s=float(vx.max()),pre_arrival_peak_abs_ax_m_s2=float(abs(ax[(ages>=100)&(ages<=arrival_age)]).max()),
        physical_command_vx_m_s=.8,source_clock_request_Z_R_q_unchanged=True,
        source_contact_IK_not_repeated=True,postarrival_X_literal_unchanged=True,
        dynamic_actuation_contact_force_feasibility='pending')
