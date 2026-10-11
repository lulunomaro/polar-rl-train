from pathlib import Path
import sys,json,time,hashlib,shlex,traceback

D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=D/'payload'
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import repair_io as io
OLD=io.NEW
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_FULLSTATE_REVIEWED_20261011'
H=lambda b:hashlib.sha256(b).hexdigest()

def save(name,v):
 p=R/name;assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');return p

def run(n,code):
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=180)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  save('ENTRY_FULLSTATE_CPU_EXECUTION_REJECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_GPU_or_PPO_or_budget_transaction=True))
  raise RuntimeError('CPU/stage refused; preserve existing root and original error')
 return json.loads(raw)

def main():
 save('ENTRY_FULLSTATE_STAGE_STARTED.json',dict(epoch=time.time(),root=NEW,trial_id='CURB20-ENTRY-ORIGIN-BOUND-FULLSTATE-01',old398_immutable=True,native20k_reused_no_replay=True,old_SDK_CURB_scope_gap_not_relabelled=True,no_new_budget_seconds=0))
 save('LOCAL_READER_PATH_ERRORS_RETAINED.json',dict(epoch=time.time(),attempts=[dict(path='MOD4_E1_CURB20_ENTRY_REPAIR_20261011/inherited_source/reviewed_budget005_source_guard.py',error='Get-Content path not found',actual_path='MOD4_E1_CURB20_ENTRY_REPAIR_20261011/payload/reviewed_budget005_source_guard.py'),dict(path='MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/payload/isaac/mod4/curb20_entry_fresh_preflight_ppo.py',error='Get-Content path not found',actual_path='MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/payload/isaac/mod4/train_curb20_entry_fresh_preflight_ppo.py')],before_GPU_or_mutation=True))
 n,w=io.connect_both()
 try:
  save('ENTRY_FULLSTATE_ACTUAL_AUTHORITY_BOUNDARY.json',io.boundary(n))
  with w.open_sftp() as f:
   names=f.listdir('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')
   assert not any('-139-' in name for name in names)
   save('ENTRY_CANDIDATE139_WINDOWS_UNUSED.json',dict(epoch=time.time(),actual_jobs_directory='D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs',actual139_absent=True,no_replay=True))
  copied=run(n,r'''from pathlib import Path
import json,time,hashlib,shutil,fcntl
old=Path(OLDROOT);new=Path(NEWROOT);E=Path(CENTRAL);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
assert not new.exists();before=B.read_bytes();assert j(B)['active_segment'] is None
st=j(old/'reports/ENTRY_NATIVE_STATE.json');passed=j(old/'reports/ENTRY_NATIVE_SCOPE_PASSED.json');assert st['child'] is None and passed['passed']
exits=[]
for loc in [st['owner']]+[v['own_child_PID'] for v in passed['results'].values()]:
 p=Path('/proc')/str(loc['pid']);actual=None
 if p.exists():
  f=(p/'stat').read_text().split(') ',1)[1].split();actual=dict(state=f[0],start_ticks=int(f[19]));assert actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
 exits.append(dict(locator=loc,actual=actual))
assert not list((E/'eval_queue').glob('*-139-*')) and not list((E/'eval_results').glob('*-139-*')) and not list((E/'results').glob('*-139-*'))
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==398
new.mkdir();(new/'reports').mkdir()
for name,h in freeze['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(old/'reports/SOURCE_SELECTED.json',new/'reports/SOURCE_SELECTED.json')
shutil.copy2(Path(TEMPLATE_ROOT)/'reports/CURB_FOUR_CASE_TEMPLATES.json',new/'reports/CURB_FOUR_CASE_TEMPLATES.json')
assert B.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),source_freeze=freeze,actual398_parent_children_exited=exits,two_OS_locks_free=locks,candidate139_central_unused=True,canonical_SHA=hashlib.sha256(before).hexdigest(),old398_allbytes_exact=True,no_GPU_PPO_or_budget_action=True)))
'''.replace('OLDROOT',repr(OLD)).replace('NEWROOT',repr(NEW)).replace('CENTRAL',repr(io.E)).replace('BUDGET',repr(io.B)).replace('TEMPLATE_ROOT',repr(io.OLD)))
  save('ENTRY_FULLSTATE_398_SOURCE_COPIED.json',copied)
  hashes=dict(copied['source_freeze']['sha256'])
  with n.open_sftp() as f:
   for p in sorted(P.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts:continue
    raw=p.read_bytes();name=p.relative_to(P).as_posix();assert name not in hashes;compile(raw,str(p),'exec');io.put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   freeze=dict(candidate_root=NEW,sha256=hashes,old398_bytes_exact_preserved=True,new_entry_origin_bound_fullstate_scope=True,no_native20k_replay=True)
   io.put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('ENTRY_FULLSTATE_SOURCE_FREEZE.json',freeze)
   review=W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011/reports/ENTRY_NATIVE_COMPLETE_FAMILY_SCHEMA_ACTUAL_REVIEW.json'
   v=json.loads(review.read_bytes());assert v['native20k_scope_passed'] and not v['SDK10_CURB_entry_scope_admission']
   io.put(f,NEW+'/reports/ENTRY_NATIVE_ACTUAL_REVIEW.json',review.read_bytes())
  cpu=run(n,r'''from pathlib import Path
import json,time,sys,ast,types,hashlib,torch,numpy as np
D=Path(NEWROOT);old=Path(OLDROOT);C=D/'isaac/mod4';sys.path.insert(0,str(D));sys.path.insert(0,str(C));torch.set_num_threads(1)
def j(p):return json.loads(p.read_bytes())
passed=j(old/'reports/ENTRY_NATIVE_SCOPE_PASSED.json');raw=old/'ENTRY_NATIVE20K.json';assert hashlib.sha256(raw.read_bytes()).hexdigest()==passed['results']['ENTRY_NATIVE20K']['sha256']
reuse=dict(epoch=time.time(),passed=True,path=str(raw),bytes=raw.stat().st_size,sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),no_PPO=True,exact_existing_native20k_reused=True)
(D/'reports/ENTRY_REUSED_NATIVE20K.json').write_text(json.dumps(reuse,indent=2))
from curb20_entry_target_cpu import verify
proof=verify(D)
from curb20_entry_v2_math import entry_map
tree=ast.parse((C/'curb20_entry_v3_runtime.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='reset_entry_xy')
mod=types.ModuleType('e1_full_pose_reset');mod.A=C;previous=sys.modules.get(mod.__name__);sys.modules[mod.__name__]=mod
ns=dict(np=np,torch=torch,entry_map=entry_map)
try:
 exec(compile(ast.Module(body=[fn],type_ignores=[]),str(C/'curb20_entry_v3_runtime.py'),'exec'),ns)
 sdk=j(old/'ENTRY_SDK10.json');assign=j(old/'ENTRY_SDK10.json.assignment.json')['actual_assignments']
 initial=np.array(sdk['reset_root_before_physics'],dtype='<f4')[:,:3];env=types.SimpleNamespace(num_envs=10,device='cpu',scene=types.SimpleNamespace(env_origins=torch.tensor(initial),terrain=types.SimpleNamespace(retention_assignment=assign,retention_assignment_sha=sdk['SDK_CURB_actual_assignment_placement']['assignment_sha256'])))
 ids=torch.arange(10);first=ns['reset_entry_xy'](env,ids);assert env._curb_entry_map_receipt['changed_environments']==0
 updated=initial.copy();updated[:,:2]=np.array(sdk['SDK_CURB_actual_assignment_placement']['requested_starts'],dtype='<f4');env.scene.env_origins.copy_(torch.tensor(updated))
 actual=ns['reset_entry_xy'](env,ids);bank=np.load(C/'MOD4_RESET_COLLISION_BANK.npz');pick=int(np.argmin(abs(bank['root_height']-.25)))
 expected,receipt=entry_map(updated,assign,bank['points_root'][pick]);assert torch.equal(actual,torch.tensor(expected,dtype=torch.float32))
 assert env._curb_entry_map_receipt['changed_environments']==10 and torch.equal(env._curb_entry_origin_snapshot,env.scene.env_origins[:,:2])
 same=ns['reset_entry_xy'](env,torch.tensor([1,4,8]));assert torch.equal(same,actual[[1,4,8]])
 for i,a in enumerate(sdk['SDK_CURB_actual_assignment_placement']['chosen_actual_assignments']):
  b=np.array(a['bounds']);assert ((actual[i].numpy()>=b[0,:2])&(actual[i].numpy()<b[1,:2])).all()
 native=j(raw);origins=np.array(native['reset_root_before_physics'],dtype='<f4')[:,:3]
 env20=types.SimpleNamespace(num_envs=20000,device='cpu',scene=types.SimpleNamespace(env_origins=torch.tensor(origins),terrain=types.SimpleNamespace(retention_assignment=assign,retention_assignment_sha=env.scene.terrain.retention_assignment_sha)))
 after=ns['reset_entry_xy'](env20,torch.arange(20000));assert torch.equal(after,torch.tensor(origins[:,:2]))
 assert hashlib.sha256(after.numpy().tobytes()).hexdigest()==native['CURB_entry_map']['map_sha256']
 component=dict(passed=True,CPU_only=True,actual_old_SDK_origin_change_fixture_bound=True,initial_changed0_then_changed10=True,selected_subset_exact=True,unchanged_native20k_XY_map_byteexact=True,native20k_map_SHA=native['CURB_entry_map']['map_sha256'],runtime_SHA=hashlib.sha256((C/'curb20_entry_v3_runtime.py').read_bytes()).hexdigest(),no_plant_or_GPU_or_PPO_execution=True)
finally:
 if previous is None:del sys.modules[mod.__name__]
 else:sys.modules[mod.__name__]=previous
assert not torch.cuda.is_initialized()
proof.update(epoch=time.time(),cache_component=component,source_count=len(j(D/'reports/SOURCE_FREEZE.json')['sha256']),no_CUDA_initialized=True,physical_SDK_fullrestore_preflights_formal_pending=True)
(D/'reports/ENTRY_TARGET_FULLSTATE_CPU_PASSED.json').write_text(json.dumps(proof,indent=2))
import supervise_curb20_entry_fullstate_once as own
own.verify();own.wait_existing()
assert own.D==D and own.R==D/'reports' and own.CODE==C and own.inherited.D==D and own.inherited.R==D/'reports'
print(json.dumps(dict(passed=True,CPU=proof,native_reuse=reuse,correct_new_import_main_paths=True,no_GPU_PPO_dispatch=True)))
'''.replace('NEWROOT',repr(NEW)).replace('OLDROOT',repr(OLD)))
  save('ENTRY_TARGET_FULLSTATE_CPU_PASSED.json',cpu)
  print(json.dumps(dict(root=NEW,source_count=len(hashes),CPU_passed=True,cache_rebind_proved=True,no_GPU_launch=True,native20k_reused=True)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_FULLSTATE_STAGE_OR_CPU_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_replay=True));raise
