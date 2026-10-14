"""Independent V4 query-support observer repair; no transport/launch/PPO."""
from pathlib import Path
import ast,hashlib,json,time,zipfile
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report_path=R/'SCENE_QUERY_V3_FAILURE_AND_V4_CPU_PREPARED.json';assert not report_path.exists()
failed=D/'actual_collections/retention_baseline1aa_flat_native120_v3/1791947633675786900/attempts/retention_baseline1aa_flat_native120_v3/output/ORIGINAL_ERROR.json'
assert failed.exists();failure=json.loads(failed.read_bytes());assert "Actual plane query missing" in failure['error'] and failure['no_PPO']
sdk=[D.parent/'MOD4_3060_DIRECT_FACTOR_20261013/sdk_readonly_source/12_isaaclab__sim__simulation_cfg.py',D.parent/'MOD4_3060_DIRECT_FACTOR_20261013/sdk_hardware_readonly_source/isaaclab_physx__physics__physx_manager_cfg.py',D.parent/'MOD4_3060_DIRECT_FACTOR_20261013/sdk_hardware_readonly_source/isaaclab_physx__physics__physx_manager.py']
for source in sdk[:2]:assert 'enable_scene_query_support: bool = False' in source.read_text(encoding='utf8')
assert 'cfg.enable_scene_query_support = sim_cfg.enable_scene_query_support' in sdk[2].read_text(encoding='utf8')
QUERY='''def plane_query_actual(e,phase):
 """Actual enabled PhysX plane query; all original hit evidence is persisted."""
 from isaaclab.sim import get_current_stage
 from pxr import UsdGeom,UsdPhysics
 from omni.physx import get_physx_scene_query_interface
 import os
 stage=get_current_stage();plane_path='/World/ground/geometry/mesh';p=stage.GetPrimAtPath(plane_path)
 assert p and p.GetTypeName()=='Plane' and p.HasAPI(UsdPhysics.CollisionAPI)
 assert p.GetAttribute('axis').Get()=='Z'
 tf=UsdGeom.XformCache().GetLocalToWorldTransform(p)
 point=tf.Transform((0.,0.,0.));normal=tf.TransformDir((0.,0.,1.))
 assert abs(float(point[2]))<=1e-6 and np.max(abs(np.asarray(normal)-[0.,0.,1.]))<=1e-6
 scene=stage.GetPrimAtPath(e.cfg.sim.physics_prim_path)
 actual_query_flag=scene.GetAttribute('physxScene:enableSceneQuerySupport').Get()
 assert e.cfg.sim.enable_scene_query_support is True and actual_query_flag is True,('Actual scene-query support not enabled',actual_query_flag)
 evidence=dict(phase=phase,actual_requested_query_support=e.cfg.sim.enable_scene_query_support,actual_physics_scene_path=e.cfg.sim.physics_prim_path,actual_USD_scene_query_support=actual_query_flag,authored_plane=dict(path=str(p.GetPath()),type=p.GetTypeName(),axis=p.GetAttribute('axis').Get(),point=list(point),normal=list(normal)),tolerance_m=1e-6,all_rays=[],no_physical_step_no_cache_forward_no_RNG=True)
 destination=Path(CONTEXT['output_dir'])/('QUERY_'+phase+'_ALLHITS_ACTUAL.json');assert not destination.exists()
 def persist():
  temporary=destination.with_suffix(destination.suffix+'.partial')
  with temporary.open('wb') as out:out.write(json.dumps(evidence,indent=2).encode('utf8'));out.flush();os.fsync(out.fileno())
  os.replace(temporary,destination)
 def value(x):
  if x is None or isinstance(x,(bool,int,float,str)):return x
  try:return [float(v) for v in x]
  except (TypeError,ValueError):return str(x)
 actual=cpu(e.scene['robot'].data.root_pos_w);rows=[];query=get_physx_scene_query_interface()
 for i,xy in enumerate(actual[:,:2]):
  allhits=[]
  def callback(hit):
   allhits.append({str(k):value(v) for k,v in hit.items()});return True
  returned=query.raycast_all((float(xy[0]),float(xy[1]),10.),(0.,0.,-1.),20.,callback)
  ray=dict(env_id=i,origin=[float(xy[0]),float(xy[1]),10.],direction=[0.,0.,-1.],maximum_distance=20.,query_return=value(returned),all_reported_hits=allhits,selected_plane_hits=[])
  for hit in allhits:
   collision=str(hit.get('collision',''))
   if collision==plane_path or collision.startswith(plane_path+'/'):
    ray['selected_plane_hits'].append(dict(hit=hit,resolved_plane_path=plane_path,identity_resolution='reported path exact or child of actual USD Plane'))
   elif collision and plane_path.startswith(collision+'/'):
    ancestor=stage.GetPrimAtPath(collision)
    colliders=[x for x in UsdGeom.PrimRange(ancestor) if x.HasAPI(UsdPhysics.CollisionAPI)] if hasattr(UsdGeom,'PrimRange') else None
    if colliders is None:
     from pxr import Usd
     colliders=[x for x in Usd.PrimRange(ancestor) if x.HasAPI(UsdPhysics.CollisionAPI)]
    if len(colliders)==1 and str(colliders[0].GetPath())==plane_path:
     ray['selected_plane_hits'].append(dict(hit=hit,resolved_plane_path=plane_path,identity_resolution='reported ancestor has exactly one actual collision shape, the frozen USD Plane'))
  evidence['all_rays'].append(ray);persist()
  assert ray['selected_plane_hits'],('Actual plane query missing',phase,i,allhits)
  selected=min(ray['selected_plane_hits'],key=lambda x:x['hit']['distance']);h=selected['hit']
  assert abs(float(h['position'][2]))<=1e-6 and abs(float(h['normal'][2])-1.)<=1e-6,('Actual plane query violates original tolerance',phase,i,h)
  rows.append(dict(env_id=i,origin=ray['origin'],hit=h,resolved_plane_path=selected['resolved_plane_path'],identity_resolution=selected['identity_resolution']))
 evidence['complete_all_envs']=True;persist()
 return dict(phase=phase,query_rows=rows,authored_plane=evidence['authored_plane'],tolerance_m=1e-6,no_physical_step_no_RNG=True,scene_query_support_requested=True,actual_USD_scene_query_support=True,allhits_evidence=dict(path=str(destination),bytes=destination.stat().st_size,sha256=hashlib.sha256(destination.read_bytes()).hexdigest()))
'''
old=P/'retention_native_witness_v3.py';tree=ast.parse(old.read_text(encoding='utf8'));fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='plane_query_actual')
lines=old.read_text(encoding='utf8').splitlines(keepends=True);new=''.join(lines[:fn.lineno-1])+QUERY+'\n'+''.join(lines[fn.end_lineno:])
path=P/'retention_native_witness_v4.py';assert not path.exists();compile(new,str(path),'exec');path.write_text(new,encoding='utf8',newline='\n')
for kind in ('flat','spin','world'):
 old=P/('retention_'+kind+'_native_v3.py');text=old.read_text(encoding='utf8').replace('retention_native_witness_v3','retention_native_witness_v4')
 text=text.replace('cfg.sim.device = args.device','cfg.sim.device = args.device\n    cfg.sim.enable_scene_query_support = True')
 path=P/('retention_'+kind+'_native_v4.py');assert not path.exists();compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
 old_fn=next(x for x in ast.parse(old.read_text(encoding='utf8')).body if isinstance(x,ast.FunctionDef));new_fn=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef))
 new_fn.body=[x for x in new_fn.body if not (isinstance(x,ast.Assign) and len(x.targets)==1 and ast.unparse(x.targets[0])=='cfg.sim.enable_scene_query_support')]
 assert ast.dump(old_fn,include_attributes=False)==ast.dump(new_fn,include_attributes=False),(kind,'physical/command loop changed')
