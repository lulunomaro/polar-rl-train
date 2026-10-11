from wave50_io import *
import ast
def main():
 assert not (R/'GPU_STAGE_STARTED.json').exists();save('GPU_STAGE_STARTED.json',dict(epoch=time.time(),new50_CPU_stage=True,no_old_once_replay=True))
 P=D/'payload';files={q.relative_to(P).as_posix():q.read_bytes() for q in P.rglob('*') if q.is_file()};assert len(files)==15
 decision=json.loads((PRIOR/'reports/WAVE50_145_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['actual_need_for_new_isolated50mm_learning']
 terrain=json.loads((PRIOR/'reports/WAVE50_WORLDMESH_FROZEN_PUBLISHED.json').read_bytes())['jobs'][0]
 cases=json.loads((PRIOR/'reports/WAVE143_COLLECTED_1791735506707673400.json').read_bytes())['cases']
 jobs=[terrain]+[x['manifest'] for name,x in cases.items() if '-retention-' in name];assert len(jobs)==4
 n,w=io.connect_both()
 try:
  listings=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
  number=146
  while any(any('episode-d3-'+str(number)+'-' in x for x in names) for host,path,names in listings):number+=1
  unused=dict(epoch=time.time(),number=number,actual_both_hosts_queue_results_jobs_unused=[dict(host=host,path=path,matches=[x for x in names if 'episode-d3-'+str(number)+'-' in x]) for host,path,names in listings])
  save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)
  boundary=run(n,r'''from pathlib import Path
import json,hashlib,sys,time,torch,shutil,fcntl
old=Path(OLD_TOKEN);cpu=Path(CPU_TOKEN);D=Path(ROOT_TOKEN);B=Path(B_TOKEN);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path[:0]=[str(old),str(old/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave35_second_bounded_once as previous
previous.prior.verify_original_records(previous.m.s.q,old)
st=j(old/'reports/E1_STATE.json');assert st['phase']=='E1_WAVE35_second_bounded_saved_review_ready' and st['child'] is None
p=j(old/'reports/e1_WAVE35_second_bounded_observation_PASSED.json');assert p['checkpoint']['sha256']==SHA_TOKEN and len(p['unique_completed_segment'])==1
for loc in (st['owner'],j(old/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=88740346)):
 actual=previous.identity(loc['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
source=Path(SOURCE_TOKEN);assert h(source)==SHA_TOKEN and previous.fullsave(source)['finite_tensors']==102
assert not previous.m.trainers();b=j(B);assert b['active_segment'] is None and not j(previous.m.s.q.ctl.STATE_PATH).get('active_training')
assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>4000
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=True))
freeze=j(cpu/'reports/SOURCE_FREEZE.json')['sha256'];original=j(old/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==377 and all(freeze[k]==v for k,v in original.items())
for name,sha in freeze.items():assert h(cpu/name)==sha
proof=j(cpu/'reports/WAVE50_TARGET_CPU_PASSED.json');assert proof['passed'] and proof['source_checkpoint']['sha256']==SHA_TOKEN
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024;disk=shutil.disk_usage(cpu);assert mem>8*1024**3 and disk.free>8*1024**3 and not D.exists()
before=B.read_bytes();D.mkdir();(D/'reports').mkdir()
for name,sha in freeze.items():q=D/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(cpu/name,q);assert h(q)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','REUSED_ACTUAL_CONTRACTS.json'):shutil.copy2(old/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),oldfreeze=freeze,selected=previous.fullsave(source),own_source_SHA=SHA_TOKEN,complete129_ancestor_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',actual_old_fullsave_PASSED_and_unique_closed=True,own_old_run=p['run'],old_actual_exits=True,two_fcntl_free=locks,canonical_SHA=h(B),remaining_seconds=b['remaining_training_seconds'],resources=dict(RAM_bytes=mem,disk_free_bytes=disk.free),no_GPU_or_budget_write=True)))
'''.replace('OLD_TOKEN',repr(OLD)).replace('CPU_TOKEN',repr(CPU_ROOT)).replace('ROOT_TOKEN',repr(ROOT)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(SOURCE_SHA)).replace('SOURCE_TOKEN',repr(SOURCE)))
  save('OWN369_ACTUAL_SOURCE_BOUNDARY.json',boundary)
  freeze=dict(boundary['oldfreeze']);new=[]
  with n.open_sftp() as f:
   for name,raw in files.items():
    if name in freeze:assert freeze[name]==H(raw);continue
    io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw);new.append(name)
   assert len(new)==7 and len(freeze)==384
   values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,old377_allbytes_exact=True,new_missing50_GPU_scope_files=new),'SOURCE_SELECTED.json':boundary['selected'],'OWN369_ACTUAL_SOURCE_BOUNDARY.json':boundary,'FROZEN145_COMPLETE_SCOPE_DECISION.json':decision,'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused,'WAVE50_FOUR_CASE_TEMPLATES.json':dict(jobs=jobs),'WAVE50_TARGET_CPU_PASSED.json':dict(passed=True,source_count=384,CPU_record_in_progress=True)}
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
  save('SOURCE_FREEZE.json',values['SOURCE_FREEZE.json'])
  result=run(n,r'''from pathlib import Path
import sys,json,time,torch,ast,contextlib,io,inspect
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_independent_scope_once as own
own.verify();own.wait_existing();p=own.source();assert own.D==D and own.R==D/'reports' and own.CODE==D/'isaac/mod4' and own.s.D==D and own.s.R==D/'reports'
import test_g4_fullstate_cpu as test
capture=io.StringIO()
with contextlib.redirect_stdout(capture):test.main(str(p))
v=json.loads(capture.getvalue());assert v['passed'] and v['source']['finite_tensors']==102 and v['no_CUDA_initialized']
missing=[]
for name in ('train_wave50_full_resume_ppo.py','train_wave50_fresh_preflight_ppo.py'):
 text=(own.CODE/name).read_text();tree=ast.parse(text)
 for node in ast.walk(tree):
  if isinstance(node,ast.For) and isinstance(node.target,ast.Name) and node.target.id=='name' and isinstance(node.iter,ast.Tuple):
   for a in node.iter.elts:
    if isinstance(a,ast.Constant) and isinstance(a.value,str) and a.value.endswith(('.py','.json')) and not (own.CODE/a.value).is_file():missing.append(a.value)
 assert 'slope5' not in text
 assert "_write_dynamic(torch.arange(env.num_envs,device=env.device))" in text
assert not missing,missing
fresh=(own.CODE/'probe_wave50_fresh_process_full_resume.py').read_text();assert 'no_optional_logger_save_requested=True' in fresh
assert "'--seed','20260928'" in inspect.getsource(own.fresh_resume)
runtime=own.runtime();assert runtime['RM_WAVE50_INITIAL_ADMISSION']=='verified_G3_to_independent_WAVE50' and runtime['RM_KEEP_STD']=='1'
assert not torch.cuda.is_initialized();result=dict(epoch=time.time(),passed=True,root=str(D),source_count=len(own.read(own.R/'SOURCE_FREEZE.json')['sha256']),source=own.s.q.base.checkpoint(p),proof=v,source_snapshot_lists_all_exist=True,actual_import_main_Popen_worker_roots_match=True,source377_immutable_preserved=True,explicit_seed_fresh_zero_steps_guards_preserved=True,actual_CUDA_SDK_native_PPO_fresh_formal_pending=True,no_GPU_or_budget_write=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('WAVE50_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(root=ROOT,source_count=384,targetCPU_passed=True,candidate_number=number,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('GPU_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True,only_unexecuted_step_can_continue=True));raise
