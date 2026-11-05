"""Two public static design poses only. No simulator, trim optimization or control.
Static proper=(0,0,9.81), zero qd/qdd/omega/alpha, fixed wheel-center F0.
Analytic constraint velocities avoid the sealed model's multi-pose FD derivative.
"""
from pathlib import Path
import os,sys,json,hashlib,traceback
for _k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[_k]='1'
ROOT=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import numpy as np
from CONTACT_PROXY_V2.nominal_model import NominalModel,ry2,cross2,vec,XML_SHA,CONSTANTS_SHA
G2=np.array([[0.,1.],[-1.,0.]])
COUNTS=dict(public_poses=0,sdk_free_fk_calls=0,analytic_tree_sweeps=0,simulator_compile_forward_step_DARE_static_optimization_oldQA=0)

def passive_derivatives(model,pose):
    """dq_joint/dq4 from differentiated AB/BP and KD/CD length constraints."""
    Dj=np.zeros((len(model.joints),4));planar=[];residuals=[];conditions=[]
    for i,side in enumerate(('left','right')):
        p=model.pins[side];v=lambda name:pose['joint_values'][model.joint_index[side+'_'+name]]
        h,c=v('hip'),v('crank');delta=c-h
        A=ry2(p['A'],delta);B=p['P']+ry2(p['B']-p['P'],v('rocker_pin'))
        C=p['P']+ry2(p['C']-p['P'],v('rocker_pin'))
        P,K,S=p['P'],p['K'],p['S'];E=K+ry2(p['D']-K,v('knee'))
        T=K+ry2(p['T']-K,v('knee'));W=K+ry2(p['W']-K,v('knee'))
        Ap=G2@A;M=np.stack((B-A,B-P));b=np.array([(B-A)@Ap,0.])
        cond1=float(np.linalg.cond(M))
        if cond1>1e8:raise ValueError('AB/BP derivative singular')
        Bp=np.linalg.solve(M,b);rp=-cross2(B-P,Bp)/float((B-P)@(B-P));Cp=rp*G2@(C-P)
        N=np.stack((E-K,E-C));a=np.array([0.,(E-C)@Cp]);cond2=float(np.linalg.cond(N))
        if cond2>1e8:raise ValueError('KD/CD derivative singular')
        Ep=np.linalg.solve(N,a);sp=-cross2(E-K,Ep)/float((E-K)@(E-K));Tp=sp*G2@(T-K)
        deriv=dict(rocker_pin=rp,coupler_pin=-cross2(B-A,Bp-Ap)/float((B-A)@(B-A))-1.,
            knee=sp,distal_pin=-cross2(E-C,Ep-Cp)/float((E-C)@(E-C))-rp,
            gas_pin=-cross2(T-S,Tp)/float((T-S)@(T-S)),gas_slide=float((T-S)@Tp)/float(np.linalg.norm(T-S)))
        for name,dv in deriv.items():Dj[model.joint_index[side+'_'+name],2*i:2*i+2]=[-dv,dv]
        for name in ('hip','drive_hip_spin'):Dj[model.joint_index[side+'_'+name],2*i]=1.
        for name in ('crank','drive_input_spin'):Dj[model.joint_index[side+'_'+name],2*i+1]=1.
        Wp=sp*G2@(W-K);world=ry2(W,h)
        planar.append(np.column_stack((G2@world-ry2(Wp,h),ry2(Wp,h))))
        residuals.extend((float(np.max(abs(M@Bp-b))),float(np.max(abs(N@Ep-a)))))
        conditions.append([cond1,cond2])
    return Dj,planar,dict(velocity_constraint_residual_max=max(residuals),circle_velocity_matrix_condition2=conditions)

