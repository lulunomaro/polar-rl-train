"""Author a closed-loop USD directly. Requires mujoco, numpy and usd-core.

No MJCF importer is involved. PhysX extension schemas are authored by their
published names; audit_import.py must be run inside Isaac before simulation.
"""
from pathlib import Path
import json, math, hashlib
import numpy as np
import mujoco
from pxr import Usd, UsdGeom, UsdPhysics, UsdShade, Sdf, Gf, Vt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'isaac';OUT.mkdir(exist_ok=True)
m=mujoco.MjModel.from_xml_path(str(ROOT/'scene.xml'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
vec=lambda x:Gf.Vec3f(*map(float,x))
qf=lambda q:Gf.Quatf(float(q[0]),vec(q[1:]))
def quat(R):
    q=np.zeros(4);mujoco.mju_mat2Quat(q,np.asarray(R,dtype=float).ravel());return q
def apply(prim,name):prim.AddAppliedSchema(name)
def attr(prim,name,value,typ=Sdf.ValueTypeNames.Float):prim.CreateAttribute(name,typ,custom=False).Set(value)
def transform(obj,p,q):
    obj.AddTranslateOp().Set(Gf.Vec3d(*map(float,p)))
    obj.AddOrientOp().Set(qf(q))

mesh_stage=Usd.Stage.CreateNew(str(OUT/'meshes.usdc'))
UsdGeom.SetStageUpAxis(mesh_stage,'Z');UsdGeom.SetStageMetersPerUnit(mesh_stage,1.)
mesh_root=UsdGeom.Scope.Define(mesh_stage,'/Meshes');mesh_stage.SetDefaultPrim(mesh_root.GetPrim())
for i in range(m.nmesh):
    mesh=UsdGeom.Mesh.Define(mesh_stage,f'/Meshes/m_{i:03}')
    va,fa=int(m.mesh_vertadr[i]),int(m.mesh_faceadr[i]);nv,nf=int(m.mesh_vertnum[i]),int(m.mesh_facenum[i])
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(m.mesh_vert[va:va+nv].astype(np.float32)))
    mesh.CreateFaceVertexCountsAttr(Vt.IntArray([3]*nf))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray.FromNumpy(m.mesh_face[fa:fa+nf].ravel().astype(np.int32)))
    mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True)
mesh_stage.GetRootLayer().Save()

stage=Usd.Stage.CreateNew(str(OUT/'robot.usd'))
UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.z);UsdGeom.SetStageMetersPerUnit(stage,1.)
UsdPhysics.SetStageKilogramsPerUnit(stage,1.)
robot=UsdGeom.Xform.Define(stage,'/Robot');stage.SetDefaultPrim(robot.GetPrim())
robot.GetPrim().SetCustomDataByKey('mod4:modelKind','closed_loop_hifi')
robot.GetPrim().SetCustomDataByKey('mod4:sourceSha256',hashlib.sha256((ROOT/'scene.xml').read_bytes()).hexdigest())
base=d.xpos[m.body('chassis').id].copy()
body_paths={i:f'/Robot/links/{m.body(i).name}' for i in range(1,m.nbody)}
contract={'format_version':1,'model_kind':'closed_loop_hifi','source_mjcf_sha256':hashlib.sha256((ROOT/'scene.xml').read_bytes()).hexdigest(),
    'bodies':{},'joints':{},'closures':{},'mimics':{},'filters':[],'geometry':{},
    'actuated_joint_names':[m.joint(int(j)).name for j in m.actuator_trnid[:,0]],
    'effort_limits_nm':m.actuator_ctrlrange[:,1].tolist(),'articulation_joint_count':m.nv-6,
    'mjcf_equality_rank_at_neutral':int(np.linalg.matrix_rank(d.efc_J.reshape(-1,m.nv)[:d.ne],tol=1e-8)),
    'independent_velocity_dofs':m.nv-int(np.linalg.matrix_rank(d.efc_J.reshape(-1,m.nv)[:d.ne],tol=1e-8)),'spawn_height_m':float(base[2]),'physics_dt_s':float(m.opt.timestep),
    'gas_springs':{},'visual_instance_count':0,'collision_primitive_count':0,
    'tendon_translation':'This MOD4 MJCF has no tendons. Identical knee, rocker and slide operating limits are authored in both formats.',
    'runtime_tested':False,'leg_motor':json.loads((ROOT/'model_parameters.json').read_text())['leg_motor'],
    'wheel_motor':json.loads((ROOT/'model_parameters.json').read_text())['wheel_motor']}

