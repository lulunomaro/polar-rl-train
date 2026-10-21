from pathlib import Path
import hashlib,json,time,numpy as np
T=Path(__file__).resolve().parent;R=T/'reports';L=T/'relocated_forensic_originals/H1step270_pairV1_closed_control318'
v=json.loads((T/'cooked_query_full20k_V9_actual/out/ACTUAL_COOKED_VS_AUTHORED_STEP270_QUERY_RESULT.json').read_bytes())
origins=np.array([[r['actual_Float3_origin'][0]-.25,r['actual_Float3_origin'][1]] for r in v['front_rows']],dtype=np.float64)
lower=origins.min(0)-2.5;upper=origins.max(0)+2.5
z=np.load(L/'control_prefix_13.npz');root=z['root13'];done=z['done'].astype(bool);outside=((root[:,:,:2]<lower)|(root[:,:,:2]>upper)).any(-1)
rows=[]
for control,env in np.argwhere(outside):
 rows.append(dict(control=int(control)+312,env=int(env),root13=root[control,env].tolist(),actual_done=bool(done[control,env]),env_origin_xy=origins[env].tolist(),outside_global_authored_floor=True))
last=[x for x in rows if x['control']==317]
out=dict(epoch=time.time(),source_actual_failed_control_completed_rows=318,original_exception='Step270 actual terrain query missing/invalid; no flat fallback',scope='CPU analysis of recorded last successful pre-selected-reset frame; failed query hit mask/origin was not saved and exact failing env remains unproven',actual_geometry_ordered_triangle_SHA=v['ordered_triangle_SHA'],actual_floor_xy_bounds=[lower.tolist(),upper.tolist()],last6_controls_root_z_minmax=[float(root[:,:,2].min()),float(root[:,:,2].max())],last6_recorded_outside_rows=rows,last_frame_outside_count=len(last),last_frame_outside_not_done=[x for x in last if not x['actual_done']],finite_root13=bool(np.isfinite(root).all()),physical_query1um_not_in_exception_path=True,no_tolerance_or_mesh_or_reward_changed=True,no_GPU_or_scene_query_replay=True,not_a_repair_or_new_admission=True)
with (R/'H1_FAILED_CONTROL318_RECORDED_WORLD_FLOOR_BOUNDS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
