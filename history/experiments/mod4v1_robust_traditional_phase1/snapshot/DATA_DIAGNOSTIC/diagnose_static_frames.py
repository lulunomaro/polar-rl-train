"""Zero-step static frames/COM/FK diagnostics, no control/DR/rollout imports.
Standalone known-pose sensors + actual model/source-trace linkage snapshots.
"""
from pathlib import Path
import hashlib,importlib.util,json,math,traceback,xml.etree.ElementTree as ET
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
MODEL=ROOT/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'
KIN=ROOT.parent/'traditional_control_20261101/kinematics.py'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x

def main():
    assert not (OUT/'STATIC_FRAME_GEOMETRY.json').exists()
    before={'model':sha(MODEL),'kinematics':sha(KIN)}
    counts={'mj_forward_calls':0,'physics_step_calls':0}
    fwd=mujoco.mj_forward
    def forward(m,d):counts['mj_forward_calls']+=1;return fwd(m,d)
    def banned(*args,**kwargs):counts['physics_step_calls']+=1;raise AssertionError('No new physics steps allowed')
    mujoco.mj_forward=forward
    for name in ['mj_step','mj_step1','mj_step2']:setattr(mujoco,name,banned)
    m=mujoco.MjModel.from_xml_path(str(MODEL));sid=m.site('imu').id;bid=m.body('chassis').id
    # R00 changes only this site translation at construction. Body/site orientations unchanged.
    authored={'actual_source_site_quat':m.site_quat[sid].copy(),'source_site_pos':m.site_pos[sid].copy(),'r00_virtual_imu_pos':[.03,0.,.04],'chassis_principal_iquat':m.body_iquat[bid].copy(),'chassis_COM':m.body_ipos[bid].copy()}
    iq=' '.join(map(str,m.body_iquat[bid]));idiag=' '.join(map(str,m.body_inertia[bid]));com=' '.join(map(str,m.body_ipos[bid]));mass=float(m.body_mass[bid])
    def tiny(rpy,free=False,anchor_dof=False):
        xyzw=Rotation.from_euler('xyz',rpy).as_quat();q=' '.join(map(str,[xyzw[3],*xyzw[:3]]))
        joint='<freejoint/>' if free else (f'<joint type="hinge" pos="{com}" axis="0 0 1"/>' if anchor_dof else '')
        xml=f'<mujoco><option gravity="0 0 -9.81"/><worldbody><body name="chassis" pos="0 0 1" quat="{q}">{joint}<inertial mass="{mass}" pos="{com}" quat="{iq}" diaginertia="{idiag}"/><site name="imu" pos=".03 0 .04"/></body></worldbody><sensor><gyro name="gyro" site="imu"/><accelerometer name="acc" site="imu"/></sensor></mujoco>'
        mm=mujoco.MjModel.from_xml_string(xml);dd=mujoco.MjData(mm)
        if free:dd.qvel[3:6]=[.2,-.3,.7]
        mujoco.mj_forward(mm,dd)
        R=np.asarray(dd.xmat[mm.body('chassis').id]).reshape(3,3);RS=np.asarray(dd.site_xmat[mm.site('imu').id]).reshape(3,3)
        return {'rpy_rad':rpy,'nv':mm.nv,'COM_anchored_stationary_fixture':anchor_dof,'site_body_rotation_matrix_max_error':float(np.max(abs(RS-R))),'gyro':dd.sensor('gyro').data.copy(),'proper_accel':dd.sensor('acc').data.copy(),'expected_fixed_proper_accel_body':R.T@np.array([0,0,9.81]),'expected_free_gyro_body':[.2,-.3,.7] if free else [0,0,0],'time':float(dd.time)}
    fixed_nv0=[tiny(p) for p in [[0,0,0],[0,.25,0],[.15,-.2,.3]]]
    fixed=[tiny(p,anchor_dof=True) for p in [[0,0,0],[0,.25,0],[.15,-.2,.3]]];free=[tiny(p,True) for p in [[0,0,0],[0,.25,.5],[.15,-.2,.3]]]
    (OUT/'STATIC_SENSOR_PRECHECK_002.json').write_text(json.dumps(plain({'zero_DOF_fixture':fixed_nv0,'COM_anchored_stationary_fixture':fixed,'free_known_omega_fixture':free}),indent=2),encoding='utf-8')
    assert max(float(np.max(abs(x['proper_accel']-x['expected_fixed_proper_accel_body']))) for x in fixed)<1e-12
    assert max(float(np.max(abs(x['gyro']-x['expected_free_gyro_body']))) for x in free)<1e-12
    assert max(x['site_body_rotation_matrix_max_error'] for x in fixed+free)<1e-12
    spec=importlib.util.spec_from_file_location('readonly_fk_for_COM',KIN);kin=importlib.util.module_from_spec(spec);spec.loader.exec_module(kin)
    modeltree=ET.parse(MODEL).getroot();modeltree.find('compiler').set('meshdir',str(MODEL.parent));modeltree.find(".//site[@name='imu']").set('pos','.03 0 .04')
    mm=mujoco.MjModel.from_xml_string(ET.tostring(modeltree,encoding='unicode'));rootid=mm.body('chassis').id
    geometry=[];errors=[]
    for case in ['r00_forward_nominal_sensors','r00_spin_nominal_sensors']:
        trace=[json.loads(x) for x in (ROOT/'results'/case/'trace.jsonl').read_text(encoding='utf-8').splitlines()]
        for i in [0,100,200,300,400,500,600,700,799]:
          try:
            row=trace[i];enc=row['encoder4'];d=mujoco.MjData(mm);d.qpos[:3]=[0,0,.6];d.qpos[3:7]=[1,0,0,0]
            kin.set_configuration(mm,d,left=(enc[0],enc[1]-enc[0]),right=(enc[2],enc[3]-enc[2]),check_limits=False)
            o=d.xpos[rootid];rw=np.mean([d.xpos[mm.body(s+'_wheel').id] for s in ['left','right']],axis=0)-o;rc=d.subtree_com[rootid]-o;ri=d.site_xpos[mm.site('imu').id]-o
            omega=np.array(row['raw_gyro']);rco=-rc;rwo=-rw
            target={'case':case,'trace_row_index':i,'packet_time_s':row['sensor_timestamp_s'],'encoder4':enc,'wheelmid_body_m':rw.copy(),'whole_COM_body_m':rc.copy(),'chassis_COM_body_m':mm.body_ipos[rootid].copy(),'imu_body_m':ri.copy(),'COM_to_IMU_body_m':ri-rc,'wheelmid_to_IMU_body_m':ri-rw,
                    'actual_raw_omega_body':omega,'rigid_about_COM_origin_centripetal_template':np.cross(omega,np.cross(omega,rco)),'rigid_about_wheelmid_origin_centripetal_template':np.cross(omega,np.cross(omega,rwo)),
                    'at_command_4pi_about_COM_origin_centripetal_template':np.cross([0,0,4*math.pi],np.cross([0,0,4*math.pi],rco)),'at_command_4pi_about_wheelmid_origin_centripetal_template':np.cross([0,0,4*math.pi],np.cross([0,0,4*math.pi],rwo)),
                    'scope':'instantaneous rigid-reference acceleration template only; moving linkage/reference derivatives and actual translational dynamics not inferred','data_time_s':float(d.time)}
            if i>0:
                gt=trace[i-1]['ground_truth'];R=Rotation.from_euler('xyz',[gt['roll_true'],gt['pitch_true'],gt['yaw_true']]).as_matrix();truthrw=R.T@(np.mean(gt['wheel_xyz'],axis=0)-gt['xyz']);target['trace_aligned_wheelmid_body_m']=truthrw;target['FK_vs_aligned_trace_wheelmid_max_error_m']=float(np.max(abs(rw-truthrw)))
            geometry.append(target)
          except Exception:errors.append({'case':case,'i':i,'error':traceback.format_exc()})
    after={'model':sha(MODEL),'kinematics':sha(KIN)};assert before==after
    out={'mode':'STATIC_FORWARD_FK_ONLY','engine':mujoco.__version__,'source_hashes':before,'source_hashes_unchanged':True,'authored_frames':authored,'original_nv0_fixture_readouts':fixed_nv0,'standalone_fixed_pose_sensor_checks':fixed,'standalone_free_known_body_omega_checks':free,'actual_model_FK_geometry_samples':geometry,'errors':errors,**counts,'physics_time_advanced_s':0.,'inertia_frame_is_not_sensor_frame_verified':True,'critical_interpretation':'Origin lever-arm compensation returns properaccel at chassis origin, not gravity. COM/wheelmid pivot compensation is a separate reference choice, and actual R00 spin never implies command4pi was reached.'}
    (OUT/'STATIC_FRAME_GEOMETRY.json').write_text(json.dumps(plain(out),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(plain({'source_hashes':before,'frames':authored,'fixed':fixed,'gyro':free,'first_FK':geometry[0],'last_forward_FK':geometry[8],'last_spin_FK':geometry[-1],**counts,'errors':errors}),ensure_ascii=False,indent=2))
    assert not errors
if __name__=='__main__':
    try:main()
    except Exception:
        (OUT/'STATIC_FRAME_FAILURE_002.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
