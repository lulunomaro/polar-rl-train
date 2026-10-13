"""Local CPU source-assembly fixture, explicitly not remote target admission.

No fake budget or resource values are provided. The target CLI rejects this
local path, and no actual remote target PASSED/lease is created by this reader.
"""
from pathlib import Path
import ast, hashlib, json, os, shutil, sys, time, traceback, zipfile
import materialize_windows20k_target_cpu_once as m

P=Path(__file__).resolve().parent
W=P.parents[1]
G=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/recovery4090_windows_CPU'

def main():
 A=P/'CPU_SOURCE_ASSEMBLY_FIXTURE_V5_FINAL_BOUND_SOURCE';assert not A.exists();A.mkdir();(A/'packages').mkdir()
 started=time.time()
 try:
  for kind,(n,sha,embedded,unpack) in m.PACKAGES.items():
   m.copy_exact(G/n,A/'packages'/n)
   with zipfile.ZipFile(G/n) as z:
    for name in z.namelist():
     q=m.safe_child(A/unpack,name);q.parent.mkdir(parents=True,exist_ok=True)
     with q.open('xb') as f:f.write(z.read(name))
  packages=m.verify_packages(A)
  S=A/'LOCAL_SOURCE_ASSEMBLY_NOT_REMOTE_TARGET'
  assembly=m.assemble(A,S,P,packages)
  CPU=m.full_cpu(S,A,packages,assembly)
  assert CPU['floating_tensors']==107 and CPU['perenv_fields']==99 and len(CPU['actual_five_metadata_changes'])==5
  # A local fixture cannot pass the executable's actual target-root assertion.
  assert A.resolve()!=Path(m.ENVIRONMENT_ROOT).resolve()
  source_sha=m.H(A/'immutable_source459/source459/checkpoint/model_32264_d05c.pt')
  assert source_sha=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
  # Import-main-Popen and demand wrapper all name the same immutable worker.
  parent=(P/'run_windows4090_stage_once.py').read_text();worker=(P/'windows4090_repair_worker.py').read_text();wrapper=(P/'windows4090_demand_task_wrapper.ps1').read_text()
  assert "str(P/'windows4090_repair_worker.py')" in parent and "guard==environment_root/'WINDOWS4090_GPU_EXCLUSIVE.lock'" in parent
  assert "['GPU_lease_explicitly_granted']" in parent and "['GPU_lease_explicitly_granted']" in worker
  assert 'run_windows4090_stage_once.py' in wrapper and '$TaskEnvironmentRoot' in wrapper
  namespace={};tree=ast.parse(worker);names=[n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='capacity_names' for t in n.targets)];assert len(names)==1
  assert tuple(ast.literal_eval(names[0].value))==m.CAPACITY_NAMES
  negatives=[]
  for name in ['../outside','C:/outside','safe\\bad']:
   try:m.safe_child(A,name)
   except AssertionError:negatives.append(name)
   else:raise AssertionError('unsafe archive member accepted')
  # Source geometry assignment unchanged. Runtime entry20k never receives L128 projection.
  assert m.H(S/'runtime20k/isaac/mod4/wave50_entry_runtime_v2.py')=='57c7234ed31f0796b4eaf335479f9a2fe0530a860c02fe092242f3015a803410'
  from prepare_windows20k_sdk_manifest_cpu_once import saved_readonly_budget_config,budget_reference
  B=S/'prepared/CPU_BUDGET_EVIDENCE_RELOCATION_FIXTURE';B.mkdir()
  actual_config=saved_readonly_budget_config(S,B);budget=budget_reference(actual_config)
  assert abs(budget['pending_unique_actual_parent_cost_seconds']-6060.857095003127)<1e-9
  assert budget['extension_records_count']==7 and budget['authorized_seconds']==1188000
  assert budget['no_second_subtraction_of_covered_localcost'] and budget['snapshot_is_not_current_live_remaining']
  assert budget['prepared_conservative_remaining_lower_bound_seconds']>3600+min(64800.,.13*budget['prepared_conservative_remaining_lower_bound_seconds'])
  wrong=dict(actual_config);wrong['budget_original_saved_reference']={**wrong['budget_original_saved_reference'],'sha256':'0'*64}
  try:budget_reference(wrong)
  except AssertionError:budget_negative=True
  else:raise AssertionError('wrong actual saved evidence SHA accepted')
  # Keep actual local fixture references, with no target/remote admission labels.

  CPU.pop('actual_target_environment_root');CPU.pop('actual_scope_root');CPU['scope']='local CPU source fixture only, no actual remote target CPU admission';CPU['local_source_fixture_root']=str(A);CPU['no_remote_target_PASSED_created']=True
  report=dict(epoch=time.time(),passed=True,elapsed_seconds=time.time()-started,local_CPU_source_fixture_only=True,actual_remote_target_CPU_passed=False,actual_GPU_SDK_native_restore_PPO_pending=True,all_three_actual_original_package_file_SHA_checked=True,source_binding_fixture=CPU,source_assembly=assembly,unsafe_archive_negative_rejections=negatives,scope_parent_child_Task_binding_actual_source_checked=True,global_environment_native_OSlock_path_not_subscope_lock=True,capacity_all11_actual_SDK_AST_no_Linux_equivalence=True,missing_budget_cost_resources_not_faked=True,actual_saved_budget_reference_fixture=budget,wrong_budget_evidence_SHA_strictly_rejected=budget_negative,prepared_sources=[m.ref(P/n) for n in m.EXECUTABLES],old_pre_materializer_source_snapshot=str(P/'prepared_source_versions/materializer_v3_before_target_scope_binding'),Git_ordinary_supplement_pending_root=True,no_SSH_GPU_Task_registration_canonical_write_or_oldsource_change=True)
  m.fresh_json(P/'reports/TARGET_MATERIALIZER_SOURCE_CPU_V5_FINAL_BOUND_SOURCE_REVIEW.json',report)
  print(json.dumps({k:report[k] for k in ['passed','elapsed_seconds','actual_remote_target_CPU_passed','actual_GPU_SDK_native_restore_PPO_pending','missing_budget_cost_resources_not_faked']}))
 except BaseException:
  m.fresh_json(P/'reports/TARGET_MATERIALIZER_CPU_V5_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),local_fixture_only=True,no_GPU_or_PPO=True));raise
if __name__=='__main__':main()
