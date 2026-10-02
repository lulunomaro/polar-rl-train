"""Independent moving-pose USD/MJCF audit; no PhysX execution is claimed.

Reconstruct the USD tree from its joint frames using SE(3) equations, without
import_contract.json or the USD exporter. Check 225 closed-branch configurations.
"""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
from pxr import Usd, UsdGeom, UsdPhysics

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kinematics import set_configuration, PARAMS

def matrix(q):
    return Rotation.from_quat([*q.GetImaginary(),q.GetReal()]).as_matrix()

def frame(p,q):
    T=np.eye(4);T[:3,:3]=matrix(q);T[:3,3]=p
    return T

def audit():
    m=mujoco.MjModel.from_xml_path(str(ROOT/'scene_training.xml'));d=mujoco.MjData(m)
    stage=Usd.Stage.Open(str(ROOT/'isaac/robot.usd'))
    edges=[];closures=[];joint_names=[]
    for prim in stage.Traverse():
        if not prim.IsA(UsdPhysics.Joint):continue
        j=UsdPhysics.Joint(prim)
        if j.GetExcludeFromArticulationAttr().Get():
            closures.append(j);continue
        assert j.GetBody0Rel().GetTargets() and j.GetBody1Rel().GetTargets()
        parent=j.GetBody0Rel().GetTargets()[0].name;child=j.GetBody1Rel().GetTargets()[0].name
        edges.append((prim.GetName(),parent,child,
            frame(j.GetLocalPos0Attr().Get(),j.GetLocalRot0Attr().Get()),
            np.linalg.inv(frame(j.GetLocalPos1Attr().Get(),j.GetLocalRot1Attr().Get())),
            prim.IsA(UsdPhysics.PrismaticJoint)))
        joint_names.append(prim.GetName())
    assert len(edges)==22 and len(closures)==6
    assert set(joint_names)=={m.joint(j).name for j in range(1,m.njnt)}
    rng=np.random.default_rng(10910)
    lo,hi=PARAMS['limits']['left']['input_difference_rad']
    cases=[(h,f,-h,f) for h in np.linspace(-.49,.49,5) for f in np.linspace(lo+1e-5,hi-1e-5,5)]
    cases += [(rng.uniform(-.49,.49),rng.uniform(lo,hi),rng.uniform(-.49,.49),rng.uniform(lo,hi)) for _ in range(200)]
    max_pos=max_rot=max_closure=0.;ranks=set();min_eig=float('inf')
    for lh,ld,rh,rd in cases:
        mujoco.mj_resetData(m,d)
        set_configuration(m,d,left=(lh,ld),right=(rh,rd))
        for side in ['left','right']:d.qpos[m.joint(side+'_wheel_spin').qposadr[0]]=rng.uniform(-6.,6.)
        mujoco.mj_forward(m,d)
        base=np.eye(4);base[:3,:3]=d.xmat[1].reshape(3,3);base[:3,3]=d.xpos[1]
        poses={'chassis':base};pending=list(edges)
        while pending:
            ready=[e for e in pending if e[1] in poses]
            assert ready,'USD tree has a cycle or unreachable body'
            for e in ready:
                name,parent,child,T0,T1,slide=e
                assert child not in poses,'Multiple tree parents'
                q=d.qpos[m.joint(name).qposadr[0]];motion=np.eye(4)
                if slide:motion[0,3]=q
                else:motion[:3,:3]=Rotation.from_rotvec([q,0,0]).as_matrix()
                poses[child]=poses[parent]@T0@motion@T1;pending.remove(e)
        for name,T in poses.items():
            b=m.body(name).id
            max_pos=max(max_pos,float(np.linalg.norm(T[:3,3]-d.xpos[b])))
            max_rot=max(max_rot,float(np.max(np.abs(T[:3,:3]-d.xmat[b].reshape(3,3)))))
        for j in closures:
            p=[]
            for i in [0,1]:
                target=getattr(j,f'GetBody{i}Rel')().GetTargets()[0].name
                anchor=getattr(j,f'GetLocalPos{i}Attr')().Get()
                p.append((poses[target]@np.r_[anchor,1])[:3])
            max_closure=max(max_closure,float(np.linalg.norm(p[0]-p[1])))
        rows=np.asarray(d.efc_type)==int(mujoco.mjtConstraint.mjCNSTR_EQUALITY)
        J=d.efc_J.reshape(-1,m.nv)[rows];ranks.add(int(np.linalg.matrix_rank(J,tol=1e-7)))
        M=np.zeros((m.nv,m.nv));mujoco.mj_fullM(m,d,M)
        min_eig=min(min_eig,float(np.linalg.eigvalsh(M)[0]))
    assert max_pos<3e-7 and max_rot<3e-6 and max_closure<3e-7,(max_pos,max_rot,max_closure)
    assert ranks=={16} and min_eig>0,(ranks,min_eig)
    manifest=json.loads((ROOT/'reports/model_manifest.json').read_text(encoding='utf8'))
    balance=float(m.body_mass.sum())-sum(p['mass_kg'] for p in manifest['part_membership'])
    assert abs(balance)<1e-7,balance
    wp=PARAMS['wheel_motor']
    for side in ['left','right']:
        b=m.body(side+'_wheel');j=m.joint(side+'_wheel_spin')
        assert abs(b.mass[0]-manifest['body_masses_kg'][side+'_wheel'])<1e-8, 'Wheel output component mass differs from CAD partition'
        assert np.isclose(m.dof_armature[j.dofadr[0]],wp['motor_rotor_inertia_kg_m2']*15.8**2)
        for g in range(m.ngeom):
            if 'housing_placeholder' in m.geom(g).name:assert m.body(m.geom_bodyid[g]).name.endswith('_shin')
    result={'status':'PASS','sampled_configurations':len(cases),'max_body_position_error_m':max_pos,
        'max_rotation_matrix_error':max_rot,'max_usd_closure_error_m':max_closure,
        'equality_ranks':sorted(ranks),'independent_velocity_dofs':m.nv-16,
        'minimum_mass_matrix_eigenvalue':min_eig,'model_mass_kg':float(m.body_mass.sum()),
        'mass_balance_error_kg':balance,'physics_engine_scope':'MuJoCo forward dynamics and independent USD kinematics; PhysX not run',
        'sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['scene_training.xml','isaac/robot.usd','model_parameters.json']}}
    (ROOT/'reports/model_parity_audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':audit()
