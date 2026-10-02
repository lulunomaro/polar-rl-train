"""Read-only CAD/MJCF extraction for the MATLAB whole-body study."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import mujoco

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'chassis_mod4'))
from kinematics import leg_configuration

MODEL_PATH = ROOT / 'chassis_mod4_work/folded_pose_sim/scene_hard_stop_audit.xml'
model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
data = mujoco.MjData(model)
params = json.loads((ROOT/'chassis_mod4/model_parameters.json').read_text(encoding='utf8'))
manifest = json.loads((ROOT/'chassis_mod4/reports/model_manifest.json').read_text(encoding='utf8'))
radius = params['wheel_motor']['wheel_radius_m']
wheel_ids = [model.body(s+'_wheel').id for s in ('left', 'right')]
fixed_ids = [model.body('chassis').id] + [model.body(s+'_drive_'+a).id for s in ('left','right') for a in ('hip','input')]
leg_ids = {s:[i for i in range(1,model.nbody) if model.body(i).name.startswith(s+'_') and i not in wheel_ids+fixed_ids] for s in ('left','right')}

def set_pose(hip, difference):
    data.qpos[:] = model.qpos0
    data.qpos[:3] = 0
    data.qpos[3:7] = [1,0,0,0]
    for s in ('left','right'):
        values,_ = leg_configuration(hip,difference,s)
        for name,v in values.items():
            j = model.joint(s+'_'+name)
            data.qpos[j.qposadr[0]]=v
    data.qvel[:]=0
    mujoco.mj_forward(model,data)
    data.qpos[2] = radius-data.xpos[wheel_ids[0],2]
    mujoco.mj_forward(model,data)

def aggregate(ids):
    mass = float(model.body_mass[ids].sum())
    com = (model.body_mass[ids,None]*data.xipos[ids]).sum(0)/mass
    inertia = np.zeros((3,3))
    for i in ids:
        r = data.ximat[i].reshape(3,3)
        d = data.xipos[i]-com
        inertia += r @ np.diag(model.body_inertia[i]) @ r.T + model.body_mass[i]*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    return mass,com,inertia

mesh_rows=[]
for gi in range(model.ngeom):
    if model.geom_type[gi] == mujoco.mjtGeom.mjGEOM_MESH:
        mi=int(model.geom_dataid[gi]); start=int(model.mesh_vertadr[mi]); n=int(model.mesh_vertnum[mi])
        mesh_rows.append((gi,model.mesh_vert[start:start+n].astype(float)))

def envelope():
    lo,hi=1e9,-1e9
    for gi,v in mesh_rows:
        z=(v@data.geom_xmat[gi].reshape(3,3).T+data.geom_xpos[gi])[:,2]
        lo=min(lo,float(z.min()));hi=max(hi,float(z.max()))
    return lo,hi

def gravity_energy(hip,difference):
    set_pose(hip,difference)
    return float(np.dot(model.body_mass, data.xipos[:,2])*9.81)

def gradients(hip,difference,eps=1e-5):
    # Both legs move symmetrically; split common virtual work equally by side.
    dh=(gravity_energy(hip+eps,difference)-gravity_energy(hip-eps,difference))/(4*eps)
    dd=(gravity_energy(hip,difference+eps)-gravity_energy(hip,difference-eps))/(4*eps)
    ghip=dh-dd
    gcrank=dd
    def virtual(qh,qc):
        vals,p=leg_configuration(qh,qc-qh,'left')
        W=p['W']; L=float(np.linalg.norm(W)); alpha=float(np.arctan2(-W[0],-W[1]))
        return np.array([L,alpha,vals['gas_slide']])
    qc=hip+difference
    j=np.column_stack(((virtual(hip+eps,qc)-virtual(hip-eps,qc))/(2*eps), (virtual(hip,qc+eps)-virtual(hip,qc-eps))/(2*eps)))
    return [ghip,gcrank],j

rows=[]
for difference in np.linspace(-.75,.40,24):
    _,p0=leg_configuration(0,float(difference),'left')
    hip=float(np.arctan2(p0['W'][0],-p0['W'][1]))
    set_pose(hip,float(difference))
    if not -.5 <= hip <= .5: continue
    mb,cb,Ib=aggregate(fixed_ids)
    ml,cl,Il=aggregate(leg_ids['left'])
    mr,cr,Ir=aggregate(leg_ids['right'])
    mw,cw,Iw=aggregate([wheel_ids[0]])
    allm,allcom,Iall=aggregate(list(range(1,model.nbody)))
    hippos=data.xpos[model.body('chassis').id].copy()
    axle=data.xpos[wheel_ids[0]].copy()
    L=float(np.linalg.norm((hippos-axle)[[0,2]]))
    com_from_wheel=(cl-axle)[[0,2]]
    com_from_hip=(cl-hippos)[[0,2]]
    qgas=float(data.qpos[model.joint('left_gas_slide').qposadr[0]])
    eye_length=float(np.linalg.norm(p0['T']-p0['S']))
    low,top=envelope()
    gtorque,J=gradients(hip,float(difference))
    set_pose(hip,float(difference))
    vertical_velocity=np.zeros(model.nv)
    vertical_velocity[2]=1.0
    active_rate=np.linalg.solve(J[:2],[1.,0.])
    eps=1e-5
    for side in ('left','right'):
        plus,_=leg_configuration(hip+eps*active_rate[0],float(difference)+eps*(active_rate[1]-active_rate[0]),side)
        minus,_=leg_configuration(hip-eps*active_rate[0],float(difference)-eps*(active_rate[1]-active_rate[0]),side)
        for name in plus:
            joint=model.joint(side+'_'+name)
            vertical_velocity[joint.dofadr[0]]=(plus[name]-minus[name])/(2*eps)
    full_mass=np.empty((model.nv,model.nv))
    mujoco.mj_fullM(model,data,full_mass)
    vertical_inertia=float(vertical_velocity@full_mass@vertical_velocity)
    # Source equations assume negative leg-COM x relative to the wheel.
    rows.append(dict(leg_length_m=L,hip_rad=hip,crank_rad=hip+float(difference),difference_rad=float(difference),
        root_height_m=float(data.qpos[2]),body_mass_kg=mb,body_com_from_hip_xz_m=(cb-hippos)[[0,2]].tolist(),body_pitch_inertia_kg_m2=float(Ib[1,1]),
        left_leg_mass_kg=ml,right_leg_mass_kg=mr,leg_com_from_wheel_xz_m=com_from_wheel.tolist(),
        leg_com_from_hip_xz_m=com_from_hip.tolist(),leg_pitch_inertia_kg_m2=float(Il[1,1]),
        wheel_mass_kg=mw,wheel_pitch_inertia_kg_m2=float(Iw[1,1]),wheel_armature_kg_m2=float(model.dof_armature[model.joint('left_wheel_spin').dofadr[0]]),
        leg_active_armature_total_kg_m2=sum(float(model.dof_armature[model.joint('left_'+j).dofadr[0]]) for j in ('hip','crank')),
        total_yaw_inertia_kg_m2=float(Iall[2,2]),gas_slide_m=qgas,spring_eye_length_m=eye_length,
        static_gravity_motor_torque_nm=gtorque,virtual_jacobian=J.tolist(),effective_vertical_inertia_kg=vertical_inertia,
        full_visual_height_m=top,visual_ground_min_m=low,
        total_com_xz_m=allcom[[0,2]].tolist(),skeleton_xz_m={k:v.tolist() for k,v in leg_configuration(hip,float(difference),'left')[1].items()}))

set_pose(0,0)
neutral_body={model.body(i).name: {'mass_kg':float(model.body_mass[i]),'com_xyz_m':data.xipos[i].tolist(),'principal_inertia_kg_m2':model.body_inertia[i].tolist()} for i in range(1,model.nbody)}
out=dict(model='MOD4',source_mjcf=str(MODEL_PATH),source_mjcf_sha256=hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest(),
    source_step_sha256=manifest['source']['source_sha256'],total_mass_kg=float(model.body_mass.sum()),
    payload_mass_kg=0, mass_status=params['mass_status'],wheel_radius_m=radius,track_m=params['wheel_tire_track_m'],
    motor_parameters=params,poses=rows,bodies=neutral_body,
    gas_model=dict(reference_definition='Per spring at gas_slide q=0, not constant force throughout stroke.',forces_n=[300,500,700],stiffness_n_m=3500,damping_n_s_m=3),
    reference_repository='https://github.com/Particlela/WBR_simulation',reference_commit='83414c0be55632b7aa1d4dc9feaa0f5f63d5d93e')
(HERE/'mod4_extracted_parameters.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'mass_kg':out['total_mass_kg'],'poses':len(rows),'range_m':[rows[0]['leg_length_m'],rows[-1]['leg_length_m']], 'body_com':rows[15]['body_com_from_hip_xz_m'],'leg_com_x':rows[15]['leg_com_from_wheel_xz_m'][0]},ensure_ascii=False))
