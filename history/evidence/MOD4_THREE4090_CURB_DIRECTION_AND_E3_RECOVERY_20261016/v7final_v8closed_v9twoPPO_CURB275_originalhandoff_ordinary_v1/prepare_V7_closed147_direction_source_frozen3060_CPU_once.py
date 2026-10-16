from pathlib import Path
import os,sys,json,time,shutil,hashlib,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';A=W/'MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016';OLD=A/'curb140_cont147_frozen35_3060_v1';E=D/'curb_v7final147_frozen35_3060_v1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not E.exists();review=json.loads((R/'V7_THREE_FINAL_MODELS_EXACT_UPDATES_COST_EXIT_LOCAL_CPU_ACTUAL.json').read_bytes());assert review['passed'];row=review['experts']['curb'];source=Path(row['local_path']);assert H(source)==row['SHA'] and row['all17Adam_after']==671400;(E/'reports').mkdir(parents=True);shutil.copytree(OLD/'eval_payload_v2',E/'eval_payload_v2',ignore=shutil.ignore_patterns('__pycache__'));Q=E/'eval_payload_v2';newname='CURB_V7_final147.pt';shutil.copy2(source,Q/'source'/newname);ROOT='D:/MOD4_async_eval/'+D.name+'/'+E.name;prep=json.loads((OLD/'reports/CURB35_CONT147_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').read_bytes());oldsha=prep['source']['sha256'];changed=[]
 for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py'):
  p=Q/name;s=p.read_text('utf8');assert s.count(oldsha)==1;new=s.replace(oldsha,row['SHA']).replace(OLD.name,E.name);assert ast.dump(ast.parse(new.replace(row['SHA'],oldsha).replace(E.name,OLD.name)))==ast.dump(ast.parse(s));p.write_text(new,encoding='utf8');changed.append(dict(path=str(p),SHA=H(p),source_SHA_and_namespace_only=True))
 mf=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';m=json.loads(mf.read_bytes());m['source_single_policy'].update(expert='CURB35_V7_direction_final147',local_path=ROOT+'/payload/source/'+newname,sha256=row['SHA'],bytes=source.stat().st_size)
 for r in m['file_rows']:
  if r['relative']=='source/CURB140_cont147.pt':r['relative']='source/'+newname
  p=Q/r['relative'];r.update(bytes=p.stat().st_size,sha256=H(p))
 mf.write_text(json.dumps(m,indent=2),encoding='utf8');prep.update(epoch=time.time(),source=m['source_single_policy'],manifest_SHA=H(mf),worker_SHA=H(Q/'paired_full80_parameter_bound_v2.py'),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),source_adapter_EXPECTED_SHA=row['SHA'],source_17Adam=671400,whole_original_source_CPU_passed=True,samehost_static_payload_reuse_plus_new_complete_model_and_two_constants_only=True,package_metadata_is_historical_static_archive_not_new_full_payload_ZIP=True);(E/'reports/CURB35_V7FINAL147_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
 for name in ('dispatch_curb113_frozen3060_unused_case_once.py','collect_curb113_own_case_actual_readonly.py','review_curb35_cont147_actual_physical_CPU_v2.py','run_new_CURB35_native_full_finite_v3_once.py','transport_249_exact_deepseek_desktop_role_v4.py','transport_249_exact_desktop_role_stdin_v5.py'):
  s=(OLD/name).read_text('utf8').replace(A.name,D.name).replace(OLD.name,E.name).replace('curb35_cont147','curb35_v7final147').replace('CURB35_CONT147','CURB35_V7FINAL147').replace('source/CURB140_cont147.pt','source/'+newname)
  if name.startswith('dispatch'):s=s.replace(repr('D:/MOD4_async_eval/'+D.name+'/curb140_frozen35_3060_v1'),repr('D:/MOD4_async_eval/'+A.name+'/curb140_frozen35_3060_v1'))
  ast.parse(s);(E/name.replace('cont147','v7final147')).write_text(s,encoding='utf8')
 identity=R/'ACTUAL_3060_DEEPSEEK_ELECTRON_GPU_ROLE_IDENTITY_READONLY.json'
 if not identity.exists():shutil.copy2(A/'reports'/identity.name,identity)
 sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
 rng=torch.get_rng_state().clone();torch.set_num_threads(2);actor=Single35(Q/'source'/newname,80,'cpu');assert actor.exact();bad=False
 try:Single35(Q/'source/CURB140_cont147.pt',80,'cpu')
 except AssertionError:bad=True
 assert bad and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();p=R/'V7_CLOSED147_DIRECTION_FROZEN3060_SOURCE_CPU_PREPARED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed_CPU_only=True,source=row,changed_source_bindings=changed,old_source_negative_rejected=True,original35mm150mm_geometry_commands_full80_runtime_byteexact=True,desktop_identity_is_existing_exact_reference_fresh_runtime_guard_still_required=True,no_future_native_or_full_pass=True,no_PPO_or_budget=True),indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_only=True,source=row['SHA'],eval_folder=str(E))))
if __name__=='__main__':main()
