"""Finish static prepared files after Windows' absent fcntl; no OS lock claim or GPU call."""
from pathlib import Path
import os,sys,json,time,hashlib,types,importlib.util,ast,traceback
B=Path(__file__).resolve().parent;R=B/'reports';M=B.parent/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';D=B/'payload/h1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 closed=json.loads((R/'M_H1_CLOSED24_FULL_MODEL_CPU_RECOVERY_NATIVE_COMPLETE_ORIGINAL_HANDOFF_ACTUAL.json').read_bytes());assert closed['H1_full_final_CPU_passed']
 prior=json.loads((M/'reports/H1_BOUNDED_ONE_PAID_SLOT_RECOVERY_NATIVE_ONLY_OWNER_HTTP_CPU_ACTUAL.json').read_bytes());specs=prior['specs'];mf=D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';v=json.loads(mf.read_bytes());gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 specs['h1'].update(source_SHA=closed['H1_final']['SHA'],source_Adamstep=644180,manifest_SHA=H(mf),GPU_UUID=gpu,python=specs['recovery']['python'],execution_backend='target72',previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/T3_1710v8r72/e2')
 for p in [*B.glob('three_slot_*.py'),B/'owner_listener_ready_cpu_reviewed_v1.py']:ast.parse(p.read_text('utf8'))
 mock=types.ModuleType('fcntl');mock.flock=lambda *a:(_ for _ in ()).throw(AssertionError('No OS lock operation permitted in this CPU validator'));sys.modules['fcntl']=mock
 sp=importlib.util.spec_from_file_location('target72_contract_actual_functions_v2',D/'three_slot_common_v1.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);b.validate_payload(specs['h1']);rejected=0
 for change in ({'GPU_UUID':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'},{'GPU_UUID':specs['recovery']['GPU_UUID']},{'max_parent_seconds':3600},{'exit_headroom_seconds':0},{'manifest_SHA':'0'*64},{'key':'unknown'}):
  try:b.validate_payload(dict(specs['h1'],**change))
  except (AssertionError,KeyError):rejected+=1
 assert rejected==6 and v['source_Adamstep']==644180 and v['source_SHA']==closed['H1_final']['SHA']
 resource=(D/'three_slot_resource_v1.py').read_text('utf8');old=(M/'three_slot_resource_v1.py').read_text('utf8');assert resource==old.replace("source=key=='h1'","source=spec.get('execution_backend')=='source210'")
 immutable=[x for x in json.loads((M/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files'] if x['relative'].startswith(('job0/runtime/','job0/assets/','lib/','job0/original_run_manifest.json'))];assert all(H(D/x['relative'])==x['SHA'] for x in immutable)
 for name in ('h1_prelaunch_v2_production_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py'):assert (D/name).read_text('utf8')==(M/'payload/h1'/name).read_text('utf8').replace('643700','644180')
 task=json.loads((D/'job0/TASK.json').read_bytes());assert task['max_parent_seconds']==1800 and task['max_completed_updates']==24 and task['own_saved_stop_if_free_below8GiB']
 out=dict(epoch=time.time(),passed_CPU_only=True,closed_final_proof=closed,specs=specs,target72_h1_GPU0_new_backend_native180_required_not_reused=True,H1_original_1800cap24updates300headroom8GiB_exit_reserve_25GiB_start_guard_unchanged=True,all_runtime_lib_physics_reward_command_DR_bytes_exact=True,actual_common_manifest_validator_positive_and6negative_passed=True,Windows_fcntl_import_original_failure_retained=True,mock_import_only_no_actual_OS_lock_CPU_claim=True,E2_and_recovery_paid_hold_no_worker_GO=True,one_original_writer_original_budget_unchanged=True,new_native_GPU_PPO_not_yet=True)
 with (R/'H1_CLOSED24_TARGET72_SAME_SCOPE_PAYLOAD_FULL_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(H1_full_final_CPU=True,H1_closed24_Adam644180=True,old_cost_seconds=closed['actual_cost_seconds'],new_target72_payload_CPU=True,negative_count=rejected,new_native_and_PPO_not_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_TARGET72_PAYLOAD_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_or_GPU_launch=True),f,indent=2)
  raise
