"""CPU component evidence and fresh storage admission; no new target root or GPU."""
from route_second_io import *

def main():
    files={p.relative_to(D/'payload').as_posix():p.read_text(encoding='utf8') for p in (D/'payload').rglob('*') if p.is_file()}
    assert len(files)==3
    for name,s in files.items():compile(s,name,'exec')
    n,w=io.connect_both()
    try:
      v=run(n,r'''from pathlib import Path
import sys,json,torch,time,copy,ast,tempfile,hashlib,fcntl,shutil
OLD=Path(OLD_TOKEN);NEXT=Path(NEXT_TOKEN);sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_fixture_reviewed_once as actual
from wave50_route_state import KEY
from retention_command_state import same
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=Path(SOURCE_TOKEN);assert h(source)==SHA_TOKEN
info=actual.fullsave(source);assert info['finite_tensors']==107 and info['initial_source_and_expert_identity_exact'] and info['parent_route_boundary_source_CPU_exact']
ck=torch.load(source,map_location='cpu',weights_only=False);before_rng=torch.get_rng_state().clone();clone=copy.deepcopy(ck);storage_count=0
def tensors(x):
 if torch.is_tensor(x):yield x
 elif isinstance(x,dict):
  for y in x.values():yield from tensors(y)
 elif isinstance(x,(list,tuple)):
  for y in x:yield from tensors(y)
for group in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
 for a,b in zip(tensors(ck[group]),tensors(clone[group])):assert a.data_ptr()!=b.data_ptr() and torch.equal(a,b);storage_count+=1
rejected=[]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'full_CPU_fixture.pt';torch.save(clone,p);assert actual.fullsave(p)['finite_tensors']==107
 for field in ('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_boundary_source_sha256','bound_episode','spawn_xy','inward_limit_m','initial_source','expert'):
  bad=copy.deepcopy(ck)
  if field=='initial_source':bad['E1_WAVE50_initial_source_sha256']='0'*64
  elif field=='expert':bad['independent_terrain_expert']='wrong'
  elif field in ('bound_episode','spawn_xy','inward_limit_m'):bad[KEY][field]+=1
  else:bad[KEY][field]='wrong' if field=='profile' else '0'*64
  torch.save(bad,p)
  try:actual.fullsave(p)
  except AssertionError:rejected.append(field)
  else:raise AssertionError('Wrong route state accepted '+field)
 p=Path(tmp)/'private_command.pt';state=ck['E1_retained_flat_command_state'];torch.save(state,p);assert same(state,torch.load(p,map_location='cpu',weights_only=False))
 assert same(clone,ck)
files=json.loads(FILES_TOKEN);context={'__name__':'route_second_component_observer','__file__':str(NEXT/'supervise_wave50_route_second_bounded_once.py')}
guard=type(sys)('wave50_route_second_source_guard');exec(compile(files['wave50_route_second_source_guard.py'],'<new-independent-guard-component>','exec'),vars(guard));sys.modules[guard.__name__]=guard
exec(compile(files['supervise_wave50_route_second_bounded_once.py'],'<new-controller-CPU-component-only>','exec'),context)
assert context['INIT_SHA']==SHA_TOKEN and context['ORIGINAL35_SHA']==ck['E1_WAVE50_initial_source_sha256']
constants=str(context['prior'].train.__code__.co_consts)
assert context['ENTRY'] in constants and 'terrain_state_restored_exact' in constants and 'predecessor_route_state_restored_exact' in constants
assert context['ENTRY'] in str(context['prior'].guardian.__code__.co_consts)
train_source=ast.unparse(ast.parse(files['supervise_wave50_route_second_bounded_once.py']));assert '1800' in train_source and '--guardian' in train_source
worker=files['isaac/mod4/train_wave50_route_same_scope_resume_ppo.py']
assert "manifest['same50_entry_direction_route_fullstate_continuation']=True" in worker and "manifest['new_route_lifecycle_axis']=False" in worker and "manifest['new_episode_direction_axis']=False" in worker and "manifest['explicit_G3_to_WAVE50_geometry_transition']=False" in worker
assert "_write_dynamic(torch.arange(env.num_envs,device=env.device))" in worker
for node in ast.walk(ast.parse(worker)):
 if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(node):
  for a in node.iter.elts:
   if isinstance(a,ast.Constant) and isinstance(a.value,str):assert (OLD/'isaac/mod4'/a.value).is_file(),a.value
assert torch.equal(torch.get_rng_state(),before_rng) and not torch.cuda.is_initialized()
freeze=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==443
for name,sha in freeze.items():assert h(OLD/name)==sha
st=j(OLD/'reports/E1_STATE.json');row=j(OLD/'reports/e1_WAVE50_route_lifecycle_observation_PASSED.json');assert st['phase']=='E1_WAVE50_route_lifecycle_saved_review_ready' and st['child'] is None and row['checkpoint']['sha256']==SHA_TOKEN
locs=(st['owner'],j(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=row['own_PID_bound_receipt']['pid'],start_ticks=93571728))
for loc in locs:
 a=actual.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
B=actual.prior.s.q.ctl.CANONICAL;raw=B.read_bytes();b=json.loads(raw);total=36000;ids=set()
for r in b['budget_extensions']:
 assert r['extension_id'] not in ids and r['state']=='applied' and r['authorization_basis']=='explicit_user_request';ids.add(r['extension_id']);total+=r['additional_training_seconds']
assert total==b['authorized_training_seconds']==1188000 and len(ids)==7 and b['active_segment'] is None and not j(actual.prior.s.q.ctl.STATE_PATH).get('active_training')
segments=[s for s in b['completed_segments'] if s['pid']==row['own_PID_bound_receipt']['pid']];assert len(segments)==1 and segments==row['unique_completed_segment']
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',actual.prior.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_fcntl_free=True))
reference=OLD.parent/'MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012';refwhole=sum(p.stat().st_size for p in reference.rglob('*') if p.is_file());rf=j(reference/'reports/SOURCE_FREEZE.json')['sha256'];refsource=sum((reference/k).stat().st_size for k in rf)
currsource=sum((OLD/k).stat().st_size for k in freeze)+sum(len(s.encode()) for s in files.values());margin=2*660000*80
required=2*refwhole+2*1024**3+2*max(0,currsource-refsource)+margin
free=shutil.disk_usage(OLD).free;mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024
assert not NEXT.exists() and B.read_bytes()==raw and h(source)==SHA_TOKEN
out=dict(epoch=time.time(),passed=True,CPU_component_only_no_target_root=True,selected_source=info,actual_source_count443_preserved=True,prepared_old443_plus3_source_count446=True,full107_CPU_private_command_diskfixture_exact=True,independent_actor_critic_optimizer_storage_tensor_count=storage_count,strict_rejected_state_source_expert_fields=rejected,prepared_same_scope_Popen_worker_guardian_and_manifest_verified=True,no_CPU_RNG_draw_or_CUDA_initialization=True,actual_old_parent_guardian_child_exit=True,two_locks_actual_fcntl_free=locks,actual_unique_old_segment=segments,canonical_SHA=hashlib.sha256(raw).hexdigest(),budget1188000_sevenextensions_registered_once=True,
 resources=dict(epoch=time.time(),actual_durable_free_bytes=free,required_second1800_bytes=required,shortfall_bytes=max(0,required-free),actual_completed1800_reference_path=str(reference),actual_completed1800_wholeoutput_bytes=refwhole,source_size_delta=max(0,currsource-refsource),route_state_file_margin_bytes=margin,RAM_available_bytes=mem,storage_admitted=free>required and mem>8*1024**3,no_storage_guard_relaxation=True,no_evidence_environment_cache_deletion_or_tmpfs=True),
 new_target_CPU_GPU_controller_dispatch_not_executed=True,new_root_not_created=True,no_preclaim_candidate_number=True,no_GPU_PPO_or_budget_write=True)
print(json.dumps(out))
'''.replace('OLD_TOKEN',repr(OLD)).replace('NEXT_TOKEN',repr(ROOT)).replace('SOURCE_TOKEN',repr(SOURCE)).replace('SHA_TOKEN',repr(INIT_SHA)).replace('FILES_TOKEN',repr(json.dumps(files))))
      save('ROUTE_SECOND1800_COMPONENT_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
      guard=dict(epoch=time.time(),passed=v['resources']['storage_admitted'],resources=v['resources'],CPU_component_passed=True,target_CPU_GPU_dispatch_not_executed=True,new_root_not_created=True,reason='durable_storage_insufficient_for_complete_bounded_window' if not v['resources']['storage_admitted'] else None,no_GPU_or_budget_cost=True,no_deletion_or_tmpfs_or_guard_relaxation=True)
      save('SECOND1800_DURABLE_STORAGE_ADMISSION_ACTUAL.json',guard)
      print(json.dumps(dict(CPU_component_passed=True,target_CPU_pending=True,storage=guard)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE_SECOND_COMPONENT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_observer_only_no_GPU_target_root_or_budget_write=True));raise
