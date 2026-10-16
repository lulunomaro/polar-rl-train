"""Human-triggered recovery: existing roots/models only, no runtime replay."""
from pathlib import Path
import sys,os,time,json,getpass,traceback,subprocess
U=Path(__file__).resolve().parent;R=U/'reports'
import collect_existing_three_slot_after_local_collector_unreported_exit_v2_once as a
READ=a.c.READ.replace("for kind,name in [('immutable_startup0'", "for kind,name in [('immutable_startup0'")
EXTRA=r'''
from pathlib import Path
import sys,json,time,hashlib,subprocess,psutil,shutil
B=Path(sys.argv[1]);key=sys.argv[2];final=B/'job0/production/FINAL.json';out=[]
if final.is_file():
 v=json.loads(final.read_bytes());r=v.get('final')
 if r:
  p=Path(r['path']);assert p.resolve().is_relative_to((B/'job0/production').resolve());assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'];out.append(dict(r,kind='actual_complete_final'))
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,utilization.gpu,memory.used,memory.free','--format=csv,noheader,nounits'],timeout=20).decode();compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,gpu_uuid,used_gpu_memory','--format=csv,noheader,nounits'],timeout=20).decode();print(json.dumps(dict(epoch=time.time(),key=key,models=out,all_GPU_snapshot=gpu,actual_compute_snapshot=compute,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(B).free,readonly=True)))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def collect(conn,py,key):
 row=a.c.a.code(conn,py,READ,a.c.ROOTS[key],key);extra=a.c.a.code(conn,py,EXTRA,a.c.ROOTS[key],key);row['resource_and_final_snapshot']=extra;row['models']+=extra['models'];folder=U/'actual_human_recovered_three_slot_models'/key;folder.mkdir(parents=True);sf=conn.open_sftp();sf.get_channel().settimeout(120);models=[]
 try:
  for item in row['models']:
   p=folder/Path(item['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(item['path'],str(tmp));assert tmp.stat().st_size==item['bytes'] and a.c.a.H(tmp)==item['SHA'];tmp.replace(p);models.append(dict(item,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return row,models
def main():
 q=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'python*' -and $_.ProcessId -ne "+str(os.getpid())+" -and $_.CommandLine -like '*MOD4_UNIFIED_THREE_SLOT_H1_E2_E3_HANDOFF_20261017*' -and $_.CommandLine -like '*collect*'} | Select-Object ProcessId,CreationDate | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True);assert not q.stdout.strip();put('HUMAN_NETWORK_RESTORED_THREE_SLOT_EXISTING_ONLY_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),all_previous_own_collectors_CIM_absent=True,actual_alive_only_exclusive_transport=True,human_network_restored_event_not_periodic_extra_watcher=True,no_GPU_or_ledger_mutation=True));pw=getpass.getpass('Host72 existing finals, human network restored (hidden): ');conn=None;out={};models={}
 try:
  conn=a.c.a.t.connect();out['owner']=a.c.a.code(conn,a.c.a.t.PY,READ,a.c.SOURCE,'owner');out['h1'],models['h1']=collect(conn,a.c.a.t.PY,'h1');out['actual_original_account_and_twofcntl_snapshot']=a.c.a.code(conn,a.c.a.t.PY,a.ACCOUNT);put('HUMAN_NETWORK_RESTORED_SOURCE210_EXISTING_FINALS_BOUND_ACTUAL.json',dict(epoch=time.time(),owner=out['owner'],h1=out['h1'],models=models['h1'],account=out['actual_original_account_and_twofcntl_snapshot']))
 finally:a.c.a.t.close(conn);conn=None
 try:
  conn=a.c.a.connect72(pw);pw=None
  for key in ('e2','recovery'):out[key],models[key]=collect(conn,a.c.a.PY,key);put('HUMAN_NETWORK_RESTORED_'+key.upper()+'_EXISTING_FINALS_BOUND_ACTUAL.json',dict(epoch=time.time(),scope=out[key],models=models[key]))
 finally:
  pw=None
  if conn:conn.close()
 out.update(epoch=time.time(),downloaded_models=models,human_network_restored_event=True,previous_timeout_and_pending0_preserved=True,no_GPU_native_Task_once_replay=True);put('HUMAN_NETWORK_RESTORED_THREE_SLOT_EXISTING_FIRST_FINALS_ACCOUNT_EXIT_RESOURCE_COLLECTION_ACTUAL.json',out);print(json.dumps(dict(epoch=out['epoch'],models={k:[dict(kind=x['kind'],SHA=x['SHA'],bytes=x['bytes']) for x in v] for k,v in models.items()},actual_original_locks=out['actual_original_account_and_twofcntl_snapshot']['actual_locks'],own_processes={k:out[k].get('actual_own_processes') for k in ('owner','h1','e2','recovery')})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('HUMAN_NETWORK_RESTORED_THREE_SLOT_EXISTING_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_native_or_once_replay=True));raise
