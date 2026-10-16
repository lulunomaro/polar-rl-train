"""New human independent-task allocation, detached source owner and target node; never retry blindly."""
from pathlib import Path
import getpass,hashlib,json,paramiko,secrets,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
SRC='/mnt/mod4_linux_durable_20261013/'+D.name;DST='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name
CODE=r'''
from pathlib import Path
import hashlib,json,os,psutil,subprocess,sys,fcntl,socket,tarfile,time
root=Path(C['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2') if C['target72'] else Path('/mnt/mod4_linux_durable_20261013');assert root.resolve().is_relative_to(owned.resolve()) and not root.is_symlink()
if C['phase']=='guard':
 assert not root.exists();disk=psutil.disk_usage(str(owned));assert disk.free>12*2**30
 gpu=subprocess.run(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True);rows=[dict(uuid=x.split(',')[0].strip(),free_MiB=int(x.split(',')[1].strip())) for x in gpu.stdout.splitlines() if x.strip()]
 needed=['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'] if C['target72'] else ['GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e']
 assert all(any(x['uuid']==uuid and x['free_MiB']>=21000 for x in rows) for uuid in needed),'Insufficient actual memory capacity; do not alter other jobs'
 assert psutil.virtual_memory().available>(80 if C['target72'] else 40)*2**30
 v=dict(epoch=time.time(),root=str(root),unused=True,GPU=rows,RAM_available=psutil.virtual_memory().available,disk_free=disk.free,other_compute_not_signalled=True)
 if not C['target72']:
  p=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');x=json.loads(p.read_bytes());assert x['active_segment'] is None and x['authorized_training_seconds']==1188000 and len(x['budget_extensions'])==7;v['canonical']={k:x[k] for k in ('active_segment','charged_training_seconds','remaining_training_seconds')}
  for p in [p.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
   with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  s=socket.socket();s.settimeout(1);rc=s.connect_ex(('10.24.4.210',29716));s.close();assert rc!=0
 print(json.dumps(v))
elif C['phase']=='mkdir':root.mkdir();print(json.dumps(dict(created=str(root))))
elif C['phase']=='extract':
 z=root/C['archive'];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert z.stat().st_size==C['bytes'] and H(z)==C['SHA'];B=root/'train';B.mkdir()
 with tarfile.open(z,'r:gz') as tf:
  for m in tf.getmembers():
   p=B/m.name;assert m.isfile() and p.resolve().is_relative_to(B.resolve()) and not p.exists();p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('xb') as f:f.write(tf.extractfile(m).read())
 assert H(B/'TRAIN_PACKAGE_MANIFEST.json')==C['manifest_SHA'];manifest=json.loads((B/'TRAIN_PACKAGE_MANIFEST.json').read_bytes())
 for r in manifest['rows']:assert (B/r['relative']).stat().st_size==r['bytes'] and H(B/r['relative'])==r['SHA'],r['relative']
 print(json.dumps(dict(epoch=time.time(),root=str(B),actual_files_SHA_verified=len(manifest['rows']),no_GPU_or_PPO=True)))
'''
def run(c,py,C,timeout=120):
 si,so,se=c.exec_command(shlex.quote(py)+' -B -',timeout=timeout);si.write('C='+repr(C)+'\n'+CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();return json.loads(raw)
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def upload(c,py,root,is72,prep):
 C=dict(root=root,target72=is72,phase='guard');g=run(c,py,C);put(('TARGET72' if is72 else 'SOURCE210')+'_DISTINCT_EXPERT_RESOURCE_ACTUAL.json',g);run(c,py,{**C,'phase':'mkdir'});sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:sf.put(prep['package']['path'],root+'/'+Path(prep['package']['path']).name)
 finally:sf.close()
 C.update(phase='extract',archive=Path(prep['package']['path']).name,bytes=prep['package']['bytes'],SHA=prep['package']['SHA'],manifest_SHA=prep['manifest_SHA']);v=run(c,py,C,180);put(('TARGET72' if is72 else 'SOURCE210')+'_DISTINCT_EXPERT_EXTRACT_CPU_ACTUAL.json',v)
def launch(c,py,root,role,config):
 cmd=shlex.quote(py)+' -u -B '+shlex.quote(root+'/train/independent_expert_cohort_owner_node_v1.py')+' --role '+role;si,so,se=c.exec_command(cmd,timeout=30);si.write(json.dumps(config)+'\n');si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 code='import json,psutil; p=psutil.Process('+str(v['detached_pid'])+'); print(json.dumps(dict(pid=p.pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())))';si,so,se=c.exec_command(shlex.quote(py)+' -B -c '+shlex.quote(code),timeout=20);data=so.read();assert so.channel.recv_exit_status()==0,se.read().decode();v['actual_identity']=json.loads(data);return v
def main():
 assert not (R/'THREE_DISTINCT_EXPERT_COHORT_DISPATCH_STARTED.json').exists();prep=json.loads((R/'INDEPENDENT_COHORT_SUM_ACTUAL_INTERVALS_IN_MEMORY_CPU_AND_PACKAGE.json').read_bytes());assert prep['passed'];token=secrets.token_hex(32);config=dict(token=token,run_id=D.name);pw=getpass.getpass('Host72 SSH password (hidden, never saved): ');c=None
 def target():
  c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';return c
 put('THREE_DISTINCT_EXPERT_COHORT_DISPATCH_STARTED.json',dict(epoch=time.time(),human='3060负责评测，三张4090负责不同专家训练',source_root=SRC,target72_root=DST,first_each_parent_max1800=True,aggregate_max5400_existing_budget=True,auth_capability_only_stdin_memory=True,no_other_process_action=True))
 try:c=target();upload(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh',DST,True,prep)
 finally:
  if c:c.close()
 try:
  c=t.connect();upload(c,t.PY,SRC,False,prep);review=R/'CURB878_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json'
  if review.exists():
   sf=c.open_sftp()
   try:sf.put(str(review),SRC+'/train/CURB_FROZEN_RESULT_REVIEW.json')
   finally:sf.close()
  v=launch(c,t.PY,SRC,'owner',config);put('SOURCE210_DISTINCT_EXPERT_OWNER_DETACHED_ACTUAL.json',v)
 finally:t.close(c)
 try:c=target();v=launch(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh',DST,'node72',config);put('TARGET72_DISTINCT_EXPERT_NODE_DETACHED_ACTUAL.json',v)
 finally:
  if c:c.close()
  pw=None;token=None;config.clear()
 put('THREE_DISTINCT_EXPERT_COHORT_DISPATCH_ACTUAL.json',dict(epoch=time.time(),new_actual_native_chain_dispatched=True,actual_PPO_updates_not_yet_inferred=True,source_root=SRC,target72_root=DST,first1800_each_after_independent_CPU_native_admission=True,CURB_learning_also_waits_actual_frozen_CPU_result=True,laptop_not_runtime_dependency=True));print(json.dumps(dict(detached=True,three_distinct_tasks_native_admission_underway_not_yet_PPO_positive=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('THREE_DISTINCT_EXPERT_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_readonly_first_no_repeat=True));raise
