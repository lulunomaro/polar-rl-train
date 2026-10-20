from pathlib import Path
import hashlib,importlib.util,json,os,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import fcntl,hashlib,json,os,platform,psutil,shutil,subprocess,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');D=Path('/mnt/mod4_linux_durable_20261013');locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 row=dict(path=str(p),exists=p.is_file())
 if p.is_file():
  with p.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);row['actual_fcntl_free']=True;fcntl.flock(f,fcntl.LOCK_UN)
   except BlockingIOError:row['actual_fcntl_free']=False
 locks.append(row)
canonical=dict(path=str(C),exists=C.is_file())
if C.is_file():
 raw=C.read_bytes();c=json.loads(raw);segments=[]
 for s in c.get('completed_segments',[]):segments.append({k:s[k] for k in ('run_id','id','segment_id','owner_parent_pid','actual_production_seconds','elapsed_seconds','charged_seconds','duration_seconds','experts','phase','started_epoch','ended_epoch','production_go_epoch','production_end_epoch') if k in s})
 canonical.update(SHA=hashlib.sha256(raw).hexdigest(),top_keys=list(c),active_segment_is_None=c.get('active_segment') is None,authorized_training_seconds=c.get('authorized_training_seconds'),remaining_training_seconds=c.get('remaining_training_seconds'),consumed_training_seconds=c.get('consumed_training_seconds'),extension_count=len(c.get('budget_extensions',[])),completed_count=len(c.get('completed_segments',[])),completed_segments=segments)
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(('/home/egde/rl_candidates/MOD4_','/mnt/mod4_linux_durable_20261013/')) for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
def run(cmd):return subprocess.check_output(cmd,timeout=20,text=True).strip()
out=dict(epoch=time.time(),system=platform.system(),release=platform.release(),boot_epoch=psutil.boot_time(),GPU=run(['nvidia-smi','--query-gpu=index,name,uuid,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits']),compute=run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),RAM_available_bytes=psutil.virtual_memory().available,durable_path=str(D),durable_exists=D.exists(),durable_is_mount=D.is_mount(),durable_disk=dict(zip(('total','used','free'),shutil.disk_usage(D if D.exists() else D.parent))),original_canonical=canonical,original_locks=locks,only_project_own_process_identities=own,source17_E2_node_exists=(D/'T3sf17_1910v22/e2/NODE_EXIT_ACTUAL.json').is_file(),no_original_account_or_training_or_peer_identity_write=True)
print(json.dumps(out))
'''
def main():
 put('RETURNED_LINUX4090_PROBE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,new_human_online_notice=True,one_finite_readonly_transport=True))
 p=B.parent/'MOD4_AVAILABLE_E2_E3_HOUR18_20261019/deploy_available_E2_E3_original_writer_V2_once.py';sp=importlib.util.spec_from_file_location('existing_original_Linux_transport_only',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);t=m.a.t;c=t.connect()
 try:
  transport=c.get_transport();transport.set_keepalive(15);fp=hashlib.sha256(transport.get_remote_server_key().asbytes()).hexdigest();cfg=json.loads((B.parent/'MOD4_POLICY_50HZ_CONTINUATION_20261020/remote_snapshot_policy50_V5/controller/SERIES_CONFIG_NO_SECRET.json').read_bytes());import base64;assert transport.get_remote_server_key().asbytes()==base64.b64decode(cfg['original_Linux_host_key'])
  cmd=shlex.quote(t.PY)+' -u -B -c '+shlex.quote(READ);_,out,err=c.exec_command(cmd,timeout=60);raw=out.read().decode();error=err.read().decode();rc=out.channel.recv_exit_status();assert rc==0,(raw,error);v=json.loads(raw);assert v['system']=='Linux';put('RETURNED_ORIGINAL_LINUX4090_READONLY_ACTUAL.json',dict(epoch=time.time(),actual=v,original_Linux_hostkey_SHA=fp,actual_finite_transport_returned=True,no_training_or_canonical_write=True));print(json.dumps(dict(system=v['system'],GPU=v['GPU'],durable_is_mount=v['durable_is_mount'],canonical_none=v['original_canonical'].get('active_segment_is_None'),canonical_remaining=v['original_canonical'].get('remaining_training_seconds'),own_processes=len(v['only_project_own_process_identities']),locks=v['original_locks'])),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('RETURNED_LINUX4090_PROBE_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_once=True));raise
