"""One authorized finite new four-case evaluation chain; sole 249 transport owner."""
from pathlib import Path
import argparse, json, os, subprocess, sys, time, hashlib, traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
E=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015'
RET=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
ROOT='D:/MOD4_async_eval/'+E.name
CASE='native3060_bodyframe_phase_final_full80_frozen1500_v1'
SHA='cfcefb1c46b33d6028bf6663921fac12a58a5abfdba782e1480a18ac84de541b'
def save(name,value,mutable=False):
 p=R/name
 if not mutable:assert not p.exists(),str(p)
 tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(value,indent=2),encoding='utf8');os.replace(tmp,p)
def phase(name,**extra):save('PHASE_FINAL_FOURCASE_FINITE_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase=name,source_SHA=SHA,**extra),True)
def command(argv,cpu=False):
 env=os.environ.copy()
 if cpu:env['CUDA_VISIBLE_DEVICES']=''
 p=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',env=env)
 assert p.returncode==0,dict(argv=argv,exit_code=p.returncode,stdout=p.stdout[-5000:],stderr=p.stderr[-7000:])
 return json.loads(p.stdout.strip().splitlines()[-1])
def wait_own_wave_exit():
 sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
 import transport_249_bodyframe_current_terminal_role_v3 as t
 for _ in range(3):time.sleep(60)
 for _ in range(20):
  c=t.connect()
  try:
   v=t.py(c,"from pathlib import Path\nimport json\np=Path("+repr(ROOT+'/attempts/'+CASE+'/PARENT_EXIT_RECEIPT.json')+")\nprint(json.dumps(dict(ended=p.exists(),receipt=json.loads(p.read_bytes()) if p.exists() else None)))")
  finally:t.close(c)
  if v['ended']:
   assert v['receipt']['exit_code']==0 and not v['receipt']['original_error_present'],v
   return v
  time.sleep(60)
 raise AssertionError('Own bounded new wave exit missing; inspect actual identity without replay or signal')
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute-root-new-fixed-fourcase',action='store_true');a=p.parse_args();assert a.execute_root_new_fixed_fourcase
 proof=json.loads((R/'PHASE_REPAIR_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json').read_bytes());assert proof['passed'] and proof['own_checkpoint']['sha256']==SHA and proof['two_locks_free']
 for folder,filename in ((E,'FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json'),(RET,'BODYFRAME_PHASE_FINAL_RETENTION_CPU_PREPARED_ACTUAL.json')):assert (folder/'reports'/filename).is_file()
 save('PHASE_FINAL_FOURCASE_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,script_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_SHA=SHA,exact_new_cases=4,sole_210_249_transport_owner_while_actual_alive=True,no_210_connection=True,no_new_PPO_or_budgetwrite=True,no_old_case_or_native_replay=True,no_retry_or_signal=True))
 phase('own_new_wave_target_CPU_and_unique_dispatch')
 dispatch=command([sys.executable,str(E/'deploy_own_phase_final_full80_unique_once.py')])
 phase('waiting_own_wave_parent_exit',dispatch=dispatch)
 ended=wait_own_wave_exit();phase('collecting_own_complete_wave',exit=ended)
 collection=command([sys.executable,str(E/'collect_left_full80_bounded_transport_actual.py')]);assert collection['lock_free'] and collection['parent_exit']['exit_code']==0
 data=command([CPU,str(E/'review_full80_full1500_CPU_actual.py')],True)
 route=command([CPU,str(E/'review_full80_original_route_prefix_CPU_actual.py')],True)
 direct=command([CPU,str(E/'review_phase_final_full80_direct_f516_prefix_actual.py')],True)
 phase('own_wave_full_CPU_reviewed_new_retention_source_upload',data=data,route=route,direct=direct)
 uploaded=command([sys.executable,str(RET/'upload_bodyframe_retention_source_namespace_CPU_once.py'),'--execute-root-upload']);assert uploaded['target_CPU_actual']
 phase('executing_exact_three_new_retention_cases',wave_route=route,retention_upload=uploaded)
 retained=command([sys.executable,str(RET/'run_phase_final_retention_fixed_three_candidate_batch_once.py'),'--execute-root-fixed-three-cases']);assert retained['complete']
 three=command([CPU,str(RET/'aggregate_phase_final_retention_complete_actual_CPU.py')],True);assert three['passed']
 complete=dict(epoch=time.time(),source_SHA=SHA,own_final_and_all_trace_CPU_verified=True,new_wave_full1500_reviewed=True,new_three_retention_full1500_reviewed=True,all_four_cases_complete=True,wave=route,wave_direct=direct,retention=three,no_PPO_or_budgetwrite=True,no_old_cases_replayed=True,no_qualification_or_third_learning_claim=True,root_handoff_only_after_actual_CIM_absent=True)
 save('PHASE_FINAL_FOURCASE_FINITE_COMPLETE_ACTUAL.json',complete);phase('all_four_new_cases_complete');print(json.dumps(complete),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  save('PHASE_FINAL_FOURCASE_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),unknown_mutation_requires_actual_readonly_recovery=True,no_retry_or_signal=True));raise
