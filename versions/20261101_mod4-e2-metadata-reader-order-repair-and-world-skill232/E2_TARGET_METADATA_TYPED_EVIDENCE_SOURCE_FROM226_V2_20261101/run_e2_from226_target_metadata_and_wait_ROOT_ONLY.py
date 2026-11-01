"""ROOT target-only CPU metadata entry. No network, SDK scene, model or assets.

Requires an installed226 job and ROOT's fresh actual authority/CPU admission.
Runs the unchanged226 probe once and captures its actual original child wait.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time,traceback
from contract_e2_from226 import (KIND,PROBE,EXPECTED,read_metadata,authority,metadata_admission,require)

CHILD_CODE='''from pathlib import Path
import json,os,psutil,runpy,sys,time
probe,job,identity=sys.argv[1:];p=psutil.Process()
value=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd(),epoch=time.time())
with Path(identity).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
sys.argv=[probe,'--job-root',job];runpy.run_path(probe,run_name='__main__')'''


def put(p,value):
 with p.open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)


def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True)
 p.add_argument('--actual-authority',type=Path,required=True);p.add_argument('--metadata-admission',type=Path,required=True)
 p.add_argument('--sdk-python-launcher',type=Path,required=True);p.add_argument('--purpose-id',required=True)
 p.add_argument('--timeout-seconds',type=int,required=True);a=p.parse_args();J=a.job_root.resolve()
 require(1<=a.timeout_seconds<=360,'ROOT bounded metadata timeout1..360 seconds')
 auth,ar=read_metadata(a.actual_authority);current=authority(auth,a.purpose_id,J)
 resource,rr=read_metadata(a.metadata_admission);metadata_admission(resource,a.purpose_id,J,ar['SHA'],a.sdk_python_launcher)
 probe=J/'probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py'
 require(hashlib.sha256(probe.read_bytes()).hexdigest()==PROBE,'Unchanged frozen226 probe')
 require(read_metadata(J/'EXPECTED226_TARGET_METADATA.json')[1]['SHA']==EXPECTED,'Fixed226 expected source contract')
 require(not (J/'METADATA226_ONCE_CONSUMED.json').exists(),'Old probe purpose already consumed;never replay')
 put(J/'E2_FROM226_ROOT_METADATA_ENTRY_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=a.purpose_id,
  authority=ar,metadata_admission=rr,current=current,model_asset_raw_GPU_calls=0,original226_probe_invocations=1))
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
 identity_path=J/'E2_FROM226_ORIGINAL_METADATA_CHILD_IDENTITY.json'
 args=[str(a.sdk_python_launcher),'-u','-B','-c',CHILD_CODE,str(probe),str(J),str(identity_path)]
 start=time.time();child=None;timed_out=False;stdout=stderr=b''
 try:
  child=subprocess.Popen(args,cwd=J,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  try:stdout,stderr=child.communicate(timeout=a.timeout_seconds)
  except subprocess.TimeoutExpired:
   timed_out=True
   put(J/'E2_FROM226_METADATA_TIMEOUT_ORIGINAL_FALSE.json',dict(
    epoch=time.time(),passed=False,purpose_id=a.purpose_id,original_Popen_PID=child.pid,
    declared_timeout_seconds=a.timeout_seconds,actual_waited=False,all_own_children_waited=False,
    original_child_still_requires_communicate_and_wait=True,no_signal_sent=True,
    FREE_or_EX_release_claimed=False,no_automatic_retry=True))
   # Preserve the original child. Continue its original pipe collection/wait;
   # the timeout remains false even if it later returns0. No FREE claim here.
   stdout,stderr=child.communicate()
 finally:
  if child is not None:child.wait()
 finished=time.time();streams=[]
 for name,data in [('E2_FROM226_METADATA_ORIGINAL_STDOUT.txt',stdout),('E2_FROM226_METADATA_ORIGINAL_STDERR.txt',stderr)]:
  path=J/name
  with path.open('xb') as f:f.write(data)
  streams.append(dict(path=str(path),bytes=len(data),SHA=hashlib.sha256(data).hexdigest()))
 report_path=J/'E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json';report=None;report_ref=None
 if report_path.exists():report,report_ref=read_metadata(report_path)
 identity=read_metadata(identity_path)[0] if identity_path.exists() else None
 passed=bool(child is not None and child.returncode==0 and not timed_out and identity and report and report.get('passed'))
 wait=dict(purpose=KIND,purpose_id=a.purpose_id,passed=passed,actual_waited=child is not None,
  returncode=child.returncode if child else None,original_child_identity=identity,original_Popen_PID=child.pid if child else None,
  started_epoch=start,finished_epoch=finished,all_own_children_waited=True,timed_out=timed_out,
  report_SHA=report_ref['SHA'] if report_ref else None,report=report_ref,original_streams=streams,
  actual_authority=ar,metadata_admission=rr,model_reads=0,model_decodes=0,physical_binary_reads=0,
  GPU_or_App_calls=0,no_training_GO_or_account_write=True)
 path=J/'E2_FROM226_ORIGINAL_METADATA_CHILD_WAIT_ACTUAL.json';put(path,wait)
 print(json.dumps(dict(passed=passed,wait=str(path),report=report_ref,model_reads=0)),flush=True)
 require(passed,'Original metadata child failed/unknown;preserve result and do not replay')


if __name__=='__main__':
 try:main()
 except BaseException:
  # Retain caller failure without hiding the probe's own original error/report.
  args=sys.argv;job=None
  if '--job-root' in args:job=Path(args[args.index('--job-root')+1])
  if job and job.is_dir():put(job/('E2_FROM226_METADATA_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_automatic_retry=True))
  raise
