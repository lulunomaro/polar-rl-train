"""Independent geometric checks before any installed SDK/GPU trial."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D/'payload/isaac/mod4'))
from g1_cad_wave_geometry import make_mesh,profile
p=profile();mesh,origin=make_mesh((8.,8.))
assert abs(np.ptp(mesh.vertices[:,2])-.01)<1e-12
assert mesh.vertices[:,0].min()==0 and mesh.vertices[:,0].max()==8
assert mesh.vertices[:,1].min()==0 and mesh.vertices[:,1].max()==8
assert mesh.vertices[0,2]==mesh.vertices[-1,2]==0
assert np.isfinite(mesh.vertices).all() and np.isfinite(origin).all()
assert (mesh.face_normals[:,2]>0).all()
assert len(mesh.faces)==2*(len(np.unique(mesh.vertices[:,0]))-1)
support=(8.-p['span_m'])*.5;assert support>2.
# Independent ray hits at random interior x/y must equal piecewise-linear profile.
rng=np.random.default_rng(20261009);xy=rng.uniform(.001,7.999,(200,2))
loc,ids,_=mesh.ray.intersects_location(np.c_[xy,np.full(200,1.)],np.tile([0.,0.,-1.],(200,1)),multiple_hits=False)
assert len(ids)==200
expected=np.interp(xy[:,0]-support,p['profile_x_m'],p['normalized_height'],left=0.,right=0.)*.01
error=float(np.max(np.abs(loc[:,2]-expected[ids])));assert error<1e-10
for bad in ((1.,8.),(8.,0.),(-8.,8.)):
 try:make_mesh(bad)
 except AssertionError:pass
 else:raise AssertionError('Invalid size accepted')
out=dict(epoch=time.time(),trial_id='E1-G1-GEOMETRY-CPU-01',passed=True,independent_random_ray_points=200,ray_height_error_m=error,flat_entry_exit_support_each_m=support,derived_peak_to_trough_m=.01,profile_sha256=hashlib.sha256((D/'payload/isaac/mod4/g1_cad_profile.json').read_bytes()).hexdigest(),no_GPU_PPO_or_budget_operations=True)
path=R/'G1_GEOMETRY_CPU_PASSED.json';assert not path.exists();path.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=True))
