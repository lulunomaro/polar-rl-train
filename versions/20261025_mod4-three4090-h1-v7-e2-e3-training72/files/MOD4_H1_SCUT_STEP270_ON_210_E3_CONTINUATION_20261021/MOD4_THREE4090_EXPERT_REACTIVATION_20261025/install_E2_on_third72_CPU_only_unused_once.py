"""Stage E2 on the authorized thirdGPU host; full target source CPU, no GPU/GO/writer."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports';N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V72_20261025'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
INSTALL=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
B=Path(v['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2');s=v['spec'];assert s['key']=='e2' and s['cross_host_qualified_source'] and s['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and not B.exists() and B.resolve().is_relative_to(owned.resolve())
for p in (Path(s['private_lock']),owned/'state/finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in x for x in compute.splitlines())
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x)
assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
base=Path(v['immutable_reuse_root']);before={r['relative']:r for r in json.loads((base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];dest=B/rel;src=base/rel;old=before.get(rel);assert dest.resolve().is_relative_to(B.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
 if old and old['SHA']==row['SHA'] and old['bytes']==row['bytes'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:shutil.copy2(src,dest);copied+=1
 else:need.append(row)
assert shutil.disk_usage(owned).free>25*1024**3
print(json.dumps(dict(epoch=time.time(),root=str(B),need_upload=need,source_immutable_files_reused=copied,GPU_line=line,durable_free_after_copy=shutil.disk_usage(owned).free,no_GPU_load_GO_writer_or_canonical_write=True,no_other_task_or_unknown_peer_modified=True)))
'''
try:
 q=json.loads((N/'reports/E2_CROSS_HOST_TARGET_PAYLOAD_SOURCE_CPU_PREPARED_V2_ACTUAL.json').read_bytes());assert q['passed']
 fix=json.loads((R/'E2_ACTUAL_NETWORK_SEND_AND_OWNER_INVENTORY_V2_CPU_ACTUAL.json').read_bytes());assert fix['passed']
 p=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025/reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json';current=json.loads(p.read_bytes())
 put('E2_THIRD_HOST_CPU_INSTALL_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,source_SHA=q['spec']['source_SHA'],root=q['root'],no_GPU_GO_or_new_writer=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 p=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py';sp=importlib.util.spec_from_file_location('memory',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:
  local=Path(q['payload']);manifest=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
  installed=d.code(c,d.PY72,INSTALL,dict(root=q['root'],spec=q['spec'],manifest=manifest,immutable_reuse_root=current['roots']['recovery']),timeout=90);put('E2_THIRD_HOST_SOURCE_FILES_RESOURCE_INSTALL_ACTUAL.json',installed)
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in installed['need_upload']:sf.put(str(local/row['relative']),q['root']+'/'+row['relative'])
   sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),q['root']+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  cpu=d.code(c,d.PY72,"import runpy,sys;sys.path.insert(0,v['root']);sys.argv=['target_two50_source_sdk_cpu_review.py',v['root']];runpy.run_path(v['root']+'/target_two50_source_sdk_cpu_review.py',run_name='__main__')",dict(root=q['root']),timeout=240);put('E2_THIRD_HOST_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json',cpu)
  admitted=d.code(c,d.PY72,"from pathlib import Path;import json,sys;sys.path.insert(0,v['root']);from original_account_policy50_source_CPU import load;print(json.dumps(load(v['spec'],Path(v['root']))))",dict(root=q['root'],spec=q['spec']),timeout=60);put('E2_THIRD_HOST_CROSS_HOST_QUALIFIED_SOURCE_CPU_ADMITTED_ACTUAL.json',admitted)
  ready=d.code(c,d.PY72,"from pathlib import Path;import json,sys,shutil;sys.path.insert(0,v['root']);from three_slot_common_v1 import valid_ready;q=v['admitted'];s=v['spec'];assert valid_ready(dict(key='e2',phase='ready',closed_source_CPU=q,manifest_SHA=s['manifest_SHA'],original_error=False),s);assert shutil.disk_usage(v['root']).free>25*1024**3;print(json.dumps(dict(epoch=__import__('time').time(),passed=True,actual_new_three_slot_valid_ready=True,kind=q['value']['kind'],durable_free_after_real_upload=shutil.disk_usage(v['root']).free,no_GPU_load_PPO_or_budget_write=True)))",dict(root=q['root'],spec=q['spec'],admitted=admitted),timeout=45);put('E2_THIRD_HOST_ACTUAL_SOURCE_VALID_READY_NO_GO_CPU_ACTUAL.json',ready)
 finally:c.close()
 put('E2_THIRD_HOST_CPU_INSTALL_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_finite_returned=True,root=q['root'],source_SHA=q['spec']['source_SHA'],source_Adam=839920,CPU=cpu,admitted=admitted,ready=ready,no_GPU_load_or_PPO_or_canonical_write=True))
 print(json.dumps(dict(passed=True,actual_full_target_CPU=True,E2_Adam=839920,no_GPU_GO_or_new_writer=True)))
except BaseException:
 put('E2_THIRD_HOST_CPU_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_retry_same_remote_root_or_once=True,no_new_writer_or_refund=True));raise