def static_terms(model,q_ref4):
    """Exactly ONE model FK at q_ref. Public fixed chassis (roll=pitch=0).
    Reuses all nominal COM/mass and passive coordinates, not inertia-based dynamics.
    """
    q=vec(q_ref4,4,'absolute reference q4');pose=model.fk(q)
    Dj,planar,info=passive_derivatives(model,pose)
    Jx=np.zeros((len(model.bodies),3,4));Jr=Jx.copy();Jcom=Jx.copy()
    for i,b in enumerate(model.bodies):
        if b['parent'] is not None:
            parent=model.body_index[b['parent']]
            Jx[i]=Jx[parent]+np.cross(Jr[parent].T,pose['body_B'][i]-pose['body_B'][parent]).T
            Jr[i]=Jr[parent].copy()
            if len(b['joint_names'])>1:raise ValueError('Explicit single-joint P0 tree expected')
            for name in b['joint_names']:
                j=model.joints[model.joint_index[name]];axis=np.asarray(j['axis'],float);axis/=np.linalg.norm(axis)
                aw=pose['R_body_B'][i]@axis;d=Dj[model.joint_index[name]]
                if j['type']=='hinge':
                    pivot=pose['body_B'][i]+pose['R_body_B'][i]@np.asarray(j['pos_m'])
                    Jx[i]+=np.outer(np.cross(aw,pose['body_B'][i]-pivot),d);Jr[i]+=np.outer(aw,d)
                elif j['type']=='slide':Jx[i]+=np.outer(aw,d)
                else:raise ValueError('Unexpected joint in public P0 tree')
        Jcom[i]=Jx[i]+np.cross(Jr[i].T,pose['com_B'][i]-pose['body_B'][i]).T
    gravity=np.einsum('nik,n,i->k',Jcom,model.mass,np.array([0.,0.,9.81]))
    gas=model.stiffness[model.gas_ids]*(model.springref[model.gas_ids]-pose['joint_values'][model.gas_ids])
    tau_gas=Dj[model.gas_ids].T@gas
    Js=np.array([Jx[b][[0,2],2*i:2*i+2]for i,b in enumerate(model.wheel_ids)])
    error=max(float(np.max(abs(J-P)))for J,P in zip(Js,planar))
    if error>1e-10:raise ValueError('Analytic tree/planar wheel Jacobian inconsistency')
    if not all(np.isfinite(a).all()for a in (Dj,Jcom,gravity,tau_gas,Js,gas)):
        raise ValueError('Nonfinite static design')
    info['tree_vs_planar_wheel_J_max']=error
    return dict(q4=q,load4=gravity,tauGas4=tau_gas,Jwheel_xz2=Js,gas_scalar_N2=gas,
                gas_slide_m2=pose['joint_values'][model.gas_ids],wheel_B=pose['wheel_B'],analytic_checks=info)

def tau_from_terms(terms,F0_xz_N2):
    """Motor output Nm = gravity generalized load - gas - Jwheel.T @ F0.
    F0 is the immutable NOMINAL DESIGN load, never current measured/proxy contact.
    Other passive/rotational/armature terms are zero in this STATIC design only.
    """
    F=np.asarray(F0_xz_N2,float)
    if F.shape!=(2,2) or not np.isfinite(F).all():raise ValueError('Fixed design wheel load shape/finite')
    external=np.concatenate([J.T@f for J,f in zip(terms['Jwheel_xz2'],F)])
    return terms['load4']-terms['tauGas4']-external

def reference_static_tau(model,q_ref4,F0_xz_N2):
    """SDK-free reusable nominal static item; no caller torque/IMU/DR feedback."""
    return tau_from_terms(static_terms(model,q_ref4),F0_xz_N2)

def clean(x):
    if isinstance(x,dict):return {k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v)for v in x]
    if hasattr(x,'tolist'):return clean(x.tolist())
    return x

