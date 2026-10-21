from pathlib import Path
import ast,hashlib,json,time,traceback
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
HELPER='''  def point_triangle_distance(point,triangle):
   a,b,c=triangle;e0=b-a;e1=c-a;normal=np.cross(e0,e1);normal=normal/np.linalg.norm(normal);projected=point-normal*float((point-a)@normal);q=projected-a;d00=float(e0@e0);d01=float(e0@e1);d11=float(e1@e1);d20=float(q@e0);d21=float(q@e1);den=d00*d11-d01*d01;uu=(d11*d20-d01*d21)/den;vv=(d00*d21-d01*d20)/den
   if uu>=0 and vv>=0 and uu+vv<=1:return abs(float((point-a)@normal))
   distances=[]
   for left,right in ((a,b),(b,c),(c,a)):
    edge=right-left;fraction=np.clip(float((point-left)@edge)/float(edge@edge),0.,1.);distances.append(float(np.linalg.norm(point-(left+fraction*edge))))
   return min(distances)
'''
try:
 ret=json.loads((R/'STEP270_COOKED_QUERY_FULL20K_V8_FINITE_RETURNED_ACTUAL.json').read_bytes());assert not ret['pending'] and ret['parent_exit']['all_own_children_waited'] and ret['parent_exit']['own_eval_lease_released'] and not ret['parent_complete']['passed']
 error=json.loads((B/'cooked_query_full20k_V8_actual/out/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').read_bytes())['error'];assert 'u>=-1e-9 and vv>=-1e-9' in error
 scope={'np':np};exec('\n'.join(line[2:] for line in HELPER.splitlines()),scope);distance=scope['point_triangle_distance'];tri=np.array([[0.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
 cases=[]
 for name,p,accepted in [('interior',[0,.2,.2],True),('two_um_plane_offset',[2e-6,.2,.2],False),('near_edge_five_nm',[0,.5,.500000005],True),('two_um_outside_edge',[0,.5,.500004],False),('far_outside_vertex',[0,1.1,-.1],False)]:
  value=distance(np.array(p),tri);assert (value<=1e-6)==accepted;cases.append(dict(name=name,distance_m=value,accepted=accepted,passed=True))
 previous=json.loads((R/'STEP270_COOKED_QUERY_FULL20K_V8_SOURCE_AST_PREPARED_ACTUAL.json').read_bytes());old=(Path(previous['payload'])/'worker.py').read_text('utf8');new=old.replace('full20k_v8_ray_equation','full20k_v9_metric_triangle')
 new=new.replace('  for i,(ox,oy,oz) in enumerate(origins):\n   origin=',HELPER+'  for i,(ox,oy,oz) in enumerate(origins):\n   origin=')
 line="   assert np.isfinite(triangle).all() and np.isfinite(ray_point).all() and 0<float(hit['distance'])<.2 and u>=-1e-9 and vv>=-1e-9 and u+vv<=1+1e-9"
 replacement="""   point_triangle_error=point_triangle_distance(ray_point,triangle);old_dimensionless_barycentric_rejected=not (u>=-1e-9 and vv>=-1e-9 and u+vv<=1+1e-9)
   if not (np.isfinite(triangle).all() and np.isfinite(ray_point).all() and 0<float(hit['distance'])<.2 and point_triangle_error<=1e-6 and geometric_error<=1e-6 and triangle_error<=1e-6):
    put('FIRST_METRIC_GEOMETRY_REJECTION_DIAGNOSTIC.json',dict(env=i,origin=actual_origin.tolist(),cooked=hit,triangle=triangle.tolist(),ray_point=ray_point.tolist(),barycentric=[u,vv],point_triangle_distance_m=point_triangle_error,geometric_error_m=geometric_error,triangle_distance_error_m=triangle_error,threshold_m=1e-6));raise RuntimeError('Metric 1um triangle geometry rejected; original values retained')"""
 assert old.count(line)==1;new=new.replace(line,replacement).replace('world_Float3_axis_error_diagnostic_m=world_error,','point_triangle_distance_m=point_triangle_error,barycentric=[u,vv],V8_extra_dimensionless_barycentric_guard_rejected=old_dimensionless_barycentric_rejected,world_Float3_axis_error_diagnostic_m=world_error,')
 ast.parse(new);restored=new.replace(HELPER,'').replace(replacement,line).replace('point_triangle_distance_m=point_triangle_error,barycentric=[u,vv],V8_extra_dimensionless_barycentric_guard_rejected=old_dimensionless_barycentric_rejected,','').replace('full20k_v9_metric_triangle','full20k_v8_ray_equation');assert ast.dump(ast.parse(restored))==ast.dump(ast.parse(old))
 payload=B/'H1_step270_cooked_query_full20k_V9_metric_triangle_delta';payload.mkdir();(payload/'worker.py').write_text(new,encoding='utf8',newline='\n');cfg=json.loads((Path(previous['payload'])/'FROZEN_CONFIG.json').read_bytes());cfg['kind']='H1_step270_cooked_PhysX_queries_full20k_v9_metric_triangle';put(payload/'FROZEN_CONFIG.json',cfg);manifest=json.loads((Path(previous['payload'])/'SOURCE_MANIFEST.json').read_bytes())
 for row in manifest['files']:
  if row['relative'] in ('worker.py','FROZEN_CONFIG.json'):
   p=payload/row['relative'];row.update(bytes=p.stat().st_size,SHA=H(p))
 put(payload/'SOURCE_MANIFEST.json',manifest);workflows=[]
 for name in ('deploy_step270_cooked_query_full20k_V8_unused_root_once.py','collect_step270_cooked_query_full20k_V8_bounded_once.py'):
  s=(B/name).read_text('utf8').replace('FULL20K_V8','FULL20K_V9').replace('full20k_2110v8','full20k_2110v9').replace('full20k_V8_actual','full20k_V9_actual');ast.parse(s);p=B/name.replace('V8','V9');p.open('x',encoding='utf8',newline='\n').write(s);workflows.append(dict(path=str(p),SHA=H(p),unused=True))
 proof=dict(epoch=time.time(),actual_V8_extra_dimensionless_barycentric_assertion_failed=True,original_V8_exact_failing_values_not_saved_unknown=True,no_claim_of_exact_V8_failure_magnitude=True,all_own_out_and_lease_released=True,repair='Replace added dimensionless 1e-9 barycentric admission with independent point-to-authored-triangle distance in metres <=1e-6. Keep ray/plane/normal <=1um; save all old world and barycentric failures as diagnostics.',new_metric_rejection_cases=cases,normalized_other_AST_exact=True,physics_mesh_material_reward_actor_optimizer_unchanged=True,not_installed_or_executed=True)
 put(R/'STEP270_V8_READER_ASSERTION_AND_V9_METRIC_TRIANGLE_CPU_ACTUAL.json',proof)
 report=dict(previous,epoch=time.time(),payload=str(payload),worker=dict(path=str(payload/'worker.py'),bytes=(payload/'worker.py').stat().st_size,SHA=H(payload/'worker.py')),workflows=workflows,V8_actual_error_preserved=True,V8_added_dimensionless_guard_replaced_with_original_physical_metre_threshold=True,metric_CPU_cases=cases,not_installed_or_executed=True);put(R/'STEP270_COOKED_QUERY_FULL20K_V9_SOURCE_AST_PREPARED_ACTUAL.json',report);print(json.dumps(dict(prepared_V9_source_only=True,physical_threshold_m=1e-6,CPU_cases=len(cases))))
except BaseException:
 put(R/('STEP270_V9_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
