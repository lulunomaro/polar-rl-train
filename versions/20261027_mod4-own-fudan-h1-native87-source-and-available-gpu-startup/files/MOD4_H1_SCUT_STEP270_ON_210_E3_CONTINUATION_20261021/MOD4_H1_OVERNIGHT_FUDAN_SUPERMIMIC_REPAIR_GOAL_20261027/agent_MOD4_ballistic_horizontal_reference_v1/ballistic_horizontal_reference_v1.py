"""Own X/VX reference only. No IK, forces, action changes or contact evidence."""
import numpy as np

def profile(ages,vpre,vflight,flight_start,touch_age=145,brake_s=.4):
    ages=np.asarray(ages);t=ages*.01;t0=1.;ta=flight_start*.01;tt=touch_age*.01
    if not (0<=vpre<=.18 and ta>t0 and brake_s>0):raise ValueError('ready-speed and ground acceleration interval required')
    ramp=.2;a=(vflight-vpre)/(ta-t0)
    x=np.where(t<=ramp,.5*(vpre/ramp)*t*t,vpre*(t-ramp/2))
    vx=np.where(t<=ramp,vpre*t/ramp,vpre)
    x100=vpre*(t0-ramp/2);xair=x100+.5*(vpre+vflight)*(ta-t0)
    ground=(ages>=100)&(ages<flight_start);tau=t[ground]-t0
    x[ground]=x100+vpre*tau+.5*a*tau*tau;vx[ground]=vpre+a*tau
    air=(ages>=flight_start)&(ages<=touch_age);x[air]=xair+vflight*(t[air]-ta);vx[air]=vflight
    after=ages>touch_age;tau=np.minimum(t[after]-tt,brake_s)
    xtouch=xair+vflight*(tt-ta)
    x[after]=xtouch+vflight*tau-.5*vflight/brake_s*tau*tau
    vx[after]=vflight*(1-tau/brake_s)
    vx[ages>=touch_age+round(brake_s/.01)]=0.
    return x,vx,dict(pre_request_speed_m_s=vpre,ground_acceleration_m_s2=a,flight_vx_m_s=vflight,
        flight_start_age=int(flight_start),first_touch_age=touch_age,X_air_m=float(xair),X_touch_m=float(xtouch),
        brake_s=brake_s,brake_deceleration_m_s2=-vflight/brake_s,stop_age=touch_age+round(brake_s/.01),
        stop_x_m=float(xtouch+.5*vflight*brake_s))

def choose_profile(ages,oldstates,low,high,flight_start,*,touch_age=145,edge=.35,top=.27,depth=.8):
    """Small bounded linear search over vflight and pre-speed feasible interval.

    Every X bound is linear in vpre and vflight. Search never modifies geometry.
    """
    ages=np.asarray(ages);local_lo=low[:,:,0]-oldstates[:,None,0];local_hi=high[:,:,0]-oldstates[:,None,0]
    candidates=[];attempts=[]
    # A uniform vpre grid is tiny metadata work; all geometry is already cached.
    for vflight in np.arange(.8,1.250001,.005):
        feasible=[]
        for vpre in np.linspace(0,.18,361):
            x,vx,meta=profile(ages,float(vpre),float(vflight),flight_start,touch_age)
            if meta['ground_acceleration_m_s2']>12:continue
            worldlo=local_lo+x[:,None];worldhi=local_hi+x[:,None]
            straddle=(worldhi>=edge)&(worldlo<edge)
            wall=straddle&(low[:,:,2]<top-1e-9)
            inside=((worldlo[touch_age:]>=edge)&(worldhi[touch_age:]<=edge+depth)).all()
            if wall.any() or not inside:continue
            if not ((low[touch_age:,:,2]>=top-1e-7).all()):raise ValueError('Input contact splice violates platform top; X-only repair cannot fix it')
            margin=min(float((edge-worldhi[(low[:,:,2]<top-1e-9)&(ages[:,None]<touch_age)]).min()),
                       float((worldlo[touch_age:]-edge).min()),float((edge+depth-worldhi[touch_age:]).min()))
            feasible.append((abs(vflight-.9)+.01*meta['ground_acceleration_m_s2']-.005*margin,vpre,x,vx,meta,margin))
        attempts.append(dict(flight_vx_m_s=float(vflight),feasible_pre_speed_count=len(feasible)))
        if feasible:candidates.append(min(feasible,key=lambda r:r[0]))
    if not candidates:raise ValueError(dict(reason='NO_READY_SPEED_BALLISTIC_X_PROFILE_IN_BOUNDED_SEARCH',flight_start=flight_start,attempts=attempts))
    best=min(candidates,key=lambda r:r[0]);_,vpre,x,vx,meta,margin=best
    meta.update(search_flight_speed_range=[.8,1.25],search_ground_acceleration_max=12.,pre_speed_grid_step=.0005,
        minimum_X_geometric_margin_m=margin,physical_public_request=[100,179],physical_command_vx_m_s=.8,
        reference_goal_only=True,dynamic_ground_acceleration_actuator_and_contact_feasibility='pending',attempts=attempts)
    return x,vx,meta
