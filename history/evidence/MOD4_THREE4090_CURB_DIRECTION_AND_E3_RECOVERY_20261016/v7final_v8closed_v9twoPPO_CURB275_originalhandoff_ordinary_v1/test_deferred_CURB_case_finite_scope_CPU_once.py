from pathlib import Path
import json,time,hashlib,copy,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from deferred_CURB_case_admission_v1 import read_ready
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 B=D/'deferred_CURB_case_CPU_fixtures_v1';B.mkdir();case=B/'case';case.mkdir();mf=case/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text('{}');s=dict(key='curb',GPU_UUID='fixture-original-GPU',python='fixture-python',max_parent_seconds=1800,exit_headroom_seconds=300,native_controls=144,native_script='native_admission_worker.py',production_script='production_worker.py',source_SHA='a'*64,manifest_SHA=H(mf));cpu=case/'TARGET_CPU_SOURCE_ADMISSION_ACTUAL.json';cpu.write_text(json.dumps(dict(passed_CPU_only=True,source_SHA=s['source_SHA'],manifest_SHA=s['manifest_SHA'],full_source_all_tensor_finite=True,all_target_manifest_files_actual_SHA=True,no_GPU_or_PPO=True)));v=dict(case_root=str(case),spec=s,target_CPU_receipt_SHA=H(cpu),existing_master_repair_axis_explicit=True,original_global_budget_unchanged=True,original_live_control_files=[]);p=B/'CURB_REPAIR_CASE_READY.json';assert read_ready(B,s) is None;p.write_text(json.dumps(v));assert read_ready(B,s)['spec']==s;bad=0
 for path,value in [(('case_root',),str(B.parent)),(('case_root',),str(B)),(('spec','GPU_UUID'),'other-GPU'),(('spec','max_parent_seconds'),1801),(('spec','native_controls'),120),(('spec','source_SHA'),'invalid'),(('target_CPU_receipt_SHA',),'0'*64),(('original_global_budget_unchanged',),False),(('existing_master_repair_axis_explicit',),False)]:
  x=copy.deepcopy(v)
  if len(path)==1:x[path[0]]=value
  else:x[path[0]][path[1]]=value
  p.write_text(json.dumps(x))
  try:read_ready(B,s)
  except AssertionError:bad+=1
  else:raise AssertionError(path)
 p.write_text(json.dumps(v));out=D/'reports/DEFERRED_CURB_SINGLE_FINITE_CASE_CPU_NEGATIVES_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),passed_CPU_fixture_only=True,missing_ready_not_admitted=True,explicit_existing_case_positive=True,outside_root_wrong_GPU_bad_hash_source_cap_and_budget_negatives_rejected=bad,no_GPU_PPO_budget_or_remote_mutation=True,not_new_CURB_case_actual_admission=True),indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_fixture_only=True,negatives=bad)))
if __name__=='__main__':main()
