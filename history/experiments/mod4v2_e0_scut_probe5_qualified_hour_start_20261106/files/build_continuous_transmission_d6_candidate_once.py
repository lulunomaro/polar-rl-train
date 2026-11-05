"""Build a reversible orientation-only regular-closure candidate, not native acceptance.

Official USD D6: three linear axes free; three angular axes locked by low>high.
Eight existing revolute coordinates remain unlimited. The four extra constraints
replace unsupported infinite-follower PhysX mimic on the neutral planar branch.
"""
from pathlib import Path
import copy,hashlib,json,math,shutil
from pxr import Usd,UsdGeom,UsdPhysics,Gf,Sdf
D=Path(__file__).resolve().parent;P=D.parent/'mod4v2_p0_mechanical_limits_20261105';src=P/'candidates/HW300N60_PHYSX_REPR_V2/package';candidate=P/'candidates/HW300N60_CONTINUOUS_D6_V3';dst=candidate/'package';receipt=D/'CONTINUOUS_D6_BUILD_RECEIPT_V1.json'
assert not candidate.exists()and not receipt.exists()
def H(raw):return hashlib.sha256(raw).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf8')
old_contract=(src/'assets/import_contract.json').read_bytes();contract=json.loads(old_contract);req=json.loads((src/'runtime_requirements.json').read_bytes());assert H(old_contract)=='5cf79932fb1f11edebcfa7e35ff63ed658bbfdf1dd56706ad201b3c4fd3141a1'
raw=(src/'assets/robot.usd').read_bytes();assert H(raw)=='47be6619a1ec78e7c1514aab673996f545feedb24fda05da3f359d69f4a4be7f'
original=Usd.Stage.Open(str(src/'assets/robot.usd'),load=Usd.Stage.LoadNone);layer=Sdf.Layer.CreateAnonymous('continuous_d6.usda');layer.TransferContent(original.GetRootLayer());stage=Usd.Stage.Open(layer,load=Usd.Stage.LoadNone);changes=[]
def only_non_mimic(op):
 n=Sdf.TokenListOp()
 if op.isExplicit:n.explicitItems=[x for x in op.explicitItems if not x.startswith('PhysxMimicJointAPI')]
 else:
  for key in('prependedItems','appendedItems','deletedItems','orderedItems'):
   setattr(n,key,[x for x in getattr(op,key)if not x.startswith('PhysxMimicJointAPI')])
 return n
for follower,relation in contract['mimics'].items():
 ref=relation['reference_joint'];fp=stage.GetPrimAtPath('/Robot/joints/'+follower);rp=stage.GetPrimAtPath('/Robot/joints/'+ref);assert fp and rp and relation['gearing']==-1.0 and relation['offset']==0.0
 fj=UsdPhysics.RevoluteJoint(fp);rj=UsdPhysics.RevoluteJoint(rp);assert math.isinf(fj.GetLowerLimitAttr().Get())and math.isinf(fj.GetUpperLimitAttr().Get())and math.isinf(rj.GetLowerLimitAttr().Get())and math.isinf(rj.GetUpperLimitAttr().Get())
 assert fj.GetAxisAttr().Get()==rj.GetAxisAttr().Get()=='X'
 assert fj.GetBody0Rel().GetTargets()==rj.GetBody0Rel().GetTargets(), 'Shared chassis hinge ancestry required'
 body0=fj.GetBody1Rel().GetTargets()[0];body1=rj.GetBody1Rel().GetTargets()[0]
 q0=UsdGeom.Xformable(stage.GetPrimAtPath(body0)).ComputeLocalToWorldTransform(Usd.TimeCode.Default()).ExtractRotationQuat().GetNormalized();q1=UsdGeom.Xformable(stage.GetPrimAtPath(body1)).ComputeLocalToWorldTransform(Usd.TimeCode.Default()).ExtractRotationQuat().GetNormalized();local1=(q1.GetInverse()*q0).GetNormalized()
 # Check axis collinearity in chassis coordinates, not an assumed gearing sign.
 l0f=fj.GetLocalRot0Attr().Get();l0r=rj.GetLocalRot0Attr().Get();vf=Gf.Rotation(Gf.Quatd(l0f)).TransformDir(Gf.Vec3d(1,0,0));vr=Gf.Rotation(Gf.Quatd(l0r)).TransformDir(Gf.Vec3d(1,0,0));assert abs(abs(Gf.Dot(vf,vr))-1)<1e-7
 op=fp.GetMetadata('apiSchemas');assert op is not None;fp.SetMetadata('apiSchemas',only_non_mimic(op))
 props=[x.GetName()for x in fp.GetProperties()if x.GetName().startswith('physxMimicJoint:')];assert props
 for name in props:assert fp.RemoveProperty(name)
 path='/Robot/joints/native_parallel_'+follower;j=UsdPhysics.Joint.Define(stage,path);j.CreateBody0Rel().SetTargets([body0]);j.CreateBody1Rel().SetTargets([body1]);j.CreateLocalPos0Attr().Set(Gf.Vec3f(0));j.CreateLocalPos1Attr().Set(Gf.Vec3f(0));j.CreateLocalRot0Attr().Set(Gf.Quatf(1));j.CreateLocalRot1Attr().Set(Gf.Quatf(local1));j.CreateExcludeFromArticulationAttr().Set(True);j.CreateJointEnabledAttr().Set(True);j.CreateCollisionEnabledAttr().Set(True)
 for axis in('rotX','rotY','rotZ'):
  limit=UsdPhysics.LimitAPI.Apply(j.GetPrim(),axis);limit.CreateLowAttr().Set(1.0);limit.CreateHighAttr().Set(-1.0)
 changes.append(dict(follower_joint=follower,reference_joint=ref,body0=str(body0),body1=str(body1),backend_joint=path,local_rot0_wxyz=[1.,0.,0.,0.],local_rot1_wxyz=[float(local1.GetReal())]+[float(x)for x in local1.GetImaginary()],three_linear_axes='FREE: no LimitAPI',three_angular_axes='LOCKED: low1 high-1 per USD D6 lock convention',exclude_from_articulation=True,collision_enabled=True,removed_mimic_property_names=props))
