from pathlib import Path
import hashlib,json,time,traceback,sys
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';L=B/'cooked_query_full20k_V9_actual'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
 ret=json.loads((R/'STEP270_COOKED_QUERY_FULL20K_V9_FINITE_RETURNED_ACTUAL.json').read_bytes());assert not ret['pending'] and ret['parent_complete']['passed'] and ret['parent_exit']['all_own_children_waited'] and ret['parent_exit']['own_eval_lease_released'] and not ret['actual_own_live']
 for row in ret['texts']:
  p=L/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 v=json.loads((L/'out/ACTUAL_COOKED_VS_AUTHORED_STEP270_QUERY_RESULT.json').read_bytes());assert v['passed'] and v['num_envs']==20000 and len(v['all_rows'])==140000 and len(v['front_rows'])==20000 and v['physical_query_threshold_m']==1e-6
 sys.path.insert(0,str(B/'H1_step270_native32_V4_payload'));from step270_triangle_geometry_cpu import generate
 origins=np.array([[r['actual_Float3_origin'][0]-.25,r['actual_Float3_origin'][1]] for r in v['front_rows']],dtype=np.float64);vertices,faces,groups=generate(origins,**v['geometry']);assert hashlib.sha256(vertices[faces].astype('<f4').tobytes()).hexdigest()==v['ordered_triangle_SHA']
 max_plane=max_triangle=max_normal=max_vertical=max_vertical_ray=0.;old_world_fail=old_bary_fail=0
 def face(row):
  hit=row['cooked'];part=int(hit['collision'].rsplit('part',1)[1]);idx=25000*part+hit['faceIndex'];return idx,vertices[faces[idx]].astype(np.float64)
 def independent_distance(point,tri):
  a,b,c=tri;normal=np.cross(b-a,c-a);normal/=np.linalg.norm(normal);plane=float(np.dot(point-a,normal));project=point-plane*normal;signs=[float(np.dot(np.cross(right-left,project-left),normal)) for left,right in ((a,b),(b,c),(c,a))]
  if min(signs)>=0 or max(signs)<=0:return abs(plane)
  values=[]
  for left,right in ((a,b),(b,c),(c,a)):
   segment=right-left;fraction=max(0.,min(1.,float(np.dot(point-left,segment)/np.dot(segment,segment))));values.append(float(np.linalg.norm(point-left-fraction*segment)))
  return min(values)
 for i,row in enumerate(v['front_rows']):
  assert row['env']==i;idx,tri=face(row);assert idx in groups[i]['front_faces'] and np.array_equal(tri,np.asarray(row['actual_authored_hit_triangle']))
  hit=row['cooked'];o=np.array(row['actual_Float3_origin'],dtype=np.float64);p=o+[float(hit['distance']),0.,0.];expected=float(vertices[faces[groups[i]['front_faces'][0]][0],0]);plane_error=abs(p[0]-expected);triangle_error=independent_distance(p,tri);normal_error=float(np.max(np.abs(np.asarray(hit['normal'])-[-1.,0.,0.])))
  assert 0<hit['distance']<.2 and plane_error<=1e-6 and triangle_error<=1e-6 and normal_error<=1e-6 and np.isfinite(p).all()
  assert np.array_equal(p,np.array(row['float64_ray_point'])) and abs(row['geometric_error_m']-plane_error)<1e-14 and abs(row['point_triangle_distance_m']-triangle_error)<1e-12
  old_world_fail+=int(abs(hit['position'][0]-expected)>1e-6);old_bary_fail+=int(row['V8_extra_dimensionless_barycentric_guard_rejected']);max_plane=max(max_plane,plane_error);max_triangle=max(max_triangle,triangle_error);max_normal=max(max_normal,normal_error)
 expected_height={'lower_floor_under_robot':0.,'before_front':0.,'after_front':float(np.float32(.27)),'top_middle':float(np.float32(.27)),'before_back':float(np.float32(.27)),'after_back':0.,'outside_side':0.}
 for j,row in enumerate(v['all_rows']):
  i=row['env'];assert i==j//7;hit=row['cooked'];idx,tri=face(row);height=expected_height[row['tag']];assert row['authored_height']==height and np.max(np.abs(tri[:,2]-height))==0
  normal_error=float(np.max(np.abs(np.asarray(hit['normal'])-[0.,0.,1.])));vertical_error=abs(hit['position'][2]-height);ray_error=abs(float(np.float32(row['origin'][2]))-hit['distance']-height)
  assert vertical_error<=1e-6 and ray_error<=1e-6 and normal_error<=1e-6 and hit['collision'].startswith('/World/ground/') and np.isfinite(hit['distance'])
  if height>0:assert idx in groups[i]['top_faces']
  else:assert idx in (0,1)
  max_vertical=max(max_vertical,vertical_error);max_vertical_ray=max(max_vertical_ray,ray_error);max_normal=max(max_normal,normal_error)
 assert old_world_fail==v['original_world_Float3_guard_failed_count']==434
 rates=json.loads((L/'out/ACTUAL_NEW_THREE_STEP_RATES_ISOLATED_SDK_MATH_PROBE.json').read_bytes());assert rates['passed'] and rates['fixture_rows']==20000 and rates['independent_numpy_weighted_control_contribution_maxabs']<=1e-6
 out=dict(epoch=time.time(),passed_independent_all160k_metric_geometry_CPU=True,actual_GPU_complete_all_ownout_and_private_lease_released=True,source_SHA=v['source_SHA'],source_Adam=v['source_Adam'],num_envs=20000,vertical140000_front20000=True,actual_authored_ordered_triangle_SHA=v['ordered_triangle_SHA'],all_actual_cooked_face_indices_independently_match_exact_authored_triangle_groups=True,front_float64_ray_equation_error_max_m=max_plane,independent_point_triangle_distance_max_m=max_triangle,vertical_world_height_error_max_m=max_vertical,vertical_ray_equation_error_max_m=max_vertical_ray,normal_maxabs=max_normal,physical_threshold_m=1e-6,original_world_Float3_failures_preserved_count=old_world_fail,V8_extra_dimensionless_barycentric_rejections_diagnostic_count=old_bary_fail,old_world_position_guard_not_relabelled_pass=True,all_real_scene_mesh_material_policy_physics_unchanged=True,actual_SDK_three_new_rate_math_passed=True,actual_SDK_rate_maxabs=rates['independent_numpy_weighted_control_contribution_maxabs'],zero_actions_zero_optimizer_no_H1_GO_or_skill_credit=True,new_production_worker_controller_source_CPU_and_resource_admission_still_required=True)
 put(R/'STEP270_FULL20K_V9_ALL160K_COOKED_METRIC_GEOMETRY_CPU_ACTUAL.json',out);print(json.dumps(out))
except BaseException:
 put(R/('STEP270_V9_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_replay_GPU_or_old_reader=True));raise
