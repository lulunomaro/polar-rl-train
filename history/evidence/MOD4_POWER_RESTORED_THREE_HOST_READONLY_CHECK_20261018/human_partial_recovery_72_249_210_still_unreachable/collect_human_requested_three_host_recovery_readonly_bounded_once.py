"""Explicit human-requested reconnection; no dispatch, mounts, ledger writes or replay."""
from pathlib import Path
import sys,os,json,time,traceback,getpass,hashlib,importlib.util,socket
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
Y=W/'MOD4_H1_ACTION_CHAIN_REPAIR_RESUME_20261018'
sp=importlib.util.spec_from_file_location('earlier_pure_readonly_code_not_main',Y/'collect_current_GPU_budget_and_actual_RSL_action_sources_bounded_once.py');prior=importlib.util.module_from_spec(sp);sp.loader.exec_module(prior);a=prior.a
sys.path[:0]=[str(W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017'),str(W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017'),str(W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017/curb275_final87_frozen3060_v1'),str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')]
import transport_249_E3_current_exact_desktop_2145_v1 as t
CODE210=r'''
from pathlib import Path
import json,time,psutil,shutil,subprocess,os
p=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');d=Path('/mnt/mod4_linux_durable_20261013')
def run(*cmd):
 v=subprocess.run(cmd,capture_output=True,text=True,timeout=20);return dict(returncode=v.returncode,stdout=v.stdout.strip(),stderr=v.stderr.strip())
own=[]
for proc in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=proc.info
  if any('/mnt/mod4_linux_durable_20261013/' in s for s in (v['cmdline'] or [])):own.append(v)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
print(json.dumps(dict(epoch=time.time(),host='10.24.4.210',boot_epoch=psutil.boot_time(),GPU=run('nvidia-smi','--query-gpu=index,uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'),compute=run('nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'),own_durable_processes=own,original_canonical_path=str(p),original_canonical=json.loads(p.read_bytes()) if p.exists() else None,D_path_exists=d.exists(),D_is_mountpoint=os.path.ismount(d),D_findmnt=run('findmnt','-T',str(d),'-J'),D_free=shutil.disk_usage(d).free if d.exists() else None,home_free=shutil.disk_usage('/home/egde').free,no_GPU_SDK_import_or_mount_or_budget_mutation=True)))
'''
CODE249=r'''
from pathlib import Path
import json,time,psutil,shutil,subprocess
def run(*cmd):
 v=subprocess.run(cmd,capture_output=True,text=True,timeout=20);return dict(returncode=v.returncode,stdout=v.stdout.strip(),stderr=v.stderr.strip())
own=[]
for proc in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=proc.info
  if any('MOD4' in s and ('async_eval' in s or 'frozen' in s) for s in (v['cmdline'] or [])):own.append(v)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
root=Path('D:/MOD4_async_eval/MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/E3_CLOSED85_FROZEN_V3')
print(json.dumps(dict(epoch=time.time(),host='10.24.4.249',boot_epoch=psutil.boot_time(),GPU=run('nvidia-smi','--query-gpu=index,uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'),compute=run('nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'),own_MOD4_eval_processes=own,D_free=shutil.disk_usage('D:/').free if Path('D:/').exists() else None,existing_E3_frozen_root_exists=root.exists(),not_GPU_admission_or_current_desktop_signature_or_MSVCRT_lock_proof=True,no_Task_or_GPU_or_budget_or_UI_mutation=True)))
'''
def main():
 with (R/'HUMAN_THREE_HOST_RECOVERY_COLLECTOR_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_identity_alive_only_exclusive_all_host_transport=True,human_manual_reconnect_overrides_defer_for_this_check_only=True,no_GPU_or_training_dispatched=True),f,indent=2)
 pw=getpass.getpass('72 recovery verification readonly (hidden): ');results={}
 for host in ('72','210','249'):
  c=None
  try:
   if host=='72':c=a.connect72(pw);v=a.code(c,a.PY,prior.CODE72,timeout=120)
   elif host=='210':c=a.t.connect();v=a.code(c,a.t.PY,CODE210,timeout=90)
   else:c=t.connect();v=t.py(c,CODE249,90)
   if host=='72':
    out=B/'actual_installed_RSL72_sources';out.mkdir()
    for row in v['files']:
     dest=out/row['relative'];dest.parent.mkdir(parents=True,exist_ok=True);raw=row['text'].encode();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA'];dest.write_bytes(raw);row['local_path']=str(dest)
   with (R/('HOST'+host+'_HUMAN_RECOVERY_CURRENT_READONLY_ACTUAL.json')).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
   results[host]=dict(SSH_authenticated_remote_execution=True,epoch=v['epoch'],GPU=v['GPU'],compute=v['compute'],own_process_count=len(v.get('own_task_processes',v.get('own_durable_processes',v.get('own_MOD4_eval_processes',[])))),files=len(v.get('files',[])),D_is_mountpoint=v.get('D_is_mountpoint'),D_free=v.get('D_free'))
  except BaseException:
   results[host]=dict(SSH_authenticated_remote_execution=False,epoch=time.time(),error=traceback.format_exc())
   with (R/('HOST'+host+'_HUMAN_RECOVERY_ORIGINAL_CONNECTION_ERROR.json')).open('x',encoding='utf8') as f:json.dump(results[host],f,indent=2)
  finally:
   if c:c.close()
  print(json.dumps(dict(host=host,result=results[host])),flush=True)
 pw=None
 try:
  with socket.create_connection(('10.24.4.249',3389),timeout=5):rdp=dict(port3389_TCP_connected=True)
 except OSError as e:rdp=dict(port3389_TCP_connected=False,error=str(e))
 report=dict(epoch=time.time(),hosts=results,RDP249=rdp,transport_returned=True,no_training_or_eval_dispatched=True,existing_deferred_automation_not_automatically_advanced=True)
 with (R/'HUMAN_THREE_HOST_CONNECTION_RECOVERY_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(all_finished=True,SSH={k:v['SSH_authenticated_remote_execution'] for k,v in results.items()},RDP249=rdp,no_dispatch=True)),flush=True)
if __name__=='__main__':main()
