"""Source MPC state/event controller, unchanged phase equations; no simulator import.

This is a diagnostic current-state controller, not a learned/deployable depth policy.
The current target interface remains50Hz; source controller was100Hz. Two10ms MPC
prediction transitions per20ms command are not claimed or silently introduced.
"""
import math,numpy as np
from linear_mpc import LinearMPC

class SourceEventMPC353:
    def __init__(self,bundle):
        self.cfg=dict(bundle['config']);self.g={k:np.array(v,float)for k,v in bundle['g'].items()};self.gn={k:np.array(v,float)for k,v in bundle['gn'].items()}
        self.ref=np.r_[self.g['q'],np.zeros(7)];self.ref[0]=self.cfg['start_x']
        self.mpc=LinearMPC(self.g,horizon=self.cfg.get('horizon',15))
        self.launch_time=None;self.launch_pose=None;self.launch_velocity=None;self.top=False;self.land_x=None;self.top_time=None;self.top_state=None;self.top_x=None;self.last_phase=None;self.calls=0
    def command(self,t,x,q6,v6):
        cfg=self.cfg;g=self.g;gn=self.gn;ref=self.ref;mpc=self.mpc
        launch_time=self.launch_time;launch_pose=self.launch_pose;launch_velocity=self.launch_velocity
        top=self.top;land_x=self.land_x;top_time=self.top_time;top_state=self.top_state;top_x=self.top_x
        push_at=cfg.get('push_at',.6);push_for=cfg.get('push_for',.14);pushdelta=cfg.get('push_delta',.4);launch_x=cfg.get('launch_x',None)
        if launch_time is None and ((launch_x is None and t>=push_at) or (launch_x is not None and x[0]>=launch_x and x[7]>=cfg.get('launch_min_speed',.7))):
            launch_time=t;launch_pose=np.array([x[3],x[4],x[5],x[6]]);launch_velocity=x[[10,11,12,13]].copy()
        active_push_at=launch_time if launch_time is not None else 1e6
        if launch_time is None:
            phase='approach';ref[0]=cfg.get('start_x',-.4)+cfg.get('speed',.8)*t;ref[7]=cfg.get('speed',.8)
            tau=mpc.command(x,ref,v6) if mpc and cfg.get('mpc_approach',True) else g['tau']-g['K']@(x-ref)
        elif t<active_push_at+push_for:
            phase='push';a=np.clip((t-active_push_at)/push_for,0,1)
            if cfg.get('measured_launch_pose',False):
                lh,ld,rh,rd=launch_pose;endh=g['q'][3]+cfg.get('hip_shift',-.5)
                h=(1-a)*lh+a*endh;delta=(1-a)*ld+a*pushdelta;hr=(1-a)*rh+a*endh;dr=(1-a)*rd+a*pushdelta
                targets=np.array([h,h+delta,hr,hr+dr]);vels=np.array([endh-lh,endh+pushdelta-lh-ld,endh-rh,endh+pushdelta-rh-rd])/push_for
            else:
                h=g['q'][3]+cfg.get('hip_shift',-.5)*a;delta=g['q'][4]+(pushdelta-g['q'][4])*a
                targets=np.array([h,h+delta,h,h+delta]);vels=np.array([cfg.get('hip_shift',-.5),cfg.get('hip_shift',-.5)+(pushdelta-g['q'][4])]*2)/push_for
            legids=[0,1,3,4];tau=g['tau'].copy();tau[legids]+=cfg.get('push_kp',280)*(targets-q6[legids])+cfg.get('push_kd',3)*(vels-v6[legids])
            wheel=cfg.get('wheel_push',3.)+cfg.get('push_pitch',20.)*(x[2]-cfg.get('push_pitch_ref',0.))+cfg.get('push_pitch_d',3.)*x[9]
            tau[[2,5]]=wheel
        else:
            phase='flight';tflight=t-(active_push_at+push_for);h=cfg.get('tuck_hip',.15);delta=cfg.get('tuck_delta',-.95)
            if tflight>cfg.get('extend_after',.25):
                blend=np.clip((tflight-cfg.get('extend_after',.25))/.1,0,1);h=(1-blend)*h+blend*gn['q'][3];delta=(1-blend)*delta+blend*gn['q'][4];phase='extend'
            legids=[0,1,3,4];targets=np.array([h,h+delta,h,h+delta]);tau=np.zeros(6)
            # Nominal spring compensation plus joint feedback; airborne torque only through real actuators.
            tau[legids]=cfg.get('air_kp',60)*(targets-q6[legids])-cfg.get('air_kd',2)*v6[legids]
            wheel=cfg.get('air_wheel',0.)+cfg.get('air_pitch',30.)*(x[2]-cfg.get('air_pitch_ref',0.))+cfg.get('air_pitch_d',6.)*x[9]
            tau[[2,5]]=wheel
            # Left/right differences are bounded feedback about the symmetric flight request.
            diff=x[3]-x[5];diffd=x[10]-x[12];dc=cfg.get('diff_kp',20)*diff+cfg.get('diff_kd',2)*diffd
            tau[0]-=dc;tau[3]+=dc
            yaw=cfg.get('yaw_kp',2)*x[1]+cfg.get('yaw_kd',.5)*x[8];tau[2]-=yaw;tau[5]+=yaw
            if top:
                phase='recover';ref=np.r_[gn['q'],np.zeros(7)];ref[0]=land_x;ref[7]=cfg.get('landing_speed',0.)
                if cfg.get('smooth_landing',False):
                    elapsed=t-top_time;blend=float(np.clip(elapsed/cfg.get('landing_blend_s',.35),0,1))
                    ref[2:7]=(1-blend)*top_state[2:7]+blend*ref[2:7]
                    ref[0]=top_x+cfg.get('landing_run_speed',.8)*min(elapsed,cfg.get('landing_run_s',.4))
                    ref[7]=cfg.get('landing_run_speed',.8) if elapsed<cfg.get('landing_run_s',.4) else 0.
                    ref[9:14]=0
                tau=gn['tau']-gn['K']@(x-ref)
                if mpc and cfg.get('mpc_landing',True):
                    if getattr(mpc,'landing_gain',False) is False:
                        from linear_mpc import LinearMPC
                        mpc=LinearMPC(gn,horizon=cfg.get('horizon',15));mpc.landing_gain=True
                    tau=mpc.command(x,ref,v6)

        self.launch_time=launch_time;self.launch_pose=launch_pose;self.launch_velocity=launch_velocity;self.mpc=mpc;self.last_phase=phase;self.calls+=1
        target=np.array(q6,float)+(tau+2.*np.array(v6,float))/60.
        for i in(2,5):target[i]=v6[i]+tau[i]/.6
        raw=target.copy();target[[0,1,3,4]]=np.clip(target[[0,1,3,4]],-3.,3.)
        for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
        target[[2,5]]=np.clip(target[[2,5]],-60.,60.)
        return dict(tau=tau,processed_target=target,raw_inversePD_target=raw,phase=phase,launch_time=launch_time,mpc_log=self.mpc.last_log if phase in('approach','recover')else None)
    def observe_top(self,t,x,actual_x,actual_vx,takeoff_observed,both_top):
        if takeoff_observed and both_top and not self.top:
            cfg=self.cfg;self.land_x=float(np.clip(actual_x+cfg.get('capture_time',.3)*max(actual_vx,0)+cfg.get('landing_offset',.1),cfg.get('landing_min_x',.35),2.5))
            self.top_time=t;self.top_state=x.copy();self.top_x=float(x[0]);self.top=True

