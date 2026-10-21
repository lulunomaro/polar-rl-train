from pathlib import Path
import sys,json,time,hashlib,numpy as np
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B/'candidate_uninstalled'))
from step270_triangle_geometry_cpu import generate
sys.path.insert(0,str(B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1/job0/runtime/isaac/mod4'))
from e1_rough_ground import TerrainTriangles,VerticalMeshOracle
origins=np.array([[0.,0.],[2.5,0.],[0.,2.5],[2.5,2.5]])
vertices,faces,groups=generate(origins);terrain=TerrainTriangles(vertices,faces,('/CPU_FIXTURE_NOT_A_USD_COLLIDER',));ray=VerticalMeshOracle(terrain)
points=[];expected=[];envs=[]
for i,(x,y) in enumerate(origins):
 for xx,yy,h in [(x,y,0),(x+1.099,y,0),(x+1.101,y,.27),(x+1.5,y,.27),(x+1.899,y,.27),(x+1.901,y,0),(x+1.5,y+.601,0)]:points.append([xx,yy,1]);expected.append(h);envs.append(i)
result=ray.cast(np.array(points));assert result['hit'].all();error=float(abs(result['height']-expected).max());assert error<1e-6 and (result['normal'][:,2]>0).all()
for p,h,face,env in zip(points,expected,result['face_id'],envs):
 assert (face in groups[env]['top_faces'])==(h==.27)
for g in groups:
 top=terrain.vertices[terrain.faces[g['top_faces']]];front=terrain.vertices[terrain.faces[g['front_faces']]]
 assert np.allclose(top[:,:,2],.27,atol=1e-7,rtol=0)
 n=np.cross(front[:,1]-front[:,0],front[:,2]-front[:,0]);assert (n[:,0]<0).all() and np.all(n[:,1:]==0)
try:generate(origins,height=.269)
except ValueError:pass
else:raise AssertionError('Below human minimum accepted')
v=dict(epoch=time.time(),passed_CPU_triangle_and_independent_vertical_oracle_fixture=True,source_path=str(B/'candidate_uninstalled/step270_triangle_geometry_cpu.py'),source_SHA=hashlib.sha256((B/'candidate_uninstalled/step270_triangle_geometry_cpu.py').read_bytes()).hexdigest(),fixture_actual_origins_xy=origins.tolist(),fixture_vertices=vertices.tolist(),fixture_faces=faces.tolist(),face_groups=groups,CPU_rays=len(points),oracle_maxabs_height_error_m=error,no_ramp_and_true_vertical_front_faces=True,all_platform_hit_face_ids_exact=True,height_below270_rejected=True,geometry_design_candidate=dict(height_m=.270,edge_local_x_m=1.1,platform_depth_m=.8,platform_width_m=1.2),not_actual_stage_or_cooked_PhysX_or_native=True,material_not_bound_until_actual_original_material_readback=True,limits='The approach speed/request and terrain layout are candidate parameters. Need actual SDK env origins, collider/world-triangle SHA, cooked query comparison, full-pose legal ground resets, and independent all-row native checks. CPU fixture is not a step-jump result.')
(B/'reports/STEP270_TRIANGLES_AND_VERTICAL_ORACLE_CPU_FIXTURE_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps({k:x for k,x in v.items() if k not in ('fixture_vertices','fixture_faces','face_groups')}))
