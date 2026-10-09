"""Prepare a labelled 10mm CAD-derived curriculum profile, CPU only."""
from pathlib import Path
import hashlib,json,time
import numpy as np
import trimesh
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=D/'payload/isaac/mod4';P.mkdir(parents=True,exist_ok=True)
assert not (P/'g1_cad_profile.json').exists()
audit=json.loads((W/'RM2026_TERRAIN_AUDIT_20261009/GEOMETRY_AUDIT.json').read_bytes())
source=json.loads((W/'rmuc2026_training/reports/source.json').read_bytes())
row=next(x for x in audit['rough'] if x['part']==181)
mesh_path=W/'rmuc2026_work/extracted/part_181.npz'
with np.load(mesh_path) as a:mesh=trimesh.Trimesh(a['vertices']*.001-np.asarray(source['cad_origin_m']),a['faces'],process=False)
period=float(np.mean(row['cad_exact_peak_spacing_mm']))*.001
center=(row['cad_exact_peaks_m'][0][0]+row['cad_exact_peaks_m'][-1][0])*.5
span=row['cad_section_span_x_mm']*.001
x=np.linspace(center-span*.5+1e-5,center+span*.5-1e-5,2407)
points,ids,_=mesh.ray.intersects_location(np.c_[x,np.full(len(x),6.45),np.full(len(x),2.)],np.tile([0.,0.,-1.],(len(x),1)),multiple_hits=True)
z=np.full(len(x),-np.inf);np.maximum.at(z,ids,points[:,2]);assert np.isfinite(z).all()
assert .065<float(np.ptp(z))<.075
h=(z-z.min())/np.ptp(z);h[0]=0.;h[-1]=0.
v=dict(version=1,revision='MOD4-RM-TERRAIN-CURRICULUM-REVISION-003',scope='E1-G1 CAD-derived scaled curriculum, not real RM70mm or whole arena',source_CAD_sha256=source['sha256'],source_part=181,source_mesh_sha256=hashlib.sha256(mesh_path.read_bytes()).hexdigest(),source_BRep_section_audit_sha256=hashlib.sha256((W/'RM2026_TERRAIN_AUDIT_20261009/GEOMETRY_AUDIT.json').read_bytes()).hexdigest(),period_m=period,span_m=span,profile_x_m=(x-x[0]).tolist(),normalized_height=h.tolist(),derived_peak_to_trough_m=.01,original_tessellation_finite_section_error_mm=row['original_tessellation_vs_exact_section_max_abs_mm'],source_mesh_profile_not_exact_BRep=True,local_floor_is_flat_for_this_derived_scope=True,all_current_other_four_families_and_proportions_retained=True)
raw=json.dumps(v,indent=2).encode();(P/'g1_cad_profile.json').write_bytes(raw)
report=dict(epoch=time.time(),trial_id='E1-G1-CAD-DERIVED-PROFILE-01',profile_sha256=hashlib.sha256(raw).hexdigest(),samples=len(x),source_peak_to_trough_m=float(np.ptp(z)),derived_height_m=.01,period_m=period,span_m=span,no_GPU_PPO_or_budget_operations=True,no_real_RM_completion_claim=True)
(R/'G1_PROFILE_PREPARED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=True))
