"""Hybrid traditional ground LQR/MPC, actuated jump, flight and landing."""
import argparse,json,math,time,numpy as np,mujoco
from control_core import ROOT
from full_lqr import AsymmetricPlant

def run(cfg,trace=False):
    p=AsymmetricPlant(cfg.get('step',True));p.use_full_lqr=True;g=p.full_lqr(cfg.get('start_delta',-.4));gn=p.full_lqr(cfg.get('landing_delta',-.2))
    sampler=None
    if cfg.get('full_dr',False):
        from dr_components import FullDR
        sampler=p.attach_dr(FullDR(int(cfg.get('seed',0))))
    p.reset(g['symmetric'],cfg.get('start_x',-.4))
    ref=np.r_[g['q'],np.zeros(7)];ref[0]=cfg.get('start_x',-.4);rows=[]
    start=time.time();best_height=-1;maxroot=0;takeoff=None;air=0;top=False;stable=0.;maxstable=0.;success=False;cross=None;wheel_top_count=0;nonwheel_steps=0;maxclosure=0.;maxmimic=0.;phase='stand';land_x=None;flight_active=False;flight_id=0;flight_clean_controls=0;cross_flight=None;min_support_footprint=10.;max_abs_tau=np.zeros(6);mpc_logs=[]
    N=round(cfg.get('duration',4.)/.01);push_at=cfg.get('push_at',.6);push_for=cfg.get('push_for',.14);pushdelta=cfg.get('push_delta',.4)
    mpc=None
    if cfg.get('mpc',False):
        from linear_mpc import LinearMPC
        mpc=LinearMPC(g,horizon=cfg.get('horizon',15))
    launch_time=None;launch_x=cfg.get('launch_x',None);launch_pose=None;launch_velocity=None;landing_flight_id=None;top_flight_id=None;first_landing_time=None;first_landing_nonwheel=False;returned_ground_after_cross=False;top_touchdown_after_cross=False;edge_return_after_cross=False
    for k in range(N):
        t=k*.01;x=p.full_state(True);s=p.state();q6=p.d.qpos[p.qids].copy();v6=p.d.qvel[p.vids].copy()
        q6[[1,0,4,3]]=p.observed['legq4'];v6[[1,0,4,3]]=p.observed['legqd4'];v6[[2,5]]=p.observed['wheelqd2']
        if launch_time is None and ((launch_x is None and t>=push_at) or (launch_x is not None and x[0]>=launch_x and x[7]>=cfg.get('launch_min_speed',.7))):
            launch_time=t;launch_pose=np.array([x[3],x[4],x[5],x[6]]);launch_velocity=x[[10,11,12,13]].copy()
        active_push_at=launch_time if launch_time is not None else 1e6
        if launch_time is None:
            phase='approach';ref[0]=cfg.get('start_x',-.4)+cfg.get('speed',.8)*t;ref[7]=cfg.get('speed',.8)
            tau=mpc.command(x,ref,v6) if mpc else g['tau']-g['K']@(x-ref)
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
                tau=gn['tau']-gn['K']@(x-ref)
                if mpc:
                    if getattr(mpc,'landing_gain',False) is False:
                        from linear_mpc import LinearMPC
                        mpc=LinearMPC(gn,horizon=cfg.get('horizon',15));mpc.landing_gain=True
                    tau=mpc.command(x,ref,v6)
        p.torque_control(tau);hh=p.health();wc=p.d.xpos[p.wheels].copy();bottom=wc[:,2]-.0625
        max_abs_tau=np.maximum(max_abs_tau,np.abs(p.d.ctrl))
        if mpc and phase in ('approach','recover'):mpc_logs.append(mpc.last_log)
        footprint=float(np.min(wc[:,0]-.0625));within_top=bool(np.all(wc[:,0]+.0625<3.) and np.all(np.abs(wc[:,1])+.01<1.))
        if bottom.min()>best_height:
            best_height=float(bottom.min());apex={'time':float(p.d.time),'wheels':wc.tolist(),'state':p.state().tolist(),'upright':hh['upright_cos']}
        maxroot=max(maxroot,hh['xyz'][2]);maxclosure=max(maxclosure,hh['closure']);maxmimic=max(maxmimic,hh['mimic'])
        support=set();tops=set();nw=0;normal_forces=[];ground_support=False
        for ci,ct in enumerate(p.d.contact):
            a,b=int(ct.geom1),int(ct.geom2);force=np.zeros(6);mujoco.mj_contactForce(p.m,p.d,ci,force)
            if force[0]<1.:continue
            tire=a if a in p.tires else b if b in p.tires else None;other=b if tire==a else a
            if p.m.geom(a).name=='ground' or p.m.geom(b).name=='ground':ground_support=True
            if tire is not None:
                support.add(tire)
                if p.m.geom(other).name=='step270' and ct.pos[2]>.267 and abs(ct.frame[2])>.8:tops.add(tire)
            elif p.m.geom(a).name in ('ground','step270') or p.m.geom(b).name in ('ground','step270'):nw+=1
        if nw:nonwheel_steps+=1
        if not support and nw==0 and bottom.min()>.008:
            air+=.01
            if not flight_active:flight_id+=1;flight_active=True;flight_clean_controls=0
            flight_clean_controls+=1
            if takeoff is None:takeoff=float(p.d.time)
        else:
            flight_clean_controls=0
        if flight_active and not support and nw==0 and flight_clean_controls>=2 and footprint>0 and bottom.min()>.268 and cross is None:
            cross={'time':float(p.d.time),'bottom':float(bottom.min()),'velocity':p.d.qvel[:3].tolist(),'flight_id':flight_id,'full_footprint_margin_m':footprint};cross_flight=flight_id
        if support or nw:
            if flight_active:
                landing_flight_id=flight_id
                if first_landing_time is None:first_landing_time=float(p.d.time);first_landing_nonwheel=bool(nw)
            flight_active=False
        if takeoff is not None and len(tops)==2:
            top_flight_id=landing_flight_id
            wheel_top_count+=1
            if not top:land_x=float(np.clip(p.d.qpos[0]+cfg.get('capture_time',.3)*max(p.d.qvel[0],0)+cfg.get('landing_offset',.1),cfg.get('landing_min_x',.35),2.5))
            top=True
        if cross is not None and ground_support:returned_ground_after_cross=True
        if cross is not None and footprint<-.02:edge_return_after_cross=True
        if cross is not None and len(tops)==2 and footprint>0:top_touchdown_after_cross=True
        if top and cross is not None and cross_flight==1 and top_touchdown_after_cross and not returned_ground_after_cross and not edge_return_after_cross and len(tops)==2 and footprint>0 and within_top and nw==0 and hh['upright_cos']>.95 and np.linalg.norm(p.d.qvel[:3])<.3 and np.linalg.norm(p.d.qvel[3:6])<.5:
            stable+=.01;maxstable=max(maxstable,stable);min_support_footprint=min(min_support_footprint,footprint)
            if stable>=.5:success=True
        else:stable=0.
        if trace and k%2==0:rows.append(dict(hh,phase=phase,tau=tau.tolist(),tops=len(tops),nonwheel=nw,qpos=p.d.qpos.tolist(),qvel=p.d.qvel.tolist()))
        if not hh['finite'] or hh['closure']>.01 or hh['mimic']>.01 or hh['upright_cos']<.45:
            stop='health';break
    else:stop='complete'
    out={'success':success,'stable_time':maxstable,'stable_at_end':stable,'min_stable_footprint_margin_m':None if min_support_footprint==10. else min_support_footprint,'max_abs_torque_actuator6':max_abs_tau.tolist(),'mpc_solve_ms_median':float(np.median([v['solve_ms'] for v in mpc_logs])) if mpc_logs else None,'mpc_solve_ms_max':max([v['solve_ms'] for v in mpc_logs]) if mpc_logs else None,'cross':cross,'landed_top':top,'top_contact_controls':wheel_top_count,'max_wheel_bottom':best_height,'apex':apex,'max_root_z':maxroot,'air_time':air,'takeoff':takeoff,'nonwheel_contact_controls':nonwheel_steps,'max_closure':maxclosure,'max_mimic':maxmimic,'last':hh,'stop_reason':stop,'steps':k+1,'wall_s':time.time()-start,'launch_time':launch_time,'landing_flight_id':landing_flight_id,'top_flight_id':top_flight_id,'first_landing_time':first_landing_time,'first_landing_nonwheel':first_landing_nonwheel,'returned_ground_after_cross':returned_ground_after_cross,'edge_return_after_cross':edge_return_after_cross,'top_touchdown_after_cross':top_touchdown_after_cross,'config':cfg,'DR':sampler,'queues':p.dr.queue_receipt() if p.dr else None}
    return out,rows
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--config');a.add_argument('--out',default='hybrid_v1');args=a.parse_args();cfg=json.load(open(args.config)) if args.config else {}
    out,rows=run(cfg,True);folder=ROOT/'results'/args.out;folder.mkdir(exist_ok=False);(folder/'result.json').write_text(json.dumps(out,indent=2));(folder/'trajectory.json').write_text(json.dumps(rows));print(json.dumps(out),flush=True)
