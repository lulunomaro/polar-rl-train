"""One sequential root transport; reuse exact remote bytes, no consumed replay."""
from pathlib import Path
import sys,os,json,time,hashlib,paramiko,getpass,shlex,secrets,subprocess,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'training_payload';S='/mnt/mod4_linux_durable_20261013/'+D.name+'/curb';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/e2';A='/mnt/mod4_linux_durable_20261013/MOD4_E1_CURB35_FROM_878_NATIVE_TRAIN_20261016/production_fresh_process_v2';OLD='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016';PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
sys.path.insert(0,str(W/'MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016'));from deploy_grounded_H1_V2_new_native_CPU_then_finite1800_once import code,H,connect72,launch,t
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,hashlib,shutil,psutil,subprocess,socket
B=Path(sys.argv[1]);A=Path(sys.argv[2]);key=sys.argv[3];owned=Path('/mnt/mod4_linux_durable_20261013') if key=='curb' else Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
g=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in g.splitlines() if sys.argv[4] in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
src=A/('job0/production_only/model_update140.pt' if key=='curb' else 'job0/production/model_update58.pt');assert hashlib.sha256(src.read_bytes()).hexdigest()==sys.argv[5]
for name in ('runtime','source','assets'):
 for p in (A/'job0'/name).rglob('*'):assert p.resolve().is_relative_to(owned.resolve())
if key=='curb':
 with socket.socket() as sock:sock.bind(('10.24.4.210',29736))
B.mkdir(parents=True);(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copytree(A/'lib',B/'lib');shutil.copy2(src,B/'job0/source'/sys.argv[6])
print(json.dumps(dict(epoch=time.time(),new_unused_root=str(B),source_local_samehost_bytes_copy=str(src),source_SHA=sys.argv[5],actual_GPU_resource=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,no_old_scope_or_other_process_changed=True,no_GPU_or_PPO_yet=True)))
'''
CPU=r'''
from pathlib import Path
import sys,os,ast,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());torch.set_num_threads(2);rng=torch.get_rng_state().clone()
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
p=B/'job0/source'/m['source_filename'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['source_SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);count=[0,0]
def walk(x):
 if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():walk(v)
 elif isinstance(x,(tuple,list)):
  for v in x:walk(v)
walk(ck);assert count==m['source_schema_counts'] and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={m['source_Adamstep']}
if m['key']=='curb':assert ck['E1_terrain_state']['CURB_height_m']==.035 and ck['E1_terrain_state']['CURB_strip_width_m']==.15
else:assert ck['E2_moving4_command_state']['moving_yaw_cap']==4. and ck['E2_moving4_command_state']['kind']=='E2_WORLD_MOVING_SIGNED4'
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();v=dict(epoch=time.time(),passed_target_CPU_only=True,files=len(m['files']),source_SHA=m['source_SHA'],source_Adamstep=m['source_Adamstep'],whole_finite_tensor_counts=count,actual_all_target_SHA_AST_exact=True,original_actor9_critic8_STD17Adam_preserved=True,global_CPU_RNG_unchanged0CUDA0optimizer=True,native_fullrestore_physics_and_PPO_not_yet_passed=True);(B/'TARGET_SOURCE_CPU_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
def upload(c,py,root,key):
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  f=Q/key/'CONTINUATION_COMPLETE_MANIFEST_V2.json';sf.put(str(f),root+'/'+f.name);v=code(c,py,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());missing=[]\nfor r in m['files']:\n p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve());\n if not p.is_file() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:missing.append(r)\nprint(json.dumps(dict(missing=missing,reused_exact_files=len(m['files'])-len(missing))))",root);put(key.upper()+'_EXACT_REUSE_MISSING_ONLY_UPLOAD_ACTUAL.json',v)
  for r in v['missing']:
   p=Q/key/r['relative'];assert p.is_file() and H(p)==r['SHA'];folder=root
   for piece in r['relative'].split('/')[:-1]:
    folder+='/'+piece
    try:sf.stat(folder)
    except FileNotFoundError:sf.mkdir(folder)
   sf.put(str(p),root+'/'+r['relative'])
 finally:sf.close()
 v=code(c,py,CPU,root,timeout=150);put(key.upper()+'_ALL_TARGET_SOURCE_CPU_ACTUAL.json',v)
def main():
 assert not (R/'TWO_NEW_CONTINUATION_TRANSPORT_STARTED_ACTUAL.json').exists();proof=json.loads((R/'COMPLETE_TWO_CONTINUATION_ACCOUNTING_GRANT_NEGATIVES_CPU_ACTUAL.json').read_bytes());assert proof['passed_CPU_only'];put('TWO_NEW_CONTINUATION_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),actual_alive_only_exclusive_sequential210_72_249_transport_owner=True,only_new_native_scopes_no_old_GPU_or_precheck_replay=True));pw=getpass.getpass('Host72 exact continuation admission password (hidden): ');c=None;cfg=None;specs={x['key']:dict(x,python=t.PY if x['key']=='curb' else PY) for x in proof['frozen']}
 try:
  c=t.connect();v=code(c,t.PY,CREATE,S,A,'curb',specs['curb']['GPU_UUID'],specs['curb']['source_SHA'],'CURB140.pt');put('CURB_NEW_OWNED_ROOT_RESOURCE_SOURCE_COPY_ACTUAL.json',v);upload(c,t.PY,S,'curb')
 finally:t.close(c);c=None
 try:
  c=connect72(pw);v=code(c,PY,CREATE,T,OLD,'e2',specs['e2']['GPU_UUID'],specs['e2']['source_SHA'],'E2_final58.pt');put('E2_NEW_OWNED_ROOT_RESOURCE_SOURCE_COPY_ACTUAL.json',v);upload(c,PY,T,'e2')
 finally:
  if c:c.close();c=None
 try:
  c=t.connect();cfg=dict(role='owner',run_id='CURB140_E2_58_HEALTHY_CONTINUATION_'+str(time.time_ns()),token=secrets.token_hex(32),curb=specs['curb'],e2=specs['e2']);owner=launch(c,t.PY,S,'cohort_finite.py',cfg);actual=code(c,t.PY,"import sys,json,psutil,time;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(owner['detached_pid']));put('CURB_ORIGINAL_OWNER_NEW_NATIVE_DETACHED_ACTUAL.json',dict(owner=owner,actual=actual,native_CPU_before_learning=True))
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;nodecfg=dict(specs['e2'],role='node',run_id=cfg['run_id'],token=cfg['token']);node=launch(c,PY,T,'cohort_finite.py',nodecfg);actual=code(c,PY,"import sys,json,psutil,time;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(node['detached_pid']));put('TWO_NEW_EXPERT_CONTINUATION_ACTUAL_DETACHED_DISPATCH.json',dict(epoch=time.time(),source_owner=owner,target_node=node,target_actual=actual,old_H1_not_signaled_or_hotpatched=True,independent_checkpoints_and_optimizers=True,actual_native_CPU_then_original_canonical_safe_handoff_required=True,no_native_or_PPO_pass_inferred=True));print(json.dumps(dict(new_source_native_owner=owner,new_target_native_node=node,actual_two_GPU_native_admission_chain_dispatched=True,not_PPO_positive_yet=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO_CONTINUATION_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_actual_inspect_before_any_continuation=True,no_blind_redeploy_or_old_once_replay=True));raise
