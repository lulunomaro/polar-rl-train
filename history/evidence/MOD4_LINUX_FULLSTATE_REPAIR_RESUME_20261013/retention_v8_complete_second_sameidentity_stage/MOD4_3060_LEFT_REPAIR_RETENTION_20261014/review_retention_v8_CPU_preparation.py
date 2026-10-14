"""Pure CPU fixtures for new readonly V8 reference and unchanged skill loops."""
from pathlib import Path
import ast,copy,hashlib,json,random,sys,time,types
import numpy as np
D=Path(__file__).parent;P=D/'payload';sys.path.insert(0,str(P))
from retention_plane_reference_v8 import query_current_positions,loaded_PhysX_binary_fingerprints,binary_stream_sha256
from represented_native_plane_CPU_component_v2 import represented_plane_from_readonly_metadata


def main():
 out=D/'reports/RETENTION_V8_REPRESENTED_REFERENCE_SYNTHETIC_CPU_PASSED.json';assert not out.exists()
 actual=D/'metadata_actual_collections/1791953869426945200/attempts/native_plane_metadata160_zero_requested_controls_v7/output/ACTUAL_NATIVE_ACTOR_AND_SOURCE_REFERENCE_VALIDATED.json'
 m=json.loads(actual.read_bytes());reference=represented_plane_from_readonly_metadata(m['metadata']);assert reference==m['reference']
 class Hit:
  def __init__(self,position,normal,path):
   self.position=position;self.normal=normal;self.distance=10-position[2];self.collision=path
   self.collision_encoded=[195329,0];self.face_index=0;self.material='/World/ground/physicsMaterial'
   self.material_encoded=[195585,0];self.protoIndex=4294967295;self.rigid_body=path;self.rigid_body_encoded=[195329,0]
 class Query:
  def __init__(self,error=0,path='/World/ground/geometry/mesh'):self.count=0;self.error=error;self.path=path
  def raycast_all(self,origin,direction,distance,callback):
   self.count+=1;n=reference['represented_plane_normal'];x,y=origin[:2];z=-(n[0]*x+n[1]*y+reference['represented_plane_offset_d'])/n[2]+self.error
   callback(Hit([x,y,z],n,self.path));return True
 def resolve(hit):
  if hit['collision']=='/World/ground/geometry/mesh':return dict(resolved_plane_path=hit['collision'],identity_resolution='CPU synthetic exact')
 before_py=random.getstate();before_np=np.random.get_state();positives=[]
 for kind,N in [('flat',80),('spin',88),('world',88)]:
  xy=np.stack((np.linspace(-14,14,N,dtype=np.float32),np.zeros(N,dtype=np.float32)),-1)
  for phase in ('first_physics','final'):
   q=Query();saved=[];evidence,rows=query_current_positions(q,xy,phase,reference,resolve,lambda v:saved.append(copy.deepcopy(v)))
   assert q.count==N and len(rows)==N and evidence['complete_all_envs']
   positives.append(dict(kind=kind,phase=phase,queries=N,source_reference_only=True,all_actual_stage_pending=True))
 after_np=np.random.get_state();assert before_py==random.getstate() and before_np[0]==after_np[0] and np.array_equal(before_np[1],after_np[1]) and before_np[2:]==after_np[2:]
 negatives=[]
 for name,q in [('height_2e6',Query(error=2e-6)),('wrong_collision',Query(path='/Wrong'))]:
  kept=[]
  try:query_current_positions(q,np.zeros((80,2),dtype=np.float32),'first_physics',reference,resolve,lambda v:kept.append(copy.deepcopy(v)))
  except AssertionError as error:
   assert q.count==1 and kept;negatives.append(dict(case=name,rejected=True,failed_prefix_evidence_retained=True,error=str(error)))
  else:raise AssertionError(name)
 fixture=D/'CPU_BINARY_ENUMERATION_SYNTHETIC_V8';assert not fixture.exists();fixture.mkdir()
 mock=fixture/'omni.physx.plugin.dll';mock.write_bytes(b'CPU MOCK ONLY; NEVER LOADED AS A BINARY')
 real_psutil=sys.modules.get('psutil');fake=types.SimpleNamespace(Process=lambda pid:types.SimpleNamespace(pid=pid,create_time=lambda:0,memory_maps=lambda grouped:[types.SimpleNamespace(path=str(mock))]))
 try:
  sys.modules['psutil']=fake;binary=loaded_PhysX_binary_fingerprints()
  assert binary['core_PhysX_plugin_identified'] and len(binary['files'])==1
  assert binary['files'][0]['sha256']==hashlib.sha256(mock.read_bytes()).hexdigest()==binary_stream_sha256(mock)
 finally:
  if real_psutil is None:sys.modules.pop('psutil',None)
  else:sys.modules['psutil']=real_psutil
 old=ast.parse((P/'retention_native_witness_v6.py').read_text(encoding='utf8'));new=ast.parse((P/'retention_native_witness_v8.py').read_text(encoding='utf8'))
 cls=lambda t:next(x for x in t.body if isinstance(x,ast.ClassDef) and x.name=='Witness')
 assert ast.dump(cls(old),include_attributes=False)==ast.dump(cls(new),include_attributes=False)
 loop_proofs=[]
 for kind in ('flat','spin','world'):
  old=ast.parse((P/f'retention_{kind}_native_v6.py').read_text(encoding='utf8'));new=ast.parse((P/f'retention_{kind}_native_v8.py').read_text(encoding='utf8'))
  fn=lambda t:next(x for x in t.body if isinstance(x,ast.FunctionDef) and x.name==f'run_{kind}')
  assert ast.dump(fn(old),include_attributes=False)==ast.dump(fn(new),include_attributes=False)
  loop_proofs.append(dict(kind=kind,original_V6_main_AST_exact=True))
 reference_ast=ast.parse((P/'retention_plane_reference_v8.py').read_text(encoding='utf8'))
 assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('step','forward','reset') for x in ast.walk(reference_ast))
 files=[]
 for p in list(P.glob('*v8.py'))+[D/'review_retention_full_actual_CPU_v8.py']:
  s=p.read_text(encoding='utf8');ast.parse(s);compile(s,str(p),'exec');files.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 report=dict(epoch=time.time(),passed_CPU_synthetic_only=True,new_backend_GPU_pass=False,
             new_query_reference_only=True,source_to_installed_binary_bitexact_proven=False,actual_shape_local_pose_read=False,
             positives=positives,negative_fixtures=negatives,query_phase_python_numpy_RNG_unchanged=True,
             readonly_observer_contains_no_physical_step_reset_forward_calls=True,
             original_Witness_class_AST_exact=True,main_loop_AST_proofs=loop_proofs,
             synthetic_own_loaded_binary_enum_and_stream_SHA_only=True,native_DLL_loaded_by_fixture=False,
             actual_native_binary_pair_identity_pending=True,old_V6_fullcase_failed_unchanged=True,
             compile_files=files,pending_Git_by_root=True)
 out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_synthetic_only=True,total_mock_queries=sum(x['queries'] for x in positives),main_AST_exact=True),indent=2))

if __name__=='__main__':main()
