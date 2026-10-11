"""Full143 decision, exact142 comparison, and approved new50mm frozen component; no GPU/PPO."""
from second_io import *
import copy,ast,zipfile,importlib.util
import numpy as np
read=lambda p:json.loads(p.read_bytes())
def main():
 vpath=sorted(R.glob('WAVE143_REVIEW_[0-9]*.json'))[-1];v=read(vpath)
 selected=read(sorted(R.glob('WAVE143_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1]);trace=read(sorted(R.glob('SECOND_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json'))[-1])
 assert v['review_complete'] and selected['review_complete'] and trace['passed'] and trace['actual_controls']==2400
 before=read(PRIOR/'reports/WAVE142_REVIEW_1791728749.json');oldc=read(Path(before['collection']));newc=read(Path(v['collection']))
 assert before['review_complete'] and len(oldc['cases'])==len(newc['cases'])==4
 import review_second_candidate_reset_schema_actual as reviewer
 terrain=lambda c:next(x['probe'] for x in c['cases'].values() if 'full_route_raw' in x['probe'])
 a,b=terrain(oldc),terrain(newc)
 for k in ('initial','geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert a[k]==b[k],k
 sensor=reviewer.final_sensor_receipt_pair(b,a);pairs={}
 for kind in ('flat','spin','world'):
  ps=[next(x['probe'] for x in c['cases'].values() if x['manifest']['kind']==kind and 'full_route_raw' not in x['probe']) for c in (oldc,newc)]
  for k in ('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments'):assert ps[0][k]==ps[1][k],(kind,k)
  params=lambda p:p.get('initial_parameter_audit') or p.get('mild_initial_parameters');assert params(ps[0])==params(ps[1])
  pairs[kind]=dict(source368=before['retention'][kind]['candidate'],candidate369=v['retention'][kind]['candidate'],candidate_reset_audit=v['retention'][kind]['reset_audit'],initial30q_parameters_recipes_assignments_exact=True)
 changed=[]
 oldrows={x['env']:x for x in before['terrain']['full_route_rows']}
 for row in v['terrain']['full_route_rows']:
  if row['group']=='stand':continue
  prev=oldrows[row['env']];changed.append(dict(env=row['env'],group=row['group'],before_complete=bool(prev['complete_episodes']),after_complete=bool(row['complete_episodes']),before_segments=prev['segments'],after_segments=row['segments']))
 pair=save('WAVE143_DIRECT142_MATCHED_FULL_REVIEW.json',dict(epoch=time.time(),source142_checkpoint_SHA=before['own']['checkpoint']['sha256'],candidate143_checkpoint_SHA=v['own']['checkpoint']['sha256'],source_full_review=str(PRIOR/'reports/WAVE142_REVIEW_1791728749.json'),candidate_full_review=str(vpath),source_review_SHA=H((PRIOR/'reports/WAVE142_REVIEW_1791728749.json').read_bytes()),candidate_review_SHA=H(vpath.read_bytes()),terrain_initial_geometry_all30q_parameters_recipes_assignments_exact=True,final_sensor_receipt=sensor,retention=pairs,all54_direction_rows_original_prefixes=changed,full_raw_and_original_flags_preserved=True,no_GPU_budget_or_result_write=True))
 t=v['terrain'];g=t['groups'];assert g['forward']['complete_envs']==g['reverse']['complete_envs']==27
 assert all(x['complete_episodes'] for x in t['full_route_rows'] if x['group']!='stand')
 cpu=read(sorted(R.glob('SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]);assert cpu['passed'] and cpu['closeout_ready']
 checkpoint=v['own']['checkpoint'];base=t['base_review']
 decision=dict(epoch=time.time(),trial_id='WAVE369-143-COMPLETE-OBSERVED35MM-SCOPE-DECISION',root=ROOT,source_count=369,own_checkpoint=checkpoint,all_four_cases_complete_errorfree_and_full_raw_reviewed=True,two_host_eight_JSON_byteSHA_exact=True,terrain_raw=a['full_route_raw'] if False else b['full_route_raw'],selected129_forward=24,source142_forward=25,candidate_forward=27,candidate_reverse=27,ordinary=base['ordinary'],unique_truncations=base['unique_truncations'],closure_mm=base['closure_mm'],observed35mm_complete_ten_wave_scope_accepted_and_frozen=True,only_observed35mm_scope_not_entire_WAVE_RM70mm_or_MoE=True,standing26_not_required_to_cross=True,original_skill_strictfalse_and_spin_physical_smoke_false_preserved=True,spin_env8_first_failure_control=370,spin_env8_episode_increment=1,selected129_diagnostics=selected['summary']['retention'],direct142_review=str(pair),full_training_trace_passed=str(sorted(R.glob('SECOND_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json'))[-1]),formal_ordinary_event_control1566_env2372_retained=True,automatic_third_same_repair_PPO_disallowed=True,E0_frozen=True,gate_untrained=True,hardware_uncalibrated=True,no_permanent_anti_forgetting_or_causal_gain_claim=True,next_approved_single_axis='RM003 derived50mm frozen fullroute from own369 b026, no learning unless actual need and new scope full admission',new_budget_seconds=0)
 save('WAVE143_COMPLETE_OBSERVED_SCOPE_DECISION.json',decision)
 parent=W/'MOD4_E1_G3_MATCHED_REVIEW_20261010/artifacts/e1-g3-derived35mm-paired-approach040-frozen-v2.zip';assert H(parent.read_bytes())=='858ad4ef431f188f3275dc8b3c3690bf1d987a5c074f9aed698e15343ad66d2b'
 with zipfile.ZipFile(parent) as z:members={n:z.read(n) for n in z.namelist()}
 manifest=read_manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[n])==h for n,h in manifest['files'].items())
 impl=D/'next_wave50_scope';assert not impl.exists();impl.mkdir()
 gp='runtime/isaac/mod4/g4_cad_wave_geometry.py';pp='runtime/isaac/mod4/g4_cad_profile.json';fp='runtime/isaac/mod4/frozen_history_flat.py'
 geom=members['runtime/isaac/mod4/g3_cad_wave_geometry.py'].decode().replace('.035','.050').replace('35mm','50mm').replace('35mm','50mm').replace('g3_cad_profile','g4_cad_profile').replace('G3','G4').replace('g3','g4')
 profile=json.loads(members['runtime/isaac/mod4/g3_cad_profile.json']);profile['derived_peak_to_trough_m']=.05
 profile=json.loads(json.dumps(profile).replace('E1-G3','E1-G4').replace('derived35mm','derived50mm'))
 (impl/'g4_cad_wave_geometry.py').write_bytes(geom.encode());(impl/'g4_cad_profile.json').write_bytes(json.dumps(profile,indent=2).encode())
 spec=importlib.util.spec_from_file_location('wave50_cpu',impl/'g4_cad_wave_geometry.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mesh,_=mod.make_mesh((9.,9.));verts=mesh.vertices.copy();verts[:,:2]-=4.5
 centers=(np.arange(80)//2+.5)*9.-180.;half=profile['span_m']/2;requested=np.r_[-half-.4,np.linspace(-half,half,33),half+.4]
 origins=np.asarray(centers[:,None]+requested,dtype=np.float32).astype(np.float64);actual=origins-centers[:,None]
 tri=verts[mesh.faces];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];direction=np.array([0.,0.,-1.]);cross=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,cross);assert np.all(abs(det)>1e-12)
 errors=[]
 for x in actual.ravel():
  origin=np.array([x,0.,2.]);delta=origin-tri[:,0];u=np.einsum('ij,ij->i',delta,cross)/det;q=np.cross(delta,e1);w=q@direction/det;dist=np.einsum('ij,ij->i',e2,q)/det
  hits=(u>=-1e-12)&(w>=-1e-12)&(u+w<=1+1e-12)&(dist>=0);assert hits.any();height=2.-dist[hits].min()
  expected=np.interp(x+half,np.asarray(profile['profile_x_m']),np.asarray(profile['normalized_height'])*.05,left=0.,right=0.);errors.append(abs(height-expected))
 assert max(errors)<1e-10 and abs(np.ptp(mesh.vertices[:,2])-.05)<1e-12 and (mesh.face_normals[:,2]>0).all()
 old=members[fp].decode();proto='approved_E1_G4_derived50mm_actualray_approach040_fullroute_behavior_v1'
 new=old.replace('g3_cad_wave_geometry','g4_cad_wave_geometry').replace('configure_g3','configure_g4').replace('CAD_derived35mm_wave','CAD_derived50mm_wave').replace('0.035001','0.050001').replace('approved_E1_G3_derived35mm_paired_approach040_behavior_v2',proto)
 anchor="    sampled = cpu(sample['height'])\n";assert new.count(anchor)==1
 extra="""    sampled = cpu(sample['height'])
    actual_world_ray_origins=cpu(torch.as_tensor(ray_starts,device=e.device,dtype=root_xy.dtype))
    actual_canonical_ray_x=actual_world_ray_origins[:,:,0].astype(np.float64)-centers[:,None,0]
    wave_profile=profile()
    expected_actual_ground=np.interp(actual_canonical_ray_x+half,np.asarray(wave_profile['profile_x_m']),np.asarray(wave_profile['normalized_height'])*.05,left=0.,right=0.)
    actual_query_height_error=float(np.max(abs(sampled-expected_actual_ground)))
    assert actual_query_height_error<=1e-6
"""
 new=new.replace(anchor,extra).replace('actual_sampled_ground=sampled.tolist(),','actual_sampled_ground=sampled.tolist(),actual_world_ray_origins=actual_world_ray_origins.tolist(),actual_canonical_ray_x=actual_canonical_ray_x.tolist(),expected_actual_sampled_ground=expected_actual_ground.tolist(),actual_query_height_error_m=actual_query_height_error,actual_query_ground_tolerance_m=1e-6,')
 loop=lambda s:next(n for n in next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='main').body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
 assert ast.dump(loop(old),include_attributes=False)==ast.dump(loop(new),include_attributes=False);compile(new,fp,'exec');(impl/'frozen_history_flat_WAVE50.py').write_bytes(new.encode())
 changes={gp:geom.encode(),pp:(impl/'g4_cad_profile.json').read_bytes(),fp:new.encode()};members.update(changes)
 manifest.update(protocol=proto,parent_archive_sha256=H(parent.read_bytes()),current_geometry_revision004='E1_WAVE50',current_frozen_scope=dict(peak_to_trough_m=.05,full_span_m=profile['span_m'],approach_m=.4,after_support_m=.2,steps=1500,num_envs=80,seconds=15,learning=False),actualfloat32query_identity_ground_tolerance_m=1e-6,original_control_loop_AST_exact=True)
 manifest['files']={n:H(raw) for n,raw in members.items() if n!='SOURCE_MANIFEST.json'};manifest['new_or_changed_members']={n:H(raw) for n,raw in changes.items()};members['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
 pkg=impl/'e1-g4-derived50mm-actualray-approach040-fullroute-frozen-v1.zip'
 with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED) as z:
  for n,raw in members.items():z.writestr(n,raw)
 with zipfile.ZipFile(pkg) as z:assert all(H(z.read(n))==h for n,h in manifest['files'].items())
 info=dict(path=str(pkg.resolve()),bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes()))
 save('WAVE50_COMPONENT_FROZEN_PREPARED.json',dict(epoch=time.time(),package=info,protocol=proto,profile=profile,source_checkpoint=checkpoint,parent_archive_SHA=H(parent.read_bytes()),all_file_map_SHA_verified=len(manifest['files']),old_members_byteexact_except_dispatcher_manifest=True,new_members=[gp,pp],full_control_loop_AST_exact=True,independent_triangle_actual_float32_rays=len(errors),maximum_height_error_m=max(errors),positive_face_normals=True,peak_to_trough_m=.05,no_PPO_or_scope_maturity_claim=True,actual_frozen_job_not_yet_allocated_or_published=True))
 print(json.dumps(dict(decision='observed35mm27of27bothdirections frozen; no thirdsameblock',next50_package=info,CPU_rays=len(errors),max_error=max(errors))))
if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE143_WAVE50_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
