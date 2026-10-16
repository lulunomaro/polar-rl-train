"""New exact H1 first1800 chain after actual native/local-source admission only.

Copies already admitted immutable bytes to a new scope, never restarts native.
Credentials and the private control capability exist only in stdin/memory.
"""
from pathlib import Path
import os,sys,json,time,hashlib,paramiko,getpass,shutil,shlex,secrets,traceback,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'first1800_actual_admitted_payload_v1';OLD='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;T=OLD+'/first1800_from_admitted_native_v1';S='/mnt/mod4_linux_durable_20261013/'+D.name+'/first1800_from_admitted_native_v1';PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
sys.path.insert(0,str(D));from deploy_H1_fullstate_native_and_collect_own_scope_finite_v1_once import code,H
sys.path.insert(0,str(D.parent/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def launch(c,py,root,name,cfg):
 si,so,se=c.exec_command(shlex.quote(py)+' -u -B '+shlex.quote(root+'/'+name),timeout=35);si.write(json.dumps(cfg)+'\n');si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode(errors='replace');return json.loads(raw)
def connect72(password):
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());c.connect('10.24.0.72',username='lc01',password=password,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';return c
def main():
 assert not (R/'H1_FIRST1800_ACTUAL_ORIGINAL_OWNER_NODE_DISPATCH.json').exists();audit=json.loads((R/'H1_COMPLETE_FULL20K_NATIVE_ALL_ROWS_TWOHOST_MODELS_LOCAL_CPU_ADMITTED_ACTUAL.json').read_bytes());assert audit['passed'];manifest=json.loads((Q/'H1_FIRST1800_PAYLOAD_MANIFEST.json').read_bytes());cert=json.loads((Q/'H1_ACTUAL_ADMISSION_CERTIFICATE.json').read_bytes());assert manifest['source_SHA']==cert['source_SHA']==audit['admitted_H1_full_source']['SHA'];put('H1_FIRST1800_NEW_UNUSED_SCOPE_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),max_initial_source_bound_collection_seconds=600,actual_alive_only_transport_owner_210_72_249=True,no_native_replay=True))
 pw=getpass.getpass('Host72 admitted H1 first1800 password (hidden): ');c=sf=None;cfg=None
 try:
  c=t.connect();v=code(c,t.PY,r'''
from pathlib import Path
import sys,json,time,fcntl,socket
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=json.loads(C.read_bytes());assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>1800+9400.860692501068+64800
locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_free=True))
with socket.socket() as sock:sock.bind(('10.24.4.210',29732))
print(json.dumps(dict(epoch=time.time(),original_canonical_active=b['active_segment'],authorized=b['authorized_training_seconds'],extensions=len(b['budget_extensions']),charged=b['charged_training_seconds'],remaining=b['remaining_training_seconds'],actual_two_fcntl_free=locks,new_owned_port29732_available=True,readonly_no_new_budget_or_learning_charge=True)))
''');put('H1_FIRST1800_SOURCE_ORIGINAL_CANONICAL_FRESH_RESOURCE_ADMISSION_ACTUAL.json',v)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);v=code(c,PY,r'''
from pathlib import Path
import sys,json,time,hashlib,fcntl,shutil,psutil,subprocess
A=Path(sys.argv[1]);B=Path(sys.argv[2]);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert B.resolve().is_relative_to(owned) and not B.exists() and A.resolve().is_relative_to(owned)
assert json.loads((A/'PARENT_FINAL.json').read_bytes())['passed'] and (A/'PARENT_EXIT_ACTUAL.json').exists();cpu=A/'job0/native/H1_NATIVE_FULL20K_ALL_ROWS_CPU_ADMITTED.json';v=json.loads(cpu.read_bytes());assert v['passed'] and hashlib.sha256(cpu.read_bytes()).hexdigest()==sys.argv[3]
scripts={str(A/n) for n in ('h1_native_finite_parent_v1.py','h1_fullstate_native_worker_v1.py','review_H1_full20k_native_allrows_CPU_v1.py')}
for p in psutil.process_iter(['cmdline']):
 try:assert not any(x in scripts for x in p.info['cmdline'] or []),p.pid
 except psutil.Error:pass
with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
g=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in g.splitlines() if 'c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
B.mkdir();(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copytree(A/'lib',B/'lib')
for p in A.glob('*.py'):shutil.copy2(p,B/p.name)
src=A/'job0/native/own_H1_full20k_native300.pt';assert hashlib.sha256(src.read_bytes()).hexdigest()==sys.argv[4];shutil.copy2(src,B/'job0/source/H1_admitted_full_source.pt')
print(json.dumps(dict(epoch=time.time(),new_unused_root=str(B),actual_native_CPU_complete_childout=True,actual_validation_fcntl_free=True,GPU1_resource=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,old_native_not_relaunched=True,all_original_entries_retained=True)))
''',OLD,T,cert['native_CPU_report_SHA'],cert['source_SHA']);put('H1_FIRST1800_TARGET_ACTUAL_NATIVE_EXIT_LOCK_RESOURCE_NEW_UNUSED_ROOT.json',v)
  sf=c.open_sftp();sf.get_channel().settimeout(120)
  for p in Q.rglob('*'):
   if p.is_file():sf.put(str(p),T+'/'+p.relative_to(Q).as_posix())
  sf.close();sf=None;verified=code(c,PY,r'''
from pathlib import Path
import sys,json,hashlib,ast,os,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(sys.argv[1]);m=json.loads((B/'H1_FIRST1800_PAYLOAD_MANIFEST.json').read_bytes())
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
for r in m['actual_RSL_sources']:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['SHA']
source=B/'job0/source/H1_admitted_full_source.pt';s=torch.load(source,map_location='cpu',weights_only=False);a=torch.load(B/'job0/source/E0_full_source.pt',map_location='cpu',weights_only=False)
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and a.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()==b.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()
 if isinstance(a,dict):return a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def finite(x):
 if torch.is_tensor(x):return not x.is_floating_point() or bool(torch.isfinite(x).all())
 if isinstance(x,dict):return all(finite(v) for v in x.values())
 if isinstance(x,(tuple,list)):return all(finite(v) for v in x)
 return True
for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[k],a[k]),k
assert finite(s) and len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={639560};assert 'H1_public_request_phase_state' in s and not torch.cuda.is_initialized()
v=dict(epoch=time.time(),files=len(m['files']),actual_all_target_bytes_SHA_exact=True,actual_original_RSL5_sources_SHA_unchanged=True,source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),admitted_H1_fullsource_actual_finite_and_ancestor_actor9critic8STD17Adamexact=True,new_H1_phase_fresh20k_restore_not_yet_passed=True,no_GPU_optimizer_or_learning_yet=True);(B/'TARGET_FIRST1800_SOURCE_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
''',T);put('H1_FIRST1800_TARGET_ALL441_SOURCE_AND_PREPARED_AST_CPU_ACTUAL.json',verified)
 finally:
  if sf:sf.close();sf=None
  if c:c.close();c=None
 try:
  c=t.connect();code(c,t.PY,"from pathlib import Path;import json,sys;B=Path(sys.argv[1]);assert B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve()) and not B.exists();B.mkdir(parents=True);print(json.dumps(dict(new_source_root=str(B),no_old_scope_changed=True)))",S);sf=c.open_sftp();sf.put(str(Q/'h1_first1800_original_canonical_owner_v1.py'),S+'/h1_first1800_original_canonical_owner_v1.py');sf.close();sf=None;cfg=dict(token=secrets.token_hex(32),run_id='H1_FIRST1800_'+str(time.time_ns()),target_root=T,source_SHA=cert['source_SHA'],native_CPU_report_SHA=cert['native_CPU_report_SHA'],local_CPU_receipt_SHA=cert['local_CPU_receipt_SHA']);owner=launch(c,t.PY,S,'h1_first1800_original_canonical_owner_v1.py',cfg);put('H1_FIRST1800_ORIGINAL_SOURCE_OWNER_DETACHED_DISPATCH_ACTUAL.json',owner)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;node=launch(c,PY,T,'h1_first1800_node72_finite_v1.py',cfg);actual=code(c,PY,"import sys,json,time,psutil;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(node['detached_pid']));put('H1_FIRST1800_ACTUAL_ORIGINAL_OWNER_NODE_DISPATCH.json',dict(epoch=time.time(),source_owner=owner,target_node=node,target_actual_process=actual,native_complete_not_reexecuted=True,source_SHA=cert['source_SHA'],original_scope1800_includes_all_learning_prechecks_save_and_exit=True,first_saved_PPO_not_inferred=True))
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close();c=None
 try:
  c=t.connect();start=time.monotonic()
  while True:
   v=code(c,t.PY,r'''
from pathlib import Path
import sys,json,time,psutil,hashlib
B=Path(sys.argv[1]);names=('OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','HUMAN_H1_FIRST1800_ORIGINAL_CANONICAL_CONTRACT.json');files=[]
for n in names:
 p=B/n
 if p.exists():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
scripts={str(B/'h1_first1800_original_canonical_owner_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=files,actual_owner_processes=procs,readonly=True)))
''',S)
   p=R/'H1_FIRST1800_SOURCE_CURRENT_FINITE_LOCAL_ACTUAL.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(v,indent=2),encoding='utf8');tmp.replace(p);current=next((x['value'] for x in v['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{})
   if current.get('row',{}).get('phase')=='production' or any('ORIGINAL_ERROR' in x['path'] or x['path'].endswith('/OWNER_EXIT_ACTUAL.json') for x in v['files']) or time.monotonic()-start>=600:break
   time.sleep(15)
  put('H1_FIRST1800_INITIAL_FINITE_SOURCE_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(actual_owner=v['actual_owner_processes'],current=current)),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_FIRST1800_NEW_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_inspect_actual_before_any_continuation=True,no_blind_relaunch_or_native_replay=True));raise
