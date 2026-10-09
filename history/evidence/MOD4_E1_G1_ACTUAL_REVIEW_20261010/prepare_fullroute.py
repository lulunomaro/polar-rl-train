"""Prepare isolated frozen route coverage correction; no learning or production edit."""
from pathlib import Path
import ast,hashlib,json,time,zipfile
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';A=D/'artifacts';A.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
old=W/'MOD4_E1_RETENTION_REPAIR_20261009/artifacts/e1-g1-cad-derived10mm-fullroute-frozen.zip'
assert sha(old.read_bytes())=='ca8a647affeb6ed5c17b5e73b7362141878f9be5dd76db9a9d7b0e6ebad49279'
with zipfile.ZipFile(old) as z:
 manifest=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in manifest['files']}
assert all(sha(b)==manifest['files'][n] for n,b in payload.items())
entry='runtime/isaac/mod4/frozen_history_flat.py';s=payload[entry].decode()
assert "e=E1ResetEvidenceLearningEnv(cfg=cfg);r=e.scene['robot'];e.reset()" in s
inject="""recipe=configure_intro(cfg)
 # Frozen evaluation alone: same actual mesh, select disjoint wave-family tiles.
 # No family ID/terrain label is given to the actor or gate.
 gen=cfg.scene.terrain.terrain_generator
 assert gen.curriculum and gen.num_rows==gen.num_cols==40
 keys=list(gen.sub_terrains);weights=np.array([gen.sub_terrains[k].proportion for k in keys]);weights/=weights.sum()
 family=np.array([int(np.min(np.where(i/40+.001<np.cumsum(weights))[0])) for i in range(40)])
 cols=np.flatnonzero(family==keys.index('random_uniform_for_rm'));assert len(cols)==6
 size=np.asarray(gen.size,dtype=float);assert np.array_equal(size,[9.,9.])
 ids=np.arange(80);tile_rows=ids//2;tile_cols=cols[ids%2]
 centers=np.stack(((tile_rows+.5)*size[0]-20*size[0],(tile_cols+.5)*size[1]-20*size[1]),axis=-1)
 from g1_cad_wave_geometry import profile
 span=profile()['span_m'];half=span*.5;support=.65
 starts=centers.copy();starts[ids%3==0,0]-=half+support;starts[ids%3==1,0]+=half+support
 assert len(np.unique(np.stack((tile_rows,tile_cols),axis=-1),axis=0))==80
 def whole_route_boundary(env):
  xy=env.scene['robot'].data.root_pos_w[:,:2]-env._g1_whole_route_centers
  return (xy[:,0].abs()>3.5)|(xy[:,1].abs()>3.)
 cfg.terminations.rough_route_boundary.func=whole_route_boundary
 assert cfg.terminations.rough_route_boundary.time_out is True
 e=E1ResetEvidenceLearningEnv(cfg=cfg);r=e.scene['robot']
 e._g1_whole_route_centers=torch.as_tensor(centers,device=e.device,dtype=e.scene.env_origins.dtype)
 e.scene.env_origins[:,:2]=torch.as_tensor(starts,device=e.device,dtype=e.scene.env_origins.dtype)
 e.reset()
 assert torch.allclose(r.data.root_pos_w[:,:2],torch.as_tensor(starts,device=e.device,dtype=r.data.root_pos_w.dtype),atol=1e-6,rtol=0)
 # Verify the selected mesh with actual authored Warp ray queries, independently of requested reset q.
 samples=np.linspace(-half,half,33);xy=np.zeros((80,35,2));xy[:,:,:]=centers[:,None,:]
 xy[:,1:34,0]+=samples;xy[:,0,0]-=half+support;xy[:,34,0]+=half+support
 ray=query(e);sample=ray.cast(torch.as_tensor(xy,device=e.device,dtype=r.data.root_pos_w.dtype),10.)
 assert sample['hit'].all() and (sample['normal'][...,2]>0).all()
 sampled=cpu(sample['height']);assert np.max(abs(sampled[:,[0,34]]))<=1e-6
 assert np.all(np.ptp(sampled[:,1:34],axis=1)>.005) and sampled.max()<=.010001
 route_scope=dict(tile_rows=tile_rows.tolist(),tile_cols=tile_cols.tolist(),family='CAD_derived10mm_wave',tile_centers=centers.tolist(),requested_starts=starts.tolist(),size_m=size.tolist(),wave_x_halfspan_m=half,flat_support_margin_m=support,actual_sampled_ground=sampled.tolist(),actual_sampled_normals=js(sample['normal']),actual_authored_ground_query_passed=True,termination_change='evaluation-only declared truncation at abs x from tile center3.5m or abs y3m',production_boundary_unchanged=True,not_training_or_RM70mm=True)
"""
s=s.replace("recipe=configure_intro(cfg);e=E1ResetEvidenceLearningEnv(cfg=cfg);r=e.scene['robot'];e.reset()",inject.rstrip())
s=s.replace("protocol='approved_E1_G1_derived10mm_route_behavior_v1'","protocol='approved_E1_G1_complete_wave_route_behavior_v2'")
s=s.replace('initial=initial,final=dict(parameters=pd,assignments=assignments(e)),geometry_recipe=recipe,geometry=e.scene.terrain.exact_partition_receipt,','initial=initial,final=dict(parameters=pd,assignments=assignments(e)),geometry_recipe=recipe,geometry=e.scene.terrain.exact_partition_receipt,route_scope=route_scope,body_names=list(r.body_names),')
assert 'route_scope=route_scope' in s;ast.parse(s);payload[entry]=s.encode()
changed={n:sha(b) for n,b in payload.items() if sha(b)!=manifest['files'][n]};assert set(changed)=={entry}
meta=dict(manifest,files={n:sha(b) for n,b in payload.items()},protocol='approved_E1_G1_complete_wave_route_behavior_v2',new_or_changed_members=changed,frozen_reset_route_only_changed=True,geometry_D0_D7_assets_hardware_byteexact=True,steps=1500,num_envs=80,seed=20260928,no_learning=True,no_canonical_write_authority=True)
p=A/'e1-g1-complete-wave-route-v2-frozen.zip';assert not p.exists()
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(meta,indent=2))
out=D/'frozen_fullroute_v2.py';out.write_text(s,encoding='utf8')
# Static installed-SDK family assignment proof; original80 grid is in central plane/ramp columns.
keys=['tiny_step','slope_for_rm_high','inv_slope_for_rm_low','plane_for_rm','random_uniform_for_rm'];weights=np.array([.2,.2,.15,.3,.15]);weights/=weights.sum()
family=[keys[int(np.min(np.where(i/40+.001<np.cumsum(weights))[0]))] for i in range(40)]
cols=[i for i,x in enumerate(family) if x=='random_uniform_for_rm'];bands=[[(i-20)*9.,(i+1-20)*9.] for i in cols]
anchor=json.loads((R/'cases/clk2500-closure-episode-d3-117-e1-g1-anchor-terrain-flat/probe.json').read_bytes())
with np.load(R/'cases/clk2500-closure-episode-d3-117-e1-g1-anchor-terrain-flat/route_raw.npz') as a:
 actual_y=[float(a['COM_link_pos'][...,1].min()),float(a['COM_link_pos'][...,1].max())]
 visited=any(actual_y[1]>=lo and actual_y[0]<=hi for lo,hi in bands);assert not visited
proof=dict(epoch=time.time(),trial_id='E1-G1-ROUTE-COVERAGE-01',installed_generator_source_sha256=sha((R/'INSTALLED_TERRAIN_GENERATOR_REUSED.py').read_bytes()),actual_G1_mesh_SHA=anchor['geometry']['triangle_world_f32_order_sha256'],actual_config_size_m=[9.,9.],curriculum_column_family=family,wave_y_bands_m=bands,original80_actual_all31_body_y_range_m=actual_y,original80_any_body_in_wave_band=False,original80_full_wave_traversal_proved=False,original_117_result_retained_not_reclassified_failed_physics=True,package=dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p.read_bytes())),changed_members=changed,new_scope='same actual G1 mesh, actual full30q reset on disjoint wave tiles, complete before-to-after routes; zero learning',planned_case_pair='rollback32053 versus failed32098, not selecting failed32098 for PPO',new_scope_pending_not_pass=True,new_budget_seconds=0,no_GPU_PPO_or_production_change=True)
(R/'FULL_ROUTE_PREPARED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof,ensure_ascii=True))
