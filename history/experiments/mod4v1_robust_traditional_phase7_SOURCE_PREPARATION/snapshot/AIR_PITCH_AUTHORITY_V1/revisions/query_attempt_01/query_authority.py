"""Exactly twelve reset nominal forward dynamics calls, no integration/control law."""
from pathlib import Path
import hashlib,importlib.util,json,math,sys,traceback,xml.etree.ElementTree as ET
import numpy as np
import mujoco
D=Path(__file__).resolve().parent;R=D.parent;O=R.parent/'traditional_control_20261101'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
method=load(D/'METHOD.json');lock=load(D/'SOURCE_LOCK.json')
assert sha(D/'METHOD.json')==lock['method_SHA']
for s in lock['sources']:assert sha(Path(s['path']))==s['SHA']
counts={n:0 for n in method['blocked_integrators']};counts.update(mj_forward=0,mj_rnePostConstraint=0)
original={};rows=[];boot=0
for name in method['blocked_integrators']:
    assert hasattr(mujoco,name)
    original[name]=getattr(mujoco,name)
    def deny(*args,_name=name,**kw):
        counts[_name]+=1;raise RuntimeError('INTEGRATOR_BLOCKED '+_name)
    setattr(mujoco,name,deny)
try:
    spec=importlib.util.spec_from_file_location('apa_nominal_fk',O/'kinematics.py');kin=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=kin;spec.loader.exec_module(kin)
    xml=ET.fromstring((R/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml').read_bytes())
    xml.find('compiler').set('meshdir',str((R/'MODEL_AUDIT').resolve()))
    m=mujoco.MjModel.from_xml_string(ET.tostring(xml,encoding='unicode'));boot=1
    assert m.nu==6 and m.na==0
    order=method['actuator_order'];jointids=[int(m.joint(n).id)for n in order]
    dofs=[int(m.jnt_dofadr[j])for j in jointids];chassis=int(m.body('chassis').id)
    free=int(m.joint('floating_base').id);root_dof=int(m.jnt_dofadr[free]);root_qadr=int(m.jnt_qposadr[free])
    assert m.jnt_type[free]==mujoco.mjtJoint.mjJNT_FREE
    pitch_index=root_dof+4
    actuators=[]
    for i,j in enumerate(jointids):
        assert m.actuator_trntype[i]==mujoco.mjtTrn.mjTRN_JOINT and m.actuator_trnid[i,0]==j
        assert np.array_equal(m.actuator_gear[i],[1.,0.,0.,0.,0.,0.])
        assert m.actuator_dyntype[i]==mujoco.mjtDyn.mjDYN_NONE and m.actuator_gaintype[i]==mujoco.mjtGain.mjGAIN_FIXED
        assert m.actuator_biastype[i]==mujoco.mjtBias.mjBIAS_NONE and m.actuator_gainprm[i,0]==1.
        actuators.append(dict(row=i,name=m.actuator(i).name,joint=order[i],joint_id=j,dof=dofs[i],
            joint_axis_local=m.jnt_axis[j].tolist(),gear=m.actuator_gear[i].tolist(),gain_prm=m.actuator_gainprm[i].tolist(),
            bias_prm=m.actuator_biasprm[i].tolist(),dyn_type=int(m.actuator_dyntype[i]),transmission_type=int(m.actuator_trntype[i]),
            ctrlrange=m.actuator_ctrlrange[i].tolist(),forcerange=m.actuator_forcerange[i].tolist()))
    sid=int(m.sensor('base_gyro').id);imu=int(m.sensor_objid[sid])
    assert m.sensor_type[sid]==mujoco.mjtSensor.mjSENS_GYRO and m.sensor_objtype[sid]==mujoco.mjtObj.mjOBJ_SITE
    assert m.site_bodyid[imu]==chassis and m.sensor_dim[sid]==3
    sensor=dict(name='base_gyro',type='gyro',site=m.site(imu).name,site_body=m.body(int(m.site_bodyid[imu])).name,
        site_pos=m.site_pos[imu].tolist(),site_quat=m.site_quat[imu].tolist(),sensor_adr=int(m.sensor_adr[sid]),
        meaning='site-local angular velocity; at queried identity this site/chassis/world orientation coincides')
    assert np.array_equal(m.site_quat[imu],[1.,0.,0.,0.])
    opts=dict(timestep=float(m.opt.timestep),integrator=int(m.opt.integrator),solver=int(m.opt.solver),
        iterations=int(m.opt.iterations),tolerance=float(m.opt.tolerance),gravity=m.opt.gravity.tolist(),
        disableflags=int(m.opt.disableflags),enableflags=int(m.opt.enableflags),jacobian=int(m.opt.jacobian))
    connects=[(x.attrib['site1'],x.attrib['site2'])for x in xml.find('equality').findall('connect')]
    mimics=[(x.attrib['joint1'],x.attrib['joint2'])for x in xml.find('equality').findall('joint')]
    max_alpha_error=0.;max_jac_error=0.;max_dynamics_residual=0.
    for pose in lock['poses']:
        statehash=None
        for query in method['queries']:
            assert counts['mj_forward']<12
            d=mujoco.MjData(m);mujoco.mj_resetData(m,d)
            q=np.asarray(pose['q7'],float)
            for side,active in (('left',q[3:5]),('right',q[5:7])):
                values,_=kin.leg_configuration(float(active[0]),float(active[1]),side)
                for name,value in values.items():d.joint(side+'_'+name).qpos[0]=value
            d.qpos[root_qadr:root_qadr+3]=method['root_xyz_m'];d.qpos[root_qadr+3:root_qadr+7]=method['root_quaternion_wxyz']
            d.qvel[:]=0.;d.ctrl[:]=0.;d.act[:]=0.;d.qacc_warmstart[:]=0.;d.qfrc_applied[:]=0.;d.xfrc_applied[:]=0.
            assert not np.any(d.qacc_warmstart)and not np.any(d.qvel)and not np.any(d.ctrl)
            qhash=hashlib.sha256(d.qpos.tobytes()).hexdigest()
            if statehash is None:statehash=qhash
            assert qhash==statehash
            ctrl=np.asarray(query['ctrl6'],float);d.ctrl[:]=ctrl
            counts['mj_forward']+=1;mujoco.mj_forward(m,d)
            assert d.time==0 and not np.any(d.qvel)and hashlib.sha256(d.qpos.tobytes()).hexdigest()==statehash
            assert np.isfinite(d.qacc).all()and np.array_equal(d.actuator_force,ctrl)
            expect=np.zeros(m.nv);expect[dofs]=ctrl;assert np.array_equal(d.qfrc_actuator,expect)
            closure=max(float(np.linalg.norm(d.site(a).xpos-d.site(b).xpos))for a,b in connects)
            mimic=max(abs(float(d.joint(a).qpos[0]-d.joint(b).qpos[0]))for a,b in mimics)
            jp=np.zeros((3,m.nv));jr=np.zeros((3,m.nv));mujoco.mj_jacBody(m,d,jp,jr,chassis)
            jerr=float(np.max(np.abs(jr[:,root_dof+3:root_dof+6]-np.eye(3))))
            max_jac_error=max(max_jac_error,jerr)
            assert np.allclose(d.xmat[chassis].reshape(3,3),np.eye(3),atol=1e-14,rtol=0.)
            assert np.allclose(d.site_xmat[imu].reshape(3,3),np.eye(3),atol=1e-14,rtol=0.)
            counts['mj_rnePostConstraint']+=1;mujoco.mj_rnePostConstraint(m,d)
            local=np.zeros(6);world=np.zeros(6)
            mujoco.mj_objectAcceleration(m,d,mujoco.mjtObj.mjOBJ_BODY,chassis,local,1)
            mujoco.mj_objectAcceleration(m,d,mujoco.mjtObj.mjOBJ_BODY,chassis,world,0)
            alpha_j=jr@d.qacc
            alpha_error=max(float(np.max(np.abs(local[:3]-d.qacc[root_dof+3:root_dof+6]))),
                float(np.max(np.abs(world[:3]-alpha_j))),abs(float(d.qacc[pitch_index]-local[1])))
            max_alpha_error=max(max_alpha_error,alpha_error)
            assert alpha_error<1e-8 and jerr<1e-14
            mv=np.zeros(m.nv);mujoco.mj_mulM(m,d,mv,d.qacc)
            residual=mv-(d.qfrc_actuator+d.qfrc_passive-d.qfrc_bias+d.qfrc_applied+d.qfrc_constraint)
            dynres=float(np.max(np.abs(residual)));max_dynamics_residual=max(max_dynamics_residual,dynres)
            eqmask=np.asarray(d.efc_type)==mujoco.mjtConstraint.mjCNSTR_EQUALITY
            eq_position_max=float(np.max(np.abs(np.asarray(d.efc_pos)[eqmask])))if np.any(eqmask)else None
            acc_res=None
            if np.asarray(d.efc_J).size==d.nefc*m.nv:
                jac=np.asarray(d.efc_J).reshape(d.nefc,m.nv)
                acc_res=float(np.max(np.abs((jac@d.qacc-np.asarray(d.efc_aref))[eqmask])))if np.any(eqmask)else None
            contacts=[dict(geom1=m.geom(int(c.geom1)).name,geom2=m.geom(int(c.geom2)).name)for c in d.contact]
            qa=np.asarray(d.qacc)[dofs].copy()
            rows.append(dict(pose=pose['name'],query=query['name'],ctrl6=ctrl.tolist(),actual_actuator_force_Nm=d.actuator_force.tolist(),
                qpos_SHA=statehash,pre_warmstart_all_zero=True,qvel_all_zero=True,time_s=float(d.time),ncon=int(d.ncon),contacts=contacts,
                nominal_air_interpretation_eligible=bool(d.ncon==0),root_qacc6=d.qacc[root_dof:root_dof+6].tolist(),
                root_pitch_qacc_rad_s2=float(d.qacc[pitch_index]),hinge_qacc6_rad_s2=qa.tolist(),
                crank_minus_hip_qacc2_rad_s2=[float(qa[1]-qa[0]),float(qa[4]-qa[3])],all_qacc=d.qacc.tolist(),
                root_angular_acceleration_local_rad_s2=local[:3].tolist(),root_angular_acceleration_world_rad_s2=world[:3].tolist(),
                gyro_sensor_rad_s=d.sensordata[int(m.sensor_adr[sid]):int(m.sensor_adr[sid])+3].tolist(),
                eq_geometry_closure_max_m=closure,eq_mimic_position_max_rad=mimic,eq_efc_position_max=eq_position_max,
                eq_acceleration_residual_max_mixed_units=acc_res,nefc=int(d.nefc),efc_types=d.efc_type.tolist(),efc_states=d.efc_state.tolist(),
                solver_niter=np.asarray(d.solver_niter).tolist(),dynamics_force_residual_max_mixed_units=dynres))
    assert len(rows)==counts['mj_forward']==12 and all(counts[n]==0 for n in method['blocked_integrators'])
    response=[]
    for pose in lock['poses']:
        group=[r for r in rows if r['pose']==pose['name']];base=group[0]
        for r in group[1:]:
            a=r['root_pitch_qacc_rad_s2']-base['root_pitch_qacc_rad_s2']
            same=(r['efc_types']==base['efc_types']and r['efc_states']==base['efc_states'])
            eligible=bool(r['ncon']==base['ncon']==0 and same)
            dq=np.asarray(r['hinge_qacc6_rad_s2'])-base['hinge_qacc6_rad_s2']
            response.append(dict(pose=pose['name'],channel=r['query'],delta_root_pitch_qacc_rad_s2=a,
                delta_hinge_qacc6_rad_s2=dq.tolist(),delta_crank_minus_hip_qacc2_rad_s2=[float(dq[1]-dq[0]),float(dq[4]-dq[3])],
                same_constraint_types_states=same,nominal_contact_free_interpretation_eligible=eligible,
                computed_coefficient_sign='POSITIVE'if a>0 else'NEGATIVE'if a<0 else'ZERO',
                restoring_k_sign_for_u_equals_k_times_positive_pitch_error=('NEGATIVE'if a>0 else'POSITIVE'if a<0 else'UNKNOWN')if eligible else'UNKNOWN_CONSTRAINT_OR_CONTACT',
                unit='rad/s^2 per +1Nm common input EACH selected actuator; pair total2Nm'))
    output=dict(kind='TWELVE_NOMINAL_ZERO_STEP_AIR_UNIT_CTRL_RESPONSES_NOT_RUNTIME_OR_ROBUSTNESS_CERTIFICATE',
        method_SHA=sha(D/'METHOD.json'),source_lock_SHA=sha(D/'SOURCE_LOCK.json'),script_SHA=sha(Path(__file__)),engine=mujoco.__version__,numpy=np.__version__,
        model=dict(nq=m.nq,nv=m.nv,nbody=m.nbody,ngeom=m.ngeom,nmesh=m.nmesh,nu=m.nu,na=m.na),model_boots=boot,calls=counts,
        model_options_unmodified=opts,actuators=actuators,gyro=sensor,
        frame=dict(freejoint='floating_base',qposadr=root_qadr,dofadr=root_dof,pitch_qacc_index=pitch_index,
            scope='identity orientation and zero qvel only; local/world coincide',max_root_Jacobian_identity_error=max_jac_error,
            max_qacc_vs_object_angular_acceleration_error=max_alpha_error),
        max_dynamics_force_residual=max_dynamics_residual,rows=rows,response=response,
        raw_or_DR_samples_read=0,mesh_asset_hashes=0,PD_or_solver_modified=False,gain_selected=False,controller_implemented=False,
        sustained_D4_torque_authority_claim=False,robustness_claim=False,PH7_pending=True)
    with (D/'RESPONSES.json').open('x',encoding='utf-8')as f:json.dump(output,f,separators=(',',':'),allow_nan=False);f.write('\n')
    print(json.dumps(dict(status='COMPLETED_12_FORWARD_0_INTEGRATOR',calls=counts,ncon=[r['ncon']for r in rows],frame=output['frame'],
        zero_baselines=[dict(pose=r['pose'],root_pitch_qacc=r['root_pitch_qacc_rad_s2'])for r in rows if r['query']=='zero'],
        max_dynamics_force_residual=max_dynamics_residual,response=response,
        result_bytes=(D/'RESPONSES.json').stat().st_size,result_SHA=sha(D/'RESPONSES.json')),indent=2))
except BaseException:
    with (D/'PARTIAL_ERROR.json').open('x',encoding='utf-8')as f:json.dump(dict(status='PARTIAL_UNKNOWN_NOT_SEALED',traceback=traceback.format_exc(),model_boots=boot,calls=counts,rows=rows),f,allow_nan=False)
    raise
finally:
    for name,fn in original.items():setattr(mujoco,name,fn)
