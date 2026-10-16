from pathlib import Path
import os,sys,json,time,hashlib,shutil,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
N=Path(__file__).resolve().parent;W=N.parent;D=W/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';P=W/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';OLD=D/'curb_v7final147_frozen35_3060_v1';E=N/'curb275_final87_frozen3060_v1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not E.exists();v=json.loads((N/'reports/CURB275_FINAL87_COMPLETE_MODEL_EXACT_COST_CPU_ACTUAL.json').read_bytes());assert v['passed'];row=v['final'];source=Path(row['local_path']);assert H(source)==row['SHA'];(E/'reports').mkdir(parents=True);shutil.copytree(OLD/'eval_payload_v2',E/'eval_payload_v2',ignore=shutil.ignore_patterns('__pycache__'));Q=E/'eval_payload_v2';newname='CURB275_first_final87.pt';shutil.copy2(source,Q/'source'/newname);oldprep=json.loads((OLD/'reports/CURB35_V7FINAL147_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').read_bytes());oldsha=oldprep['source']['sha256'];ROOT='D:/MOD4_async_eval/'+N.name+'/'+E.name
 for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py'):
  p=Q/name;s=p.read_text('utf8');assert oldsha in s;p.write_text(s.replace(oldsha,row['SHA']).replace(OLD.name,E.name),encoding='utf8')
 # Identical authored scalar-height geometry to the actual closed27.5 training source.
 for name in ('curb35_profile.json','curb35_geometry.py'):shutil.copy2(P/'short_tmp_v2_payload/job0/runtime/isaac/mod4'/name,Q/'runtime/isaac/mod4'/name)
 p=Q/'full80_runtime_native_v1.py';s=p.read_text('utf8');assert '.035' in s;p.write_text(s.replace('.035','.0275').replace('derived35mm','derived27p5mm'),encoding='utf8');m=json.loads((Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes());m['source_single_policy'].update(expert='CURB275_first_final87',local_path=ROOT+'/payload/source/'+newname,sha256=row['SHA'],bytes=source.stat().st_size)
 for r in m['file_rows']:
  if r['relative']=='source/CURB_V7_final147.pt':r['relative']='source/'+newname
  p=Q/r['relative'];r.update(bytes=p.stat().st_size,sha256=H(p))
 mf=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';mf.write_text(json.dumps(m,indent=2),encoding='utf8');prep=dict(oldprep,epoch=time.time(),source=m['source_single_policy'],manifest_SHA=H(mf),worker_SHA=H(Q/'paired_full80_parameter_bound_v2.py'),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),source_adapter_EXPECTED_SHA=row['SHA'],source_17Adam=673940,whole_original_source_CPU_passed=True,explicit_new_source_and27p5_scalar_geometry_with_same_original_physics_query_contact_hardware=True,package_metadata_is_historical_archive_not_new_full_payload_ZIP=True)
 (E/'reports/CURB275_FINAL87_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
 names=['dispatch_curb_v7final147_parentguard_v8_unused_case_once.py','collect_curb113_own_case_actual_readonly.py','review_curb35_v7final147_actual_physical_CPU_v2.py','run_new_CURB35_native_full_finite_v3_once.py','transport_249_exact_desktop_role_fresh2233_v6.py','transport_249_exact_desktop_role_stdin_fresh2233_v7.py']
 for name in names:
  s=(OLD/name).read_text('utf8').replace(D.name,N.name).replace(OLD.name,E.name).replace('curb35_v7final147','curb275_final87').replace('CURB35_V7FINAL147','CURB275_FINAL87').replace('source/CURB_V7_final147.pt','source/'+newname)
  # Copy a real existing payload, then upload all explicit changed scalar-height files.
  if name.startswith('dispatch'):
   stale='D:/MOD4_async_eval/MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016/curb140_frozen35_3060_v1';s=s.replace(stale,'D:/MOD4_async_eval/'+D.name+'/'+OLD.name);needle="'source/"+newname+"'):sf.put";assert needle in s;s=s.replace(needle,"'source/"+newname+"','full80_runtime_native_v1.py','runtime/isaac/mod4/curb35_profile.json','runtime/isaac/mod4/curb35_geometry.py'):sf.put");s=s.replace("ck['E1_terrain_state']['CURB_height_m']==.035","ck['E1_terrain_state']['CURB_height_m']==.0275")
  if name.startswith('review'):s=s.replace("scope['height_m']==.035","scope['height_m']==.0275")
  if name=='transport_249_exact_desktop_role_fresh2233_v6.py':s=s.replace("D=E.parent;W=D.parent","D=E.parent;W=D.parent")
  ast.parse(s);(E/name.replace('curb_v7final147','curb275_final87').replace('curb35_v7final147','curb275_final87')).write_text(s,encoding='utf8')
 shutil.copy2(D/'reports/ACTUAL_3060_DEEPSEEK_SAME_BINARY_FRESH_GPU_ROLE_2233_READONLY.json',N/'reports/ACTUAL_3060_DEEPSEEK_SAME_BINARY_FRESH_GPU_ROLE_2233_READONLY.json')
 # This fixed80 actor adapter changes only immutable source; all original35 action/clock logic exact.
 sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
 rng=torch.get_rng_state().clone();torch.set_num_threads(2);actor=Single35(Q/'source'/newname,80,'cpu');assert actor.exact();bad=False
 try:Single35(Q/'source/CURB_V7_final147.pt',80,'cpu')
 except AssertionError:bad=True
 assert bad and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,source=row,actual_new_geometry_height_m=.0275,source_profile_and_geometry_byteexact_from_actual_native_and_training=True,old_source_negative_rejected=True,sourcefreeze_native120_full1500_resource_OSlock_actual_required=True,old35_and20_results_not_relabelled=True,no_future_GPU_or_route_pass=True,no_PPO_budget=True);p=N/'reports/CURB275_FINAL87_FROZEN3060_NEW_SOURCE_GEOMETRY_CPU_PREPARED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_only=True,source_SHA=row['SHA'],folder=str(E))),flush=True)
if __name__=='__main__':main()
