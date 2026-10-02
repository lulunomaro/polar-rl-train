"""Fail closed on altered/missing USD topology. Also usable without Isaac.

Static USD inspection cannot prove a PhysX solver created the constraints.
RuntimeGuard additionally checks their motion at every physics step.
"""
from pathlib import Path
import argparse, json
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics, Gf

HERE=Path(__file__).resolve().parent
CONTRACT=json.loads((HERE/'import_contract.json').read_text())

def audit_stage(stage,root='/Robot',require_physx=False):
    c=CONTRACT; errors=[]
    def check(ok,why):
        if not ok:errors.append(why)
    def at(path):
        p=stage.GetPrimAtPath(root+path)
        return p if p and p.IsActive() else Usd.Prim()
    def near(a,b,label,tol=2e-6):
        check(a is not None and np.allclose(a,b,rtol=2e-5,atol=tol),label)
    def targets(prim,name):return [str(p) for p in prim.GetRelationship(name).GetTargets()] if prim else []
    def value(prim,name):return prim.GetAttribute(name).Get() if prim else None
    check(bool(at('')),'robot root missing')
    check(abs(UsdGeom.GetStageMetersPerUnit(stage)-1)<1e-12,'stage is not in meters')
    check(UsdGeom.GetStageUpAxis(stage)=='Z','stage is not Z-up')
    roots=[];actual_bodies=[];actual_joints=[];visuals=0;colliders=0
    if at(''):
        for prim in Usd.PrimRange(at('')):
            if prim.HasAPI(UsdPhysics.ArticulationRootAPI):roots.append(prim)
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):actual_bodies.append(prim.GetName())
            if prim.IsA(UsdPhysics.Joint):actual_joints.append(prim.GetName())
            if prim.HasAPI(UsdPhysics.CollisionAPI):colliders+=1
            elif prim.IsA(UsdGeom.Mesh):visuals+=1
    check(len(roots)==1,'expected one articulation root')
    check(set(actual_bodies)==set(c['bodies']),'rigid-body set changed')
    check(set(actual_joints)==set(c['joints'])|set(c['closures']),'joint set changed')
    check(visuals==c['visual_instance_count'],'HiFi visual instance count changed')
    check(colliders==c['collision_primitive_count'],'collision primitive count changed')
    for name,exp in c['bodies'].items():
        p=at('/links/'+name);check(bool(p),'missing body '+name)
        if not p:continue
        rel,_=UsdGeom.XformCache().ComputeRelativeTransform(p,at(''))
        near(rel.ExtractTranslation(),exp['neutral_position_m'],name+' neutral position')
        q=rel.ExtractRotationQuat()
        check(abs(np.dot(np.r_[q.GetReal(),list(q.GetImaginary())],exp['neutral_quat_wxyz']))>1-1e-5,name+' neutral orientation')
        near(value(p,'physics:mass'),exp['mass_kg'],name+' mass')
        near(value(p,'physics:centerOfMass'),exp['com_m'],name+' center of mass')
        near(value(p,'physics:diagonalInertia'),exp['diagonal_inertia_kg_m2'],name+' inertia',1e-9)
        near(value(p,'physxRigidBody:linearDamping'),0.,name+' unexpected linear body damping')
        near(value(p,'physxRigidBody:angularDamping'),0.,name+' unexpected angular body damping')
        q=value(p,'physics:principalAxes')
        if q is not None:
            actual=np.r_[q.GetReal(),list(q.GetImaginary())];expected=exp['principal_axes_wxyz']
            check(abs(np.dot(actual,expected))>1-1e-5,name+' inertia orientation')
        else:check(False,name+' missing inertia orientation')
    for name,exp in c['geometry'].items():
        p=at('/links/'+exp['body']+'/'+name)
        check(bool(p),name+' missing/reparented geometry')
        if not p:continue
        near(value(p,'xformOp:translate'),exp['position_m'],name+' geometry position')
        q=value(p,'xformOp:orient')
        check(q is not None and abs(np.dot(np.r_[q.GetReal(),list(q.GetImaginary())],exp['quat_wxyz']))>1-1e-5,name+' geometry orientation')
        if exp['visual']:check(not p.HasAPI(UsdPhysics.CollisionAPI),name+' visual was made a collider')
        else:
            check(p.HasAPI(UsdPhysics.CollisionAPI),name+' missing CollisionAPI')
            check(value(p,'physics:collisionEnabled') is not False,name+' disabled collision')
            if exp['type'] in [2,3,5]:near(value(p,'radius'),exp['size'][0],name+' collision radius')
            if exp['type'] in [3,5]:near(value(p,'height'),exp['size'][1]*2,name+' collision height')
            if exp['type']==6:near(value(p,'xformOp:scale'),exp['size'],name+' collision box scale')
    for name,exp in c['joints'].items():
        p=at('/joints/'+name);check(bool(p),'missing joint '+name)
        if not p:continue
        cls=UsdPhysics.PrismaticJoint if exp['type']=='slide' else UsdPhysics.RevoluteJoint
        check(p.IsA(cls),name+' joint type')
        check(value(p,'physics:jointEnabled') is not False,name+' disabled joint')
        check(value(p,'physics:excludeFromArticulation') is not True,name+' tree joint excluded from articulation')
        check(value(p,'physics:axis')=='X',name+' joint axis')
        for k,body in [('body0','parent'),('body1','child')]:
            check(targets(p,'physics:'+k)==[root+'/links/'+exp[body]],name+' '+k+' topology')
        for i in [0,1]:
            near(value(p,'physics:localPos'+str(i)),exp['local_pos'+str(i)],name+' anchor '+str(i))
            q=value(p,'physics:localRot'+str(i))
            if q is not None:check(abs(np.dot(np.r_[q.GetReal(),list(q.GetImaginary())],exp['local_rot'+str(i)]))>1-1e-5,name+' axis frame '+str(i))
            else:check(False,name+' missing frame')
        if exp['limits_si'] is not None:
            factor=1 if exp['type']=='slide' else 180/np.pi
            near(value(p,'physics:lowerLimit'),exp['limits_si'][0]*factor,name+' lower limit')
            near(value(p,'physics:upperLimit'),exp['limits_si'][1]*factor,name+' upper limit')
        near(value(p,'physxJoint:armature'),exp['armature'],name+' armature',1e-9)
        if require_physx:check('PhysxJointAPI' in p.GetAppliedSchemas(),name+' PhysX joint schema is not registered')
        drive='linear' if exp['type']=='slide' else 'angular'
        near(value(p,'drive:'+drive+':physics:damping'),exp['damping_si']*(1 if drive=='linear' else np.pi/180),name+' drive damping/unit conversion')
        check(value(p,'drive:'+drive+':physics:type')=='force',name+' wrong drive type')
    for name,exp in c['closures'].items():
        p=at('/closures/'+name);check(bool(p),'MISSING CLOSURE '+name)
        if not p:continue
        check(p.IsA(UsdPhysics.SphericalJoint),name+' must be a spherical point closure')
        check(value(p,'physics:excludeFromArticulation') is True,name+' must be outside articulation')
        for i in [0,1]:
            check(targets(p,'physics:body'+str(i))==[root+'/links/'+exp['body'+str(i)]],name+' body pair')
            near(value(p,'physics:localPos'+str(i)),exp['anchor'+str(i)+'_m'],name+' closure anchor')
        check(value(p,'physics:jointEnabled') is not False,name+' closure disabled')
        try:
            cache=UsdGeom.XformCache()
            anchors=[]
            for i in [0,1]:
                body=at('/links/'+exp['body'+str(i)])
                anchors.append(np.array(cache.GetLocalToWorldTransform(body).Transform(Gf.Vec3d(*exp['anchor'+str(i)+'_m']))))
            check(np.linalg.norm(anchors[0]-anchors[1])<2e-6,name+' anchors do not meet in the authored neutral pose')
        except Exception:check(False,name+' cannot evaluate neutral anchors')
    for name,exp in c['mimics'].items():
        p=at('/joints/'+name)
        # GetAppliedSchemas omits unregistered PhysX schemas in plain usd-core.
        raw=p.GetMetadata('apiSchemas') if p else None
        check(raw is not None and 'PhysxMimicJointAPI:rotX' in raw.GetAppliedItems(),name+' MISSING MIMIC API')
        check(targets(p,'physxMimicJoint:rotX:referenceJoint')==[root+'/joints/'+exp['reference_joint']],name+' mimic reference')
        for k in ['gearing','offset']:near(value(p,'physxMimicJoint:rotX:'+k),exp[k],name+' mimic '+k)
        if require_physx:check('PhysxMimicJointAPI:rotX' in p.GetAppliedSchemas(),name+' PhysX mimic schema is not registered in this Isaac installation')
    for a,b in c['filters']:
        check(root+'/links/'+b in targets(at('/links/'+a),'physics:filteredPairs'),a+' / '+b+' collision filter missing')
    for name,exp in c['gas_springs'].items():
        p=at('/joints/'+name)
        for usd,key in [('stiffness','stiffness_n_m'),('damping','damping_n_s_m'),('targetPosition','target_position_m')]:
            near(value(p,'drive:linear:physics:'+usd),exp[key],name+' gas spring '+key)
    for name,effort in zip(c['actuated_joint_names'],c['effort_limits_nm']):
        near(value(at('/joints/'+name),'drive:angular:physics:maxForce'),effort,name+' effort limit')
    if errors:raise RuntimeError('Unsafe robot import; training must not start:\n- '+'\n- '.join(errors))
    return {'status':'PASS_STATIC_ONLY','bodies':len(actual_bodies),'joints':len(c['joints']),'closures':6,'mimics':4,
        'hifi_visuals':visuals,'collision_primitives':colliders,'physx_schema_registration_checked':require_physx}

