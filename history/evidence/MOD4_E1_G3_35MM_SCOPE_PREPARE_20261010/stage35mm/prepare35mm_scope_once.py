"""Preserve complete124 tradeoff and prepare only the approved next35mm geometry."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,zipfile,traceback
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
def put(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 R.mkdir(parents=True,exist_ok=True)
 put('PREPARE_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-CPU-GEOMETRY-01',no_GPU_PPO=True))
 C=W/'MOD4_E1_G2_MATCHED_CONTINUE_20261010';old=W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010'
 review_path=sorted((C/'reports').glob('CONTINUATION_124_REVIEW_*.json'))[-1];review=json.loads(review_path.read_bytes());assert review['review_complete'] and not review['pending']
 final=json.loads((C/'reports/FINAL_ACTUAL_VERIFIED_1791571039.json').read_bytes());assert final['active_Sactive_empty'] and final['parent_guardian_child_actual_exited'] and final['source_count']==330
 selected=json.loads((C/'reports/SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json').read_bytes());source=selected['source'];assert source['sha256']=='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b' and source['finite_tensors']==96
 prior=json.loads((C/'reports/MATCHED_123_REVIEW.json').read_bytes());assert prior['review_complete']
 groups={}
 for role in ('baseline32053','candidate'):
  rows=review['retention']['world'][role]['world_target']['rows'];groups[role]={}
  for yaw in (-2.,-1.,1.,2.):
   a=[x for x in rows if x['command_yaw_rad_s']==yaw]
   groups[role][str(yaw)]=dict(count=len(a),passed=sum(x['pass_'] for x in a),mean_cross_m_s=float(np.mean([x['cross_m_s'] for x in a])),max_abs_cross_m_s=max(abs(x['cross_m_s']) for x in a),all_full_signed_cycles_retained=True)
 put('CANDIDATE124_RETENTION_DECISION.json',dict(epoch=time.time(),trial_id='E1-G2-124-COMPLETE-RETENTION-DECISION-01',review_path=str(review_path),review_sha256=H(review_path.read_bytes()),own_final_SHA=final['checkpoint']['sha256'],source32103_not_selected_for_further_learning=True,world63_to62_to49_of64_actual=True,world_direction_groups=groups,terrain_forward_reverse27_of27=review['summary']['terrain'],flat_spin_world_all_actual_complete=True,original_flags_and_cost_preserved=True,decision='Use the earlier complete matched32058 for the next approved35mm frozen geometry admission; do not add more blind20mm PPO.',reason='After900s, signed yaw2 cross drift worsens across both directions; terrain traversal improved but this is not permanent retention repair.',causality='Narrow stand/slow yaw0 commands are a plausible forgetting cause, not a proved causal mechanism.',no_fixed_percentage_graduation_line=True,no_new_training_or_70_20_10_mix=True,new_budget_seconds=0))
 put('SELECTED_E1_G3_FROZEN_SCOPE_SOURCE.json',dict(epoch=time.time(),source=source,bytes=16750577,source_count=329,snapshot_count=62,finite_tensors=96,behavior_review_complete=True,paired_cases=prior['retention'],terrain_review=prior['terrain']['groups'],source_selected_by_actual_behavior_not_iteration=True,old_32053_and_32103_and_costs_retained=True,selected_for_frozen_scope_only=True,no_G3_learning_admission_yet=True))
 oldpkg=old/'artifacts/e1-g2-derived20mm-complete-route-frozen.zip';assert H(oldpkg.read_bytes())=='c4255fe5c3407a42019416fdffa6d6786a51b84ae4312f6e362e2b2a60ba1271'
 with zipfile.ZipFile(oldpkg) as z:members={n:z.read(n) for n in z.namelist()}
 prefix='runtime/isaac/mod4/'
 profile=json.loads(members[prefix+'g2_cad_profile.json']);assert profile['derived_peak_to_trough_m']==.02
 profile['derived_peak_to_trough_m']=.035;profile['scope']='E1-G3 CAD-derived scaled curriculum, not real RM70mm or whole arena'
 (D/'payload').mkdir();p=D/'payload/g3_cad_profile.json';p.write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf8')
 original=members[prefix+'g2_cad_wave_geometry.py'].decode('utf8')
 geometry=original.replace('g2_cad_profile.json','g3_cad_profile.json').replace('configure_g2','configure_g3').replace('G2','G3').replace('g2','g3').replace('20mm','35mm').replace('_20mm','_35mm').replace('.02','.035')
 assert original.count('.02')==4;ast.parse(geometry)
 g=D/'payload/g3_cad_wave_geometry.py';g.write_text(geometry,encoding='utf8')
 spec=importlib.util.spec_from_file_location('g3_cpu',g);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 mesh,origin=mod.make_mesh((9.,9.));vertices=mesh.vertices;faces=mesh.faces;start=(9.-profile['span_m'])/2
 xs=np.r_[np.linspace(.05,8.95,200),start+np.array(profile['profile_x_m'])[np.argmax(profile['normalized_height'])],start,start+profile['span_m']]
 # Independent vertical rays via triangle XY barycentric coordinates, not the generator interpolation.
 triangles=vertices[faces];errors=[]
 for x in xs:
  y=2.1;lo=triangles[:,:,:2].min(1);hi=triangles[:,:,:2].max(1);chosen=np.flatnonzero((lo[:,0]<=x)&(hi[:,0]>=x)&(lo[:,1]<=y)&(hi[:,1]>=y));hits=[]
  for f in chosen:
   tri=triangles[f];weights=np.linalg.solve(np.vstack((tri[:,:2].T,np.ones(3))),np.array([x,y,1.]))
   if weights.min()>=-1e-9:hits.append(float(weights@tri[:,2]))
  assert hits,'CPU ray misses actual authored mesh'
  expected=float(np.interp(x-start,profile['profile_x_m'],np.array(profile['normalized_height'])*.035,left=0,right=0));errors.append(abs(max(hits)-expected))
 assert max(errors)<1e-12 and abs(np.ptp(vertices[:,2])-.035)<1e-12 and np.min(mesh.face_normals[:,2])>0
 oldprofile=json.loads(members[prefix+'g2_cad_profile.json']);assert all(profile[k]==oldprofile[k] for k in ('profile_x_m','normalized_height','period_m','span_m','source_CAD_sha256','source_mesh_sha256','original_tessellation_finite_section_error_mm'))
 put('CPU_GEOMETRY_REVIEW.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-CPU-GEOMETRY-01',actual_authored9m_mesh=True,peak_to_trough_m=.035,period_m=profile['period_m'],span_m=profile['span_m'],flat_support_each_m=start,independent_vertical_rays=len(xs),max_error_m=max(errors),positive_upward_triangle_normals=True,normalized_CAD_x_waveform_original_exact=True,other_four_families_and_proportions_unchanged=True,original_finite_section_tessellation_error_mm=profile['original_tessellation_finite_section_error_mm'],no_SDK_GPU_PPO_or_clock_experiment=True))
 dispatcher=members[prefix+'frozen_history_flat.py'].decode('utf8').replace('g2_cad_wave_geometry','g3_cad_wave_geometry').replace('configure_g2','configure_g3').replace('G2','G3').replace('derived20mm','derived35mm').replace('CAD_derived20mm','CAD_derived35mm').replace('sampled.max()<=.020001','sampled.max()<=.035001')
 assert 'derived20mm' not in dispatcher and 'g2_cad_wave_geometry' not in dispatcher;ast.parse(dispatcher)
 (D/'frozen35mm_route.py').write_text(dispatcher,encoding='utf8')
 new=dict(members);new[prefix+'g3_cad_profile.json']=p.read_bytes();new[prefix+'g3_cad_wave_geometry.py']=g.read_bytes();new[prefix+'frozen_history_flat.py']=dispatcher.encode()
 changed=[n for n in new if n not in members or new[n]!=members[n]];assert set(changed)=={prefix+'g3_cad_profile.json',prefix+'g3_cad_wave_geometry.py',prefix+'frozen_history_flat.py'}
 (D/'artifacts').mkdir();pkg=D/'artifacts/e1-g3-derived35mm-complete-route-frozen.zip'
 with zipfile.ZipFile(pkg,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for n,b in new.items():z.writestr(n,b)
 m=json.loads((C/'reports/cases/clk2500-closure-episode-d3-123-e1-g2-observation-terrain-flat/manifest.json').read_bytes()) if (C/'reports/cases/clk2500-closure-episode-d3-123-e1-g2-observation-terrain-flat/manifest.json').exists() else json.loads((W/'MOD4_E1_G2_LEARNING_PREPARE_20261010/reports/cases/clk2500-closure-episode-d3-123-e1-g2-observation-terrain-flat/manifest.json').read_bytes())
 assert m['artifacts']['checkpoint']['sha256']==source['sha256'] and '/artifacts/' in m['artifacts']['checkpoint']['path']
 m.update(protocol='approved_E1_G3_derived35mm_complete_wave_route_behavior_v1',role='reviewed32058_next35mm_geometry',actual_behavior_scope='003 derived35mm next geometric axis frozen scope: actual front support, two-wheel complete10-wave traversal and rear support. No new learning.',no_learning=True,no_auto_new_PPO=True,scope_pending_actual_review=True,canonical_write_authority=False,geometry_curriculum_revision='MOD4-RM-TERRAIN-CURRICULUM-REVISION-003')
 m.pop('job_id',None);m.pop('published_epoch',None)
 put('MANIFEST_TEMPLATE.json',m)
 put('PREPARED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-FROZEN-PREPARE-01',package=dict(path=str(pkg.resolve()),bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes())),protocol=m['protocol'],selected_source=source,changed_or_added_members=changed,all_other_original_DR_assets_hardware_and_geometry_byteexact=True,previous_G2_package_sha256=H(oldpkg.read_bytes()),CPU_geometry_only=True,no_SDK_native_PPO_or_learning_executor_deployed=True,actual_35mm_behavior_pending=True,new_budget_seconds=0))
 print(json.dumps(dict(prepared=str(R/'PREPARED.json'),source_SHA=source['sha256'],package_SHA=H(pkg.read_bytes()),CPU_ray_error=max(errors),new_budget_seconds=0)))
if __name__=='__main__':
 try:main()
 except Exception:
  R.mkdir(parents=True,exist_ok=True);put('PREPARE_ERROR.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-CPU-GEOMETRY-01',error=traceback.format_exc(),old_reports_and_source_retained=True,no_production_change=True));raise
