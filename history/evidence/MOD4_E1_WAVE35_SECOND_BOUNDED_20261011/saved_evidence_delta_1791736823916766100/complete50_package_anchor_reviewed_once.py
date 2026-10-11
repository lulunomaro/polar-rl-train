"""Complete only package section after saved authored-span CPU proof and anchor-reader rejection."""
from second_io import *
import ast,zipfile
proof=json.loads((R/'WAVE50_AUTHORED_JOIN_QUERY_CPU_REVIEW.json').read_bytes());assert proof['CPU_only_authored_query_max_error_m']<1e-10 and proof['original_geometry_and_profile_bytes_not_changed']
assert not (R/'WAVE50_COMPONENT_FROZEN_PREPARED.json').exists()
impl=D/'next_wave50_scope';parent=W/'MOD4_E1_G3_MATCHED_REVIEW_20261010/artifacts/e1-g3-derived35mm-paired-approach040-frozen-v2.zip'
with zipfile.ZipFile(parent) as z:members={n:z.read(n) for n in z.namelist()}
manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[n])==h for n,h in manifest['files'].items())
gp='runtime/isaac/mod4/g4_cad_wave_geometry.py';pp='runtime/isaac/mod4/g4_cad_profile.json';fp='runtime/isaac/mod4/frozen_history_flat.py'
geom=(impl/'g4_cad_wave_geometry.py').read_text(encoding='utf8');profile=json.loads((impl/'g4_cad_profile.json').read_bytes());checkpoint=json.loads((R/'WAVE143_COMPLETE_OBSERVED_SCOPE_DECISION.json').read_bytes())['own_checkpoint']
save('WAVE50_QUERY_CONTINUATION_ANCHOR_REVIEW.json',dict(epoch=time.time(),prior_error='CPU proof saved, but incorrect four-space textual anchor rejected before package or GPU; actual one-space anchor only completes unexecuted package section',original_source=str(D/'repair50_unexecuted_query_scope_once.py'),original_source_SHA=H((D/'repair50_unexecuted_query_scope_once.py').read_bytes()),CPU_proof_reused_exact=True,no_rewrite_or_GPU_replay=True))
old=members[fp].decode();proto='approved_E1_G4_derived50mm_actualray_approach040_fullroute_behavior_v1'
new=old.replace('g3_cad_wave_geometry','g4_cad_wave_geometry').replace('configure_g3','configure_g4').replace('CAD_derived35mm_wave','CAD_derived50mm_wave').replace('0.035001','0.050001').replace('approved_E1_G3_derived35mm_paired_approach040_behavior_v2',proto)
anchor="    sampled = cpu(sample['height'])\n";assert new.count(anchor)==1
extra="""    sampled = cpu(sample['height'])
   actual_world_ray_origins=cpu(torch.as_tensor(ray_starts,device=e.device,dtype=root_xy.dtype))
   actual_canonical_ray_x=actual_world_ray_origins[:,:,0].astype(np.float64)-centers[:,None,0]
   wave_profile=profile()
   expected_actual_ground=np.interp(actual_canonical_ray_x+half,np.r_[np.asarray(wave_profile['profile_x_m'])[:-1],wave_profile['span_m']],np.asarray(wave_profile['normalized_height'])*.05,left=0.,right=0.)
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
save('WAVE50_COMPONENT_FROZEN_PREPARED.json',dict(epoch=time.time(),package=info,protocol=proto,profile=profile,source_checkpoint=checkpoint,parent_archive_SHA=H(parent.read_bytes()),all_file_map_SHA_verified=len(manifest['files']),old_members_byteexact_except_dispatcher_manifest=True,new_members=[gp,pp],full_control_loop_AST_exact=True,independent_triangle_actual_float32_rays=2800,maximum_height_error_m=proof['CPU_only_authored_query_max_error_m'],positive_face_normals=True,peak_to_trough_m=.05,no_PPO_or_scope_maturity_claim=True,actual_frozen_job_not_yet_allocated_or_published=True))
print(json.dumps(dict(decision='observed35mm27of27bothdirections frozen; no thirdsameblock',next50_package=info,CPU_rays=2800,max_error=proof['CPU_only_authored_query_max_error_m'])))