def audit_runtime_parameters(robot):
    """Read values back from PhysX after actuator initialization, before randomization."""
    import torch
    c=CONTRACT;view=robot.root_physx_view;errors=[]
    def compare(label,actual,expected,atol=1e-6):
        # [workspace patch 2026-09-10] Isaac Lab 6.x returns numpy arrays from the
        # root_physx_view getters, so `actual.dtype` was a numpy/python type and
        # `torch.as_tensor(..., dtype=...)` raised.  Normalise to torch first.
        actual=torch.as_tensor(actual,device=robot.device,dtype=torch.float32)
        expected=torch.as_tensor(np.asarray(expected,dtype=np.float32),device=actual.device,dtype=actual.dtype)
        if not torch.isfinite(actual).all() or not torch.allclose(actual,expected.expand_as(actual),rtol=2e-4,atol=atol):
            errors.append(label+' changed in PhysX initialization')
    compare('body masses',view.get_masses(),[c['bodies'][n]['mass_kg'] for n in robot.body_names])
    compare('armatures',view.get_dof_armatures(),[c['joints'][n]['armature'] for n in robot.joint_names],1e-8)
    compare('damping',view.get_dof_dampings(),[c['joints'][n]['damping_si'] for n in robot.joint_names])
    compare('stiffness',view.get_dof_stiffnesses(),[c['gas_springs'].get(n,{}).get('stiffness_n_m',0.) for n in robot.joint_names])
    effort=view.get_dof_max_forces();limits=view.get_dof_limits()
    for name,limit in zip(c['actuated_joint_names'],c['effort_limits_nm']):
        compare(name+' effort limit',effort[:,robot.joint_names.index(name)],limit)
    for name,p in c['joints'].items():
        if p['limits_si'] is not None:compare(name+' position limits',limits[:,robot.joint_names.index(name)],p['limits_si'])
    if errors:raise RuntimeError('PhysX parameter acceptance failed:\n- '+'\n- '.join(errors))
    return {'status':'PASS_RUNTIME_PARAMETERS','scope':'Unrandomized initialization, read back through PhysX tensor view'}

