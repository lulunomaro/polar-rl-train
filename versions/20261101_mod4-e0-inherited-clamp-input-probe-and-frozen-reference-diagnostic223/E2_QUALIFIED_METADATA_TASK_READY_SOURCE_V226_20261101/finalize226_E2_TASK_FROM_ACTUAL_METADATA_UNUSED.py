"""ROOT JSON-only fresh report/wait/resource join;no model/SDK/actor access."""
from pathlib import Path
import argparse,hashlib,json
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--actual-wait',type=Path,required=True)
 p.add_argument('--actual-runtime-admission',type=Path);a=p.parse_args();J=a.job_root.resolve()
 report=read(J/'E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json');wait=read(a.actual_wait);expected=J/'EXPECTED226_TARGET_METADATA.json'
 assert report['passed'] and report['kind']=='NEW226_E2_213_SOURCE_AND_SDK_METADATA' and report['source_SHA']=='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
 assert report['expected226_SHA']==H(expected) and report['model_reads']==report['old_fixture_replays']==report['App_or_actor_constructions']==report['GPU_calls']==0
 assert wait['purpose']=='NEW226_E2_213_SOURCE_AND_SDK_METADATA' and wait['actual_waited'] and wait['returncode']==0 and wait['report_SHA']==H(J/'E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json')
 #New exact original wait bytes are retained under the frozen213 ABI name.
 proof=dict(wait,passed=True,actual_waited=True,returncode=0,not_old_V5_wait=True)
 target=J/'E2_NEW86_CPU_ORIGINAL_WAIT_PROOF.json'
 if target.exists():assert read(target)==proof,'Existing different wait proof must not be overwritten'
 else:
  with target.open('x',encoding='utf8') as f:json.dump(proof,f,indent=2,allow_nan=False)
 task=read(J/'FROZEN_CASE_TASK_PENDING226.json');task.update(actual_target_SDK_new213_source_admission_passed=True,
  actual_CPU_report_SHA=H(J/'E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json'),actual_CPU_waited_proof_SHA=H(target))
 name='FROZEN_CASE_TASK_READY_FOR_CURRENT_RESOURCE_ADMISSION.json'
 if a.actual_runtime_admission:
  r=read(a.actual_runtime_admission)
  assert r['passed'] and r['fresh_current_CNone'] and r['original_private_EX_held'] and r['original_shared_guard_passed'] and r['original_resources_passed']
  assert r['num_envs']==20000 and r['source_SHA']==task['source_SHA'] and r['worker_SHA']==task['worker_SHA']
  task.update(GPU_UUID=r['GPU_UUID'],actual_private_GPU_EX_held_by_parent=True,canonical72_known_owner_readonly_passed=True)
  name='FROZEN_CASE_TASK.json'
 with (J/name).open('x',encoding='utf8') as f:json.dump(task,f,indent=2,allow_nan=False)
 print(json.dumps(dict(metadata_and_original_wait_join_passed=True,task=str(J/name),runtime_resource_admitted=bool(a.actual_runtime_admission),model_reads=0)))
if __name__=='__main__':main()