for i,path in body_paths.items():
    body=UsdGeom.Xform.Define(stage,path);prim=body.GetPrim()
    transform(body,d.xpos[i]-base,d.xquat[i])
    UsdPhysics.RigidBodyAPI.Apply(prim).CreateRigidBodyEnabledAttr(True)
    mass=UsdPhysics.MassAPI.Apply(prim);mass.CreateMassAttr(float(m.body_mass[i]))
    mass.CreateCenterOfMassAttr(vec(m.body_ipos[i]));mass.CreateDiagonalInertiaAttr(vec(m.body_inertia[i]));mass.CreatePrincipalAxesAttr(qf(m.body_iquat[i]))
    apply(prim,'PhysxRigidBodyAPI');attr(prim,'physxRigidBody:enableGyroscopicForces',True,Sdf.ValueTypeNames.Bool)
    # Explicitly disable PhysX's default body drag, as in SCUT's asset config.
    # Dissipation is already modeled at joints/contacts, not on every link's spin.
    attr(prim,'physxRigidBody:linearDamping',0.)
    attr(prim,'physxRigidBody:angularDamping',0.)
    attr(prim,'physxRigidBody:maxDepenetrationVelocity',1.)
    contract['bodies'][m.body(i).name]={'mass_kg':float(m.body_mass[i]),'com_m':m.body_ipos[i].tolist(),
        'diagonal_inertia_kg_m2':m.body_inertia[i].tolist(),'principal_axes_wxyz':m.body_iquat[i].tolist(),
        'neutral_position_m':(d.xpos[i]-base).tolist(),'neutral_quat_wxyz':d.xquat[i].tolist()}
chassis=stage.GetPrimAtPath(body_paths[m.body('chassis').id])
UsdPhysics.ArticulationRootAPI.Apply(chassis);apply(chassis,'PhysxArticulationAPI')
attr(chassis,'physxArticulation:enabledSelfCollisions',True,Sdf.ValueTypeNames.Bool)
attr(chassis,'physxArticulation:solverPositionIterationCount',32,Sdf.ValueTypeNames.Int)
attr(chassis,'physxArticulation:solverVelocityIterationCount',8,Sdf.ValueTypeNames.Int)

for g in range(m.ngeom):
    bid=int(m.geom_bodyid[g])
    if not bid:continue
    path=body_paths[bid]+'/'+m.geom(g).name
    typ=int(m.geom_type[g]);sz=m.geom_size[g]
    is_visual=not(m.geom_contype[g] or m.geom_conaffinity[g])
    contract['geometry'][m.geom(g).name]={'body':m.body(bid).name,'visual':is_visual,'type':typ,
        'size':sz.tolist(),'position_m':m.geom_pos[g].tolist(),'quat_wxyz':m.geom_quat[g].tolist()}
    if typ==mujoco.mjtGeom.mjGEOM_MESH:
        obj=UsdGeom.Mesh.Define(stage,path)
        obj.GetPrim().GetReferences().AddReference('meshes.usdc',f'/Meshes/m_{m.geom_dataid[g]:03}')
        obj.GetPrim().SetInstanceable(True)
    elif typ==mujoco.mjtGeom.mjGEOM_BOX:
        obj=UsdGeom.Cube.Define(stage,path);obj.CreateSizeAttr(2.)
    elif typ==mujoco.mjtGeom.mjGEOM_SPHERE:
        obj=UsdGeom.Sphere.Define(stage,path);obj.CreateRadiusAttr(float(sz[0]))
    elif typ in [mujoco.mjtGeom.mjGEOM_CAPSULE,mujoco.mjtGeom.mjGEOM_CYLINDER]:
        cls=UsdGeom.Capsule if typ==mujoco.mjtGeom.mjGEOM_CAPSULE else UsdGeom.Cylinder
        obj=cls.Define(stage,path);obj.CreateRadiusAttr(float(sz[0]));obj.CreateHeightAttr(float(2*sz[1]));obj.CreateAxisAttr('Z')
    else:raise ValueError((m.geom(g).name,typ))
    transform(obj,m.geom_pos[g],m.geom_quat[g])
    if typ==mujoco.mjtGeom.mjGEOM_BOX:obj.AddScaleOp().Set(vec(sz))
    if is_visual:
        rgba=m.mat_rgba[m.geom_matid[g]] if m.geom_matid[g]>=0 else m.geom_rgba[g]
        obj.CreateDisplayColorAttr([vec(rgba[:3])]);obj.CreateDisplayOpacityAttr([float(rgba[3])])
        contract['visual_instance_count']+=1
    else:
        prim=obj.GetPrim();UsdPhysics.CollisionAPI.Apply(prim)
        apply(prim,'PhysxCollisionAPI');attr(prim,'physxCollision:contactOffset',.001)
        attr(prim,'physxCollision:restOffset',0.)
        mat=UsdShade.Material.Define(stage,'/Robot/materials/contact_'+str(g))
        ph=UsdPhysics.MaterialAPI.Apply(mat.GetPrim())
        ph.CreateStaticFrictionAttr(float(m.geom_friction[g,0]));ph.CreateDynamicFrictionAttr(float(m.geom_friction[g,0]));ph.CreateRestitutionAttr(0.)
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(mat,materialPurpose='physics')
        obj.CreateVisibilityAttr('invisible');contract['collision_primitive_count']+=1

