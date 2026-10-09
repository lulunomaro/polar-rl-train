"""Retain the rejected two-coordinate ray preparation; correct to the installed SDK xyz shape."""
from pathlib import Path
import ast,hashlib,json,time,zipfile
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';A=D/'artifacts';sha=lambda b:hashlib.sha256(b).hexdigest()
old=A/'e1-g1-complete-wave-route-v2-frozen.zip'
with zipfile.ZipFile(old) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
entry='runtime/isaac/mod4/frozen_history_flat.py';s=payload[entry].decode()
bad="ray=query(e);sample=ray.cast(torch.as_tensor(xy,device=e.device,dtype=r.data.root_pos_w.dtype),10.)"
assert bad in s
fixed="ray=query(e);ray_starts=np.concatenate((xy,np.full((80,35,1),float(ray.geometry.vertices[:,2].max())+2.)),axis=-1)\n sample=ray.cast(torch.as_tensor(ray_starts,device=e.device,dtype=r.data.root_pos_w.dtype),10.)"
s=s.replace(bad,fixed).replace('approved_E1_G1_complete_wave_route_behavior_v2','approved_E1_G1_complete_wave_route_behavior_v3')
ast.parse(s);payload[entry]=s.encode();m.update(files={n:sha(b) for n,b in payload.items()},protocol='approved_E1_G1_complete_wave_route_behavior_v3',rejected_v2_retained=True)
p=A/'e1-g1-complete-wave-route-v3-frozen.zip';assert not p.exists()
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(m,indent=2))
(D/'frozen_fullroute_v3.py').write_text(s,encoding='utf8')
weights=np.array([.2,.2,.15,.3,.15]);weights/=weights.sum();families=np.array([np.where(i/40+.001<np.cumsum(weights))[0].min() for i in range(40)]);cols=np.flatnonzero(families==4)
assert np.array_equal(cols,np.arange(34,40));ids=np.arange(80);rows=ids//2;cs=cols[ids%2]
centers=np.stack(((rows+.5)*9.-180.,(cs+.5)*9.-180.),axis=-1);span=2.4064227271861265;half=span/2;starts=centers.copy();starts[ids%3==0,0]-=half+.65;starts[ids%3==1,0]+=half+.65
assert len(np.unique(np.stack((rows,cs),axis=-1),axis=0))==80
assert ((cs>=34)&(cs<40)).all() and ((rows>=0)&(rows<40)).all()
assert np.all(abs(starts-centers)<3.5)
assert np.allclose(starts[ids%3==0,0]-centers[ids%3==0,0],-half-.65)
assert np.allclose(starts[ids%3==1,0]-centers[ids%3==1,0],half+.65)
assert span+1.3<.3*15
assert 3.5<4.5 and half+.65<3.5
xyz=np.concatenate((np.zeros((80,35,2)),np.full((80,35,1),3.)),axis=-1);assert xyz.shape==(80,35,3)
base=D.parent/'MOD4_E1_RETENTION_REPAIR_20261009/artifacts/e1-g1-cad-derived10mm-fullroute-frozen.zip'
with zipfile.ZipFile(base) as z:
 bm=json.loads(z.read('SOURCE_MANIFEST.json'));assert all(payload[n]==z.read(n) for n in bm['files'] if n!=entry)
v=dict(epoch=time.time(),trial_id='E1-G1-ROUTE-XYZ-SHAPE-02',retained_pre_GPU_rejection=dict(id='E1-G1-ROUTE-XY-SHAPE-01',path=str(old.resolve()),sha256=sha(old.read_bytes()),error='Installed AuthoredTerrainRaycast.cast requires [environment,ray,xyz]; draft supplied xy. Detected during source review before queue publication; never GPU-run.'),CPU=dict(passed=True,unique80_disjoint_wave_tiles=True,installed_curriculum_assignment_exact=True,forward_reverse_stand_starts_audited=True,flat_support_and_tile_bounds_checked=True,nominal15s_time_to_full_route_feasible_not_actual_success=True,SDK_ray_xyz_shape=True,all_original_geometry_DR_assets_hardware_members_byteexact=True,no_terrain_truth_actor_input=True,AST_parse_passed=True),package=dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p.read_bytes())),protocol=m['protocol'],actual_fullroute_pending=True,no_learning_or_canonical_or_production_write=True,new_budget_seconds=0)
(R/'FULL_ROUTE_XYZ_CPU_PREPARED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,ensure_ascii=True))
