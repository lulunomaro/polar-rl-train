"""Read-only USD physics inventory. Does not run PhysX or certify RL readiness."""
from pathlib import Path
import argparse,json,hashlib,math,collections
import numpy as np
from pxr import Usd,UsdGeom,UsdPhysics,Gf

def serial(x):
 if x is None or isinstance(x,(str,bool,int)):return x
 if isinstance(x,float):return x if math.isfinite(x) else str(x)
 if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
 if hasattr(x,'GetReal'):return [float(x.GetReal()),*[float(v) for v in x.GetImaginary()]]
 try:return [serial(v) for v in x]
 except TypeError:return str(x)
def rot(q):
 if q is None:return np.eye(3)
 w,x,y,z=serial(q);return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def attrs(p):
 out={}
 for a in p.GetAttributes():
  n=a.GetName()
  if a.HasAuthoredValueOpinion() and (n.startswith(('physics:','physx','drive:','limit:','state:'))):out[n]={'value':serial(a.Get()),'type':str(a.GetTypeName())}
 return out

def inspect(path):
 stage=Usd.Stage.Open(str(path));assert stage
 prims=list(Usd.PrimRange(stage.GetPseudoRoot(),Usd.TraverseInstanceProxies()))
 bodies=[p for p in prims if p.HasAPI(UsdPhysics.RigidBodyAPI)];joints=[p for p in prims if p.IsA(UsdPhysics.Joint)];colliders=[p for p in prims if p.HasAPI(UsdPhysics.CollisionAPI)]
 cache=UsdGeom.XformCache();bodypaths={str(p.GetPath()):p for p in bodies};brows=[];errors=[]
 for p in bodies:
  m=UsdPhysics.MassAPI(p);mass=m.GetMassAttr().Get();diag=m.GetDiagonalInertiaAttr().Get();q=m.GetPrincipalAxesAttr().Get();tensor=rot(q)@np.diag(diag)@rot(q).T if diag is not None else None
  row={'name':p.GetName(),'path':str(p.GetPath()),'mass':serial(mass),'com':serial(m.GetCenterOfMassAttr().Get()),'diagonal_inertia':serial(diag),'principal_axes_wxyz':serial(q),'inertia_tensor_body':serial(tensor),'world_transform_row':serial(cache.GetLocalToWorldTransform(p)),'attrs':attrs(p),'schemas':list(p.GetAppliedSchemas()),'raw_api_schemas':str(p.GetMetadata('apiSchemas'))}
  if mass is None or not np.isfinite(mass) or mass<=0:errors.append(p.GetName()+':invalid_or_missing_mass')
  if tensor is not None:
   eig=np.linalg.eigvalsh(tensor);row['inertia_eigenvalues']=eig.tolist();row['inertia_positive']=bool(np.all(np.isfinite(eig)) and np.all(eig>0))
   if not row['inertia_positive']:errors.append(p.GetName()+':nonpositive_or_nonfinite_explicit_inertia')
  brows.append(row)
 jrows=[]
 for p in joints:
  j=UsdPhysics.Joint(p);ends=[]
  for side in (0,1):
   targets=getattr(j,f'GetBody{side}Rel')().GetTargets();target=str(targets[0]) if targets else None;pos=getattr(j,f'GetLocalPos{side}Attr')().Get();q=getattr(j,f'GetLocalRot{side}Attr')().Get();world=None
   if target and pos is not None:
    owner=stage.GetPrimAtPath(target)
    if owner:world=serial(cache.GetLocalToWorldTransform(owner).Transform(Gf.Vec3d(*pos)))
   ends.append({'body':target,'local_pos':serial(pos),'local_rot':serial(q),'anchor_world':world})
  gap=float(np.linalg.norm(np.array(ends[0]['anchor_world'])-np.array(ends[1]['anchor_world']))) if all(e['anchor_world'] is not None for e in ends) else None
  jrows.append({'name':p.GetName(),'path':str(p.GetPath()),'type':p.GetTypeName(),'body0':ends[0],'body1':ends[1],'home_anchor_gap_m':gap,'exclude_from_articulation':j.GetExcludeFromArticulationAttr().Get(),'attrs':attrs(p),'schemas':list(p.GetAppliedSchemas()),'raw_api_schemas':str(p.GetMetadata('apiSchemas'))})
 crows=[]
 for p in colliders:
  owner=p
  while owner and str(owner.GetPath()) not in bodypaths:owner=owner.GetParent()
  rels={r.GetName():[str(t) for t in r.GetTargets()] for r in p.GetRelationships() if 'material' in r.GetName() or 'filter' in r.GetName()}
  crows.append({'path':str(p.GetPath()),'type':p.GetTypeName(),'body':owner.GetName() if owner else None,'attrs':attrs(p),'bindings_and_filters':rels})
 arows=[{'path':str(p.GetPath()),'attrs':attrs(p),'schemas':list(p.GetAppliedSchemas()),'raw_api_schemas':str(p.GetMetadata('apiSchemas'))} for p in prims if p.HasAPI(UsdPhysics.ArticulationRootAPI)]
 materials=[{'path':str(p.GetPath()),'attrs':attrs(p)} for p in prims if p.HasAPI(UsdPhysics.MaterialAPI)]
 layerrows=[]
 for l in stage.GetUsedLayers():
  lp=Path(l.realPath) if l.realPath else None;layerrows.append({'identifier':l.identifier,'real_path':l.realPath,'exists':bool(lp and lp.is_file()),'bytes':lp.stat().st_size if lp and lp.is_file() else None,'sha256':hashlib.sha256(lp.read_bytes()).hexdigest() if lp and lp.is_file() else None})
 return {'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'usd_version':Usd.GetVersion(),'default_prim':str(stage.GetDefaultPrim().GetPath()),'meters_per_unit':UsdGeom.GetStageMetersPerUnit(stage),'kilograms_per_unit':UsdPhysics.GetStageKilogramsPerUnit(stage),'up_axis':UsdGeom.GetStageUpAxis(stage),'root_layer_custom_data':serial(stage.GetRootLayer().customLayerData),'counts':{'rigid_bodies':len(bodies),'joints':len(joints),'colliders':len(colliders),'articulation_roots':len(arows),'physics_materials':len(materials)},'joint_types':dict(collections.Counter(p.GetTypeName() for p in joints)),'collider_types':dict(collections.Counter(p.GetTypeName() for p in colliders)),'nominal_mass_sum_kg':sum(b['mass'] for b in brows if isinstance(b['mass'],(int,float))),'body_property_errors':errors,'bodies':brows,'joints':jrows,'colliders':crows,'articulations':arows,'physics_materials':materials,'layers':layerrows,'runtime_verified':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('usd',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists(),'Do not overwrite an earlier audit';data=inspect(a.usd.resolve());a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in data.items() if k not in ['bodies','joints','colliders']},ensure_ascii=False,indent=2));print('BODY_SUMMARY',json.dumps([{'name':b['name'],'mass':b['mass'],'inertia_positive':b.get('inertia_positive')} for b in data['bodies']],ensure_ascii=False));print('JOINT_SUMMARY',json.dumps([{'name':j['name'],'type':j['type'],'excluded':j['exclude_from_articulation'],'home_anchor_gap_m':j['home_anchor_gap_m'],'armature':j['attrs'].get('physxJoint:armature'),'friction':j['attrs'].get('physxJoint:jointFriction')} for j in data['joints']],ensure_ascii=False))
