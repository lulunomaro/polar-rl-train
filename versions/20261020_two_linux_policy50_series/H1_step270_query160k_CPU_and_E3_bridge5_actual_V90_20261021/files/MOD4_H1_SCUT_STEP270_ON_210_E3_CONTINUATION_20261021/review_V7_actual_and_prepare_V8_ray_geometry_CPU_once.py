"""Preserve the failed world-Float3 audit; qualify a ray-equation numerical repair."""
from pathlib import Path
import ast, hashlib, json, math, time, traceback
import numpy as np
B=Path(__file__).resolve().parent; R=B/'reports'
def put(path,value):
    with path.open('x',encoding='utf8') as f: json.dump(value,f,indent=2)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

try:
    receipt=json.loads((R/'STEP270_COOKED_QUERY_FULL20K_V7_FINITE_RETURNED_ACTUAL.json').read_bytes())
    assert not receipt['pending'] and not receipt['parent_complete']['passed']
    assert receipt['parent_exit']['all_own_children_waited'] and receipt['parent_exit']['own_eval_lease_released'] and not receipt['actual_own_live']
    local=B/'cooked_query_full20k_V7_actual'
    for row in receipt['texts']:
        p=local/row['relative']; assert p.stat().st_size==row['bytes'] and sha(p)==row['SHA']
    q=json.loads((local/'out/FIRST_ACTUAL_FRONT_1UM_GUARD_DIAGNOSTIC.json').read_bytes())
    rates=json.loads((local/'out/ACTUAL_NEW_THREE_STEP_RATES_ISOLATED_SDK_MATH_PROBE.json').read_bytes())
    o=np.asarray(q['actual_Float3_origin'],dtype=np.float64); hit=q['cooked']; p=np.asarray(hit['position'],dtype=np.float64)
    expected=float(q['expected_authored_f32_front_x']); actual_distance=float(hit['distance'])
    ray_x=float(o[0]+actual_distance); world_error=abs(p[0]-expected); ray_error=abs(ray_x-expected)
    assert world_error==q['world_position_axis_error_m']==q['position_ULP_m'] and world_error>1e-6
    assert ray_error==q['ray_distance_error_m'] and ray_error<1e-6
    assert hit['normal']==[-1.,0.,-0.] and q['original_guard_still_rejected']
    assert rates['passed'] and rates['actual_reward_manager_type']=='isaaclab.managers.reward_manager.RewardManager'
    # Independent scalar evaluation of the four real SDK fixture cases.
    f32=lambda x:float(np.float32(x))
    contributions=[(-2*(3-f32(1.2))*(k!=1 and k!=2)-(f32(.4)**2+2*(f32(.1)**2+f32(.2)**2))*(k==3))*.01 for k in range(4)]
    assert rates['fixture_rows']==20000 and rates['case_patterns']==4 and rates['actual_SDK_dt']==.01
    assert rates['actual_configured_weights']==dict(release_shortfall=-2.,landing_yaw_rate=-1.,landing_planar_stop=-2.)
    assert rates['independent_numpy_weighted_control_contribution_maxabs']<1e-6 and rates['live_trajectory_or_actor_or_phase_or_rng_not_modified']
    cases=[]
    def distance_pass(d): return math.isfinite(d) and 0<d<.2 and abs(float(o[0]+d)-expected)<=1e-6
    for name,d,accepted in [('actual_float3_world_failure_ray_distance',actual_distance,True),('positive_two_micrometre_geometric_error',expected-o[0]+2e-6,False),('negative_two_micrometre_geometric_error',expected-o[0]-2e-6,False),('nonfinite_distance',float('nan'),False),('negative_distance',-.1,False),('beyond_query_length',.3,False)]:
        assert distance_pass(d)==accepted; cases.append(dict(name=name,passed=True,accepted=accepted))
    proof=dict(epoch=time.time(),actual_V7_failed_world_position_guard_retained=True,actual_allout_and_private_lease_released=True,actual_env=q['env'],actual_world_position_error_m=world_error,world_f32_ULP_m=q['position_ULP_m'],independent_float64_ray_equation_error_m=ray_error,old_world_position_guard_not_relabelled_pass=True,physical_geometry_threshold_m=1e-6,repair_scope='Use submitted Float3 origin plus actual PhysX ray distance in float64; independently intersect the exact saved authored hit triangle. World Float3 output remains a recorded diagnostic, not a sub-ULP geometric estimator.',actual_SDK_three_rate_math_passed=True,independent_four_case_contributions=contributions,actual_SDK_numpy_maxabs=rates['independent_numpy_weighted_control_contribution_maxabs'],CPU_rejection_cases=cases,no_physics_material_mesh_actor_or_PPO_change=True,no_H1_learning_GO=True)
    put(R/'STEP270_V7_ACTUAL_FLOAT3_REJECTION_AND_RAY_EQUATION_CPU_ACTUAL.json',proof)

    previous=json.loads((R/'STEP270_COOKED_QUERY_FULL20K_V7_SOURCE_AST_PREPARED_ACTUAL.json').read_bytes())
    old=(Path(previous['payload'])/'worker.py').read_text('utf8')
    start=old.index('  fronts=[]\n'); end=old.index('  for i,point in enumerate(',start)
    replacement='''  # The original Float3 world-point failure is preserved in the V7 receipt.
  # Keep the physical 1um criterion using the actual ray equation in float64.
  from pxr import UsdGeom
  mesh_cache={};fronts=[];world_point_rejections=0;max_ray_geometry_error=0.
  def exact_hit_triangle(hit):
   path=hit['collision']
   if path not in mesh_cache:
    mesh=UsdGeom.Mesh(env.sim.stage.GetPrimAtPath(path));verts=np.asarray(mesh.GetPointsAttr().Get(),dtype=np.float32);indices=np.asarray(mesh.GetFaceVertexIndicesAttr().Get(),dtype=np.int64).reshape(-1,3);counts=np.asarray(mesh.GetFaceVertexCountsAttr().Get());assert (counts==3).all();mesh_cache[path]=(verts,indices)
   verts,indices=mesh_cache[path];return verts[indices[hit['faceIndex']]].astype(np.float64)
  for i,(ox,oy,oz) in enumerate(origins):
   origin=(float(ox+.25),float(oy),.135);hit=cast(origin,(1.,0.,0.),.2);actual_origin=np.asarray(origin,dtype=np.float32).astype(np.float64);triangle=exact_hit_triangle(hit);expected=float(np.float32(float(ox)+.35));ray_point=actual_origin+np.array([hit['distance'],0.,0.],dtype=np.float64)
   # Independent Moller-Trumbore intersection against the exact authored triangle.
   a,b,c=triangle;e1=b-a;e2=c-a;direction=np.array([1.,0.,0.]);cross=np.cross(direction,e2);det=float(e1@cross);assert abs(det)>1e-12;tvec=actual_origin-a;u=float(tvec@cross)/det;qvec=np.cross(tvec,e1);vv=float(direction@qvec)/det;t=float(e2@qvec)/det
   geometric_error=abs(float(ray_point[0])-expected);triangle_error=abs(float(hit['distance'])-t);world_error=abs(hit['position'][0]-expected);max_ray_geometry_error=max(max_ray_geometry_error,geometric_error,triangle_error);world_point_rejections+=int(world_error>1e-6)
   assert np.isfinite(triangle).all() and np.isfinite(ray_point).all() and 0<float(hit['distance'])<.2 and u>=-1e-9 and vv>=-1e-9 and u+vv<=1+1e-9
   assert np.max(np.abs(triangle[:,0]-expected))==0 and geometric_error<=1e-6 and triangle_error<=1e-6
   assert abs(hit['normal'][0]+1)<=1e-6 and abs(hit['normal'][1])+abs(hit['normal'][2])<=1e-6
   fronts.append(dict(env=i,origin=list(origin),actual_Float3_origin=actual_origin.tolist(),expected_x=expected,cooked=hit,actual_authored_hit_triangle=triangle.tolist(),float64_ray_point=ray_point.tolist(),independent_triangle_ray_distance=t,geometric_error_m=geometric_error,triangle_distance_error_m=triangle_error,world_Float3_axis_error_diagnostic_m=world_error,original_world_point_guard_failed=world_error>1e-6))
'''
    new=(old[:start]+replacement+old[end:]).replace('H1_step270_cooked_PhysX_queries_full20k_v7_diagnostic','H1_step270_cooked_PhysX_queries_full20k_v8_ray_equation')
    new=new.replace("front_face_points=len(fronts),vertical_height_maxabs_m=", "front_face_points=len(fronts),physical_query_threshold_m=1e-6,front_ray_geometry_maxabs_m=max_ray_geometry_error,original_world_Float3_guard_failed_count=world_point_rejections,original_world_Float3_failures_retained_not_relabelled=True,front_physical_point_uses_float64_ray_equation_and_independent_authored_triangle=True,vertical_height_maxabs_m=")
    ast.parse(new)
    restored=new.replace(replacement,old[start:end]).replace('H1_step270_cooked_PhysX_queries_full20k_v8_ray_equation','H1_step270_cooked_PhysX_queries_full20k_v7_diagnostic').replace('front_face_points=len(fronts),physical_query_threshold_m=1e-6,front_ray_geometry_maxabs_m=max_ray_geometry_error,original_world_Float3_guard_failed_count=world_point_rejections,original_world_Float3_failures_retained_not_relabelled=True,front_physical_point_uses_float64_ray_equation_and_independent_authored_triangle=True,vertical_height_maxabs_m=','front_face_points=len(fronts),vertical_height_maxabs_m=')
    assert ast.dump(ast.parse(restored))==ast.dump(ast.parse(old))
    payload=B/'H1_step270_cooked_query_full20k_V8_ray_equation_delta';payload.mkdir();(payload/'worker.py').write_text(new,encoding='utf8',newline='\n')
    cfg=json.loads((Path(previous['payload'])/'FROZEN_CONFIG.json').read_bytes());cfg['kind']='H1_step270_cooked_PhysX_queries_full20k_v8_ray_equation';put(payload/'FROZEN_CONFIG.json',cfg)
    manifest=json.loads((Path(previous['payload'])/'SOURCE_MANIFEST.json').read_bytes())
    for row in manifest['files']:
        if row['relative'] in ('worker.py','FROZEN_CONFIG.json'):
            p=payload/row['relative'];row.update(bytes=p.stat().st_size,SHA=sha(p))
    put(payload/'SOURCE_MANIFEST.json',manifest)
    workflows=[]
    for name in ('deploy_step270_cooked_query_full20k_V7_unused_root_once.py','collect_step270_cooked_query_full20k_V7_bounded_once.py'):
        text=(B/name).read_text('utf8').replace('FULL20K_V7','FULL20K_V8').replace('full20k_2110v7','full20k_2110v8').replace('full20k_V7_actual','full20k_V8_actual');ast.parse(text);p=B/name.replace('V7','V8');p.open('x',encoding='utf8',newline='\n').write(text);workflows.append(dict(path=str(p),SHA=sha(p),unused=True))
    report=dict(previous,epoch=time.time(),payload=str(payload),worker=dict(path=str(payload/'worker.py'),bytes=(payload/'worker.py').stat().st_size,SHA=sha(payload/'worker.py')),workflows=workflows,normalized_rest_AST_exact=True,actual_V7_original_world_failure_retained=True,CPU_actual_proof=str(R/'STEP270_V7_ACTUAL_FLOAT3_REJECTION_AND_RAY_EQUATION_CPU_ACTUAL.json'),physical_threshold_m=1e-6,old_world_output_failure_is_not_pass=True,front_ray_equation_and_exact_authored_triangle_required=True,no_distance_only_waiver=True,not_installed_or_executed=True)
    # Historical V7 fields explicitly superseded by this documented numerical repair.
    report['no_distance_guard_substitution']=False;report['all_original_query_guards_unchanged']=False;report['all_original_query_guards_unchanged_except_documented_numerical_point_reconstruction']=True
    put(R/'STEP270_COOKED_QUERY_FULL20K_V8_SOURCE_AST_PREPARED_ACTUAL.json',report)
    print(json.dumps(dict(actual_V7_original_failure_retained=True,CPU_ray_error_m=ray_error,new_V8_source_AST_only=True,physical_1um_unchanged=True)))
except BaseException:
    put(R/('STEP270_V7_CPU_V8_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
