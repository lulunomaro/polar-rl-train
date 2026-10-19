"""Read only missing process identity for the extra GPU process already observed."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports'
sys.path.insert(0,str(W/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'))
import deploy_three_next_closed_source_hours_once as d
CODE=r'''
import json,time,psutil,subprocess
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();rows=[]
for line in compute.splitlines():
 fields=[x.strip() for x in line.split(',')]
 if len(fields)<3 or fields[0] not in ('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'):continue
 pid=int(fields[1]);row=dict(GPU_UUID=fields[0],pid=pid,used_MiB=fields[2])
 try:
  p=psutil.Process(pid);cmd=p.cmdline();root='/home/lc01/Zonglin Li/zonglin2/tasks/T3sf9_1910v14/'
  row.update(ppid=p.ppid(),create_time=p.create_time(),name=p.name(),exe=p.exe(),cwd=p.cwd(),is_our_exact_ninth_namespace=any(x.startswith(root) for x in cmd),script_paths_only=[x for x in cmd if x.endswith('.py')],full_argv_intentionally_not_collected=True)
 except psutil.Error as exc:row['actual_lookup_error']=type(exc).__name__
 rows.append(row)
print(json.dumps(dict(epoch=time.time(),actual_GPU_compute_snapshot=compute,processes=rows,read_only_identity_no_job_files_or_secrets_read=True,no_process_or_GPU_or_training_mutation=True)))
'''
def put(name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2)
def main():
 put('EXTRA_GPU_IDENTITY_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,finite_metadata_missing_only=True))
 pw=getpass.getpass('72 observed extra GPU process identity only (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None
  actual=d.a.code(c,d.a.PY,CODE,timeout=45);put('CURRENT_TARGET_GPU_PROCESS_IDENTITIES_ACTUAL.json',actual)
  print(json.dumps(actual,ensure_ascii=False))
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('GPU_IDENTITY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
