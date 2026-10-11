"""New immutable root plus new fullstate CPU admission; no GPU launch here."""
from direction_io import *
def main():
 assert not (R/'STAGE_STARTED.json').exists();save('STAGE_STARTED.json',dict(epoch=time.time(),new_direction_fullstate_scope=True,no_old_once_replay=True))
 files={p.relative_to(D/'payload').as_posix():p.read_bytes() for p in (D/'payload').rglob('*') if p.is_file()};assert len(files)==12
 for name,raw in files.items():compile(raw,name,'exec')
 decision=json.loads((PRIOR/'reports/CANDIDATE149_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['all_four_actual_complete_errorfree_fullraw_reviewed'] and decision['candidate_forward_complete']==1
 n,w=io.connect_both()
 try:
  listings=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
  number=150
  while any(any('episode-d3-'+str(number)+'-' in name for name in names) for host,path,names in listings):number+=1
  unused=dict(epoch=time.time(),number=number,actual_both_hosts_queue_results_jobs_unused=[dict(host=h,path=p,matches=[]) for h,p,names in listings]);save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)
  boundary=run(n,r'''from pathlib import Path
import sys,json,torch,hashlib,time,shutil,fcntl
OLD=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);B=Path(B_TOKEN);sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once_v2 as previous
from wave50_entry_source_guard import verify_original_records
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();verify_original_records(previous.s.q,OLD)
st=j(OLD/'reports/E1_STATE.json');passed=j(OLD/'reports/e1_WAVE50_entry_second_bounded_observation_PASSED.json')
assert st['phase']=='E1_WAVE50_entry_second_bounded_saved_review_ready' and st['child'] is None and passed['checkpoint']['sha256']=='9bfe7655b8a641660548c2a62d2ac3151e25bdf1f0e943d529099c017a2e986e' and len(passed['unique_completed_segment'])==1
for loc in (st['owner'],j(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=91013803)):
 a=previous.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
assert not previous.trainers();b=j(B);assert b['active_segment'] is None and not j(previous.s.q.ctl.STATE_PATH).get('active_training') and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>1920
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',previous.s.q.P/'autonomy_controller.lock'):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=True))
source=Path(SOURCE_TOKEN);info=previous.inherited.fullsave(source);assert h(source)==SHA_TOKEN and info['finite_tensors']==102
freeze=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==412
for name,sha in freeze.items():assert h(OLD/name)==sha
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024;disk=shutil.disk_usage(OLD)
priorbytes=sum(p.stat().st_size for p in OLD.rglob('*') if p.is_file());required=2*priorbytes+2*1024**3
assert mem>8*1024**3 and disk.free>required and not D.exists(),dict(free=disk.free,required=required,prior_actual_completed_wholeoutput=priorbytes)
reuse=j(OLD/'reports/REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices']
# Only unchanged geometry/clock/DR/hardware receipts are reused here.
# None of the predecessor directionless GPU receipts admit the new direction scope.
for row in reuse:assert h(Path(row['path']))==row['sha256']
before=B.read_bytes();D.mkdir();(D/'reports').mkdir()
for name,sha in freeze.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json'):shutil.copy2(OLD/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),source=info,oldfreeze=freeze,old_own_PASSED=passed,actual_old_parent_guardian_child_exit=True,two_fcntl_free=locks,canonical_SHA=h(B),remaining_seconds=b['remaining_training_seconds'],resources=dict(RAM_available_bytes=mem,disk_free_bytes=disk.free,prior_actual_completed_wholeoutput_bytes=priorbytes,required_bytes=required),reused=dict(actual_original_file_indices=reuse,only_geometry_clock_DR_hardware_admitted_for_new_scope=True,new_direction_GPU_contracts_all_required=True),no_GPU_or_budget_write=True)))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('B_TOKEN',repr(io.B)).replace('SOURCE_TOKEN',repr(SOURCE)).replace('SHA_TOKEN',repr(SOURCE_SHA)))
  save('OLD412_ACTUAL_BOUNDARY_AND_INITIAL35_SOURCE.json',boundary);freeze=dict(boundary['oldfreeze'])
  with n.open_sftp() as f:
   for name,raw in files.items():
    assert name not in freeze
    parent=ROOT+'/'+str(Path(name).parent).replace('\\','/')
    try:f.stat(parent)
    except FileNotFoundError:f.mkdir(parent)
    io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw)
   values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,all412_old_bytes_exact=True,new_files=list(files),direction_only_new_axis=True),'COMPLETE149_DIRECTION_AXIS_DECISION.json':decision,'REUSED_ACTUAL_CONTRACTS.json':boundary['reused'],'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused}
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode());save(name,value)
  result=run(n,r'''from pathlib import Path
import sys,json,time,torch,ast
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_once as own
from test_wave50_direction_target_cpu import verify
own.wait_existing();source=own.source();proof=verify(D,str(source));assert proof['passed'] and proof['no_CUDA_initialized']
assert own.D==D and own.CODE==D/'isaac/mod4' and own.s.D==D and own.s.R==D/'reports'
constants=str(own.train.__code__.co_consts);assert 'train_wave50_direction_resume_ppo.py' in constants and 'train_wave50_direction_fresh_preflight_ppo.py' in constants and '20260928' in constants
assert 'train_wave50_direction_resume_ppo.py' in str(own.guardian.__code__.co_consts)
for name in ('native_e1_wave50_direction_scope_probe.py','supervise_wave50_direction_once.py'):ast.parse((D/name).read_text())
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=len(own.read(own.R/'SOURCE_FREEZE.json')['sha256']),source_checkpoint=own.inherited.fullsave(source),proof=proof,import_main_Popen_guardian_roots_exact=True,SDK_native_fullstate_CUDA_PPO_fresh_formal_pending=True,no_GPU_or_canonical_write=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.verify();print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('DIRECTION_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(root=ROOT,source_count=len(freeze),target_CPU_passed=True,candidate_number=number,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),original_sources_retained=True,only_unexecuted_steps_may_continue=True));raise
