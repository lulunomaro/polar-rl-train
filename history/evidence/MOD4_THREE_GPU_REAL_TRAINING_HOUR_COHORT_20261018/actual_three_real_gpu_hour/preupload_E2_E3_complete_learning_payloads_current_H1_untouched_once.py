"""Install source-bound learning payloads now; no new writer or production before old H1 handoff."""
from pathlib import Path
import os,sys,json,time,getpass,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';S=W/'MOD4_THREE_GPU_UTILIZATION_STORAGE_RECOVERY_20261018';sys.path.insert(0,str(S));import deploy_two_idle_4090_linux_reward_frame_observations_once as d
a=d.a;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ROOTS={'e2':'/mnt/mod4_linux_durable_20261013/T3h_1810v1/e2p','recovery':'/home/lc01/Zonglin Li/zonglin2/tasks/T3h_1810v1/recovery'}
G=W/'MOD4_UNIFIED_THREE_SLOT_H1_E2_E3_HANDOFF_20261017';sp=importlib.util.spec_from_file_location('old_deployer_CPU_only_never_main',G/'deploy_three_slot_after_actual_N72_closed_handoff_once.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def upload(c,py,key,local,root):
 cfg=dict(d.S['E2' if key=='e2' else 'E3'],root=root);code=d.ADMIT.replace("B.mkdir();print", "B.parent.mkdir(parents=True,exist_ok=True);B.mkdir();print");put(key.upper()+'_LEARNING_SLOT_PREUPLOAD_FRESH_RESOURCE_REAL_FCNTL_ACTUAL.json',a.code(c,py,d.codefmt(code,cfg),timeout=90));sf=c.open_sftp();made={root}
 try:
  sf.get_channel().settimeout(120)
  for p in sorted(local.rglob('*')):
   if '__pycache__' in p.parts:continue
   remote=root+'/'+p.relative_to(local).as_posix()
   if p.is_dir():
    if remote not in made:sf.mkdir(remote);made.add(remote)
   else:sf.put(str(p),remote)
 finally:sf.close()
 cpu=a.code(c,py,old.CPU,root,timeout=180);put(key.upper()+'_LEARNING_SLOT_TARGET_SOURCE_ACTUAL_RSL_SDK_CPU_PREUPLOADED.json',cpu)
 m=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());proof=json.loads((local/'ADMITTED_NATIVE_REUSE_PROVENANCE.json').read_bytes());spec=dict(key=key,source_SHA=m['source_SHA'],GPU_UUID=proof['GPU_UUID'],execution_backend=proof['execution_backend'],native_controls=proof['controls'])
 reuse=a.code(c,py,"from pathlib import Path;import sys,json,time;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from admitted_existing_same_source_native_CPU_v1 import load;spec=json.loads(sys.argv[2]);v=load(spec,B);print(json.dumps(dict(epoch=time.time(),strict_original_native_same_source_backend_GPU_reuse_passed=True,proof=v,no_native_GPU_replay_or_PPO_or_budget=True)))",root,json.dumps(spec),timeout=180);put(key.upper()+'_LEARNING_SLOT_TARGET_ACTUAL_EXISTING_NATIVE_REUSE_CPU_PROOF.json',reuse);return dict(key=key,root=root,manifest_SHA=H(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),actual_source_CPU=True,actual_native_reuse_CPU=True)
def main():
 put('E2_E3_LEARNING_PAYLOAD_PREUPLOAD_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transport=True,no_live_H1_or_owner_change=True));pw=getpass.getpass('72 E3 complete learning payload, current H1 untouched (hidden): ');c=None;results=[]
 try:
  c=a.t.connect();results.append(upload(c,a.t.PY,'e2',B/'payload/e2_paid',ROOTS['e2']));c.close();c=a.connect72(pw);pw=None;results.append(upload(c,a.PY,'recovery',B/'payload/recovery',ROOTS['recovery']));put('E2_E3_COMPLETE_LEARNING_PAYLOADS_PREUPLOADED_CPU_READY_ACTUAL.json',dict(epoch=time.time(),results=results,no_production_GO_or_new_writer_yet=True,current_H1_hour_not_interrupted=True,finite_transport_returned=True));print(json.dumps(dict(results=results,H1_training_untouched=True,new_training_not_claimed_before_GO=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_E3_PREUPLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_no_repeat_or_live_patch=True));raise
