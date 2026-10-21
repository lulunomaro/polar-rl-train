from pathlib import Path
import hashlib,json,sys,time
import numpy as np

B=Path(__file__).resolve().parent;R=B/'reports';P=B/'H1_step270_native32_V4_payload'
sys.path.insert(0,str(P));from step270_triangle_geometry_cpu import generate
receipt=json.loads((R/'STEP270_COOKED_QUERY_V5_FINITE_RETURNED_ACTUAL.json').read_bytes())
assert not receipt['pending'] and receipt['parent_complete']['passed'] and not receipt['parent_complete']['errors']
assert receipt['parent_exit']['all_own_children_waited'] and receipt['parent_exit']['own_eval_lease_released'] and not receipt['actual_own_live']
v=json.loads((B/'cooked_query_V5_actual/out/ACTUAL_COOKED_VS_AUTHORED_STEP270_QUERY_RESULT.json').read_bytes())
assert v['passed'] and v['num_envs']==32 and len(v['all_rows'])==224 and len(v['front_rows'])==32 and v['original_query_threshold_m']==1e-6
origins=np.array([x['origin'][:2] for x in v['all_rows'] if x['tag']=='lower_floor_under_robot']);assert origins.shape==(32,2)
vertices,faces,groups=generate(origins,**v['geometry']);tri=vertices[faces]
assert hashlib.sha256(tri.astype('<f4').tobytes()).hexdigest()==v['ordered_triangle_SHA']
a=tri[:,0].astype(np.float64);ab=tri[:,1].astype(np.float64)-a;ac=tri[:,2].astype(np.float64)-a
def cast(o,d,distance):
    o=np.array(o,np.float64);d=np.array(d,np.float64);h=np.cross(np.broadcast_to(d,ac.shape),ac);det=np.einsum('ij,ij->i',ab,h);valid=np.abs(det)>1e-12;inv=np.divide(1.,det,out=np.zeros_like(det),where=valid);s=o-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,ab);vv=inv*np.einsum('j,ij->i',d,q);tt=inv*np.einsum('ij,ij->i',ac,q);valid&=(u>=-1e-10)&(vv>=-1e-10)&(u+vv<=1+1e-10)&(tt>=0)&(tt<=distance);assert valid.any();dist=np.where(valid,tt,np.inf);i=int(dist.argmin());normal=np.cross(ab[i],ac[i]);normal/=np.linalg.norm(normal);return o+d*dist[i],normal,int(i)
maxpos=maxnormal=0.;rows=[]
for row,d,distance in [(x,(0,0,-1),4.) for x in v['all_rows']]+[(x,(1,0,0),.2) for x in v['front_rows']]:
    p,n,face=cast(row['origin'],d,distance);hit=row['cooked'];assert hit['collision'].startswith('/World/ground/')
    pe=float(np.abs(np.asarray(hit['position'])-p).max());ne=float(np.abs(np.asarray(hit['normal'])-n).max());maxpos=max(maxpos,pe);maxnormal=max(maxnormal,ne)
    rows.append(dict(env=row['env'],tag=row.get('tag','vertical_front_face'),independent_triangle=face,position_error_m=pe,normal_error=ne,expected_position=p.tolist(),expected_normal=n.tolist(),cooked_position=hit['position'],cooked_normal=hit['normal']))
out=dict(epoch=time.time(),passed=maxpos<=1e-6 and maxnormal<=1e-6,source_SHA=v['source_SHA'],source_Adam=674740,actual_cooked_scene_queries=256,independent_Moller_Trumbore_triangle_rows=rows,actual_cooked_vs_independent_position_maxabs_m=maxpos,actual_cooked_vs_independent_normal_maxabs=maxnormal,original_1um_query_guard_unchanged=True,ordered_authored_triangle_SHA=v['ordered_triangle_SHA'],all_own_children_out_and_lease_released=True,actual_read_only_zero_optimizer_no_learning_GO=True,not_20k_admission_or_skill_PASS=True,old_V1_to_V4_errors_preserved=True)
with (R/'STEP270_COOKED_QUERY_V5_ALL256_CPU_V2_DIAGNOSTIC_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps({k:x for k,x in out.items() if k!='independent_Moller_Trumbore_triangle_rows'}))