# Reverse only the declared four replacements and compare the complete layer.
check=Sdf.Layer.CreateAnonymous('reverse.usda');check.TransferContent(layer);back=Usd.Stage.Open(check)
for row in changes:
 back.RemovePrim(row['backend_joint']);path='/Robot/joints/'+row['follower_joint'];back.RemovePrim(path);assert Sdf.CopySpec(original.GetRootLayer(),path,check,path)
assert check.ExportToString()==original.GetRootLayer().ExportToString(), 'Undeclared USD content changed'
shutil.copytree(src,dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'));assert stage.GetRootLayer().Export(str(dst/'assets/robot.usd'))
newmeta=dict(schema='mod4v2.continuous_transmission.regular_D6.v1',implementation='HW300N60_CONTINUOUS_D6_V3',source_USD_sha256=H(raw),replacement_scope='Four unsupported unlimited-follower PhysX mimic APIs replaced by orientation-only excluded regular D6 closures',hardware_revolute_axes_limits_changed=False,added_backend_constraints=changes,logical_hardware_joint_table_unchanged=True,backend_joint_count=len(contract['joints'])+4,physical_bodies_or_mass_or_collision_shapes_changed=False,neutral_planar_branch_equivalence='All eight hinges share chassis/coplanar axis; original canonical relation follower=reference. Neutral-aligned angular closure imposes difference 2*pi*k; continuous neutral-connected lift fixes k=0. Two other angular rows already follow existing hinge axes; translations free. Not global arbitrary independent winding or 3D collision proof.',SDK_GPU_dynamics_verified=False,original_mimic_predicate_and_threshold_unchanged=True,official_API='https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/dev_guide/rigid_bodies_articulations/joints.html#d6-joint',known_numerical_limitation='Excluded D6 articulation loops require actual native dynamic validation; not proven stable by this build')
contract['native_transmission']=newmeta;contract['runtime_tested']=False
# Keep logical 36-joint/4-mimic contract semantics unchanged for original observers.
for key in('bodies','joints','closures','mimics','filters','gas_springs','mechanical_limits_v2','hardware_configuration'):
 assert contract[key]==json.loads(old_contract)[key],key
dump(dst/'assets/import_contract.json',contract);req['native_transmission']=newmeta;req['target_physx_verified']=False;req['runtime_validation_status']='PENDING_N16_NATIVE_D6_TRANSMISSION_DIAGNOSTIC'
for rel in req['native_implementation']['bindings_sha256']:
 req['native_implementation']['bindings_sha256'][rel]=H((dst/rel).read_bytes())
dump(dst/'runtime_requirements.json',req)
assert (dst/'runtime_adapter_v2.py').read_bytes()==(src/'runtime_adapter_v2.py').read_bytes()
assert (dst/'mjcf/scene.xml').read_bytes()==(src/'mjcf/scene.xml').read_bytes(), 'Existing MJCF equality backend intentionally unchanged'
r=dict(kind='CONTINUOUS_D6_STATIC_CANDIDATE_NOT_NATIVE_ACCEPTANCE',package=str(dst),source_package=str(src),changes=changes,hardware_and_logical_contract_unchanged=True,full_USD_reverse_comparison=True,added_backend_regular_closures=4,active_and_follower_continuous_axes=8,body_count=len(contract['bodies']),USD_sha256=H((dst/'assets/robot.usd').read_bytes()),contract_sha256=H((dst/'assets/import_contract.json').read_bytes()),runtime_sha256=H((dst/'runtime_adapter_v2.py').read_bytes()),requirements_sha256=H((dst/'runtime_requirements.json').read_bytes()),SDK_or_simulation_or_training_started=False,force_curve_calibrated=False)
dump(receipt,r);print(json.dumps(r,indent=2))