class RuntimeGuard:
    """Checks actual body poses/velocities, not merely authored USD declarations."""
    def __init__(self,robot,closure_tolerance=.002,mimic_tolerance=.01):
        import torch
        self.torch=torch;self.robot=robot;self.c=CONTRACT;self.closure_tolerance=closure_tolerance;self.mimic_tolerance=mimic_tolerance
        if set(self.c['joints'])!=set(robot.joint_names):raise RuntimeError('Articulation runtime joint set differs from contract')
        missing=set(self.c['bodies'])-set(robot.body_names)
        if missing:raise RuntimeError('Runtime is missing bodies: '+str(sorted(missing)))
        self.pairs=[]
        for name,v in self.c['closures'].items():
            self.pairs.append((name,robot.body_names.index(v['body0']),robot.body_names.index(v['body1']),
                torch.tensor(v['anchor0_m'],device=robot.device),torch.tensor(v['anchor1_m'],device=robot.device)))
        # [workspace patch 2026-09-10] Keep (mimic, reference) index pairs.  The relation
        # PhysX actually enforces on this plant is readout-equal (the MJCF equality is
        # polycoef="0 1 0 0 0"); the authored gearing=-1 lives in PhysX's internal joint
        # convention, and probe_mimic.py verifies the links stay parallel under load.
        self.mimics=[(robot.joint_names.index(a),robot.joint_names.index(v['reference_joint'])) for a,v in self.c['mimics'].items()]
        self.max_closure=0.;self.max_mimic=0.
    def check(self):
        t=self.torch;r=self.robot
        pos=r.data.body_pos_w;quat=r.data.body_quat_w
        def rotate(q,v):
            # [workspace patch 2026-09-10] Isaac Lab 3.0/6.x stores quaternions as
            # (x, y, z, w) with identity [0, 0, 0, 1], while 2.x used (w, x, y, z).
            # Hard-coding the 2.x order turned every identity quaternion into a 180 deg
            # rotation and reported a phantom 0.36 m closure error.  Delegate to the
            # installed Isaac Lab maths so the guard tracks the engine convention.
            try:
                from isaaclab.utils.math import quat_apply
            except Exception:
                v=v.expand(q.shape[0],3);u=q[:,1:];uv=t.cross(u,v,dim=-1)
                return v+2*(q[:,:1]*uv+t.cross(u,uv,dim=-1))
            return quat_apply(q,v.expand(q.shape[0],3))
        for x in [pos,quat,r.data.joint_pos,r.data.joint_vel]:
            if not t.isfinite(x).all():raise FloatingPointError('Non-finite PhysX state')
        if (r.data.joint_vel.abs()>1000).any():raise FloatingPointError('PhysX generalized speed exceeds acceptance envelope')
        for name,a,b,pa,pb in self.pairs:
            err=(pos[:,a]+rotate(quat[:,a],pa)-pos[:,b]-rotate(quat[:,b],pb)).norm(dim=-1).max().item()
            self.max_closure=max(self.max_closure,err)
            if err>self.closure_tolerance:raise RuntimeError(f'{name} separated by {err:.6g} m; constraint missing or unstable')
        for a,b in self.mimics:
            # [workspace patch 2026-09-10] MJCF closes the sprockets with polycoef="0 1 0 0 0"
            # and PhysX reproduces that readout, so the delivery's |q_mimic - q_ref| check is the
            # right one; comparing against the authored gearing=-1 fails a healthy plant at 2*|q|.
            err=(r.data.joint_pos[:,a]-r.data.joint_pos[:,b]).abs().max().item();self.max_mimic=max(self.max_mimic,err)
            if err>self.mimic_tolerance:raise RuntimeError(f'Chain coupling failed: {r.joint_names[a]}, {err:.6g} rad')
        # The knee bounds include a two-degree reserve inside the CAD-safe range.
        for name in ['left_knee','right_knee']:
            lo,hi=self.c['joints'][name]['limits_si'];q=r.data.joint_pos[:,r.joint_names.index(name)]
            if ((q<lo-.03)|(q>hi+.03)).any():raise RuntimeError(name+' consumed the stop safety reserve')
        # [handoff 2026-09-12 §1.5] The CAD stop constrains `crank - hip`, NOT the individual hip,
        # crank or knee joints: a policy can hold every joint inside its own range and still drive
        # the couple past the stop.  Check the couple directly, every step.
        stop=self.c.get('mechanical_stop',{}).get('input_difference_rad',-1.0863195404360622)
        train=self.c.get('training_window',{}).get('input_difference_min_rad',-1.0843)
        for side in ('left','right'):
            i=r.joint_names.index(side+'_crank');j=r.joint_names.index(side+'_hip')
            diff=(r.data.joint_pos[:,i]-r.data.joint_pos[:,j])
            worst=float(diff.min().item());self.min_difference=min(getattr(self,'min_difference',0.),worst)
            self.max_training_excess=max(getattr(self,'max_training_excess',0.),train-worst)
            # 1e-6 rad tolerance: the clamp writes crank = hip + bound in float32, so the state
            # sits ON the bound to ~3e-8 rad.  Physical excursion is reported separately.
            if worst<stop-1e-6:
                raise RuntimeError('%s input_difference %.9f is BELOW the mechanical stop %.9f'
                                   %(side,worst,stop))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('usd',nargs='?',default=str(HERE/'robot.usd'));ap.add_argument('--root',default='/Robot');ap.add_argument('--require-physx',action='store_true')
    args=ap.parse_args();print(json.dumps(audit_stage(Usd.Stage.Open(args.usd),args.root,args.require_physx),indent=2))
