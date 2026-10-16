"""New isolated reward axis; original native/CPU admission precedes any PPO GO.

Reuse immutable old payload, never replays any consumed H1 task. Credentials and
signed bridge capability exist only in stdin/memory; no deletion or SDK changes.
"""
from pathlib import Path
import sys,os,json,time,hashlib,paramiko,getpass,shlex,secrets,traceback,subprocess
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports';H0=W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'
A='/home/lc01/Zonglin Li/zonglin2/tasks/'+H0.name;OLD=A+'/first1800_from_admitted_native_v1';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;S='/mnt/mod4_linux_durable_20261013/'+D.name;PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
sys.path.insert(0,str(H0));from deploy_H1_fullstate_native_and_collect_own_scope_finite_v1_once import code,H
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t

def put(n,v,rolling=False):
 p=R/n
 if rolling:q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def connect72(password):
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());c.connect('10.24.0.72',username='lc01',password=password,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';return c

def launch(c,py,root,name,cfg):
 si,so,se=c.exec_command(shlex.quote(py)+' -u -B '+shlex.quote(root+'/'+name),timeout=35);si.write(json.dumps(cfg)+'\n');si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode(errors='replace');return json.loads(raw)

def main():
 assert not (R/'V2_NEW_NATIVE_CPU_FINITE_TRANSPORT_STARTED_ACTUAL.json').exists();manifest=Q/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json';m=json.loads(manifest.read_bytes());proof=R/'H1_V2_COMPLETE_SOURCE_MIGRATION_INVERSE_AST_GRANT_NEGATIVES_CPU_ACTUAL.json';v=json.loads(proof.read_bytes());assert v['CPU_candidate_passed'] and v['complete_manifest_SHA']==H(manifest);first=json.loads((H0/'reports/H1_PRODUCTION_FINAL10_COMPLETE_MODEL_EXACT_COST_EXIT_LOCAL_CPU_ACTUAL.json').read_bytes());assert m['source_SHA']=='78d44aa801e06c962b2ee8cf289a8d5ed3229fb13814c8d820c26e89adb2183d'
 put('V2_NEW_NATIVE_CPU_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),actual_alive_only_transport_owner_all210_72_249=True,one_bounded_initial_same_connection_900s=True,source_SHA=m['source_SHA'],native0PPO_before_actual_GPU_CPU_and_original_GO=True));pw=getpass.getpass('Host72 new H1 isolated admission password (hidden): ');c=sf=None;cfg=None
 try:
  c=t.connect();v=code(c,t.PY,r'''
from pathlib import Path
import sys,json,time,fcntl,socket,psutil
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=json.loads(C.read_bytes());assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>1800+9400.860692501068+64800
locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_free=True))
with socket.socket() as sock:sock.bind(('10.24.4.210',29734))
old=C.parent
B=Path(sys.argv[1]);assert B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve()) and not B.exists()
print(json.dumps(dict(epoch=time.time(),original_canonical_active=b['active_segment'],authorized=b['authorized_training_seconds'],extensions=len(b['budget_extensions']),charged=b['charged_training_seconds'],remaining=b['remaining_training_seconds'],actual_two_fcntl_free=locks,new_port29734_available=True,no_budget_write_no_new_owner_yet=True)))
''',S);put('V2_SOURCE_ORIGINAL_CANONICAL_LOCK_PORT_FRESH_READONLY_ACTUAL.json',v)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);v=code(c,PY,r'''
from pathlib import Path
import sys,json,time,hashlib,fcntl,shutil,psutil,subprocess
A=Path(sys.argv[1]);P=Path(sys.argv[2]);B=Path(sys.argv[3]);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert B.resolve().is_relative_to(owned) and not B.exists() and A.resolve().is_relative_to(owned) and P.resolve().is_relative_to(owned)
assert json.loads((P/'job0/production/FINAL.json').read_bytes())['passed'] and json.loads((P/'NODE_EXIT_ACTUAL.json').read_bytes())['all_own_children_actual_waited']
ident=json.loads((P/'NODE_IDENTITY.json').read_bytes())
if psutil.pid_exists(ident['pid']):
 proc=psutil.Process(ident['pid']);assert abs(proc.create_time()-ident['creation'])>.01 or proc.cmdline()!=ident['argv']
with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
g=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in g.splitlines() if 'c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
src=P/'job0/production/model_update10.pt';assert src.stat().st_size==16400923 and hashlib.sha256(src.read_bytes()).hexdigest()==sys.argv[4]
for name in ('runtime','source','assets'):
 for p in (A/'job0'/name).rglob('*'):assert p.resolve().is_relative_to(owned)
B.mkdir();(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copytree(A/'lib',B/'lib')
for p in A.glob('*.py'):shutil.copy2(p,B/p.name)
shutil.copy2(src,B/'job0/source/H1_final10_protected.pt')
print(json.dumps(dict(epoch=time.time(),new_unused_root=str(B),actual_old_H1_FINAL_and_children_out=True,actual_validation_fcntl_free=True,GPU1_resource=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,protected_actual_final10_SHA=sys.argv[4],all_original_entries_retained=True,no_GPU_or_native_or_PPO_started_yet=True)))
''',A,OLD,T,m['source_SHA']);put('V2_TARGET_RESOURCE_OLD_EXIT_NEW_ROOT_REUSE_PROTECTED_FINAL10_ACTUAL.json',v)
  sf=c.open_sftp();sf.get_channel().settimeout(120);sf.put(str(manifest),T+'/'+manifest.name);diff=code(c,PY,r'''
from pathlib import Path
import sys,json,hashlib
B=Path(sys.argv[1]);m=json.loads((B/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json').read_bytes());missing=[]
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve())
 if not p.is_file() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:missing.append(r)
print(json.dumps(dict(missing=missing,reused_exact_files=len(m['files'])-len(missing))))
''',T);put('V2_REUSE_EXACT_BYTES_ONLY_MISSING_UPLOAD_LIST_ACTUAL.json',diff)
  for row in diff['missing']:
   p=Q/row['relative'];assert p.is_file() and p.stat().st_size==row['bytes'] and H(p)==row['SHA'],row['relative'];parts=row['relative'].split('/')[:-1];remote=T
   for piece in parts:
    remote+='/'+piece
    try:sf.stat(remote)
    except FileNotFoundError:sf.mkdir(remote)
   sf.put(str(p),T+'/'+row['relative'])
  sf.close();sf=None;v=code(c,PY,r'''
from pathlib import Path
import sys,json,hashlib,ast,os,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(sys.argv[1]);m=json.loads((B/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json').read_bytes());torch.set_num_threads(2);rng=torch.get_rng_state().clone()
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
for r in m['actual_RSL_sources']:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['SHA']
sdk=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/utils/math.py');assert hashlib.sha256(sdk.read_bytes()).hexdigest()==m['SDK_math_actual_SHA']
src=B/'job0/source/H1_final10_protected.pt';s=torch.load(src,map_location='cpu',weights_only=False)
def tree(x):
 if torch.is_tensor(x):return (1,int(x.is_floating_point()),not x.is_floating_point() or bool(torch.isfinite(x).all()))
 vals=x.values() if isinstance(x,dict) else x if isinstance(x,(tuple,list)) else []
 rows=[tree(v) for v in vals];return (sum(v[0] for v in rows),sum(v[1] for v in rows),all(v[2] for v in rows))
count=tree(s);assert count[2] and len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={639760}
sys.path[:0]=[str(B),str(B/'job0/runtime/isaac/mod4')];from h1_takeoff_progress_phase_v2 import H1TakeoffProgressPhaseV2,EXTRA
p=H1TakeoffProgressPhaseV2(20000,'cpu');p.load_state_dict(s['H1_public_request_phase_state']['phase']);assert all(not p.tensors()[k].any() for k in EXTRA) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
v=dict(epoch=time.time(),all448_target_bytes_SHA_AST_exact=True,files=len(m['files']),payload_manifest_SHA=hashlib.sha256((B/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json').read_bytes()).hexdigest(),actual_original_RSL_SDK_math_SHA_unchanged=True,source_SHA=hashlib.sha256(src.read_bytes()).hexdigest(),complete_checkpoint_tensor_counts=count,source_actor9_critic8_STD17Adam639760_finite=True,actual_saved20k_V1_phase_CPU_migration_three_new_fields0=True,global_CPU_RNG_unchanged0CUDA0optimizer=True,new_target_native_fullrestore_physics_PPO_not_yet_passed=True);(B/'TARGET_V2_ALL_SOURCE_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
''',T);put('V2_TARGET_ALL448_SDK_SOURCE_TYPED_MIGRATION_CPU_ACTUAL.json',v)
 finally:
  if sf:sf.close();sf=None
  if c:c.close();c=None
 try:
  c=t.connect();v=code(c,t.PY,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);assert B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve()) and not B.exists();B.mkdir();print(json.dumps(dict(new_source_root=str(B),no_existing_scope_changed=True)))",S);put('V2_SOURCE_NEW_OWNED_FINITE_ROOT_ACTUAL.json',v);sf=c.open_sftp();sf.put(str(Q/'h1_prelaunch_v2_original_canonical_owner_v1.py'),S+'/h1_prelaunch_v2_original_canonical_owner_v1.py');sf.close();sf=None;cfg=dict(token=secrets.token_hex(32),run_id='H1_GROUND_PRELAUNCH_V2_'+str(time.time_ns()),target_root=T,source_SHA=m['source_SHA'],payload_manifest_SHA=H(manifest),local_CPU_receipt_SHA=H(proof));owner=launch(c,t.PY,S,'h1_prelaunch_v2_original_canonical_owner_v1.py',cfg);put('V2_ORIGINAL_OWNER_DETACHED_DISPATCH_ACTUAL.json',owner)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;node=launch(c,PY,T,'h1_prelaunch_v2_native_CPU_production_node_v1.py',cfg);actual=code(c,PY,"import sys,json,time,psutil;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(node['detached_pid']));put('V2_NEW_NATIVE_CPU_THEN_FINITE_PRODUCTION_ACTUAL_DISPATCH.json',dict(epoch=time.time(),source_owner=owner,target_node=node,target_actual_creation_argv=actual,new_native180_CPU_not_inferred_passed=True,actual_original_GO_after_native_CPU_required=True,no_learning_granted_by_prepared_files=True))
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close();c=None
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   v=code(c,t.PY,r'''
from pathlib import Path
import sys,json,time,psutil,hashlib
B=Path(sys.argv[1]);files=[]
for n in ('OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','OWNER_NOT_GRANTED_TERMINAL.json','HUMAN_H1_PRELAUNCH_V2_CONTINUE_ORIGINAL_CANONICAL_CONTRACT.json'):
 p=B/n
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if str(B/'h1_prelaunch_v2_original_canonical_owner_v1.py') in (p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=files,actual_owner_processes=procs,readonly_ownroot=True)))
''',S);put('V2_SOURCE_FINITE_INITIAL_CURRENT_ACTUAL.json',v,True);cur=next((x['value'] for x in v['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{})
   if cur.get('row',{}).get('phase')=='production' or any(x['path'].endswith(('/OWNER_EXIT_ACTUAL.json','/OWNER_ORIGINAL_ERROR.json','/OWNER_NOT_GRANTED_TERMINAL.json')) for x in v['files']) or time.monotonic()-begun>=900:break
   time.sleep(15)
  put('V2_INITIAL_SAME_CONNECTION_FINITE_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],actual_owner_processes=v['actual_owner_processes'],phase=cur.get('row',{}).get('phase'),go=cur.get('go'),node_error=cur.get('row',{}).get('original_error'))),flush=True)
 finally:t.close(c)

if __name__=='__main__':
 try:main()
 except BaseException:put('V2_NEW_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_requires_actual_inspection_no_blind_relaunch=True,no_consumed_task_or_native_replay=True));raise
