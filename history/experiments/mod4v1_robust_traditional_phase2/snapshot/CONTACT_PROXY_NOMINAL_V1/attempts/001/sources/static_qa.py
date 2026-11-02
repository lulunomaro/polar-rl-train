"""Fresh PUBLIC nominal model oracle only. No saved episode/DR/contact reads.
MuJoCo is used here, never in observer/model runtime. mj_step is forbidden.
"""
from pathlib import Path
import hashlib
import numpy as np
from nominal_model import NominalModel,XML_SHA

def run_static_qa():
    import mujoco
    root=Path(__file__).resolve().parent.parent;path=root/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==XML_SHA
    model=NominalModel();mj=mujoco.MjModel.from_xml_path(str(path));data=mujoco.MjData(mj);forwards=0;steps=[0]
    def no_step(*args,**kwargs):steps[0]+=1;raise AssertionError('No physics step allowed in static QA')
    mujoco.mj_step=no_step;mujoco.mj_step1=no_step;mujoco.mj_step2=no_step
    bids=[mj.body(b['name']).id for b in model.bodies];jids=[mj.joint(j['name']).id for j in model.joints];dofs=np.array([mj.jnt_dofadr[i] for i in jids]);chassis=mj.body('chassis').id
    poses=[model.q_nominal.copy()]
    for h in (.05,.15,.25,.35):
        for delta in (-.15,-.2,-.25):poses.append(np.array([h,h+delta,h+.01,h+.01+delta-.01]))
    records=[]
    for q in poses:
        k=model.derivatives(q);p=k['pose'];data.qpos[:]=mj.qpos0;data.qpos[:3]=[0,0,1.];data.qpos[3:7]=[1.,0,0,0];data.qvel[:]=0.;data.ctrl[:]=0.
        for jid,value in zip(jids,p['joint_values']):data.qpos[mj.jnt_qposadr[jid]]=value
        mujoco.mj_forward(mj,data);forwards+=1
        # Relative body geometry of a freshly authored nominal fixture, not a
        # sensor estimate or runtime rootGT input to the observer.
        sdk_pos=data.xpos[bids]-data.xpos[chassis];sdk_com=data.xipos[bids]-data.xpos[chassis]
        t=model.terms(q,np.zeros(4),np.zeros(4),[0,0,9.81],[0,0,0],[0,0,0]);sdk_g=k['Djoint'].T@data.qfrc_bias[dofs];sdk_passive=k['Djoint'].T@data.qfrc_passive[dofs]
        records.append({'q4':q.tolist(),'body_position_max_error_m':float(np.max(abs(sdk_pos-p['body_B']))),'COM_max_error_m':float(np.max(abs(sdk_com-p['com_B']))),'rotation_max_error':float(np.max(abs(data.xmat[bids].reshape(-1,3,3)-p['R_body_B']))),'gravity_virtual_projection_error_Nm':float(np.max(abs(sdk_g-t['load4']))),'spring_passive_projection_error_Nm':float(np.max(abs(sdk_passive-t['tauGas4']-t['tauOtherPassive4']))),'time_s':float(data.time)})
    peaks={key:max(r[key] for r in records) for key in records[0] if key.endswith(('_m','_Nm')) or key=='rotation_max_error'}
    assert peaks['body_position_max_error_m']<1e-8 and peaks['COM_max_error_m']<1e-8 and peaks['rotation_max_error']<1e-8
    assert peaks['gravity_virtual_projection_error_Nm']<1e-5 and peaks['spring_passive_projection_error_Nm']<1e-5
    assert steps[0]==0 and data.time==0.
    return {'status':'STATIC_PUBLIC_NOMINAL_FK_MCI_GRAVITY_SPRING_PROJECTIONS_MATCH','poses':records,'peaks':peaks,'static_forwards':forwards,'physics_steps':steps[0],'runtime_contact_reads':0,'randomized_episode_parameters_read':False,'fresh_public_model_only':True,'not_a_full_dynamic_RNE_validation':True}
