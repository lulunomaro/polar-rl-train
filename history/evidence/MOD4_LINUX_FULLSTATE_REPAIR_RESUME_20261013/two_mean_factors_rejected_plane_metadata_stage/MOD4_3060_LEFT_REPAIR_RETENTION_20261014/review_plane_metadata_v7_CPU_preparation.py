"""CPU synthetic API and static scope checks; never starts the metadata worker."""
from pathlib import Path
import ast,copy,hashlib,json,random,sys,time
import numpy as np
D=Path(__file__).parent;P=D/'payload';sys.path.insert(0,str(P))
from retention_plane_metadata_v7 import query_positions_only,SDKCallAudit,SMALL_EVAL_CAPACITY
from represented_native_plane_CPU_component_v2 import SOURCE_COMMIT,source_sha_manifest,represented_plane_from_readonly_metadata


def main():
 out=D/'reports/PLANE_METADATA_V7_SYNTHETIC_CPU_FIXTURE_PASSED.json';assert not out.exists()
 source=json.loads((P/'FAILED_V6_FULL1500_FIRST_LAST_XY80_ACTUAL.json').read_bytes())
 metadata=dict(source_commit=SOURCE_COMMIT,source_file_sha256=source_sha_manifest(),approved_axis='Z',
     actual_USD_plane=dict(path='/World/ground/geometry/mesh',type='Plane',axis='Z',CollisionAPI=True,
                          RigidBodyAPI_ancestor_paths=[],world_position=[0,0,0],world_rotation_xyzw=[0,0,0,1]),
     actual_actor_getter=dict(path='/World/ground/geometry/mesh',ret_val=True,position=[0,0,0],rotation_xyzw=[0,0,0,1]))
 reference=represented_plane_from_readonly_metadata(metadata)
 class FakeRaycastHit:
  def __init__(self,x,y,z,normal,collision):
   self.distance=10-z;self.face_index=0;self.material='/World/ground/physicsMaterial'
   self.material_encoded=[195585,0];self.normal=normal;self.position=[x,y,z]
   self.collision=collision;self.collision_encoded=[195329,0];self.protoIndex=4294967295
   self.rigid_body='/World/ground/geometry/mesh';self.rigid_body_encoded=[195329,0]
 class FakeQuery:
  def __init__(self,error=0,collision='/World/ground/geometry/mesh'):self.calls=0;self.error=error;self.collision=collision
  def raycast_all(self,origin,direction,distance,callback):
   self.calls+=1;n=reference['represented_plane_normal'];x,y=origin[:2]
   z=-(n[0]*x+n[1]*y+reference['represented_plane_offset_d'])/n[2]+self.error
   assert callback(FakeRaycastHit(x,y,z,n,self.collision)) is True
   return True
 def resolver(h):
  if h['collision']=='/World/ground/geometry/mesh':return dict(resolved_plane_path=h['collision'],identity_resolution='CPU synthetic exact path')
 class FakeSDKBase:
  def reset(self):self.step();self.forward()
  def step(self):return None
  def forward(self):return None
  def render(self):return None
 class FakeSDK(FakeSDKBase):pass
 before_names=set(FakeSDK.__dict__);audit=SDKCallAudit(FakeSDK).install();FakeSDK().reset()
 audit.phase='readonly_metadata_and_queries';before_calls=dict(audit.counts)
 py_rng=random.getstate();np_rng=np.random.get_state();persisted=[];query=FakeQuery()
 result=query_positions_only(query,source,reference,resolver,lambda v:persisted.append(copy.deepcopy(v)))
 assert query.calls==160 and len(result['all_rays'])==160 and result['completed_160_actual_rays']
 assert audit.counts==before_calls and random.getstate()==py_rng
 new_np=np.random.get_state();assert np_rng[0]==new_np[0] and np.array_equal(np_rng[1],new_np[1]) and np_rng[2:]==new_np[2:]
 audit.restore();assert set(FakeSDK.__dict__)==before_names
 negatives=[]
 for name,query in [('height_error_2e6',FakeQuery(error=2e-6)),('wrong_collision_identity',FakeQuery(collision='/wrong'))]:
  kept=[]
  try:query_positions_only(query,source,reference,resolver,lambda v:kept.append(copy.deepcopy(v)))
  except AssertionError as error:
   assert kept and query.calls==1;negatives.append(dict(case=name,rejected=True,original_partial_evidence_retained=True,error=str(error)))
  else:raise AssertionError(name)
 for name,change in [('wrong_actor_pose',lambda x:x['actual_actor_getter'].update(rotation_xyzw=[0,0,1,0])),
                     ('missing_native_actor',lambda x:x['actual_actor_getter'].update(ret_val=False)),
                     ('wrong_axis',lambda x:x['actual_USD_plane'].update(axis='X'))]:
  m=copy.deepcopy(metadata);change(m)
  try:represented_plane_from_readonly_metadata(m)
  except ValueError as error:negatives.append(dict(case=name,rejected=True,error=str(error)))
  else:raise AssertionError(name)
 files=[]
 for name in ('retention_plane_metadata_v7.py','retention_plane_metadata_worker_v7.py','retention_plane_metadata_parent_v7.py','represented_native_plane_CPU_component_v2.py'):
  p=P/name;s=p.read_text(encoding='utf-8');tree=ast.parse(s);compile(s,str(p),'exec')
  if name=='retention_plane_metadata_v7.py':
   forbidden=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('step','forward','reset')]
   assert not forbidden,forbidden
   imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
   assert not any(x and ('frozen_history_policy' in x or 'rsl_rl' in x) for x in imports)
  if name=='retention_plane_metadata_worker_v7.py':assert 'torch.load' not in s and 'checkpoint' not in s
  files.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),CPUcompile=True))
 v6=ast.parse((P/'retention_native_witness_v6.py').read_text(encoding='utf-8'))
 oldcap=next(n.value for n in v6.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SMALL_EVAL_CAPACITY' for t in n.targets))
 cap=eval(compile(ast.Expression(oldcap),'cpu_literal_only','eval'),{'__builtins__':{},'dict':dict})
 assert SMALL_EVAL_CAPACITY==cap
 report=dict(epoch=time.time(),passed_CPU_synthetic_only=True,no_actual_GPU_SDK_pass=True,
             synthetic_positive_actual_raycast_API_calls=160,requested_evaluation_controls=0,policy_calls=0,
             readonly_phase_extra_SDK_step_forward_reset_render_calls=0,readonly_phase_python_numpy_RNG_draws=0,
             synthetic_initialization_calls_disclosed=before_calls,total_actual_physics_zero_not_claimed=True,
             inherited_SDK_audit_attributes_restored_exact=True,negative_fixtures=negatives,
             V6_capacity_literal_exact=True,source_reference_only=True,actual_shape_local_pose_read=False,
             public_source_to_installed_binary_bitexact_proven=False,files=files,pending_Git_by_root=True)
 out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(dict(passed_CPU_synthetic_only=True,positive_queries=160,negative_cases=len(negatives),report=str(out.resolve())),indent=2))

if __name__=='__main__':main()
