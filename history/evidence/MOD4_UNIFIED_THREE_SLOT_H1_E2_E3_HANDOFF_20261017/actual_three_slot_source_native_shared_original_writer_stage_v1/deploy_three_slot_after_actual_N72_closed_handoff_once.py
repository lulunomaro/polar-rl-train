"""Fresh three-slot pipeline only after actual previous full saves and original handoff."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback
U=Path(__file__).resolve().parent;W=U.parent;N=W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017';R=U/'reports';Q=U/'payload';sys.path.insert(0,str(N))
import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
from stdin_only_finite_launch_v1 import launch
SOURCE='/mnt/mod4_linux_durable_20261013/T3_1710v1/owner';ROOTS={'h1':'/mnt/mod4_linux_durable_20261013/T3_1710v1/h1',**{k:'/home/lc01/Zonglin Li/zonglin2/tasks/T3_1710v1/'+k for k in ('e2','recovery')}}
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,os,json,time,hashlib,shutil,psutil,subprocess
B=Path(sys.argv[1]);A=Path(sys.argv[2]);key=sys.argv[3];owned=Path('/mnt/mod4_linux_durable_20261013') if key=='h1' else Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and A.resolve().is_relative_to(owned.resolve()) and not B.exists() and len(str(B/'job0/tmp'))<100
if key=='h1':
 assert json.loads((A/'PARENT_FINAL.json').read_bytes())['passed'] and json.loads((A/'PARENT_EXIT_ACTUAL.json').read_bytes())['own_child_actual_waited_out'];src=A/'job0/source/H1_final10_protected.pt'
else:
 e=json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes());assert e['actual_all_own_children_waited'] and e['validation_fcntl_released'];v=json.loads((A/'job0/production/FINAL.json').read_bytes());assert v['passed'];src=Path(v['final']['path']);assert src.resolve().is_relative_to((A/'job0/production').resolve())
alive=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(s.startswith(str(A)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive,alive;assert hashlib.sha256(src.read_bytes()).hexdigest()==sys.argv[4];gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if sys.argv[6] in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3;B.mkdir(parents=True);(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copy2(src,B/'job0/source'/sys.argv[5]);print(json.dumps(dict(epoch=time.time(),new_root=str(B),previous_all_own_children_actual_out=True,actual_source_SHA=sys.argv[4],actual_GPU_resource=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,new_files_only_no_old_mutation_or_GPU_or_GO=True)))
'''
CPU=r'''
from pathlib import Path
import sys,os,json,time,hashlib,ast,importlib.util
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch;torch.set_num_threads(2);B=Path(sys.argv[1]);mf=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';m=json.loads(mf.read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rng=torch.get_rng_state().clone()
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
source=B/'job0/source'/m['source_filename'];assert H(source)==m['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);counts=[0,0]
def finite(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,(tuple,list)):
  for v in x:finite(v)
finite(s);assert counts==m['source_schema_counts'] and len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in s['optimizer_state_dict']['state'].values()}=={m['source_Adamstep']};rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)));actual=[]
for r in m['expected_actual_RSL_sources']:
 p=rsl/r['relative'];assert p.stat().st_size==r['bytes'] and H(p)==r['SHA'];actual.append(dict(path=str(p),SHA=H(p)))
sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))/'utils/math.py';assert H(sdk)==m['expected_actual_SDK_math_SHA'];assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();v=dict(epoch=time.time(),passed_CPU_only=True,key=m['key'],source_SHA=m['source_SHA'],source_schema_counts=counts,all17Adam=m['source_Adamstep'],all_target_manifest_SHA_AST_passed=True,manifest_SHA=H(mf),actual_RSL_sources=actual,actual_SDK_math=dict(path=str(sdk),SHA=H(sdk)),CPU_RNG_unchanged0CUDA0optimizer=True,native_and_PPO_not_yet_passed=True);(B/'TARGET_FULL_SOURCE_INSTALLED_RSL_SDK_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
def upload(c,py,key,spec):
 root=ROOTS[key];put(key.upper()+'_PREVIOUS_EXIT_SOURCE_NEW_ROOT_RESOURCE_ACTUAL.json',a.code(c,py,CREATE,root,spec['previous_runtime_root'],key,spec['source_SHA'],spec['source_filename'],spec['GPU_UUID']));sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  mf=Q/key/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';sf.put(str(mf),root+'/'+mf.name);v=a.code(c,py,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());print(json.dumps(dict(missing=[r for r in m['files'] if not (B/r['relative']).is_file() or (B/r['relative']).stat().st_size!=r['bytes'] or hashlib.sha256((B/r['relative']).read_bytes()).hexdigest()!=r['SHA']])))",root);put(key.upper()+'_MISSING_ONLY_UPLOAD_LIST_ACTUAL.json',v)
  for row in v['missing']:
   p=Q/key/row['relative'];assert a.H(p)==row['SHA'];folder=root
   for piece in row['relative'].split('/')[:-1]:
    folder+='/'+piece
    try:sf.stat(folder)
    except FileNotFoundError:sf.mkdir(folder)
   sf.put(str(p),root+'/'+row['relative'])
 finally:sf.close()
 put(key.upper()+'_ALL_TARGET_SOURCE_INSTALLED_RSL_SDK_CPU_ADMITTED_ACTUAL.json',a.code(c,py,CPU,root,timeout=180))
def main():
 prep=json.loads((R/'THREE_SLOT_ACTUAL_CLOSED_SOURCES_FULL_CPU_FROZEN_PAYLOADS_PREPARED.json').read_bytes());assert prep['passed_CPU_only'] and prep['old_owner_and_children_actual_out_original_two_fcntl_free'];specs=prep['specs'];put('THREE_SLOT_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,all_source_target_CPU_before_owner_and_nodes=True));pw=getpass.getpass('Host72 new three-slot same-scope handoff (hidden): ');c=None;cfg=None
 try:
  c=a.t.connect();upload(c,a.t.PY,'h1',specs['h1'])
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw)
  for key in ('e2','recovery'):upload(c,a.PY,key,specs[key])
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();v=a.code(c,a.t.PY,r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,socket
B=Path(sys.argv[1]);assert B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve()) and not B.exists();old=Path('/mnt/mod4_linux_durable_20261013/N72_1710v2');assert json.loads((old/'COHORT_FINAL.json').read_bytes())['original_cost_settled'] and json.loads((old/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];i=json.loads((old/'OWNER_IDENTITY.json').read_bytes())
if psutil.pid_exists(i['pid']):
 p=psutil.Process(i['pid']);assert abs(p.create_time()-i['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());assert v['active_segment'] is None and v['authorized_training_seconds']==1188000 and len(v['budget_extensions'])==7;locks=[]
for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(path))
with socket.socket() as sock:sock.bind(('10.24.4.210',29754))
B.mkdir(parents=True);print(json.dumps(dict(epoch=time.time(),actual_old_owner_and_children_closed_cost_settled=True,actual_original_canonical_activeNone_twofcntl_free=locks,new_unused_owner_root=str(B),port29754_available=True,no_canonical_write=True)))
''',SOURCE);put('ORIGINAL_PREVIOUS_OWNER_ACTUAL_OUT_CANONICAL_NONE_TWO_LOCKS_NEW_OWNER_ADMISSION.json',v);sf=c.open_sftp()
  try:
   for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py'):sf.put(str(U/name),SOURCE+'/'+name)
  finally:sf.close()
  cfg=dict(role='owner',experts=specs,run_id='THREE_INDEPENDENT_H1_E2_E3_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);put('THREE_SLOT_ONE_ORIGINAL_OWNER_ACTUAL_DETACHED_DISPATCH.json',dict(epoch=time.time(),owner=owner,all_targets_CPU_complete=True));h1=launch(a.code,c,a.t.PY,ROOTS['h1'],'three_slot_finite_node_v1.py',dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']));put('H1_SAME_NATIVE_REUSE_FRESH_PRODUCTION_NODE_ACTUAL_DETACHED.json',dict(epoch=time.time(),node=h1,not_yet_actual_GO_or_PPO=True))
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;nodes={'h1':h1}
  for key in ('e2','recovery'):nodes[key]=launch(a.code,c,a.PY,ROOTS[key],'three_slot_finite_node_v1.py',dict(specs[key],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('THREE_SLOT_ACTUAL_H1_REUSE_E2_E3_NEW_NATIVE_FINITE_CHAIN_DETACHED.json',dict(epoch=time.time(),owner=owner,nodes=nodes,source_root=SOURCE,roots=ROOTS,source_SHA={k:s['source_SHA'] for k,s in specs.items()},source_Adamstep={k:s['source_Adamstep'] for k,s in specs.items()},new_H1_reuse_and_E2_E3_native_not_PPO_pass=True,per_slot_caps={'h1':1800,'e2':3600,'recovery':3600},headroom300_each=True,one_original_writer_sum_actual_distinct_intervals_only=True,capability_transport_SSH_stdin_child_stdin_no_CFG_argv=True,no_new_budget_or_automatic_next_window=True));print(json.dumps(dict(owner=owner,nodes=nodes,actual_detached_not_native_or_PPO_pass=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE_SLOT_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_actual_inspection_only_no_blind_retry=True));raise