joint_paths={}
for j in range(1,m.njnt):
    name=m.joint(j).name;b=int(m.jnt_bodyid[j]);p=int(m.body_parentid[b]);adr=int(m.jnt_dofadr[j])
    path='/Robot/joints/'+name;joint_paths[name]=path
    slider=m.jnt_type[j]==mujoco.mjtJoint.mjJNT_SLIDE
    obj=(UsdPhysics.PrismaticJoint if slider else UsdPhysics.RevoluteJoint).Define(stage,path)
    obj.CreateAxisAttr('X');obj.CreateBody0Rel().SetTargets([body_paths[p]]);obj.CreateBody1Rel().SetTargets([body_paths[b]])
    # Identical world joint frames make all new-neutral coordinates zero.
    x=d.xaxis[j];y=np.array([0.,0.,1.])
    if abs(x@y)>.95:y=np.array([0.,1.,0.])
    y=y-x*(x@y);y/=np.linalg.norm(y);frame=np.column_stack((x,y,np.cross(x,y)))
    a=d.xanchor[j];Rp=d.xmat[p].reshape(3,3);Rb=d.xmat[b].reshape(3,3)
    pos0=Rp.T@(a-d.xpos[p]);pos1=Rb.T@(a-d.xpos[b]);rot0=quat(Rp.T@frame);rot1=quat(Rb.T@frame)
    obj.CreateLocalPos0Attr(vec(pos0));obj.CreateLocalPos1Attr(vec(pos1))
    obj.CreateLocalRot0Attr(qf(rot0));obj.CreateLocalRot1Attr(qf(rot1));obj.CreateCollisionEnabledAttr(False)
    limits=None
    if m.jnt_limited[j]:limits=m.jnt_range[j].copy()
    if limits is not None:
        scale=1 if slider else 180/math.pi
        obj.CreateLowerLimitAttr(float(limits[0]*scale));obj.CreateUpperLimitAttr(float(limits[1]*scale))
    prim=obj.GetPrim()
    # All tree joints are single-axis. Use the published 4.5/5.1-compatible
    # schema, rather than relying on newer per-axis schemas being registered.
    apply(prim,'PhysxJointAPI')
    attr(prim,'physxJoint:armature',float(m.dof_armature[adr]))
    attr(prim,'physxJoint:jointFriction',0.)
    attr(prim,'physxJoint:maxJointVelocity',1000.*(1 if slider else 180/math.pi))
    # Passive viscous damping is represented by a force drive, including on older Isaac builds.
    drive=UsdPhysics.DriveAPI.Apply(prim,'linear' if slider else 'angular')
    drive.CreateTypeAttr('force');drive.CreateStiffnessAttr(0.)
    drive.CreateDampingAttr(float(m.dof_damping[adr]*(1 if slider else math.pi/180)))
    drive.CreateTargetVelocityAttr(0.);drive.CreateMaxForceAttr(1e6)
    if m.jnt_stiffness[j] or name.endswith('_gas_slide'):
        target=float(m.qpos_spring[m.jnt_qposadr[j]])
        drive.CreateStiffnessAttr(float(m.jnt_stiffness[j]));drive.CreateTargetPositionAttr(target)
        contract['gas_springs'][name]={'target_position_m':target,'stiffness_n_m':float(m.jnt_stiffness[j]),'damping_n_s_m':float(m.dof_damping[adr])}
    if name in contract['actuated_joint_names']:
        k=contract['actuated_joint_names'].index(name);drive.CreateMaxForceAttr(float(contract['effort_limits_nm'][k]))
    contract['joints'][name]={'parent':m.body(p).name,'child':m.body(b).name,'type':'slide' if slider else 'hinge',
        'local_pos0':pos0.tolist(),'local_pos1':pos1.tolist(),'local_rot0':rot0.tolist(),'local_rot1':rot1.tolist(),
        'limits_si':None if limits is None else limits.tolist(),'armature':float(m.dof_armature[adr]),'damping_si':float(m.dof_damping[adr])}

