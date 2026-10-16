"""V5 targetCPU rejected inherited878 constants before lease/Task/GPU; new bundle."""
from pathlib import Path
import os,sys,json,time,ast,shutil,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;OLD=D/'curb140_frozen35_3060_v1';E=D/'curb140_frozen35_3060_v2';R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();SHA='84d29fa99c0a75f2273cf2d427bc729e8bb614fef7a8fa25d8b9889361e1e626';LEGACY='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1';ROOT='D:/MOD4_async_eval/'+D.name+'/'+E.name;OLDROOT='D:/MOD4_async_eval/'+D.name+'/'+OLD.name
def main():
 assert not E.exists();shutil.copytree(OLD/'eval_payload_v2',E/'eval_payload_v2',ignore=shutil.ignore_patterns('__pycache__'));(E/'reports').mkdir();Q=E/'eval_payload_v2';changes=[]
 for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py'):
  p=Q/name;s=p.read_text('utf8');assert s.count(LEGACY)==1;fixed=s.replace(LEGACY,SHA,1)
  if name.startswith('paired'):fixed=fixed.replace("lease['namespace']=='curb140_frozen35_3060_v1'","lease['namespace']=='curb140_frozen35_3060_v2'")
  inverse=fixed.replace(SHA,LEGACY,1).replace("lease['namespace']=='curb140_frozen35_3060_v2'","lease['namespace']=='curb140_frozen35_3060_v1'");assert ast.dump(ast.parse(inverse))==ast.dump(ast.parse(s));p.write_text(fixed,encoding='utf8');changes.append(dict(relative=name,original_SHA=H(OLD/'eval_payload_v2'/name),new_SHA=H(p),only_source_or_namespace_constants=True))
 mf=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';m=json.loads(mf.read_bytes());m['source_single_policy']['local_path']=ROOT+'/payload/source/CURB140.pt';m['explicit_new_scope']='Source140 binding constants repaired independently after targetCPU rejection; original physical loop unchanged; no oldscope GPU replay.'
 for row in m['file_rows']:
  p=Q/row['relative'];row.update(bytes=p.stat().st_size,sha256=H(p))
 mf.write_text(json.dumps(m,indent=2),encoding='utf8');prep=json.loads((OLD/'reports/CURB35_LEARNED140_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').read_bytes());prep.update(epoch=time.time(),source=m['source_single_policy'],manifest_SHA=H(mf),worker_SHA=H(Q/'paired_full80_parameter_bound_v2.py'),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),source_adapter_EXPECTED_SHA=SHA,samehost_exact_existing_payload_reuse_with_only_two_source_and_manifest_overlay=True,V1_CPU_prepared_label_did_not_test_inherited_actor_constructor_or_worker_source_assert=True,target_native_full_not_passed=True);(E/'reports/CURB35_LEARNED140_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
 # Helpers are new namespaces/cases; old attempts and reports remain untouched.
 for name in ('collect_curb113_own_case_actual_readonly.py','review_curb35_learned140_actual_physical_CPU_v2.py','run_new_CURB35_native_full_finite_v3_once.py'):
  s=(OLD/name).read_text('utf8').replace(OLDROOT,ROOT).replace('curb35_learned140_{steps}_v1','curb35_learned140_{steps}_v2').replace('curb35_learned140_{a.steps}_v1','curb35_learned140_{a.steps}_v2').replace('curb35_learned140_{S}_v1','curb35_learned140_{S}_v2');ast.parse(s);(E/name).write_text(s,encoding='utf8')
 s=(OLD/'dispatch_curb113_frozen3060_unused_case_once.py').read_text('utf8').replace(OLDROOT,ROOT).replace('curb35_learned140_{steps}_v1','curb35_learned140_{steps}_v2').replace('MOD4_CURB35_LEARNED140_3060_{steps}_v1_20261016','MOD4_CURB35_LEARNED140_3060_{steps}_v2_20261016').replace('import transport_249_bodyframe_current_terminal_role_v3 as t','import transport_249_exact_desktop_role_stdin_v5 as t');s=s.replace('t.ROOT=ROOT','t.ROOT=ROOT')
 upload="sf.mkdir(ROOT);z=Path(prep['package']['path']);assert H(z)==prep['package']['sha256'];sf.put(str(z),ROOT+'/'+z.name)";replacement="sf.mkdir(ROOT);copied=t.py(c,\"from pathlib import Path;import shutil,json;A=Path(\"+repr("+repr(OLDROOT)+")+\");B=Path(\"+repr(ROOT)+\");assert A.is_relative_to(Path('D:/MOD4_async_eval')) and not (B/'payload').exists();shutil.copytree(A/'payload',B/'payload');print(json.dumps(dict(existing_exact_payload_copied=True,no_GPU=True)))\");save(case+'_EXISTING_SOURCE_REUSE_ACTUAL.json',copied)\n   for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'):sf.put(str(Q/name),ROOT+'/payload/'+name)";assert s.count(upload)==1;s=s.replace(upload,replacement,1)
 start="if C['steps']==120:\n z=R/C['package'];";a=s.index(start);b=s.index("assert H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')",a);s=s[:a]+"if C['steps']==120:\n assert Q.is_dir();(R/'attempts').mkdir();(R/'leases').mkdir()\n"+s[b:];ast.parse(s);(E/'dispatch_curb113_frozen3060_unused_case_once.py').write_text(s,encoding='utf8')
 # Transport is new V2 namespace, original exact signed desktop identity guard unchanged.
 for name in ('transport_249_exact_deepseek_desktop_role_v4.py','transport_249_exact_desktop_role_stdin_v5.py'):
  s=(OLD/name).read_text('utf8').replace("/curb140_frozen35_3060_v1'","/curb140_frozen35_3060_v2'");(E/name).write_text(s,encoding='utf8')
 sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
 rng=torch.get_rng_state().clone();torch.set_num_threads(2);actor=Single35(Q/'source/CURB140.pt',80,'cpu');assert actor.exact();oldsource=next(p for p in (Q/'source').glob('*.pt') if H(p)==LEGACY);rejected=False
 try:Single35(oldsource,80,'cpu')
 except AssertionError:rejected=True
 assert rejected and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();report=dict(epoch=time.time(),passed_CPU_only=True,new_scope=str(E),source_SHA=SHA,source_adapter_constructor_and_all9STD_exact=True,old878_source_negative_rejected=True,two_source_inverse_AST_exact_except_explicit_constants=changes,original_payload_worker_adapter_constants_disagreement_preserved=True,no_oldlease_Task_native_or_GPU_consumed=True,new_native_full_targetCPU_and_resource_still_required=True,prepared_stage_not_full_GPU_admission=True,only_two_changed_source_files_and_new_manifest_uploaded_no_repeat_large_archive=True);(R/'CURB140_V6_EXACT_SOURCE_BINDINGS_LOCAL_CONSTRUCTOR_NEGATIVE_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_only=True,source_adapter_EXPECTED_and_worker_SHA_correct=True,old878_negative=True)))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('CURB140_V6_BINDING_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
