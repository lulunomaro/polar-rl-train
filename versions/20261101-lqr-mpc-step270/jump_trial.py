"""LQR baseline with scheduled squat/push/tuck; no direct root forces or pose writes."""
import argparse,json,time,numpy as np,mujoco
from control_core import Plant,ROOT

def run(cfg,trace=False):
    p=Plant(step=cfg.get('step',True));g=p.lqr(cfg.get('start_delta',-.35))
    dr_sample=None
    if cfg.get('full_dr',False):
        from dr_components import FullDR
        dr_sample=p.attach_dr(FullDR(int(cfg.get('seed',0))))
    p.reset(g,cfg.get('start_x',-.6))
    rows=[];summary={'max_wheel_bottom':-1,'max_root_z':0.,'air_time':0.,'landed_top':False,'stable_time':0.,'success':False};stable=0;clean_air=0;in_air=False;takeoff=None;on_top=False
    xref=cfg.get('start_x',-.6);t_end=cfg.get('duration',4.);push=cfg.get('push_at',1.);push_for=cfg.get('push_for',.22);delta_push=cfg.get('push_delta',.35);delta_tuck=cfg.get('tuck_delta',-1.)
    qref=g['q'].copy();qref[0]=xref
    for k in range(round(t_end/.01)):
        t=k*.01;x=p.observe();q=qref.copy();v=np.zeros(4);tau=g['tau'].copy();phase='hold'
        if t<push:
            v[0]=cfg.get('speed',0.);q[0]=xref+v[0]*t
            tau-=g['K']@(x-np.r_[q,v])
        elif t<push+push_for:
            phase='push';a=np.clip((t-push)/push_for,0,1);delta=g['q'][3]+(delta_push-g['q'][3])*a
            h=g['q'][2]+cfg.get('hip_shift',-.35)*a
            q[2]=h;q[3]=delta;v[2]=cfg.get('hip_shift',-.35)/push_for;v[3]=(delta_push-g['q'][3])/push_for
            desired=np.array([q[2],q[2]+q[3]]);actual=np.array([x[2],x[2]+x[3]]);vel=np.array([x[6],x[6]+x[7]])
            tau[:2]=g['tau'][:2]+cfg.get('push_kp',180.)*(desired-actual)+cfg.get('push_kd',3.)*(np.array([v[2],v[2]+v[3]])-vel)
            tau[2]=cfg.get('wheel_push',0.)+cfg.get('pitch_gain',12.)*(x[1])+cfg.get('pitch_d',2.)*x[5]
        else:
            phase='tuck';delta=delta_tuck
            h=cfg.get('tuck_hip',.3)
            if on_top:phase='land';h=g['q'][2];delta=g['q'][3]
            desired=np.array([h,h+delta]);actual=np.array([x[2],x[2]+x[3]]);vel=np.array([x[6],x[6]+x[7]])
            tau[:2]=cfg.get('air_kp',60.)*(desired-actual)-cfg.get('air_kd',2.)*vel
            tau[2]=cfg.get('air_wheel',0.)+cfg.get('air_pitch',25.)*x[1]+cfg.get('air_pitch_d',5.)*x[5]
            if on_top:
                q[0]=max(.25,x[0]);tau=g['tau']-g['K']@(x-np.r_[q,np.zeros(4)])
        tau=np.clip(tau,[-40,-40,-5.7759],[40,40,5.7759]);p.torque_control(tau);hh=p.health()
        wheels=p.d.xpos[p.wheels];bottom=wheels[:,2]-.0625
        if float(bottom.min())>summary['max_wheel_bottom']:
            summary['max_wheel_bottom']=float(bottom.min());summary['apex_time']=float(p.d.time);summary['apex_wheels']=wheels.tolist();summary['apex_state']=p.state().tolist();summary['apex_upright']=hh['upright_cos']
        summary['max_root_z']=max(summary['max_root_z'],hh['xyz'][2])
        contact_wheels=set();top_wheels=set();nonwheel=0
        for ct in p.d.contact:
            a,b=int(ct.geom1),int(ct.geom2)
            tire=a if a in p.tires else b if b in p.tires else None
            other=b if tire==a else a
            if tire is not None:
                contact_wheels.add(tire)
                if p.m.geom(other).name=='step270' and ct.pos[2]>.265:top_wheels.add(tire)
            elif p.m.geom(a).name in ('ground','step270') or p.m.geom(b).name in ('ground','step270'):nonwheel+=1
        if not contact_wheels and not nonwheel and bottom.min()>.008:
            clean_air+=1;summary['air_time']+=.01
            if clean_air>=2 and takeoff is None:takeoff=float(p.d.time);summary['takeoff']=takeoff
        else:clean_air=0
        if takeoff is not None and len(top_wheels)==2 and np.min(wheels[:,0])>.0625:
            on_top=True;summary['landed_top']=True
        if on_top and len(top_wheels)==2 and nonwheel==0 and hh['upright_cos']>.95 and np.linalg.norm(p.d.qvel[:3])<.3:
            stable+=.01;summary['stable_time']=max(summary['stable_time'],stable)
            if stable>=.5:summary['success']=True
        else:stable=0
        if trace and k%2==0:rows.append(dict(hh,phase=phase,tau=tau.tolist(),bottom=bottom.tolist(),contacts=len(contact_wheels),nonwheel=nonwheel))
        if not hh['finite'] or hh['closure']>.01 or hh['mimic']>.01 or hh['upright_cos']<.5:
            summary['stop_reason']='health';break
    summary.update(last=hh,config=cfg,steps=k+1,dr_sample=dr_sample,dr_queue_receipt=p.dr.queue_receipt() if p.dr else None)
    return summary,rows
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--config');ap.add_argument('--out',default='jump_v1');args=ap.parse_args()
    cfg=json.loads(open(args.config).read()) if args.config else {'step':False,'speed':0,'start_delta':-.35,'hip_shift':-.4,'push_for':.18,'push_delta':.35,'tuck_delta':-.85,'tuck_hip':.4}
    summary,rows=run(cfg,True);(ROOT/'results'/args.out).mkdir(exist_ok=True)
    (ROOT/'results'/args.out/'result.json').write_text(json.dumps(summary,indent=2));(ROOT/'results'/args.out/'trace.json').write_text(json.dumps(rows))
    print(json.dumps(summary),flush=True)