for side in ['left','right']:
    for label,s1,s2 in [('proximal','proximal_a','proximal_b'),('distal','distal_a','distal_b'),('gas','gas_end','gas_mount')]:
        a=m.site(side+'_'+s1).id;b=m.site(side+'_'+s2).id
        name=side+'_'+label+'_closure';obj=UsdPhysics.SphericalJoint.Define(stage,'/Robot/closures/'+name)
        obj.CreateBody0Rel().SetTargets([body_paths[int(m.site_bodyid[a])]])
        obj.CreateBody1Rel().SetTargets([body_paths[int(m.site_bodyid[b])]])
        obj.CreateLocalPos0Attr(vec(m.site_pos[a]));obj.CreateLocalPos1Attr(vec(m.site_pos[b]))
        obj.CreateExcludeFromArticulationAttr(True);obj.CreateCollisionEnabledAttr(False)
        contract['closures'][name]={'body0':m.body(int(m.site_bodyid[a])).name,'body1':m.body(int(m.site_bodyid[b])).name,
            'anchor0_m':m.site_pos[a].tolist(),'anchor1_m':m.site_pos[b].tolist()}
    for follower,leader in [('drive_hip_spin','hip'),('drive_input_spin','crank')]:
        name=side+'_'+follower;ref=side+'_'+leader;prim=stage.GetPrimAtPath(joint_paths[name])
        apply(prim,'PhysxMimicJointAPI:rotX')
        attr(prim,'physxMimicJoint:rotX:gearing',-1.)
        attr(prim,'physxMimicJoint:rotX:offset',0.)
        attr(prim,'physxMimicJoint:rotX:referenceJointAxis','rotX',Sdf.ValueTypeNames.Token)
        prim.CreateRelationship('physxMimicJoint:rotX:referenceJoint',custom=False).SetTargets([joint_paths[ref]])
        contract['mimics'][name]={'reference_joint':ref,'gearing':-1.,'offset':0.}

import xml.etree.ElementTree as ET
for ex in ET.parse(ROOT/'scene.xml').getroot().findall('contact/exclude'):
    a,b=ex.get('body1'),ex.get('body2')
    prim=stage.GetPrimAtPath(body_paths[m.body(a).id]);api=UsdPhysics.FilteredPairsAPI.Apply(prim)
    api.CreateFilteredPairsRel().AddTarget(body_paths[m.body(b).id]);contract['filters'].append([a,b])

stage.GetRootLayer().Save()
(OUT/'import_contract.json').write_text(json.dumps(contract,indent=2),encoding='utf8')
print('USD authored:',len(contract['bodies']),'bodies,',len(contract['joints']),'tree joints,',len(contract['closures']),'external closures,',len(contract['mimics']),'mimics,',contract['visual_instance_count'],'visuals')
