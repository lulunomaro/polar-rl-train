"""Evaluate the already completed continuation before another curb learning axis."""
from pathlib import Path
import os,sys,json,time,shutil,hashlib,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';OLD=D/'curb140_frozen35_3060_v2';E=D/'curb140_cont147_frozen35_3060_v1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();OLDSHA='84d29fa99c0a75f2273cf2d427bc729e8bb614fef7a8fa25d8b9889361e1e626'
def main():
 assert not E.exists();v=json.loads((R/'TWO_CONTINUATION_FINAL147_75_COMPLETE_MODELS_EXACT_COST_LOCAL_CPU_ACTUAL.json').read_bytes());assert v['passed'];row=next(x for x in v['models'] if x['key']=='curb');SHA=row['model']['SHA'];source=Path(row['model']['path']);assert H(source)==SHA and row['all17Adam_to']==666140;(E/'reports').mkdir(parents=True);shutil.copytree(OLD/'eval_payload_v2',E/'eval_payload_v2',ignore=shutil.ignore_patterns('__pycache__'));Q=E/'eval_payload_v2';shutil.copy2(source,Q/'source/CURB140_cont147.pt');ROOT='D:/MOD4_async_eval/'+D.name+'/'+E.name
 changed=[]
 for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py'):
  p=Q/name;s=p.read_text('utf8');assert s.count(OLDSHA)==1;new=s.replace(OLDSHA,SHA,1).replace(OLD.name,E.name);assert ast.dump(ast.parse(new.replace(SHA,OLDSHA,1).replace(E.name,OLD.name)))==ast.dump(ast.parse(s));p.write_text(new,encoding='utf8');changed.append(dict(path=str(p),SHA=H(p),source_SHA_and_namespace_only=True))
 mf=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';m=json.loads(mf.read_bytes());m['source_single_policy'].update(expert='CURB35_from140_plus147',local_path=ROOT+'/payload/source/CURB140_cont147.pt',sha256=SHA,bytes=source.stat().st_size)
 for r in m['file_rows']:
  if r['relative']=='source/CURB140.pt':r['relative']='source/CURB140_cont147.pt'
  p=Q/r['relative'];r.update(bytes=p.stat().st_size,sha256=H(p))
 mf.write_text(json.dumps(m,indent=2),encoding='utf8');prep=json.loads((OLD/'reports/CURB35_LEARNED140_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').read_bytes());prep.update(epoch=time.time(),source=m['source_single_policy'],manifest_SHA=H(mf),worker_SHA=H(Q/'paired_full80_parameter_bound_v2.py'),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),source_adapter_EXPECTED_SHA=SHA,source_17Adam=666140,whole_original_source_CPU_passed=True,samehost_static_payload_reuse_plus_new_complete_model_and_two_source_constants_only=True)
 (E/'reports/CURB35_CONT147_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
 for name in ('dispatch_curb113_frozen3060_unused_case_once.py','collect_curb113_own_case_actual_readonly.py','review_curb35_learned140_actual_physical_CPU_v2.py','run_new_CURB35_native_full_finite_v3_once.py','transport_249_exact_deepseek_desktop_role_v4.py','transport_249_exact_desktop_role_stdin_v5.py'):
  s=(OLD/name).read_text('utf8').replace(OLD.name,E.name).replace('curb35_learned140','curb35_cont147').replace('CURB35_LEARNED140','CURB35_CONT147').replace('source/CURB140.pt','source/CURB140_cont147.pt')
  if name.startswith('dispatch'):
   marker="for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'):";assert s.count(marker)==1;s=s.replace(marker,"for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json','source/CURB140_cont147.pt'):",1)
  ast.parse(s);(E/name.replace('learned140','cont147')).write_text(s,encoding='utf8')
 sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
 rng=torch.get_rng_state().clone();torch.set_num_threads(2);actor=Single35(Q/'source/CURB140_cont147.pt',80,'cpu');assert actor.exact();rejected=False
 try:Single35(Q/'source/CURB140.pt',80,'cpu')
 except AssertionError:rejected=True
 assert rejected and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();report=dict(epoch=time.time(),passed_CPU_only=True,source=row,changed_source_bindings=changed,source140_negative_rejected=True,source35_geometry_and_allphysical_runtime_unchanged=True,previous_source140_full35_up6_down27_not_improved_from_protected878_descriptive_up8_down27=True,no_blind_additional_CURB_training_window=True,new_full_evaluation_not_yet_passed=True,no_new_budget_or_PPO=True);(R/'CURB_FROM140_PLUS147_FROZEN_SOURCE_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_only=True,actual_new_source_SHA=SHA,only_new_unused_frozen_native_full_next=True)))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('CURB_CONT147_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),indent=2),encoding='utf8');raise