path=P/'retention_worker_v4.py';assert not path.exists();text=(P/'retention_worker_v3.py').read_text(encoding='utf8').replace('RETENTION_CPU_MANIFEST_V3.json','RETENTION_CPU_MANIFEST_V4.json').replace('retention_native_witness_v3','retention_native_witness_v4').replace("'_native_v3.py'","'_native_v4.py'").replace("+'_native_v3'","+'_native_v4'")
text=text.replace("CONTEXT['save']=save","CONTEXT['save']=save;CONTEXT['output_dir']=str(O)");compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
path=P/'retention_parent_v4.py';assert not path.exists();text=(P/'retention_parent_v3.py').read_text(encoding='utf8').replace('retention_worker_v3.py','retention_worker_v4.py').replace('RETENTION_CPU_MANIFEST_V3.json','RETENTION_CPU_MANIFEST_V4.json');compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
path=D/'review_retention_full_actual_CPU_v3.py';assert not path.exists();text=(D/'review_retention_full_actual_CPU_v2.py').read_text(encoding='utf8').replace('RETENTION_CPU_MANIFEST_V3.json','RETENTION_CPU_MANIFEST_V4.json')
text=text.replace("assert hit['hit']['collision']=='/World/ground/geometry/mesh'", "assert hit['resolved_plane_path']=='/World/ground/geometry/mesh'")
text=text.replace("  for hit in row['query_rows']:","  assert row['scene_query_support_requested'] and row['actual_USD_scene_query_support']\n  allhits=O/Path(row['allhits_evidence']['path']).name;assert H(allhits)==row['allhits_evidence']['sha256'] and allhits.stat().st_size==row['allhits_evidence']['bytes']\n  original_hits=read(allhits);assert original_hits['complete_all_envs'] and len(original_hits['all_rays'])==N\n  for hit in row['query_rows']:")
compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
report=dict(epoch=time.time(),status='V4_CPU_PREPARED_ONLY',approved_GPU=False,original_V3_failure=dict(path=str(failed),sha256=H(failed),error=failure,no_PPO=True,original_PASS_not_claimed=True),source_evidence=[dict(path=str(x),bytes=x.stat().st_size,sha256=H(x)) for x in sdk],source_observation='SimulationCfg and PhysxCfg defaults false; actual installed backend forwards sim_cfg flag and GUI alone overrides true',inference='Missing headless scene-query manager is consistent with original no-hit failure; actual V4 query still required',new_axis='Explicit scene query support before env construction plus readonly all-hit/query-path evidence; no extra simulation or cache forward',only_cfg_flag_added_physical_command_reward_reset_loop_AST_exact=True,old_solver_contact_geometry_DR_RNG_thresholds_unchanged=True,original_ground_tolerance_m=1e-6,no_ideal_plane_fallback=True,no_SSH_no_GPU_no_PPO=True)
manifest=json.loads((P/'RETENTION_CPU_MANIFEST_V3.json').read_bytes());manifest['v4_scene_query_repair']=report
manifest['prepared_files_v4']=[dict(path=str(x),relative=x.relative_to(P).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in sorted(P.glob('*v4.py'))]
(P/'RETENTION_CPU_MANIFEST_V4.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
files=[P/'retention_worker_v4.py',P/'retention_parent_v4.py',P/'retention_native_witness_v4.py']+[P/('retention_'+k+'_native_v4.py') for k in ('flat','spin','world')]+[P/'RETENTION_CPU_MANIFEST_V4.json']+list((P/'original').glob('*.py'))+list((P/'cpu_contracts').glob('*.py'))
zip_path=D/'retention_scenequery_support_v4_CPU_COMPONENTS.zip';assert not zip_path.exists()
with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for x in files:z.write(x,x.relative_to(P).as_posix())
report['package']=dict(path=str(zip_path),bytes=zip_path.stat().st_size,sha256=H(zip_path));report['package_files']=[dict(relative=x.relative_to(P).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in files]
report_path.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('status','approved_GPU','new_axis','package')}))
