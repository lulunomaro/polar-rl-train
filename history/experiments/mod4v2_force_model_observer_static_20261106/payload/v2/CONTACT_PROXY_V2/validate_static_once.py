"""At most three fresh PUBLIC poses, zero integration; not task/contact testing."""
from pathlib import Path
import hashlib,importlib.util,json,math,os,time,traceback
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import numpy as np
from nominal_model import NominalModel,XML_SHA
from contact_proxy import ContactProxy,Config,SensorInput,TorqueDomain,ALL_VALID
D=Path(__file__).resolve().parent
PACKAGE=D.parent.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
COUNTS=dict(model_compiles=0,mj_forward_calls=0,forbidden_integration_attempts=0,pure_nominal_fk_calls=0,source_leg_configuration_calls=0,sensor_fixture_calls=0)
RECORDS=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(n,obj):
    with (D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(clean(obj),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def clean(x):
    if isinstance(x,dict):return {k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v)for v in x]
    if hasattr(x,'tolist'):return clean(x.tolist())
    if isinstance(x,float) and not math.isfinite(x):return None
    return x
def main():
    assert not(D/'STATIC_PREEXEC.json').exists(),'Static budget consumed: inspect prefix; no replay'
    started=time.perf_counter();local=['validate_static_once.py','nominal_model.py','contact_proxy.py','PUBLIC_NOMINAL_CONSTANTS.json']
    protected=[PACKAGE/'mjcf/scene.xml',PACKAGE/'kinematics_v2.py',PACKAGE/'model_parameters.json',D.parent/'nominal_gain_v2.json']
    before={str(p):sha(p)for p in [D/n for n in local]+protected}
    assert before[str(PACKAGE/'mjcf/scene.xml')]==XML_SHA
    q=np.array(json.loads((D/'PUBLIC_NOMINAL_CONSTANTS.json').read_text(encoding='utf-8'))['nominal_q4'])
    poses=[('nominal_delta_minus_point2',q),('same_physical_pose_common_full_turn',q+2*math.pi),
           ('public_asymmetric',q+np.array([.035,.025,-.025,-.005]))]
    new('STATIC_PREEXEC.json',dict(sources_before=before,poses=poses,maximum_mj_forward_calls=3,all_integration_forbidden=True,
        tolerances=dict(body_COM_m=1e-8,rotation=1e-8,BODY_inertia_kgm2=1e-9,reduced_J_m_or_rad=1e-7,gravity_passive_Nm=1e-5),
        purpose='public model algebra/kinematics only; no episode/static trim/LQR recomputation'))
    import mujoco
    originals={}
    def denied(*a,**k):
        COUNTS['forbidden_integration_attempts']+=1;raise AssertionError('Integration not permitted')
    for n in ('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit','mj_integratePos'):
        if hasattr(mujoco,n):originals[n]=getattr(mujoco,n);setattr(mujoco,n,denied)
    forward=mujoco.mj_forward
    def counted_forward(*a,**k):
        assert COUNTS['mj_forward_calls']<3,'Three-public-pose forward cap'
        COUNTS['mj_forward_calls']+=1;return forward(*a,**k)
    mujoco.mj_forward=counted_forward
    fk=NominalModel.fk
    def counted_fk(self,*a,**k):COUNTS['pure_nominal_fk_calls']+=1;return fk(self,*a,**k)
    NominalModel.fk=counted_fk
    try:
        spec=importlib.util.spec_from_file_location('_static_oracle_source_kin_v2',PACKAGE/'kinematics_v2.py')
        kin=importlib.util.module_from_spec(spec);spec.loader.exec_module(kin)
        source_leg=kin.leg_configuration
        def counted_leg(*a,**k):
            COUNTS['source_leg_configuration_calls']+=1;return source_leg(*a,**k)
        kin.leg_configuration=counted_leg
        constants=NominalModel();mj=mujoco.MjModel.from_xml_path(str(PACKAGE/'mjcf/scene.xml'));COUNTS['model_compiles']+=1;data=mujoco.MjData(mj)
        assert (mj.nbody,mj.nq,mj.nv,mj.nu,mj.neq)==(32,37,36,6,10)
        bids=np.array([mj.body(b['name']).id for b in constants.bodies]);jids=[mj.joint(j['name']).id for j in constants.joints]
        dofs=np.array([mj.jnt_dofadr[i]for i in jids]);chassis=mj.body('chassis').id
        def source_values(q4):
            values={}
            for i,side in enumerate(('left','right')):
                v,_=kin.leg_configuration(q4[2*i],q4[2*i+1],side,check_limits=True)
                values.update({side+'_'+key:value for key,value in v.items()})
            return np.array([values.get(j['name'],0.)for j in constants.joints])  # Unobserved guide spin held zero in this public fixture.
        for name,q4 in poses:
            data.qpos[:]=mj.qpos0;data.qpos[:3]=[0.,0.,1.];data.qpos[3:7]=[1.,0.,0.,0.]
            data.qvel[:]=0.;data.ctrl[:]=0.
            # Actual package setter performs exactly one guarded forward per pose.
            kin.set_configuration(mj,data,left=tuple(q4[:2]),right=tuple(q4[2:]),check_limits=True)
            terms=constants.terms(q4,np.zeros(4),np.zeros(4),[0.,0.,9.81],[0.,0.,0.],[0.,0.,0.])
            k=terms['jacobians'];p=k['pose'];Ds=np.zeros((len(jids),4))
            for i in range(4):
                e=np.eye(4)[i]*constants.h;v=source_values(q4+e)-source_values(q4-e)
                v[constants.hinges]=(v[constants.hinges]+np.pi)%(2*np.pi)-np.pi
                Ds[:,i]=v/(2*constants.h)
            pos=data.xpos[bids]-data.xpos[chassis];com=data.xipos[bids]-data.xpos[chassis]
            ib=data.ximat[bids].reshape(-1,3,3)
            sdk_I=np.array([r@np.diag(mj.body_inertia[bid])@r.T for r,bid in zip(ib,bids)])
            proxy_I=np.einsum('nij,njk,nlk->nil',p['R_body_B'],constants.I_local,p['R_body_B'])
            jac_com=[];jac_rot=[];jac_wheel=[]
            for bid in bids:
                jp=np.zeros((3,mj.nv));jr=np.zeros((3,mj.nv));mujoco.mj_jacBodyCom(mj,data,jp,jr,int(bid))
                jac_com.append(jp[:,dofs]@Ds);jac_rot.append(jr[:,dofs]@Ds)
            for side in ('left','right'):
                jp=np.zeros((3,mj.nv));jr=np.zeros((3,mj.nv));mujoco.mj_jacBody(mj,data,jp,jr,mj.body(side+'_wheel').id)
                jac_wheel.append(jp[:,dofs]@Ds)
            gravity=Ds.T@data.qfrc_bias[dofs];passive=Ds.T@data.qfrc_passive[dofs]
            solved=constants.solve_terms(terms,constants.tau_nominal)
            known=np.array([[5.,70.],[-3.,65.]])
            motor=terms['load4']-terms['tauGas4']-terms['tauOtherPassive4']
            for i in range(2):motor[2*i:2*i+2]-=terms['Jwheel_xz2'][i].T@known[i]
            inverse=constants.solve_terms(terms,motor)
            errors=dict(body_position_m=float(np.max(abs(pos-p['body_B']))),COM_m=float(np.max(abs(com-p['com_B']))),
                rotation=float(np.max(abs(data.xmat[bids].reshape(-1,3,3)-p['R_body_B']))),inertia_kgm2=float(np.max(abs(sdk_I-proxy_I))),
                joint_value_rad_or_m=float(np.max(abs(data.qpos[mj.jnt_qposadr[jids]]-p['joint_values']))),
                joint_J=float(np.max(abs(Ds-k['Djoint']))),COM_J=float(np.max(abs(np.array(jac_com)-k['Jcom']))),
                angular_J=float(np.max(abs(np.array(jac_rot)-k['Jrot']))),wheel_J=float(np.max(abs(np.array(jac_wheel)-k['Jwheel']))),
                gravity_Nm=float(np.max(abs(gravity-terms['load4']))),passive_Nm=float(np.max(abs(passive-terms['tauGas4']-terms['tauOtherPassive4']))),
                known_force_inverse_N=float(np.max(abs(inverse['force_body_xz_N2']-known))),
                axial_Tp_virtual_work_Nm=max(float(np.max(abs(solved['leg_coordinates2'][i]['generalized_reconstruction_Nm']-terms['Jwheel_xz2'][i].T@solved['force_body_xz_N2'][i])))for i in range(2)))
            record=dict(name=name,q4=q4,errors=errors,nominal_motor_fixture_tau4=constants.tau_nominal,
                nominal_motor_fixture_force_xz_N2=solved['force_body_xz_N2'],condition2=solved['condition2'],
                leg_axial_compression_N2=solved['leg_axial_compression_N2'],leg_Tp_y_Nm2=solved['leg_Tp_y_Nm2'],
                gas_slide_m=terms['gas_slide2'],gas_scalar_N=terms['gas_scalar_force_N2'],time_s=float(data.time))
            RECORDS.append(record);new('STATIC_PREFIX_%02d.json'%len(RECORDS),record)
            assert errors['body_position_m']<1e-8 and errors['COM_m']<1e-8 and errors['rotation']<1e-8
            assert errors['inertia_kgm2']<1e-9 and max(errors[n]for n in ('COM_J','angular_J','wheel_J','joint_J'))<1e-7
            assert errors['gravity_Nm']<1e-5 and errors['passive_Nm']<1e-5 and errors['known_force_inverse_N']<1e-8
            assert errors['axial_Tp_virtual_work_Nm']<1e-8 and errors['joint_value_rad_or_m']<1e-8 and data.time==0.
        no_g=constants.terms(poses[0][1],np.zeros(4),np.zeros(4),[0.,0.,0.],[0.,0.,0.],[0.,0.,0.])
        free=constants.solve_terms(no_g,-no_g['tauGas4']-no_g['tauOtherPassive4'])
        assert np.max(abs(no_g['load4']))==0. and np.max(abs(free['force_body_xz_N2']))==0.
        proxy=ContactProxy(Config(execution_context='synthetic_fixture',allow_nominal_design_fixture=True))
        fixture=[]
        for i in range(3):
            t=i*.01;sensor=SensorInput(t,t,t,ALL_VALID,tuple(q), (0.,)*4,tuple(constants.tau_nominal),(0.,0.,9.81),(0.,)*3,(0.,)*3,
                TorqueDomain.NOMINAL_DESIGN_OUTPUT_FIXTURE,'synthetic_public_trim_not_measured',torque_sign_verified=True,
                proper_reference='chassis_origin',torque_confidence4=(1.,)*4,torque_sigma_Nm4=(.05,)*4,
                encoder_calibration_confidence=1.,proper_confidence=1.,omega_confidence=1.,alpha_confidence=1.,encoder_qd_sigma4=(0.,)*4)
            COUNTS['sensor_fixture_calls']+=1;out=proxy.step(sensor,t)
            fixture.append(dict(time_s=t,normal_proxy_N2=out.normal_proxy_N2,confidence2=out.confidence2,common_reasons=out.common_reasons,
                leg_axial_compression_proxy_N2=out.leg_axial_compression_proxy_N2,leg_Tp_y_proxy_Nm2=out.leg_Tp_y_proxy_Nm2))
        assert all(c<=.55 for c in out.confidence2) and out.normal_proxy_N2[0] is not None
        cap_rejected=False
        try:Config(nominal_model_confidence_cap=.56)
        except ValueError:cap_rejected=True
        assert cap_rejected
        assert COUNTS['mj_forward_calls']==3 and COUNTS['forbidden_integration_attempts']==0
        after={path:sha(Path(path))for path in before};assert before==after
        new('RESULT.json',dict(status='THREE_PUBLIC_STATIC_POSES_MATCH_NO_INTEGRATION_NOT_CONTACT_CALIBRATION',
            counts=COUNTS,poses=RECORDS,source_before_after_equal=True,source_SHA=before,
            zero_proper_consistent_motor_force_xz_N2=free['force_body_xz_N2'],fixture_static_sensor_outputs=fixture,
            confidence_cap_raise_rejected=cap_rejected,wall_s=time.perf_counter()-started,
            runtime_contacts_rootGT_DR_reads=0,parent_controller_modified=False,old_QA_run=False))
        print(json.dumps(clean(dict(status='THREE_POSE_STATIC_PASS',counts=COUNTS,poses=RECORDS,fixture=fixture)),ensure_ascii=True))
    finally:
        NominalModel.fk=fk;mujoco.mj_forward=forward
        for n,v in originals.items():setattr(mujoco,n,v)
if __name__=='__main__':
    try:main()
    except BaseException:
        new('STATIC_ERROR.json',dict(traceback=traceback.format_exc(),counts=COUNTS,completed_pose_prefix=RECORDS,
            no_automatic_retry=True,no_physics=True))
        raise
