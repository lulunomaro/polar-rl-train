"""Current user-requested status and source diagnosis; sequential readonly hosts."""
from pathlib import Path
import sys,os,json,time,traceback,getpass,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True)
P=B.parent/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017';sys.path.insert(0,str(P))
from deploy_human_requested_H1_new_finite_strict_native_reuse_once import a
CODE72=r'''
from pathlib import Path
import json,time,hashlib,subprocess,psutil,shutil
root=Path('/home/lc01/Zonglin Li/zonglin2');site=root/'envs/mod4/lib/python3.12/site-packages';rsl=site/'rsl_rl';lab=root/'src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab_rl/isaaclab_rl/rsl_rl';rows=[];missing=[]
for base,label in ((rsl,'rsl_rl'),(lab,'isaaclab_rl/rsl_rl')):
 if not base.is_dir():missing.append(str(base));continue
 for p in sorted(base.rglob('*.py')):
  raw=p.read_bytes();s=raw.decode('utf8')
  if any(k in s for k in ('std_param','GaussianDistribution','clip_actions')) or p.name in ('ppo.py','on_policy_runner.py'):
   rows.append(dict(path=str(p),relative=label+'/'+p.relative_to(base).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=s))
assert next(x['SHA'] for x in rows if x['relative']=='rsl_rl/algorithms/ppo.py')=='a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c'
assert next(x['SHA'] for x in rows if x['relative']=='rsl_rl/runners/on_policy_runner.py')=='39358a0a60219fdb360df7acddf80f6a382837aa58e2ec0ccf875df4afee4825'
def run(*cmd):return subprocess.run(cmd,capture_output=True,text=True,timeout=20).stdout.strip()
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=p.info;cmd=v['cmdline'] or []
  if any(str(root/'tasks') in s for s in cmd):own.append(v)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
print(json.dumps(dict(epoch=time.time(),host='10.24.0.72',GPU=run('nvidia-smi','--query-gpu=index,uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'),compute=run('nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'),own_task_processes=own,target_disk_free=shutil.disk_usage(root).free,files=rows,source_lookup_missing=missing,readonly_no_GPU_SDK_import=True)))
'''
CODE210=r'''
from pathlib import Path
import json,time,subprocess,psutil,shutil
p=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def run(*cmd):return subprocess.run(cmd,capture_output=True,text=True,timeout=20).stdout.strip()
own=[]
for proc in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=proc.info;cmd=v['cmdline'] or []
  if any('/mnt/mod4_linux_durable_20261013/' in s for s in cmd):own.append(v)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
print(json.dumps(dict(epoch=time.time(),host='10.24.4.210',GPU=run('nvidia-smi','--query-gpu=index,uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'),compute=run('nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'),own_durable_processes=own,original_canonical_path=str(p),original_canonical=json.loads(p.read_bytes()),D_free=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,home_free=shutil.disk_usage('/home/egde').free,readonly_no_budget_or_GPU_import=True)))
'''
def main():
 with (R/'CURRENT_GPU_BUDGET_SOURCE_FINITE_COLLECTOR_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_creation_argv_alive_only_exclusive_transport=True,readonly_two_hosts_sequential_no249=True),f,indent=2)
 results={};pw=getpass.getpass('72 status and actual source readonly (hidden): ')
 for host in ('72','210'):
  c=None
  try:
   c=a.connect72(pw) if host=='72' else a.t.connect();v=a.code(c,a.PY if host=='72' else a.t.PY,CODE72 if host=='72' else CODE210,timeout=120)
   if host=='72':
    out=B/'actual_installed_RSL72_readonly_sources';out.mkdir()
    for row in v['files']:
     dest=out/row['relative'];dest.parent.mkdir(parents=True,exist_ok=True);raw=row['text'].encode();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA'];dest.write_bytes(raw);row['local_path']=str(dest)
   with (R/('HOST'+host+'_CURRENT_GPU_BUDGET_ACTUAL_SOURCES_READONLY.json')).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
   results[host]=dict(passed=True,epoch=v['epoch'],compute=v['compute'],GPU=v['GPU'],files=len(v.get('files',[])))
  except BaseException:
   results[host]=dict(passed=False,epoch=time.time(),error=traceback.format_exc())
   with (R/('HOST'+host+'_CURRENT_STATUS_SOURCE_ORIGINAL_ERROR.json')).open('x',encoding='utf8') as f:json.dump(results[host],f,indent=2)
  finally:
   if c:c.close()
 pw=None
 with (R/'CURRENT_GPU_BUDGET_SOURCES_BOUNDED_COLLECTION_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),results=results,transport_returned=True,no_249_connection_or_training_budget_mutation=True),f,indent=2)
 print(json.dumps(results),flush=True)
if __name__=='__main__':main()
