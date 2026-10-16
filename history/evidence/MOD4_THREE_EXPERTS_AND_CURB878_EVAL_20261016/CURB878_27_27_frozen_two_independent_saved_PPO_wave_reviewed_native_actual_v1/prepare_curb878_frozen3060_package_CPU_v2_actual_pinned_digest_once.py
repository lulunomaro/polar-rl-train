"""Own unused CURB878 frozen route; reuse original geometry and unmodified physical loop."""
from pathlib import Path
import ast,hashlib,json,os,shutil,sys,time,traceback,zipfile
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'eval_payload_v2';R=D/'reports';ROOT='D:/MOD4_async_eval/'+D.name
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FINAL='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1'
def main():
 R.mkdir(exist_ok=True);assert not Q.exists();old=W/'MOD4_S5_SINGLE_W35_MATCHED35_20261015/payload';shutil.copytree(old,Q,ignore=shutil.ignore_patterns('__pycache__'))
 src=W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/final878_actual/source210/rank0/model_update878.pt';assert H(src)==FINAL;shutil.copyfile(src,Q/'source/CURB_final878.pt')
 curb=W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/implementation'
 for name in ('curb20_geometry.py','curb20_profile.json'):shutil.copyfile(curb/name,Q/'runtime/isaac/mod4'/name)
 p=Q/'s5_single_frozen35_v1.py';adapter=p.read_text(encoding='utf8').replace('b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',FINAL).replace('Single frozen W35 actor','Single frozen CURB878 actor').replace('only_single_W35_actor_executed','only_single_CURB_actor_executed');p.write_text(adapter,encoding='utf8')
 original=(Q/'full80_runtime_native_v1.py').read_text(encoding='utf8');new=original.replace('from g3_cad_wave_geometry import configure_g3 as configure_intro','from curb20_geometry import configure_curb as configure_intro')
 a=new.index('    from g3_cad_wave_geometry import profile\n');b=new.index('    assert e.physics_dt',a)
 oldprepare=ast.parse((W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/prepare_curb_frozen_scope_once.py').read_text(encoding='utf8'))
 pref=next(x.value.value for x in ast.walk(oldprepare) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in x.targets) and isinstance(x.value,ast.Constant))
 pref=pref.replace("root_xy=r.data.root_pos_w.torch[:,:2]","root_xy=tensor(r.data.root_pos_w)[:,:2]")
 independent='''    actual_world_ray_origins=cpu(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype))
    from curb_worldmesh_query_contract_v1 import expected_ground
    expected_actual_ground,world_mesh_receipts,query_world_triangles=expected_ground(ray.geometry.vertices,ray.geometry.faces,centers,actual_world_ray_origins)
    actual_query_height_error=float(np.max(abs(sampled-expected_actual_ground)))
    assert actual_query_height_error<=1e-6
    query_evidence_path=Path(args.output).with_name(Path(args.output).name+'.worldmesh_query.npz')
    assert not query_evidence_path.exists()
    np.savez_compressed(query_evidence_path,actual_world_ray_origins=actual_world_ray_origins,actual_canonical_ray_x=(actual_world_ray_origins[:,:,0].astype(np.float64)-centers[:,None,0])*orientation[:,None],actual_sampled_ground=sampled,expected_actual_ground=expected_actual_ground,ideal_profile_ground=np.broadcast_to(expected[None,:],sampled.shape),world_triangles=query_world_triangles)
    assert all((r['mirrored']==bool(o<0)) for r,o in zip(world_mesh_receipts,orientation))
    route_scope.update(actual_world_ray_origins=actual_world_ray_origins.tolist(),actual_query_height_error_m=actual_query_height_error,actual_query_ground_tolerance_m=1e-6,expected_actual_sampled_ground=expected_actual_ground.tolist(),world_mesh_receipts=world_mesh_receipts,query_worldmesh_evidence=dict(path=str(query_evidence_path),bytes=query_evidence_path.stat().st_size,sha256=hashlib.sha256(query_evidence_path.read_bytes()).hexdigest()))
'''
 new=new[:a]+pref+independent+new[b:]
 new=new.replace('targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups]','targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups] * torch.as_tensor(orientation,device=e.device,dtype=torch.float32)')
 new=new.replace('target = float((0.3, -0.3, 0.0)[i])',"target = data['targets_m_s'][ids][None,:]").replace('command_vx_m_s=target,','command_vx_m_s=target[0].tolist(),').replace('approved_S4_E0_WAVE35_rule_original35_worldmesh_actualray_approach040_transition_v1','approved_CURB20_final878_original_mirrored_approach040_worldmesh_v1')
 def loop(s):
  f=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='run_full80');return next(x for x in f.body if isinstance(x,ast.For) and ast.unparse(x.target)=='step')
 assert ast.dump(loop(original),include_attributes=False)==ast.dump(loop(new),include_attributes=False)
 compile(new,'full80_runtime_native_v1.py','exec');(Q/'full80_runtime_native_v1.py').write_text(new,encoding='utf8')
 query='''from pathlib import Path
import hashlib,numpy as np
from curb20_geometry import make_mesh
from g4_worldmesh_query_contract import canonical_triangles,downward_triangle_heights
def expected_ground(actual_vertices,actual_faces,centers,actual_starts):
 tri=np.asarray(actual_vertices,dtype=np.float32)[actual_faces];centroid=tri.astype(np.float64).mean(1);out=[];receipts=[];evidence=[]
 for center,starts in zip(centers,actual_starts):
  selected=tri[np.all(abs(centroid[:,:2]-center)<4.5,axis=1)];lhs=canonical_triangles(selected);matches=[]
  for mirrored in (False,True):
   mesh,_=make_mesh((9.,9.),mirrored);v=mesh.vertices.copy();v[:,:2]-=4.5;v[:,:2]+=center;pred=v.astype(np.float32)[mesh.faces]
   if np.array_equal(lhs,canonical_triangles(pred)):matches.append((mirrored,pred))
  assert len(matches)==1,'Authored CURB mesh differs from both pinned procedural mirror variants'
  mirrored,pred=matches[0];u=pred[:,1]-pred[:,0];v=pred[:,2]-pred[:,0];det=u[:,0]*v[:,1]-u[:,1]*v[:,0];horizontal=abs(det)>1e-12
  assert len(pred)==8 and horizontal.sum()==6,'Vertical riser triangles kept for identity, excluded only from downward nonparallel intersection'
  out.append(downward_triangle_heights(pred[horizontal],starts));evidence.append(selected);receipts.append(dict(mirrored=mirrored,triangles=8,actual_SHA=hashlib.sha256(lhs.tobytes()).hexdigest(),expected_SHA=hashlib.sha256(canonical_triangles(pred).tobytes()).hexdigest(),byteexact=True,vertical_faces_preserved=2))
 return np.asarray(out),receipts,np.stack(evidence)
'''
 (Q/'curb_worldmesh_query_contract_v1.py').write_text(query,encoding='utf8')
 sys.path[:0]=[str(Q),str(Q/'runtime/isaac/mod4')]
 from curb_worldmesh_query_contract_v1 import expected_ground
 from curb20_geometry import make_mesh
 fixtures=[]
 for mirrored in (False,True):
  mesh,_=make_mesh((9.,9.),mirrored);v=mesh.vertices.copy();v[:,:2]-=4.5;v=v.astype(np.float32);o=-1 if mirrored else 1;xx=np.linspace(-.475,.475,35);starts=np.stack((o*xx,np.zeros(35),np.ones(35)*2),-1)[None]
  y,rec,_=expected_ground(v,mesh.faces,np.zeros((1,2)),starts);err=float(abs(y-np.where(xx<-.075,0.,.020)[None]).max());assert err<=1e-6
  bad=v.copy();bad[0,2]+=.001
  try:expected_ground(bad,mesh.faces,np.zeros((1,2)),starts)
  except AssertionError:rejected=True
  else:raise AssertionError('Corrupt mesh accepted')
  fixtures.append(dict(mirrored=mirrored,rows=35,error=err,wrong_mesh_rejected=rejected))
 worker=(Q/'paired_full80_parameter_bound_v2.py').read_text(encoding='utf8').replace('MOD4_S5_SINGLE_W35_MATCHED35_20261015',D.name).replace('b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',FINAL);(Q/'paired_full80_parameter_bound_v2.py').write_text(worker,encoding='utf8')
 from s5_single_frozen35_v1 import Single35
 ck=torch.load(src,map_location='cpu',weights_only=False);x=torch.zeros(80,35);x[:,28]=1;rng=torch.get_rng_state().clone();c=Single35(Q/'source/CURB_final878.pt',80,'cpu');z=c.begin(0,lambda:x);expected=x
 for i in (0,2,4,6):
  expected=torch.nn.functional.linear(expected,ck['actor_state_dict'][f'mlp.{i}.weight'],ck['actor_state_dict'][f'mlp.{i}.bias'])
  if i<6:expected=torch.nn.functional.elu(expected)
 assert torch.equal(expected,z['raw_action']);c.finish(z['clipped_action'],torch.zeros(80,dtype=torch.bool));assert c.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 m=dict(epoch=time.time(),source_single_policy=dict(expert='CURB_final878',local_path=ROOT+'/payload/source/CURB_final878.pt',sha256=FINAL,bytes=src.stat().st_size,CPU_floating=102),no_PPO=True,approved_GPU=False,current_geometry='original CURB20 mirrored 150mm strip, not WAVE',original_physical_control_loop_AST_exact=True,route_contract='Original CURB132 approach0.4m, 15s,80env, before-after0.2m two-wheel strict1N; new source, native120 thenfull1500')
 m['file_rows']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'];(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 z=D/'CURB878_FROZEN_3060_V1.zip';assert not z.exists()
 with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED,compresslevel=1) as out:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:out.write(p,p.relative_to(Q).as_posix())
 report=dict(epoch=time.time(),passed_CPU_only=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),worker_SHA=H(Q/'paired_full80_parameter_bound_v2.py'),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),source=m['source_single_policy'],original_physical_loop_AST_exact=True,mirror_query_CPU_fixtures=fixtures,all6_CPUmean_exact=True,global_CPU_RNG_unchanged=True,no_CUDA_optimizer_or_target_GPU=True,older_unused_sources_retained_not_forwarded=True,lookup_misses_before_prepare=['Wrong transport/worker file basenames were read-only misses; original tool errors retained, not GPU faults'])
 (R/'CURB878_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);(R/('CURB878_CPU_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_runtime_dispatch=True),indent=2));raise
