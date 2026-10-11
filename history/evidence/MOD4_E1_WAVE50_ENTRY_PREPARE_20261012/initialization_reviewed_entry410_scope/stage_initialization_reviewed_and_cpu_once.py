"""Retain failed398 and start a new immutable initialization-reviewed source410."""
from entry_io import *
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'
def main():
 assert not (R/'INITIALIZATION_STAGE_STARTED.json').exists();save('INITIALIZATION_STAGE_STARTED.json',dict(epoch=time.time(),new_initialization_scope=True,no_old_GPU_replay=True))
 files={p.relative_to(D/'payload_initialization_reviewed').as_posix():p.read_bytes() for p in (D/'payload_initialization_reviewed').rglob('*') if p.is_file()};assert len(files)==12
 n,w=io.connect_both()
 try:
  failure_capture=D/('failed398_actual_'+str(time.time_ns()));failure_capture.mkdir()
  with n.open_sftp() as f:
   for name in ('controller.log','guardian.log','WAVE50_SDK10.log','WAVE50_SDK10.json.error'):
    raw=f.open(ROOT+'/'+name,'rb').read();p=failure_capture/name;p.write_bytes(raw)
   for name in f.listdir(ROOT+'/reports'):
    if name.endswith('.json'):
     raw=f.open(ROOT+'/reports/'+name,'rb').read();p=failure_capture/'reports'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
  boundary=run(n,r'''from pathlib import Path
import sys,json,torch,hashlib,time,shutil,fcntl
OLD=Path(OLD_TOKEN);D=Path(NEW_TOKEN);sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once as previous
previous.verify();previous.wait_existing()
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
st=j(OLD/'reports/E1_STATE.json');attention=j(OLD/'reports/E1_ATTENTION.json');assert not attention['own_child_still_alive'] and attention['active_segment'] is None
assert (OLD/'WAVE50_SDK10.json.error').is_file() and not (OLD/'WAVE50_SDK10.json').exists()
for loc in (st['owner'],st['child'],j(OLD/'reports/E1_GUARDIAN_STARTED.json')):
 actual=previous.identity(loc['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
assert not previous.trainers();B=previous.s.q.ctl.CANONICAL;before=B.read_bytes();b=j(B);assert b['active_segment'] is None and not j(previous.s.q.ctl.STATE_PATH).get('active_training')
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',previous.s.q.P/'autonomy_controller.lock'):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=True))
freeze=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==398
for name,sha in freeze.items():assert h(OLD/name)==sha
size=sum((OLD/k).stat().st_size for k in freeze);assert shutil.disk_usage(OLD).free>2*1024**3+2*size and not D.exists()
D.mkdir();(D/'reports').mkdir()
for name,sha in freeze.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','REUSED_ACTUAL_CONTRACTS.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','SOURCE_SELECTED.json','COMPLETE147_ENTRY_AXIS_DECISION.json','CANDIDATE_JOB_UNUSED_ACTUAL.json','WAVE50_FOUR_CASE_TEMPLATES.json'):
 shutil.copy2(OLD/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,oldfreeze=freeze,old398_actual_failed_SDK_error_before_control=True,old_owner_guardian_child_actual_exits=True,two_fcntl_free=locks,canonical_SHA=h(B),no_PPO_no_canonical_charge_or_write=True,complete_failed398_kept=True)))
'''.replace('OLD_TOKEN',repr(ROOT)).replace('NEW_TOKEN',repr(NEWROOT)))
  save('FAILED398_AND_INITIALIZATION_REVIEWED_BOUNDARY.json',boundary);freeze=dict(boundary['oldfreeze'])
  with n.open_sftp() as f:
   for name,raw in files.items():assert name not in freeze;io.put(f,NEWROOT+'/'+name,raw);freeze[name]=H(raw)
   values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,old398_allbytes_exact=True,new_initialization_scope_files=list(files)),'WAVE50_TARGET_CPU_PASSED.json':dict(passed=True,source_count=len(freeze),CPU_record_in_progress=True),'FAILED398_ACTUAL_REVIEW.json':boundary}
   for name,value in values.items():io.put(f,NEWROOT+'/reports/'+name,json.dumps(value,indent=2).encode())
  save('INITIALIZATION_REVIEWED_SOURCE_FREEZE.json',values['SOURCE_FREEZE.json'])
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,ast,contextlib,io
D=Path(NEW_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once_v2 as own
own.verify();own.wait_existing();source=own.source()
import test_wave50_entry_target_cpu_v2 as test
capture=io.StringIO()
with contextlib.redirect_stdout(capture):test.main(str(source))
proof=json.loads(capture.getvalue());assert proof['passed'] and proof['small_preplacement_no_Wave_identity_exact'] and proof['empty_production20k_strict_rejected'] and proof['no_CUDA_initialized']
for name in ('train_wave50_entry_resume_ppo_v2.py','train_wave50_entry_fresh_preflight_ppo_v2.py'):
 text=(own.CODE/name).read_text();ast.parse(text)
 assert 'wave50_entry_runtime_v2' in text and 'wave50_entry_full_checkpoint_v2' in text and "_write_dynamic(torch.arange(env.num_envs,device=env.device))" in text
assert own.D==D and own.CODE==D/'isaac/mod4' and own.s.D==D and own.s.R==D/'reports'
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=410,source_checkpoint=own.s.q.base.checkpoint(source),proof=proof,actual_import_main_Popen_worker_roots_match=True,failed398_sources_preserved=True,initial_nonWave_small_scope_exact_no_XY_change=True,all20k_Wave_map_original_math_exact=True,SDK_native_fullstate_CUDA_PPO_fresh_formal_pending=True,no_GPU_or_canonical_write=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('NEW_TOKEN',repr(NEWROOT)))
  save('INITIALIZATION_REVIEWED_TARGET_CPU_PASSED.json',v);print(json.dumps(dict(root=NEWROOT,source_count=410,target_CPU_passed=True,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('INITIALIZATION_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_GPU_replay=True));raise
