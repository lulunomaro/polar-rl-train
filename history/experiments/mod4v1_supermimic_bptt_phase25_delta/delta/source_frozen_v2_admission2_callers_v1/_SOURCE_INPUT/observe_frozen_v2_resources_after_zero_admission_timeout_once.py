"""NEW read-only release witness AFTER closed zero-admission V2 timeout.
Not an extension/retry of old parent: no locks, parent, model, SDK or C writes.
"""
from pathlib import Path
import sys,json,time,shlex,hashlib
R=Path(__file__).resolve().parent;guard=R/'FROZEN_V2_POST_TIMEOUT_RELEASE_OBSERVER_STARTED_ONCE.json';out=R/'reports/FROZEN_V2_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json';current=R/'reports/FROZEN_V2_POST_TIMEOUT_RESOURCE_OBSERVER_CURRENT_V1.json';assert not guard.exists()and not out.exists();p=json.loads((R/'FROZEN_E3_W35_BATCH_V2_LATEST_CLOSED_RESULT_PATH.json').read_bytes());closedpath=Path(p['path']);raw=closedpath.read_bytes();v=json.loads(raw);t=v['top'];end=t['PARENT_EXIT_SCOPE.json'];assert v['closed']and not v['early_parent_dead']and t['ACTUAL_GROUP_ADMISSION.json']is None and t['CHILDREN.json']is None and t['GROUP_EVAL_START.json']is None and end['all_own_children_waited']and end['child_waits']==[]and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released']and end['canonical_writes']==0;assert len(v['rows'])==2 and all(x['status']=='NOT_ADMITTED'and x['FINAL']is None and x['WORKER_SCENE_READY']is None for x in v['rows']);assert 'Originalresourcewait1800sexpired'in str(t['PARENT_ORIGINAL_ERROR.json']);guard.write_text(json.dumps(dict(epoch=time.time(),old_root=v['root'],old_closed_epoch=end['epoch'],old_closed_metadata_SHA=hashlib.sha256(raw).hexdigest(),observer_only_no_parent_retry=True,cap_seconds=1800,interval_seconds=20),indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code=r'''
from pathlib import Path
import json,time,os,subprocess,shutil
B=Path('/home/lc01/Zonglin Li/zonglin2');D=B/'state/mod4_single_canonical_authority_20261026';C=json.loads((D/'TRAINING_BUDGET_10H.json').read_bytes());gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';locks=[D/'native_floor_supervisor.lock',D/'autonomy_controller.lock',B/'state/finite_environment_validation.lock',B/('state/three_expert_v2_'+gpu+'.lock')];kernel=Path('/proc/locks').read_text().splitlines();rows=[]
for path in locks:
 try:
  st=path.stat();key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}';rows.append(dict(path=str(path),records=[x for x in kernel if key in x.split()]))
 except FileNotFoundError:rows.append(dict(path=str(path),missing=True,records=[]))
summary={k:C.get(k)for k in('authority_generation','active_segment','remaining_training_seconds','charged_training_seconds','finite_minimum_remaining_seconds')};leases_clear=C.get('active_segment')is None and all(not x.get('missing')and not x['records']for x in rows);hardware=None;ready=False
if leases_clear:
 def q(args):
  x=subprocess.run(['nvidia-smi','--id='+gpu]+args,capture_output=True,text=True,timeout=20);assert x.returncode==0,x.stderr;return x.stdout.strip()
 card=q(['--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits']);apps=q(['--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']);fields=[a.strip()for a in card.split(',')];mem=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024;disk=shutil.disk_usage(B).free;ready=fields[0]==gpu and'4090'in fields[1]and int(fields[2])>=23500 and int(fields[3])==0 and not apps and mem>=96*1024**3 and disk>=25*1024**3 and float(C['remaining_training_seconds'])>=float(C['finite_minimum_remaining_seconds']);hardware=dict(card=card,compute_apps=apps,available_RAM_bytes=mem,disk_free_bytes=disk)
print(json.dumps(dict(epoch=time.time(),canonical_summary=summary,required_project_lock_rows=rows,original_relevant_leases_clear=leases_clear,hardware_if_leases_clear=hardware,original_frozen_resources_observed_clear=ready,actual_future_admission_not_guaranteed=True,lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0)))
'''
c=connect72();deadline=time.monotonic()+1800;last=None
try:
 while True:
  i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,err;a=json.loads(text);assert a['epoch']>=end['epoch'];record=dict(kind='READONLY_POST_FROZEN_V2_ZERO_ADMISSION_RESOURCE_RELEASE_WITNESS_NOT_ADMISSION',old_root=v['root'],old_closed_epoch=end['epoch'],old_closed_metadata_SHA=hashlib.sha256(raw).hexdigest(),actual=a,observer_only=True,old_parent_wait_not_extended=True);current.write_text(json.dumps(record,indent=2),encoding='utf-8');active=a['canonical_summary'].get('active_segment');state=(a['original_relevant_leases_clear'],a['original_frozen_resources_observed_clear'],active.get('owner_run_id')if isinstance(active,dict)else None)
  if state!=last:print('FROZEN_POST_TIMEOUT_RESOURCE_STATE '+json.dumps(dict(ready=state[1],leases_clear=state[0],owner=state[2],epoch=a['epoch'])),flush=True);last=state
  if a['original_frozen_resources_observed_clear']or time.monotonic()>=deadline:
   record.update(resource_release_observed=a['original_frozen_resources_observed_clear'],observer_timed_out=not a['original_frozen_resources_observed_clear']);out.write_text(json.dumps(record,indent=2),encoding='utf-8');print('FROZEN_RELEASE_WITNESS '+str(out));break
  time.sleep(min(20,max(0,deadline-time.monotonic())))
finally:c.close()
