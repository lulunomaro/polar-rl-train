"""Reject inherited cfce identity before deployment; preserve unused V1 bytes."""
from pathlib import Path
import json,time,hashlib,shutil,zipfile
import importlib.util,numpy as np
A=Path(__file__).resolve().parent;W=A.parent;N=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_20261015';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=N/'payload';Q=N/'payload_v2';assert not Q.exists();shutil.copytree(old,Q)
m=json.loads((old/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes())
assert m['source_SHA'].startswith('cfce') and m['S4_transition_scope']['policy_rule_only']
reject=dict(epoch=time.time(),original_v1_manifest_SHA=H(old/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),original_source_cfce_metadata_inherited_not_own_S4_identity=True,unused_V1_rejected_before_any_SSH_GPU=True,old_V1_payload_and_package_unchanged=True)
(N/'reports/S4_TRANSITION_V1_INHERITED_CFCE_METADATA_REJECTION_ACTUAL.json').write_text(json.dumps(reject,indent=2),encoding='utf8')
own=dict(epoch=time.time(),file_rows=m['file_rows'],S4_transition_scope=m['S4_transition_scope'],source_pair=m['S4_transition_scope']['only_source_pair'],source_SHA=m['S4_transition_scope']['only_source_pair'][1]['sha256'],source_checkpoint_field_W35_scene_anchor_not_single_actor_policy=True,gate_fixture_untrained_and_critic_new_optimizer_unused_for_rule=True,no_PPO=True,training_DR_fullstate_restore_not_claimed=True,original_archived_manifest_provenance=dict(path=str(old/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(old/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),inherited_cfce_metadata_rejected_not_current_identity=True))
(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(own,indent=2),encoding='utf8')
g=Q/'runtime/isaac/mod4/g3_cad_wave_geometry.py';spec=importlib.util.spec_from_file_location('exact_original_G3_mesh_math',g);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
profile=mod.profile();mesh,origin=mod.make_mesh((9.,9.));v=np.asarray(mesh.vertices);f=np.asarray(mesh.faces)
assert H(g)==H(old/'runtime/isaac/mod4/g3_cad_wave_geometry.py') and profile['derived_peak_to_trough_m']==.035
assert np.ptp(v[:,2])==.035 and (mesh.face_normals[:,2]>0).all()
flat=(9-profile['span_m'])/2;assert flat>.4 and profile['span_m']>2
assert np.all(v[v[:,0]<=flat,2]==0) and np.all(v[v[:,0]>=9-flat,2]==0)
assert np.isfinite(v).all() and f.max()<len(v) and f.min()>=0
for sign in (-1,1):
 start=4.5-sign*(profile['span_m']/2+.4);finish=4.5+sign*(profile['span_m']/2+.2)
 assert 0<start<9 and 0<finish<9 and sign*(finish-start)>profile['span_m']
oldprep=json.loads((N/'reports/S4_ORIGINAL35_TRANSITION_RULE_SOURCE_CPU_PREPARED_ACTUAL.json').read_bytes())
z=N/'S4_ORIGINAL35_TRANSITION_RULE_SOURCE_V2.zip';assert not z.exists()
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
 for row in own['file_rows']:assert H(Q/row['relative'])==row['sha256'];out.write(Q/row['relative'],row['relative'])
 out.write(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')
 for row in own['source_pair']:out.write(Q/'source'/Path(row['local_path']).name,'source/'+Path(row['local_path']).name)
new=dict(oldprep);new.update(epoch=time.time(),active_payload=str(Q),own_V2_identity_metadata_explicit=True,unused_V1_original_rejection=str(N/'reports/S4_TRANSITION_V1_INHERITED_CFCE_METADATA_REJECTION_ACTUAL.json'),package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest=dict(path=str(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')),worker=dict(path=str(Q/'paired_full80_parameter_bound_v2.py'),sha256=H(Q/'paired_full80_parameter_bound_v2.py')),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),original35_mesh_CPU_geometry=dict(source_path=str(g),source_SHA=H(g),profile_SHA=H(mod.PROFILE),full_ten_wave_span_m=profile['span_m'],height_peak_trough_m=.035,flat_support_length_each_m=flat,positive_triangle_normal=True,original_direct_g3_bytes_exact=True,CPU_geometry_not_actual_authored_GPU_query=True))
p=N/'reports/S4_ORIGINAL35_TRANSITION_RULE_SOURCE_CPU_PREPARED_ACTUAL_V2.json';assert not p.exists();p.write_text(json.dumps(new,indent=2),encoding='utf8')
(N/'reports/S4_TRANSITION_SOURCE_READER_PATH_ERRORS_ACTUAL.json').write_text(json.dumps(dict(errors=['Guessed native3060_worker_v2.py missing os2; actual file found by rg','Guessed deploy_left_full80_frozen_unique_once.py missing os2; actual file found by rg','Guessed g1_terrain_wave.py missing os2; g3_cad_wave_geometry.py exact found by rg'],no_GPU_or_PPO=True,original_errors_kept=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(p),package=new['package'],original35_CPU_scope=True,no_GPU=True)))
