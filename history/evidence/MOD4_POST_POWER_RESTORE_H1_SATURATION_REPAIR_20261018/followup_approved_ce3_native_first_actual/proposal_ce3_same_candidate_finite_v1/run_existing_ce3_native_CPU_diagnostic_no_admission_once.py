"""One new CPU-only audit of saved failed-native raw; no restart/GO/canonical write."""
from pathlib import Path
import sys,os,json,time,getpass,traceback
import deploy_human_approved_ce3_new_native_then_one_finite1800_once as d
B=d.B;R=d.R;a=d.a;TARGET=d.TARGET

def main():
 prep=json.loads((R/'CE3_EXISTING_NATIVE_NUMERICAL_REJECTION_CPU_DIAGNOSTIC_PREPARED_ACTUAL.json').read_bytes());assert prep['original_admission_false_retained'] and prep['new_admitted_filename_never_written']
 d.put('CE3_SAVED_NATIVE_CPU_DIAGNOSTIC_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_creationargv_alive_only_exclusive_all_transport=True,CPU_only_no_native_GPU_worker_or_GO=True))
 pw=getpass.getpass('72 existing ce3 raw CPU-only diagnosis (hidden): ');c=None
 try:
  c=a.connect72(pw);pw=None
  pre=a.code(c,a.PY,"from pathlib import Path;import json,sys,psutil,os,fcntl;B=Path(sys.argv[1]);assert (B/'NODE_EXIT_ACTUAL.json').is_file() and (B/'NODE_ORIGINAL_ERROR.json').is_file() and not (B/'job0/production').exists();alive=[p.info for p in psutil.process_iter(['pid','create_time','cmdline']) if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or [])];assert not alive,alive;print(json.dumps(dict(actual_prior_node_all_children_out=True,original_failed_native_preserved_no_production=True)))",TARGET,timeout=60);d.put('CE3_CPU_DIAGNOSTIC_PRIOR_ERROR_NO_PRODUCTION_ALL_OUT_ACTUAL.json',pre)
  sf=c.open_sftp()
  try:
   for name in ('ce3_existing_native_dual_mean_strict_false_diagnostic_only_v1.py','review_existing_ce3_native_strict_actor_false_all_other_rows_diagnostic_CPU_once.py'):
    try:sf.stat(TARGET+'/'+name)
    except FileNotFoundError:sf.put(str(B/name),TARGET+'/'+name)
    else:raise AssertionError('CPU diagnosis once already exists')
  finally:sf.close()
  code=r'''
from pathlib import Path
import os,sys,json,time,runpy,contextlib,psutil
B=Path(sys.argv[1]);os.environ['CUDA_VISIBLE_DEVICES']=''
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='2'
sys.path.insert(0,str(B));begin=time.time();pid=os.getpid();creation=psutil.Process(pid).create_time()
with (B/'CE3_EXISTING_NATIVE_CPU_DIAGNOSTIC_CONSOLE.log').open('x') as log:
 with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):runpy.run_path(str(B/'review_existing_ce3_native_strict_actor_false_all_other_rows_diagnostic_CPU_once.py'),run_name='__main__')
report=json.loads((B/'job0/native/H1_CE3_NATIVE180_STRICT_ACTOR_FALSE_ALL_OTHER_ROWS_DIAGNOSTIC_CPU_ACTUAL.json').read_bytes());assert report['passed'] is False and report['diagnostic_only_not_native_admission'];print(json.dumps(dict(epoch=time.time(),CPU_pid=pid,creation=creation,elapsed=time.time()-begin,report=report,no_GPU_native_GO_or_canonical_mutation=True)))
'''
  result=a.code(c,a.PY,code,TARGET,timeout=900);d.put('CE3_EXISTING_NATIVE_STRICT_ACTOR_FALSE_ALL_ROWS_CPU_DIAGNOSTIC_ACTUAL.json',result);print(json.dumps(dict(all_other_checks=result['report']['all_other_original_checks_passed'],strict_actor_reference_pass=result['report']['strict_actor_reference_pass'],FP64_max=result['report']['all_saved_actor_CPUmean_maxabs'],FP32_max=result['report']['original_FP32_maxabs_diagnostic'],no_GO=True)),flush=True)
 finally:
  pw=None
  if c:c.close()

if __name__=='__main__':
 try:main()
 except BaseException:d.put('CE3_CPU_DIAGNOSTIC_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_permission_from_diagnostic=True));raise
