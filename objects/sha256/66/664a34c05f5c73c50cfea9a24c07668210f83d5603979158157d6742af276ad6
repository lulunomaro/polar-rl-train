"""Read-only model geometry audit for a 250 mm high horizontal tunnel."""
from pathlib import Path
import sys, json
import numpy as np
import mujoco
from scipy.spatial import ConvexHull
from scipy.optimize import differential_evolution, minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'chassis_mod4'))
from kinematics import leg_configuration, PARAMS, PINS
sys.stdout.reconfigure(encoding='utf8')
OUT = ROOT / 'chassis_mod4_work' / 'tunnel_250'
OUT.mkdir(exist_ok=True)
m = mujoco.MjModel.from_xml_path(str(ROOT / 'chassis_mod4' / 'scene.xml'))
d = mujoco.MjData(m)
manifest = json.loads((ROOT/'chassis_mod4/reports/model_manifest.json').read_text(encoding='utf8'))
parts = json.loads((ROOT/'chassis_mod4/reports/cad_parts.json').read_text(encoding='utf8'))
visual = []
by_body = {}
rot = np.zeros(9)
for g in range(m.ngeom):
    if m.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH:
        continue
    mesh = m.geom_dataid[g]
    verts = m.mesh_vert[m.mesh_vertadr[mesh]:m.mesh_vertadr[mesh]+m.mesh_vertnum[mesh]].astype(float)
    mujoco.mju_quat2Mat(rot, m.geom_quat[g])
    verts = verts @ rot.reshape(3,3).T + m.geom_pos[g]
    bid = int(m.geom_bodyid[g])
    visual.append((g, bid, verts))
    by_body.setdefault(bid, []).append(verts)
hulls = {}
for bid, meshes in by_body.items():
    pts = np.concatenate(meshes)
    xz = pts[:, [0,2]]
    hulls[bid] = xz[ConvexHull(xz).vertices]
chassis_id = m.body('chassis').id
wheel_ids = [m.body(s+'_wheel').id for s in ['left', 'right']]
joint_ids = {s:{n:m.joint(s+'_'+n).id for n in leg_configuration(0,0,s)[0]} for s in ['left','right']}
radius = PARAMS['wheel_motor']['wheel_radius_m']

def pose(hip, difference, pitch=0):
    d.qpos[:]=m.qpos0
    d.qpos[:3]=0
    d.qpos[3:7]=[np.cos(pitch/2),0,np.sin(pitch/2),0]
    for side in ['left','right']:
        vals,_=leg_configuration(hip,difference,side)
        for name,value in vals.items():
            j=joint_ids[side][name]
            if m.jnt_limited[j] and not m.jnt_range[j,0]-1e-8 <= value <= m.jnt_range[j,1]+1e-8:
                raise ValueError(name)
            d.qpos[m.jnt_qposadr[j]]=value
    mujoco.mj_kinematics(m,d)
    lift=radius-d.xpos[wheel_ids[0],2]
    d.qpos[2]=lift
    mujoco.mj_kinematics(m,d)
    lower=[];upper=[]
    for bid,pts in hulls.items():
        z=pts @ d.xmat[bid].reshape(3,3)[2,[0,2]]+d.xpos[bid,2]
        lower.append((float(z.min()),bid));upper.append((float(z.max()),bid))
    bottom=min(lower);top=max(upper)
    nonground=min(t for t in lower if t[1] not in wheel_ids)
    mujoco.mj_comPos(m,d)
    balance=float(d.subtree_com[chassis_id,0]-d.xpos[wheel_ids[0],0])
    return dict(hip_rad=float(hip),difference_rad=float(difference),pitch_rad=float(pitch),
                height_m=top[0],top_body=m.body(top[1]).name,
                lowest_nonwheel_m=nonground[0],lowest_nonwheel_body=m.body(nonground[1]).name,
                bottom_m=bottom[0],base_height_m=float(lift),com_axle_x_m=balance,
                spring_eye_m=float(np.linalg.norm(PINS['left']['T']-PINS['left']['S'])+d.qpos[m.joint('left_gas_slide').qposadr[0]]))

