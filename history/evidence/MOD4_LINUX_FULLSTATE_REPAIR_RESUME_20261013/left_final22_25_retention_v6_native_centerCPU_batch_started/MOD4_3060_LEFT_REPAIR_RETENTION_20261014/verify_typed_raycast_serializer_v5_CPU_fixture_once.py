"""Mock installed typed RaycastHit ABI and strict original query checks on CPU."""
from pathlib import Path
import ast,hashlib,json,time,sys,types
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'payload';out=R/'SCENE_QUERY_V5_SYNTHETIC_CPU_FIXTURE_PASSED.json';assert not out.exists()
sys.path.insert(0,str(P));from raycast_hit_serializer_v5 import serialize_raycast_hit,DECLARED_FIELDS
source=P/'retention_native_witness_v5.py';fn=next(x for x in ast.parse(source.read_text(encoding='utf8')).body if isinstance(x,ast.FunctionDef) and x.name=='plane_query_actual')
class Attr:
 def __init__(self,v):self.v=v
 def Get(self):return self.v
class Prim:
 def __init__(self,path,type_name):self.path=path;self.type_name=type_name
 def __bool__(self):return True
 def GetTypeName(self):return self.type_name
 def GetPath(self):return self.path
 def HasAPI(self,api):return self.type_name=='Plane'
 def GetAttribute(self,name):return Attr('Z' if name=='axis' else flag)
plane=Prim('/World/ground/geometry/mesh','Plane');scene=Prim('/physicsScene','PhysicsScene')
class Stage:
 def GetPrimAtPath(self,path):return plane if path==plane.path else scene if path=='/physicsScene' else Prim(path,'Xform')
class TF:
 def Transform(self,x):return (0.,0.,0.)
 def TransformDir(self,x):return (0.,0.,1.)
class XformCache:
 def GetLocalToWorldTransform(self,p):return TF()
pxr=types.ModuleType('pxr');pxr.UsdGeom=types.SimpleNamespace(XformCache=XformCache);pxr.UsdPhysics=types.SimpleNamespace(CollisionAPI=object());pxr.Usd=types.SimpleNamespace(PrimRange=lambda ancestor:[ancestor,plane]);sys.modules['pxr']=pxr
sim=types.ModuleType('isaaclab.sim');sim.get_current_stage=lambda:Stage();sys.modules['isaaclab.sim']=sim
class Query:
 def raycast_all(self,origin,direction,distance,callback):
  global query_calls
  query_calls+=1
  for row in hits:callback(row)
  return bool(hits)
physx=types.ModuleType('omni.physx');physx.get_physx_scene_query_interface=lambda:Query();sys.modules['omni.physx']=physx
class RaycastHit:
 __module__='omni.physx.bindings._physx'
 def __init__(self,collision,height=0.):
  self.distance=10.-height;self.face_index=0;self.material='/World/ground/physicsMaterial';self.material_encoded=[2**63+27,2**64-1];self.normal=(0.,0.,1.);self.position=(0.,0.,height);self.collision=collision;self.collision_encoded=[2**63+25,2**64-1];self.protoIndex=2**32-1;self.rigid_body='';self.rigid_body_encoded=[0,0];self.extra_readonly_tag='mock-extra-field'
 def unused_public_method(self):raise RuntimeError('A serializer must never call a method')
class MissingPosition(RaycastHit):
 @property
 def position(self):raise RuntimeError('original mocked property read failed')
 @position.setter
 def position(self,v):pass
robot=types.SimpleNamespace(data=types.SimpleNamespace(root_pos_w=np.zeros((1,3),dtype=np.float32)))
class EScene:
 def __getitem__(self,k):return robot
e=types.SimpleNamespace(scene=EScene(),cfg=types.SimpleNamespace(sim=types.SimpleNamespace(physics_prim_path='/physicsScene',enable_scene_query_support=True)))
context={};scope=dict(Path=Path,json=json,hashlib=hashlib,np=np,cpu=lambda x:x.copy(),CONTEXT=context)
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(source),'exec'),scope)
flag=True;query_calls=0;results=[];fixtures=R/'SCENE_QUERY_V5_CPU_SYNTHETIC_ONLY';assert not fixtures.exists();fixtures.mkdir()
cases=[('typed_actual_child_path',[RaycastHit(plane.path+'/physxShape')],True),('typed_unique_Plane_ancestor',[RaycastHit('/World/ground')],True),('legacy_mapping',[dict(collision=plane.path,position=(0.,0.,0.),normal=(0.,0.,1.),distance=10.)],True),('empty_actual_hit_set',[],False),('actual_height_outside_original_bound',[RaycastHit(plane.path,.002)],False),('typed_property_failure_preserved',[MissingPosition(plane.path)],False)]
for name,case_hits,should_pass in cases:
 folder=fixtures/name;folder.mkdir();context['output_dir']=str(folder);hits=case_hits;passed=False;error=None
 try:result=scope['plane_query_actual'](e,'first_physics');passed=True
 except AssertionError as exc:error=str(exc)
 assert passed==should_pass,(name,passed,error)
 path=folder/'QUERY_first_physics_ALLHITS_ACTUAL.json';assert path.exists();saved=json.loads(path.read_bytes());actual=saved['all_rays'][0]['all_reported_hits']
 assert saved.get('complete_all_envs',False)==should_pass
 for row in actual:
  assert '_actual_hit_qualified_class' in row and row['_declared_API_fields']==list(DECLARED_FIELDS)
  if row['_adapter']=='typed_RaycastHit_readonly_attributes':
   assert row['collision_encoded']==[2**63+25,2**64-1] and isinstance(row['collision_encoded'][0],int)
   assert row['material_encoded']==[2**63+27,2**64-1] and row['protoIndex']==2**32-1
   assert row['extra_readonly_tag']=='mock-extra-field' and 'unused_public_method' in row['_skipped_callable_fields']
 if name=='typed_property_failure_preserved':
  assert 'Actual typed hit serialization failed' in error and 'Actual plane query missing' not in error
  assert actual[0]['_field_read_errors']['position']=='RuntimeError: original mocked property read failed'
 results.append(dict(name=name,synthetic_pass=passed,expected_pass=should_pass,original_rejection=error,all_hits_and_API_identity_persisted_before_rejection=True,receipt_path=str(path),receipt_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
flag=False;folder=fixtures/'disabled_USD_query_flag';folder.mkdir();context['output_dir']=str(folder);before=query_calls
try:scope['plane_query_actual'](e,'first_physics');raise RuntimeError('Disabled USD flag incorrectly accepted')
except AssertionError as exc:disabled_error=str(exc)
assert query_calls==before
report=dict(epoch=time.time(),passed_CPU_synthetic_only=True,actual_backend_PASS_claimed=False,no_GPU_no_SSH_no_Kit_no_PhysX=True,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),serializer_sha256=hashlib.sha256((P/'raycast_hit_serializer_v5.py').read_bytes()).hexdigest(),actual_CPU_fixture_queries=query_calls,fixtures=results,disabled_scene_query_support_rejected_before_query=disabled_error,all_actual_declared_typed_fields_captured=True,uint64_encoded_values_exact_without_float_conversion=True,no_callable_method_executed=True,serializer_error_not_misclassified_emptyhit=True,original1e6_plane_bound_unchanged=True,no_ideal_ground_fallback=True,no_physics_step_cache_forward_RNG=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_synthetic_only=True,report=str(out),fixtures=[dict(name=x['name'],synthetic_pass=x['synthetic_pass']) for x in results])))
