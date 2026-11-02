"""Fresh public nominal COM/derivative oracle, never a runtime truth input."""
from pathlib import Path
import hashlib
import numpy as np
from com_motion import Geometry,Config,XML_SHA

def run_static():
    import mujoco
    root=Path(__file__).resolve().parent.parent;path=root/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml';assert hashlib.sha256(path.read_bytes()).hexdigest()==XML_SHA
    m=mujoco.MjModel.from_xml_path(str(path));d=mujoco.MjData(m);g=Geometry();calls=[0];steps=[0]
    def forbidden(*a,**k):steps[0]+=1;raise AssertionError('No physics time step in public static oracle')
    mujoco.mj_step=forbidden;mujoco.mj_step1=forbidden;mujoco.mj_step2=forbidden
    bids=[m.body(b['name']).id for b in g.base.bodies];jids=[m.joint(j['name']).id for j in g.base.joints];root_id=m.body('chassis').id
    def sdk_com(q,phi):
        values=g.base.joint_values(q);values=values.copy()
        for side,x in zip(('left','right'),phi):values[g.base.joint_index[side+'_wheel_spin']]=x
        d.qpos[:]=m.qpos0;d.qpos[:3]=[0,0,1.];d.qpos[3:7]=[1,0,0,0];d.qvel[:]=0;d.ctrl[:]=0
        for jid,value in zip(jids,values):d.qpos[m.jnt_qposadr[jid]]=value
        mujoco.mj_forward(m,d);calls[0]+=1
        return np.sum(m.body_mass[bids,None]*(d.xipos[bids]-d.xpos[root_id]),axis=0)/np.sum(m.body_mass[bids])
    rows=[];dt=g.c.motion_difference_dt_s
    for h,delta in ((.1,-.15),(.25,-.2),(.35,-.25),(.2,-.1)):
        q=np.array([h,h+delta,h+.01,h+delta]);v=np.array([.2,-.15,.25,-.1]);a=np.array([.1,.2,-.1,.3]);phi=np.array([.4,-.7]);w=np.array([20.,-25.]);acc=np.array([100.,-200.]);p=g.motion(q,v,a,phi,w,acc)
        r=sdk_com(q,phi);rp=sdk_com(q+dt*v+.5*dt*dt*a,phi+dt*w+.5*dt*dt*acc);rm=sdk_com(q-dt*v+.5*dt*dt*a,phi-dt*w+.5*dt*dt*acc);rd=(rp-rm)/(2*dt);rdd=(rp-2*r+rm)/(dt*dt)
        rows.append({'q4':q.tolist(),'COM_max_error_m':float(max(abs(p['r_B']-r))),'rDot_max_error_m_s':float(max(abs(p['rDot_B']-rd))),'rDDot_max_error_m_s2':float(max(abs(p['rDDot_B']-rdd))),'time_s':float(d.time)})
    peaks={k:max(x[k] for x in rows) for k in ('COM_max_error_m','rDot_max_error_m_s','rDDot_max_error_m_s2')}
    assert peaks['COM_max_error_m']<1e-8 and peaks['rDot_max_error_m_s']<1e-7 and peaks['rDDot_max_error_m_s2']<1e-6
    assert steps[0]==0 and d.time==0.
    return {'status':'FRESH_PUBLIC_NOMINAL_STATIC_COM_AND_KINEMATIC_VECTOR_MATCH','poses':rows,'peaks':peaks,'static_forwards':calls[0],'physics_steps':steps[0],'contacts_read':False,'runtime_GT_or_DR_input':False,'not_dynamic_or_contact_or_hardware_validation':True}