def new(name,obj):
    with (D/name).open('x',encoding='utf-8')as f:json.dump(clean(obj),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def split(v):
    return dict(common_Nm2=(v[:2]+v[2:])/2,differential_Nm2=(v[:2]-v[2:])/2)

def main():
    if (D/'PREEXEC.json').exists():raise RuntimeError('Two-pose design consumed; inspect evidence, no replay')
    gain=json.loads((ROOT/'nominal_gain_v2.json').read_text(encoding='utf-8'))
    if gain['model_SHA']!=XML_SHA:raise ValueError('P0 nominal gain identity differs')
    g=gain['gain'];q0=np.array([g['q'][3],g['q'][3]+g['q'][4],g['q'][5],g['q'][5]+g['q'][6]])
    tau0=np.asarray(g['tau'],float)[[0,1,3,4]];dq=np.array([.02,-.02,-.02,.02]);q1=q0+dq
    new('PREEXEC.json',dict(kind='ONLY_TWO_PUBLIC_REFERENCE_STATIC_DESIGN_POSES',q0=q0,q1=q1,dq=dq,
        proper_BODY=[0,0,9.81],qd_qdd_omega_alpha='zero STATIC assumption only',roll_pitch='fixed0',
        F0='derived once from q0+existing trim; no mg/2 substitution; not measured Fn',
        source_model_SHA=XML_SHA,public_constants_SHA=CONSTANTS_SHA,
        script_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),max_model_fk_calls=2,
        finite_difference_pose_or_grid_calls=0,simulator_compile_forward_step_DARE_static_optimization_oldQA=0))
    model=NominalModel();original_fk=model.fk
    def limited_fk(*a,**kw):
        if COUNTS['sdk_free_fk_calls']>=2:raise RuntimeError('Exact two-pose FK budget exhausted')
        COUNTS['sdk_free_fk_calls']+=1;return original_fk(*a,**kw)
    model.fk=limited_fk
    terms=[]
    for q in (q0,q1):
        terms.append(static_terms(model,q));COUNTS['public_poses']+=1;COUNTS['analytic_tree_sweeps']+=1
    base,asym=terms
    F0=np.array([np.linalg.solve(J.T,(base['load4']-base['tauGas4']-tau0)[2*i:2*i+2])
                 for i,J in enumerate(base['Jwheel_xz2'])])
    F0.flags.writeable=False
    reproduced=tau_from_terms(base,F0);tau1=tau_from_terms(asym,F0);delta=tau1-tau0
    dgrav=asym['load4']-base['load4'];dgas=-(asym['tauGas4']-base['tauGas4'])
    dload=delta-dgrav-dgas;pd=120.*dq;norm=float(dq@dq)
    stiffness=dict(required_motor_total=float(delta@dq/norm),gravity=float(dgrav@dq/norm),
        minus_gas=float(dgas@dq/norm),minus_JTF0=float(dload@dq/norm))
    stiffness['old_PD_120I_plus_required_secant']=120.+stiffness['required_motor_total']
    stiffness['signed_required_vs_reference_PD_ratio']=stiffness['required_motor_total']/120.
    result=dict(status='TWO_POSE_NOMINAL_REFERENCE_STATIC_FF_DESIGN_NOT_CONTROLLER_OR_CONTACT_VALIDATION',
        q0=q0,q1=q1,dq_abs_hip_crank=dq,F0_design_xz_N2=F0,original_trim4_Nm=tau0,
        tau_reproduced_q0_Nm4=reproduced,q0_consistency_max_Nm=float(np.max(abs(reproduced-tau0))),
        tau_static_q1_Nm4=tau1,delta_required_Nm4=delta,delta_split=split(delta),
        decomposition_delta_Nm4=dict(gravity=dgrav,minus_gas=dgas,minus_JTF0=dload),
        old_PD_reference_step_120dq_Nm4=pd,old_PD_step_split=split(pd),equivalent_static_error_delta_over120_rad4=delta/120.,
        directional_secant_Nm_per_rad=stiffness,
        secant_interpretation='ONLY along dq: at fixed reference residual change projection is -(120+k_required)*dq; negative k_required weakens this quasistatic directional restoring component. Not full4x4 stiffness, local derivative, dynamics or stability proof.',
        base=base,asym=asym,counts=COUNTS,
        nominal_only_no_sampledDR_or_measuredFn_alpha=True,gas_k_N_m=2000.,gas_d_Ns_m=3.,gas_not_calibrated=True,
        load_frame='Fx,Fz wheel-center external forces in fixed roll=pitch=0 chassis design frame',
        active_q_ref_only_no_actual_state_closed_loop=True,parent_controller_or_model_modified=False,
        no_other_pose_FK_old_QA_raw_hardware_Git_agent=True)
    new('RESULT.json',result)
    if float(np.max(abs(reproduced-tau0)))>1e-10:raise ValueError('Existing nominal trim not reproduced')
    if np.max(abs(F0[:,0]))>1e-5 or np.max(abs(F0[:,1]-np.array([70.057416,70.168100])))>1e-5:
        raise ValueError('Natural trim inverse inconsistent with provided nominal load; not fit/replace')
    print(json.dumps(clean(dict(status=result['status'],F0_design_xz_N2=F0,delta_required_Nm4=delta,
        delta_split=split(delta),directional_secant_Nm_per_rad=stiffness,counts=COUNTS)),ensure_ascii=True))
if __name__=='__main__':
    try:main()
    except BaseException:
        error=traceback.format_exc()
        if not (D/'ERROR.json').exists():new('ERROR.json',dict(error=error,counts=COUNTS,no_automatic_retry=True))
        print(error);raise
