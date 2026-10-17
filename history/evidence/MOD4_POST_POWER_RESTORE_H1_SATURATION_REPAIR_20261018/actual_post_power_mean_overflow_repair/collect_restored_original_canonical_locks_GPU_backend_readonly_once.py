"""New human-restored boundary; read original ledger and real locks without mutation."""
from pathlib import Path
import json,sys,time,os,getpass,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';Z=B.parent/'MOD4_POWER_RESTORED_THREE_HOST_READONLY_CHECK_20261018'
sp=importlib.util.spec_from_file_location('recovery_pure_helpers_not_once_main',Z/'collect_human_requested_three_host_recovery_readonly_bounded_once.py');z=importlib.util.module_from_spec(sp);sp.loader.exec_module(z);a=z.a
CODE210=z.CODE210.replace("print(json.dumps(dict(","v=dict(").replace("no_GPU_SDK_import_or_mount_or_budget_mutation=True)))","no_GPU_SDK_import_or_mount_or_budget_mutation=True)\n")+r'''
import fcntl,socket
locks=[]
for p in (p.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 item=dict(path=str(p),exists=p.exists())
 if p.exists():
  st=p.stat();item.update(inode=st.st_ino,device=st.st_dev)
  try:
   with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   item['actual_nonblocking_fcntl_free']=True
  except BlockingIOError:item['actual_nonblocking_fcntl_free']=False
 locks.append(item)
old=Path('/mnt/mod4_linux_durable_20261013/H1r_1810v4/owner');old_reports={}
for n in ('OWNER_IDENTITY.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json'):
 p=old/n;old_reports[n]=json.loads(p.read_bytes()) if p.exists() else None
v.update(original_locks=locks,last_original_owner_reports=old_reports)
print(json.dumps(v))
'''
CODE72=r'''
from pathlib import Path
import json,time,psutil,shutil,subprocess,fcntl
B=Path('/home/lc01/Zonglin Li/zonglin2')
def run(*cmd):
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=20);return dict(returncode=r.returncode,stdout=r.stdout.strip(),stderr=r.stderr.strip())
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=p.info
  if any(str(B/'tasks') in s for s in (v['cmdline'] or [])):own.append(v)
 except psutil.Error:pass
locks=[]
for name in ('three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock','three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock','finite_environment_validation.lock'):
 p=B/'state'/name;v=dict(path=str(p),exists=p.exists())
 if p.exists():
  st=p.stat();v.update(inode=st.st_ino,device=st.st_dev)
  try:
   with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   v['actual_fcntl_free']=True
  except BlockingIOError:v['actual_fcntl_free']=False
 locks.append(v)
print(json.dumps(dict(epoch=time.time(),boot_epoch=psutil.boot_time(),GPU=run('nvidia-smi','--query-gpu=index,uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'),compute=run('nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'),own_tasks=own,actual_locks=locks,disk_free=shutil.disk_usage(B).free,RAM_available=psutil.virtual_memory().available,no_new_GPU_or_runtime_budget_mutation=True)))
'''
def main():
 with (R/'RESTORED_ORIGINAL_BOUNDARY_COLLECTOR_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_created_argv_alive_only_exclusive_all_transport=True),f,indent=2)
 pw=getpass.getpass('72 restored original boundary readonly (hidden): ');out={}
 for key,code in [('210',CODE210),('72',CODE72)]:
  c=None
  try:
   c=a.t.connect() if key=='210' else a.connect72(pw);v=a.code(c,a.t.PY if key=='210' else a.PY,code,timeout=90)
   with (R/('HOST'+key+'_RESTORED_CANONICAL_LOCKS_GPU_ACTUAL.json')).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
   out[key]=dict(passed_readonly=True,epoch=v['epoch'],GPU=v['GPU'],compute=v['compute'],D_is_mountpoint=v.get('D_is_mountpoint'),original_active_None=v.get('original_canonical',{}).get('active_segment') is None if v.get('original_canonical') else None)
  except BaseException:
   out[key]=dict(passed_readonly=False,error=traceback.format_exc())
   with (R/('HOST'+key+'_RESTORED_BOUNDARY_ORIGINAL_ERROR.json')).open('x',encoding='utf8') as f:json.dump(out[key],f,indent=2)
  finally:
   if c:c.close()
  print(json.dumps(dict(host=key,summary=out[key])),flush=True)
 pw=None
 with (R/'RESTORED_ORIGINAL_BOUNDARY_FINITE_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),results=out,transport_returned=True,no_GPU_or_budget_or_mount_write=True),f,indent=2)
if __name__=='__main__':main()