def exact_details(row):
    pose(row['hip_rad'],row['difference_rad'],row['pitch_rad'])
    results=[]
    for g,bid,verts in visual:
        world=verts@d.xmat[bid].reshape(3,3).T+d.xpos[bid]
        name=m.geom(g).name
        idx=int(name.split('_')[-1])
        results.append(dict(geom=name,cad_name=parts[idx]['name'],body=m.body(bid).name,min_m=world.min(0).tolist(),max_m=world.max(0).tolist()))
    return sorted(results,key=lambda r:r['max_m'][2],reverse=True)

def solve(pitch_bounds=None,balance=False):
    bounds=[tuple(PARAMS['hip_range_rad']),tuple(PARAMS['limits']['left']['input_difference_rad'])]
    if pitch_bounds is not None:bounds.append(pitch_bounds)
    def objective(x):
        try:r=pose(*x)
        except ValueError:return 10.
        value=r['height_m']+100.*max(0,.003-r['lowest_nonwheel_m'])
        if balance:value+=100.*max(0,abs(r['com_axle_x_m'])-.005)
        return value
    sol=differential_evolution(objective,bounds,popsize=12,maxiter=180,tol=1e-9,seed=731,polish=True)
    r=pose(*sol.x)
    r.update(search_success=bool(sol.success),evaluations=int(sol.nfev),objective=float(sol.fun),balance_constraint=balance)
    r['top_geoms']=exact_details(r)[:5]
    print(json.dumps(r,ensure_ascii=False),flush=True)
    return r

if __name__=='__main__':
    report={'scope':'All 277 CAD visual meshes. Symmetric legs, both wheels on level floor, no roll. Keep current MJCF joint limits. Non-wheel ground clearance >= 3 mm. Geometry feasibility only, no controller simulation.',
            'mesh_deflection_mm':manifest['source']['mesh_deflection_mm'],
            'tunnel_height_m':.250,'neutral':pose(0,0)}
    print('NEUTRAL',report['neutral'],flush=True)
    pts=np.concatenate(by_body[chassis_id])
    report['rigid_chassis_dimensions_m']=np.ptp(pts,axis=0).tolist()
    print('CHASSIS',report['rigid_chassis_dimensions_m'],flush=True)
    report['level_body_min']=solve()
    report['pitched_30deg_min']=solve((-np.pi/6,np.pi/6))
    report['pitched_90deg_min']=solve((-np.pi/2,np.pi/2))
    report['balanced_30deg_min']=solve((-np.pi/6,np.pi/6),balance=True)
    for key in ['neutral','level_body_min','pitched_30deg_min','pitched_90deg_min','balanced_30deg_min']:
        row=report[key]
        pose(row['hip_rad'],row['difference_rad'],row['pitch_rad'])
        mujoco.mj_forward(m,d)
        row['collision_proxy_contacts']=[dict(geom1=m.geom(c.geom1).name,geom2=m.geom(c.geom2).name,distance_m=float(c.dist)) for c in d.contact[:d.ncon]]
        row['height_margin_m']=.25-row['height_m']
    ch=hulls[chassis_id]
    def thickness(pitch):
        z=ch@np.array([-np.sin(pitch),np.cos(pitch)])
        return float(np.ptp(z))
    res=differential_evolution(lambda x:thickness(x[0]),[(-np.pi/2,np.pi/2)],seed=731,tol=1e-10)
    report['rigid_chassis_min_pitch_thickness_m']=float(res.fun)
    report['rigid_chassis_min_pitch_rad']=float(res.x[0])
    (OUT/'geometry_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print('SAVED',OUT/'geometry_audit.json',flush=True)
