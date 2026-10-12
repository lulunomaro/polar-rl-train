from route_second_io import *
import shlex

def main():
    save('SECOND_ROUTE_STAGE_STARTED.json',dict(epoch=time.time(),human_old_obsolete_checkpoint_cleanup_completed=True,no_oldonce_replay=True))
    files={p.relative_to(D/'payload').as_posix():p.read_bytes() for p in (D/'payload').rglob('*') if p.is_file()};assert len(files)==3
    for name,raw in files.items():compile(raw,name,'exec')
    decision=json.loads((R/'COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json').read_bytes());assert decision['all_four_actual_complete_errorfree_fullraw_reviewed']
    n,w=io.connect_both()
    try:
      first=run(n,r'''from pathlib import Path
import json,time,sys,torch,hashlib,shutil,fcntl
OLD=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_fixture_reviewed_once as previous
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
st=j(OLD/'reports/E1_STATE.json');row=j(OLD/'reports/e1_WAVE50_route_lifecycle_observation_PASSED.json');assert st['phase']=='E1_WAVE50_route_lifecycle_saved_review_ready' and st['child'] is None and row['checkpoint']['sha256']==SHA_TOKEN
for loc in (st['owner'],j(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=row['own_PID_bound_receipt']['pid'],start_ticks=93571728)):
 a=previous.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
assert not previous.prior.trainers();B=previous.prior.s.q.ctl.CANONICAL;raw=B.read_bytes();b=j(B);assert b['active_segment'] is None and not j(previous.prior.s.q.ctl.STATE_PATH).get('active_training') and b['remaining_training_seconds']>1920
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',previous.prior.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_fcntl_free=True))
segments=[s for s in b['completed_segments'] if s['pid']==row['own_PID_bound_receipt']['pid']];assert len(segments)==1 and segments==row['unique_completed_segment']
source=Path(SOURCE_TOKEN);info=previous.fullsave(source);assert info['sha256']==h(source)==SHA_TOKEN and info['finite_tensors']==107
freeze=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==443
for k,v in freeze.items():assert h(OLD/k)==v
reference=OLD.parent/'MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012';refwhole=sum(p.stat().st_size for p in reference.rglob('*') if p.is_file());rf=j(reference/'reports/SOURCE_FREEZE.json')['sha256'];refsource=sum((reference/k).stat().st_size for k in rf);current=sum((OLD/k).stat().st_size for k in freeze)+NEWBYTES_TOKEN
required=2*refwhole+2*1024**3+2*max(0,current-refsource)+2*660000*80;free=shutil.disk_usage(OLD).free;mem=int(next(s for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')).split()[1])*1024
assert free>required and mem>8*1024**3 and not D.exists(),dict(actual_free_bytes=free,required=required)
reuse=[]
for name in ('WAVE50_SDK10_PASSED.json','WAVE50_NATIVE20K_PASSED.json','WAVE50_SDK10_ROUTE_GPU_SCOPE_PASSED.json','WAVE50_NATIVE20K_ROUTE_GPU_SCOPE_PASSED.json','WAVE50_NATIVE_SCOPE_PASSED.json','wave50_discard128_PASSED.json','wave50_discard20k_PASSED.json','WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'):
 p=OLD/'reports'/name;a=j(p);reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
 if 'checkpoint' in a:
  p=Path(a['checkpoint']['path']);assert h(p)==a['checkpoint']['sha256'];reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),discarded_preflight=True,large_index_only=True))
 if 'path' in a and 'sha256' in a:
  p=Path(a['path']);assert h(p)==a['sha256'];reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),large_index_only=True))
reuse+=j(OLD/'reports/REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices']
D.mkdir();(D/'reports').mkdir()
for k,v in freeze.items():p=D/k;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/k,p);assert h(p)==v
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json','COMPLETE149_DIRECTION_AXIS_DECISION.json','COMPLETE151_ROUTE_AXIS_DECISION.json'):
 shutil.copy2(OLD/'reports'/name,D/'reports'/name)
assert B.read_bytes()==raw and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,oldfreeze=freeze,selected=info,old_own_save= row,actual_old_parent_guardian_child_exit=True,two_fcntl_free=locks,old_unique_segment=segments,canonical_SHA=h(B),no_budget_write=True,resources=dict(actual_free_bytes=free,required_bytes=required,actual_completed1800_refwhole=refwhole,positive_source_delta=max(0,current-refsource),RAM_available_bytes=mem,storage_admitted=True,no_guard_relaxation=True),reused=dict(passed=True,actual_original_file_indices=reuse,no_SDK_native_small_big_fresh_clock_replay=True,same50_entry_direction_route=True))))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('SOURCE_TOKEN',repr(SOURCE)).replace('SHA_TOKEN',repr(INIT_SHA)).replace('NEWBYTES_TOKEN',str(sum(len(x) for x in files.values()))))
      save('OLD443_BOUNDARY_NEW_STORAGE_ACTUAL.json',first);freeze=dict(first['oldfreeze'])
      with n.open_sftp() as f:
        for name,raw in files.items():assert name not in freeze;io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw)
        values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,old443_allbytes_exact=True,new_files=list(files),same_scope_continuation_only=True),'MATCHED_SOURCE_SELECTED.json':first['selected'],'COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json':decision,'REUSED_ACTUAL_CONTRACTS.json':first['reused']}
        for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
      for name,value in values.items():
        if name!='COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json':save(name,value)
      cpu=run(n,r'''from pathlib import Path
import json,time,sys,torch,ast,copy,tempfile,hashlib
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_second_bounded_once as own
from wave50_route_state import KEY
from retention_command_state import same
own.boundary();source=own.source();info=own.fullsave(source);ck=torch.load(source,map_location='cpu',weights_only=False);assert info['sha256']==SHA_TOKEN and info['finite_tensors']==107 and ck['E1_WAVE50_initial_source_sha256']==own.ORIGINAL35_SHA
rejects=[]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'same_route_CPU_fixture.pt';torch.save(ck,p);assert own.fullsave(p)['finite_tensors']==107
 for field in ('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_boundary_source_sha256','bound_episode','spawn_xy','inward_limit_m'):
  bad=copy.deepcopy(ck)
  if field in ('bound_episode','spawn_xy','inward_limit_m'):bad[KEY][field]+=1
  else:bad[KEY][field]='wrong' if field=='profile' else '0'*64
  torch.save(bad,p)
  try:own.fullsave(p)
  except AssertionError:rejects.append(field)
  else:raise AssertionError('wrong route accepted '+field)
 p=Path(tmp)/'command.pt';state=ck['E1_retained_flat_command_state'];torch.save(state,p);assert same(state,torch.load(p,map_location='cpu',weights_only=False))
assert own.D==own.prior.D==D and own.CODE==own.prior.CODE==D/'isaac/mod4' and own.s.D==D and own.s.R==D/'reports'
constants=str(own.prior.train.__code__.co_consts);assert own.ENTRY in constants and '--seed' in constants and '20260928' in constants
assert own.ENTRY in str(own.prior.guardian.__code__.co_consts)
assert not any(k.endswith('INITIAL_ADMISSION') for k in own.runtime()) and own.runtime()['RM_KEEP_STD']=='1'
worker=(own.CODE/own.ENTRY).read_text();assert "manifest['same50_entry_direction_route_fullstate_continuation']=True" in worker and "manifest['new_route_lifecycle_axis']=False" in worker and "manifest['new_episode_direction_axis']=False" in worker and "manifest['explicit_G3_to_WAVE50_geometry_transition']=False" in worker
assert '_write_dynamic(torch.arange(env.num_envs,device=env.device))' in worker
for node in ast.walk(ast.parse(worker)):
 if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(node):
  for x in node.iter.elts:
   if isinstance(x,ast.Constant) and isinstance(x.value,str):assert (own.CODE/x.value).is_file(),x.value
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=446,full_source_checkpoint=info,actual_source_CPU107_full_D0D7_named_private_route_schema_verified=True,strict_rejected_route_fields=rejects,private_command_CPU_disk_fixture_exact=True,import_main_Popen_guardian_worker_root_exact=True,truthful_same_scope_manifest_only_worker_change=True,explicit_seed20260928=True,no_CUDA_initialized=True,actual_GPU_startup_CPUCUDA_restore_still_required=True,old443_allbytes_exact=True)
(D/'reports/WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.verify();print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('SHA_TOKEN',repr(INIT_SHA)))
      save('ROUTE_SECOND_TARGET_CPU_PASSED.json',cpu)
      listings=[]
      with n.open_sftp() as f,w.open_sftp() as g:
        for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
      number=153
      while any(any('episode-d3-'+str(number)+'-' in x for x in names) for host,path,names in listings):number+=1
      unused=dict(epoch=time.time(),number=number,actual_both_host_queue_results_jobs_unused=[dict(host=host,path=path,matches=[]) for host,path,names in listings])
      save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)
      with n.open_sftp() as f:io.put(f,ROOT+'/reports/CANDIDATE_JOB_UNUSED_ACTUAL.json',json.dumps(unused,indent=2).encode())
      dispatch=run(n,r'''from pathlib import Path
import sys,json,time,subprocess,os
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')]
import supervise_wave50_route_second_bounded_once as own
own.verify();own.boundary();assert not (D/'reports/PARENT_DISPATCH_ACTUAL_RECEIPT.json').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
with (D/'controller.log').open('x') as f:p=subprocess.Popen([own.s.q.base.PY,str(D/'supervise_wave50_route_second_bounded_once.py')],cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.3);loc=own.identity(p.pid);assert loc and str(D/'supervise_wave50_route_second_bounded_once.py') in loc['argv']
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=446,actual_parent=loc,selected_source=own.source().as_posix(),source_SHA=own.INIT_SHA,chosen_seconds=1800,old_preflight_clock_DR_exact_reuse_no_replay=True,new_budget_seconds=0)
(D/'reports/PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
      save('SECOND_ROUTE_DISPATCH_ACTUAL_RECEIPT.json',dispatch);print(json.dumps(dispatch))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('SECOND_ROUTE_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_actual_root_reports_PID_before_continuation_no_oldonce_replay=True));raise