def state_and_inverse_feedback353(root13,default_joint_pos,policy,legjoint_ids,wheeljoint_ids,origin,edge_x):
    """Use actual original D1-D3 policy feedback plus declared privileged translation/yaw."""
    # policy unscaled slicing supplied explicitly by runtime adapter, no guessed35 ABI.
    x,y,z,w=root13[3:7];R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    omega=policy['base_ang_vel'];gravity=policy['projected_gravity'];lq=policy['leg_pos']+default_joint_pos[legjoint_ids];lv=policy['leg_vel'];wv=policy['wheel_vel']
    predict_s=.005;lq=lq+predict_s*lv;gravity=gravity-predict_s*np.cross(omega,gravity)
    roll=math.atan2(-gravity[1],-gravity[2]);pitch=math.atan2(gravity[0],math.hypot(gravity[1],gravity[2]));yaw=math.atan2(R[1,0],R[0,0])
    state=np.array([root13[0]-origin[0]-edge_x,yaw,pitch,lq[1],lq[0]-lq[1],lq[3],lq[2]-lq[3],root13[7],(omega[1]*math.sin(roll)+omega[2]*math.cos(roll))/max(math.cos(pitch),.15),omega[1]*math.cos(roll)-omega[2]*math.sin(roll),lv[1],lv[0]-lv[1],lv[3],lv[2]-lv[3]])
    q6=np.array([lq[1],lq[0],0.,lq[3],lq[2],0.]);v6=np.array([lv[1],lv[0],wv[0],lv[3],lv[2],wv[1]])
    assert np.isfinite(state).all()and np.isfinite(q6).all()and np.isfinite(v6).all()
    return state,q6,v6
