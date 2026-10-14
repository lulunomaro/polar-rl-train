"""Synthetic API-shape/path/strict-negative tests, no actual Kit or PhysX load."""
from pathlib import Path
import ast,hashlib,json,time,sys,types
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'payload';out=R/'SCENE_QUERY_V4_SYNTHETIC_CPU_FIXTURE_PASSED.json';assert not out.exists()
source=P/'retention_native_witness_v4.py';fn=next(x for x in ast.parse(source.read_text(encoding='utf8')).body if isinstance(x,ast.FunctionDef) and x.name=='plane_query_actual')
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
  return len(hits)
physx=types.ModuleType('omni.physx');physx.get_physx_scene_query_interface=lambda:Query();sys.modules['omni.physx']=physx
robot=types.SimpleNamespace(data=types.SimpleNamespace(root_pos_w=np.zeros((1,3),dtype=np.float32)))
class EScene:
 def __getitem__(self,k):return robot
e=types.SimpleNamespace(scene=EScene(),cfg=types.SimpleNamespace(sim=types.SimpleNamespace(physics_prim_path='/physicsScene',enable_scene_query_support=True)))
context={};scope=dict(Path=Path,json=json,hashlib=hashlib,np=np,cpu=lambda x:x.copy(),CONTEXT=context)
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(source),'exec'),scope)
flag=True;query_calls=0;results=[]
fixtures=R/'SCENE_QUERY_V4_CPU_SYNTHETIC_ONLY';assert not fixtures.exists();fixtures.mkdir()
for name,collision,height,should_pass in [('actual_child_path','/World/ground/geometry/mesh/physxShape',0.,True),('unique_Plane_ancestor','/World/ground',0.,True),('empty_actual_hit_set',None,0.,False),('actual_height_outside_original_bound','/World/ground/geometry/mesh',.002,False)]:
 folder=fixtures/name;folder.mkdir();context['output_dir']=str(folder)
 hits=[] if collision is None else [dict(collision='/World/envs/env_0/Robot/links/chassis',position=(0.,0.,.25),normal=(0.,0.,1.),distance=9.75),dict(collision=collision,position=(0.,0.,height),normal=(0.,0.,1.),distance=10.-height)]
 passed=False;error=None
 try:
  v=scope['plane_query_actual'](e,'first_physics');passed=True
  assert v['query_rows'][0]['resolved_plane_path']==plane.path and v['query_rows'][0]['hit']['collision']==collision
 except AssertionError as exc:error=str(exc)
 assert passed==should_pass,(name,passed,error)
 receipt=folder/'QUERY_first_physics_ALLHITS_ACTUAL.json';assert receipt.exists()
 saved=json.loads(receipt.read_bytes());assert saved['all_rays'][0]['all_reported_hits']==json.loads(json.dumps(hits))
 assert saved.get('complete_all_envs',False)==should_pass
 results.append(dict(name=name,synthetic_pass=passed,expected_pass=should_pass,original_rejection=error,all_hits_persisted_before_rejection=True,receipt_path=str(receipt),receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest()))
flag=False;folder=fixtures/'disabled_USD_query_flag';folder.mkdir();context['output_dir']=str(folder);before=query_calls
try:scope['plane_query_actual'](e,'first_physics');raise RuntimeError('Disabled USD flag incorrectly accepted')
except AssertionError as exc:disabled_error=str(exc)
assert query_calls==before
report=dict(epoch=time.time(),passed_CPU_synthetic_only=True,actual_backend_PASS_claimed=False,no_GPU_no_SSH_no_Kit_no_PhysX=True,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),actual_CPU_fixture_queries=query_calls,fixtures=results,disabled_scene_query_support_rejected_before_query=disabled_error,original1e6_plane_bound_unchanged=True,no_ideal_ground_fallback=True,no_physics_step_cache_forward_RNG=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
