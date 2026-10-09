"""Prepare only next approved single geometric axis; no installed runtime or GPU authority."""
from pathlib import Path
import json,ast,hashlib,sys,time
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';old=W/'MOD4_E1_RETENTION_REPAIR_20261009/payload/isaac/mod4';new=D/'next20mm_cpu';assert not new.exists();new.mkdir()
H=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((old/'g1_cad_profile.json').read_bytes());original=json.loads(json.dumps(p));p['derived_peak_to_trough_m']=.02;p['scope']=p['scope'].replace('E1-G1','E1-G2')
assert p['profile_x_m']==original['profile_x_m'] and p['normalized_height']==original['normalized_height']
(new/'g2_cad_profile.json').write_text(json.dumps(p,indent=2),encoding='utf8')
s=(old/'g1_cad_wave_geometry.py').read_text(encoding='utf8').replace('10mm','20mm').replace('10mm','20mm').replace('10mm','20mm').replace('g1_cad_profile','g2_cad_profile').replace('configure_g1','configure_g2').replace('G1','G2').replace('_10mm_','_20mm_').replace('.01','.02')
ast.parse(s);(new/'g2_cad_wave_geometry.py').write_text(s,encoding='utf8');sys.path.insert(0,str(new));from g2_cad_wave_geometry import profile,make_mesh
v=profile();mesh,origin=make_mesh((9.,9.));assert abs(np.ptp(mesh.vertices[:,2])-.02)<1e-12 and (mesh.face_normals[:,2]>0).all()
assert np.array_equal(np.unique(mesh.vertices[:,1]),[0.,9.]);assert mesh.vertices[0,2]==mesh.vertices[-1,2]==0
support=(9.-v['span_m'])*.5;assert support>3.
rng=np.random.default_rng(20261010);xy=rng.uniform(.001,8.999,(200,2));loc,ids,_=mesh.ray.intersects_location(np.c_[xy,np.ones(200)],np.tile([0.,0.,-1.],(200,1)),multiple_hits=False)
assert len(ids)==200;expected=np.interp(xy[:,0]-support,v['profile_x_m'],v['normalized_height'],left=0.,right=0.)*.02
error=float(np.max(abs(loc[:,2]-expected[ids])));assert error<1e-10
report=dict(epoch=time.time(),trial_id='E1-G2-20MM-GEOMETRY-CPU-PREPARE-01',passed_CPU_geometry_only=True,actual9m_tile_fixture=True,peak_to_trough_m=.02,period_m=v['period_m'],full_span_m=v['span_m'],normalized_CAD_profile_and_x_exact=True,flat_support_each_m=support,independent_rays=200,ray_error_m=error,files=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=H(q.read_bytes())) for q in new.iterdir() if q.is_file()],source_old_geometry_SHA=H((old/'g1_cad_wave_geometry.py').read_bytes()),no_SDK_GPU_PPO_executor_or_deployment=True,no_runtime_canonical_or_budget_write=True,not_real_RM70mm=True,next_actual_new_geometry_contact_ground_reset_fullresume_scope_required=True)
(R/'NEXT20MM_GEOMETRY_CPU_PREPARED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='files'}))
