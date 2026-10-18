"""Actual original FP32 audit of saved native with the unchanged original absolute bound."""
from pathlib import Path
import os,sys,time,json,getpass,traceback
import deploy_human_approved_ce3_new_native_then_one_finite1800_once as d
B=d.B;R=d.R;a=d.a;TARGET=d.TARGET

def main():
 prep=json.loads((R/'CE3_ORIGINAL_FP32_REFERENCE_SAME_BOUND_EXISTING_RAW_CPU_PREPARED_ACTUAL.json').read_bytes());assert prep['original_absolute1e4_unchanged'] and prep['all_original_FP32_actor_and_physics_guard_AST_unchanged']
 d.put('CE3_ORIGINAL_FP32_EXISTING_RAW_CPU_VERIFY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_transport=True,CPU_only_no_GPU_or_GO=True))
 pw=getpass.getpass('72 original FP32 formal CPU check of existing raw (hidden): ');c=None
 try:
  c=a.connect72(pw);pw=None;name='review_ce3_native_original_FP32_reference_allrows_CPU_once.py';sf=c.open_sftp()
  try:
   try:sf.stat(TARGET+'/'+name)
   except FileNotFoundError:sf.put(str(B/name),TARGET+'/'+name)
   else:raise AssertionError('Formal original FP32 reader once already uploaded')
  finally:sf.close()
  code=r'''
from pathlib import Path
import sys,json,time,runpy,os,psutil,hashlib,contextlib
B=Path(sys.argv[1]);name=sys.argv[2];assert not (B/'job0/production').exists() and (B/'NODE_EXIT_ACTUAL.json').exists();os.environ['CUDA_VISIBLE_DEVICES']=''
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='2'
sys.path.insert(0,str(B));begin=time.time();pid=os.getpid();creation=psutil.Process(pid).create_time()
with (B/'CE3_ORIGINAL_FP32_FORMAL_READER_CONSOLE.log').open('x') as log:
 with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):runpy.run_path(str(B/name),run_name='__main__')
path=B/'job0/native/H1_CE3_ORIGINAL_FP32_NATIVE180_ALL_ROWS_CPU_ACTUAL.json';v=json.loads(path.read_bytes());assert v['passed'] and v['all_saved_actor_CPUmean_maxabs']<=1e-4;assert not (B/'job0/native/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json').exists();print(json.dumps(dict(epoch=time.time(),CPU_pid=pid,creation=creation,elapsed=time.time()-begin,original_FP32_formal_allrow_CPU=v,CPU_report=dict(path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest()),dual_FP64_admission_false_unchanged=True,old_owner_node_failure_not_relabelled_pass=True,no_GPU_or_GO_or_canonical_write=True)))
'''
  out=a.code(c,a.PY,code,TARGET,name,timeout=900);d.put('CE3_ORIGINAL_FP32_FORMAL_NATIVE_ALL_ROWS_CPU_SAME_BOUND_ACTUAL.json',out);print(json.dumps(dict(original_FP32_full_batch_passed=True,mean_max=out['original_FP32_formal_allrow_CPU']['all_saved_actor_CPUmean_maxabs'],no_GO=True)),flush=True)
 finally:
  pw=None
  if c:c.close()

if __name__=='__main__':
 try:main()
 except BaseException:d.put('CE3_ORIGINAL_FP32_FORMAL_VERIFY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_GO_or_gate_relaxation=True));raise
