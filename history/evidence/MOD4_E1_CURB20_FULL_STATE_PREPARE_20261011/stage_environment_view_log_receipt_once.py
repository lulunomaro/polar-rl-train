"""Independent384 after actual pre-learning380 rejection; CPU property contract first."""
from stage_reviewed_fullstate_once import D,R,E,B,PY,connect_both,cleanup,linux_json,H,save,put
import json,time,shlex,traceback
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FULL_STATE_REVIEWED_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENVIRONMENT_VIEW_20261011'
def main():
 save('ENVIRONMENT_VIEW_LOG_RECEIPT_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='CURB-ENVVIEW-384-LOG-RECEIPT-STAGE-CONTINUATION-01',no_GPU_or_ledger_transaction=True))
 n,w=connect_both()
 try:
  copy=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,shutil,fcntl
old=Path(OLD);new=Path(NEW);B=Path(BUDGET);budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes());assert not new.exists()
att=j(old/'reports/E1_REVIEWED_CONTROLLER_ATTENTION.json');s=j(old/'reports/E1_STATE.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
for v in [s['owner'],j(old/'reports/E1_GUARDIAN_STARTED.json'),s['child']]:
 p=Path('/proc')/str(v['pid'])
 if p.exists():a=(p/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=v['start_ticks']
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
seg=[x for x in l['completed_segments'] if x['pid']==s['child']['pid']];assert len(seg)==1
logs=old/'discard_logs';error=list(old.glob('curb_discard20k_*.log'));assert len(error)==1 and "has no attribute 'num_envs'" in error[0].read_text();assert not list(logs.glob('curb_discard20k_*.error.txt'))
runs=[p for p in logs.glob('*curb_discard20k*') if p.is_dir()];assert len(runs)==1 and not (runs[0]/'run_manifest.json').exists() and not (runs[0]/'latest_complete.json').exists()
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
f=j(old/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==380;new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB132_COMPLETE_ACTUAL_REVIEW.json','CURB_REUSED_NATIVE.json','CURB_FOUR_CASE_TEMPLATES.json','CURB_TARGET_FULLSTATE_CPU_PASSED.json'):
 shutil.copy2(old/'reports'/name,new/'reports'/name)
small=j(old/'reports/curb_discard128_PASSED.json');assert small['discarded_preflight'] and small['actual_updates']==2 and len(small['unique_completed_segment'])==1
(new/'reports/REUSED_SMALL128.json').write_text(json.dumps(small,indent=2))
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=time.time(),source_freeze=f,old380_all_bytes_preserved=True,actual_old380_exit_two_OS_locks_free=True,failed_big_before_PPO_with_no_future_save=True,unique_failed_load_exit_segment=seg,failed_error=dict(path=str(error[0]),bytes=error[0].stat().st_size,sha256=hashlib.sha256(error[0].read_bytes()).hexdigest(),text=error[0].read_text()),canonical_SHA=hashlib.sha256(budget).hexdigest(),small_actual_reused=small)))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')').replace('BUDGET',repr(B)))
  save('ENVIRONMENT_VIEW_380_COPIED.json',copy)
  with n.open_sftp() as f:
   freeze=copy['source_freeze'];hashes=dict(freeze['sha256'])
   for p in sorted((D/'environment_view_payload').rglob('*')):
    if not p.is_file():continue
    name=p.relative_to(D/'environment_view_payload').as_posix();raw=p.read_bytes();compile(raw,name,'exec');assert name not in hashes
    put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   assert len(hashes)==384;freeze=dict(freeze,candidate_root=NEW,sha256=hashes,old380_all_source_bytes_preserved=True,new_manager_source_identity_view_property_repair=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('ENVIRONMENT_VIEW_SOURCE_FREEZE.json',freeze)
   manager_path='/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/managers/manager_base.py'
   manager=f.open(manager_path).read();p=D/'inherited_source/installed_manager_base.py';assert not p.exists();p.write_bytes(manager)
   save('ENVIRONMENT_VIEW_MANAGER_API_SOURCE.json',dict(path=manager_path,bytes=len(manager),sha256=H(manager),local_exact_source=str(p),CPU_AST_fixture_not_an_app_import=True))
  code=r'''from pathlib import Path
import ast,sys,json,time,copy,torch,hashlib
from types import SimpleNamespace
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_environment_view_once as own
from retention_command_state import FIELDS,validate,same
from curb20_command_migration_environment_view import restore_source_then_bind_CURB
source=own.read(D/'reports/SOURCE_SELECTED.json');ck=torch.load(source['path'],map_location='cpu',weights_only=False)
assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']==own.prior.SOURCE_SHA
info=own.prior.inherited.fullsave(Path(source['path']));assert info['finite_tensors']==102
s=copy.deepcopy(ck['E1_retained_flat_command_state']);s.update(rng_device_type='cpu',rng=torch.Generator().manual_seed(93811).get_state())
manager=Path('/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/managers/manager_base.py')
tree=ast.parse(manager.read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ManagerTermBase')
props=[x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name in ('num_envs','device')];assert len(props)==2
node=ast.ClassDef(name='ActualManagerProperties',bases=[],keywords=[],body=props,decorator_list=[]);ns={'torch':torch}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<actual-installed-manager-properties>','exec'),ns)
class Fixture(ns['ActualManagerProperties']):
 @property
 def _retention_rng(self):return self._retention_rng_owner['generator']
 @_retention_rng.setter
 def _retention_rng(self,value):self._retention_rng_owner={'generator':value}
tree=ast.parse((D/'isaac/mod4/retention_flat_runtime.py').read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='RetainedFlatCommand')
ns=dict(torch=torch,PROFILE=s['profile'],FIELDS=FIELDS,validate=validate)
for fn in [x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name in ('load_state_retention','state_dict_retention')]:
 exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<original-strict-loader>','exec'),ns);setattr(Fixture,fn.name,ns[fn.name])
f=Fixture();f._env=SimpleNamespace(num_envs=20000,device='cpu',scene=SimpleNamespace(terrain=SimpleNamespace(retention_assignment_sha='f'*64)));original_env=f._env;f._retention_rng=torch.Generator().manual_seed(2)
for k in FIELDS:setattr(f,k,torch.zeros_like(s[k]))
f.world_direction=torch.zeros(20000);f.is_moving_spin=torch.zeros(20000,dtype=torch.bool);f.vel_command_b=torch.zeros((20000,3))
try:f.load_state_retention(s);raise RuntimeError('Original loader must reject source on new assignment')
except AssertionError:pass
proof=restore_source_then_bind_CURB(f,s,s['assignment_sha256']);assert f._env is original_env and same(f.state_dict_retention(),dict(s,assignment_sha256='f'*64))
assert not torch.cuda.is_initialized()
own.verify();own.wait_existing()
v=dict(epoch=time.time(),passed=True,CPU_only=True,no_CUDA_initialized=True,source_fullsave=info,source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),actual_installed_ManagerTermBase_properties_used=['num_envs','device'],manager_source_SHA=hashlib.sha256(manager.read_bytes()).hexdigest(),strict_original_loader_and_private_owner_preserved=True,source_identity_view_CPU_property_contract=proof,original_live_environment_object_not_changed=True,old380_prelearning_error_retained=True,small_native_SDK_exact_reused=True,actual_CUDA_fullstate_and_big_PPO_pending=True)
(D/'reports/CURB_ENVIRONMENT_VIEW_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(NEW))
  compile(code,'<actual-manager-sourceview-CPU>','exec');_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('ENVIRONMENT_VIEW_CPU_REJECTED.json',dict(epoch=time.time(),stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),returncode=rc,no_GPU_launch=True));raise RuntimeError('New CPU property contract rejected')
  v=json.loads(raw);save('ENVIRONMENT_VIEW_TARGET_CPU_PASSED.json',v);print(json.dumps(dict(root=NEW,source_count=384,CPU_passed=True,SDK_native_small_reused=True,big_CUDA_formal_pending=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ENVIRONMENT_VIEW_LOG_RECEIPT_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),old_error_and_new_scope_retained=True,no_replay_stage=True));raise
