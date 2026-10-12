from route_fixture_io import *

def main():
 assert not (R/'FIXTURE_STAGE_STARTED.json').exists();save('FIXTURE_STAGE_STARTED.json',dict(epoch=time.time(),only_missing_postcontrol_fixture_API_scope_repaired=True))
 files={p.relative_to(D/'payload_fixture_reviewed').as_posix():p.read_bytes() for p in (D/'payload_fixture_reviewed').rglob('*') if p.is_file()};assert len(files)==3
 for name,raw in files.items():compile(raw,name,'exec')
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   dest=D/'failed440_actual';dest.mkdir(exist_ok=True);indices=[]
   paths=['controller.log','guardian.log','WAVE50_SDK10.log','WAVE50_SDK10.json.error','reports/E1_ATTENTION.json','reports/E1_STATE.json','reports/WAVE50_SDK10_PID_RECEIPT.json','reports/E1_GUARDIAN_STARTED.json','reports/E1_DISPATCH_STARTED.json','reports/PARENT_DISPATCH_ACTUAL_RECEIPT.json','reports/WAVE50_TARGET_CPU_PASSED.json','reports/SOURCE_FREEZE.json']
   try:paths.extend('WAVE50_SDK10_trace/'+x for x in f.listdir(FAILED_ROOT+'/WAVE50_SDK10_trace') if x.endswith('.npz'))
   except FileNotFoundError:pass
   for name in paths:
    raw=f.open(FAILED_ROOT+'/'+name,'rb').read();p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(raw);indices.append(dict(remote_path=FAILED_ROOT+'/'+name,local_path=str(p.resolve()),bytes=len(raw),sha256=H(raw)))
  save('SOURCE440_FAILED_SDK_ACTUAL_COLLECTION.json',dict(epoch=time.time(),classification='Post300control fixture API AttributeError after regular physics assertions, before final result write; incomplete SDK scope, zeroPPO, old error/raw/cost retained',indices=indices,original_report_not_generated_and_not_CPU_reconstructed=True,no_old_controller_or_GPU_replay=True))
  boundary=run(n,r'''from pathlib import Path
import json,sys,torch,time,hashlib,fcntl,shutil
P=Path(FAILED_TOKEN);D=Path(ROOT_TOKEN);sys.path[:0]=[str(P),str(P/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_source_reviewed_once as failed
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();st=j(P/'reports/E1_STATE.json');attention=j(P/'reports/E1_ATTENTION.json');assert not attention['own_child_still_alive'] and attention['active_segment'] is None and st['phase']=='WAVE50_new_SDK_native_no_PPO'
assert (P/'WAVE50_SDK10.json.error').exists() and not (P/'WAVE50_SDK10.json').exists() and not (P/'learning_logs').exists()
for loc in (st['owner'],j(P/'reports/E1_GUARDIAN_STARTED.json'),j(P/'reports/WAVE50_SDK10_PID_RECEIPT.json')['child']):
 a=failed.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
assert not failed.prior.trainers();B=failed.s.q.ctl.CANONICAL;before=B.read_bytes();assert j(B)['active_segment'] is None and not j(failed.s.q.ctl.STATE_PATH).get('active_training');locks=[]
for p in (B.parent/'native_floor_supervisor.lock',failed.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_fcntl_free=True))
f=j(P/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==440 and not D.exists()
for name,sha in f.items():assert h(P/name)==sha
reference=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_EPISODE_DIRECTION_REVIEWED_20261012');ref_f=j(reference/'reports/SOURCE_FREEZE.json')['sha256'];whole=sum(p.stat().st_size for p in reference.rglob('*') if p.is_file());size=sum((P/k).stat().st_size for k in f);refsize=sum((reference/k).stat().st_size for k in ref_f);need=2*whole+2*1024**3+2*max(0,size-refsize)+2*660000*20;free=shutil.disk_usage(P).free;assert free>need,dict(free=free,required=need)
D.mkdir();(D/'reports').mkdir()
for name,sha in f.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json','COMPLETE149_DIRECTION_AXIS_DECISION.json','COMPLETE151_ROUTE_AXIS_DECISION.json','REUSED_ACTUAL_CONTRACTS.json','CANDIDATE_JOB_UNUSED_ACTUAL.json'):shutil.copy2(P/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized();print(json.dumps(dict(epoch=time.time(),passed=True,oldfreeze=f,old440_actual_parent_guardian_SDKchild_naturally_exited=True,two_fcntl_free=locks,old440_zero_PPO_nocharge=True,canonical_SHA=h(B),resources=dict(durable_free_bytes=free,required_bytes=need),old_fullstate_CPU_proof=j(P/'reports/WAVE50_TARGET_CPU_PASSED.json'),no_GPU_yet=True)))
'''.replace('FAILED_TOKEN',repr(FAILED_ROOT)).replace('ROOT_TOKEN',repr(ROOT)))
  save('FAILED440_BOUNDARY_AND_FIXTURE_RESOURCES_ACTUAL.json',boundary);freeze=dict(boundary['oldfreeze'])
  with n.open_sftp() as f:
   for name,raw in files.items():assert name not in freeze;io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw)
   io.put(f,ROOT+'/reports/SOURCE_FREEZE.json',json.dumps(dict(epoch=time.time(),sha256=freeze,all440_oldbytes_exact=True,new_native_fixture_and_report_save_only=True,new_files=list(files)),indent=2).encode())
  proof=run(n,r'''from pathlib import Path
import sys,json,time,torch,types,hashlib
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_fixture_reviewed_once as own
from wave50_route_fixture_adapter_v2 import verify_GPU_boundary_fixture
from wave50_entry_runtime_v2 import reset_entry_xy
nativepath=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012/WAVE50_NATIVE20K.json');native=json.loads(nativepath.read_bytes());xy=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2];rows=native['actual_generated_family_assignments'];family=torch.full((40,40),-1,dtype=torch.long);bounds=torch.zeros((40,40,2,3));names=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
for a in rows:family[a['row'],a['column']]=names.index(a['family']);bounds[a['row'],a['column']]=torch.tensor(a['bounds'])
t=types.SimpleNamespace(retention_size=(9.,9.),retention_family=family,retention_bounds=bounds,retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256']);env=types.SimpleNamespace(num_envs=20000,device='cpu',_e1_episode=torch.zeros(20000,dtype=torch.long),_rough_spawn_xy=xy.clone(),scene=types.SimpleNamespace(terrain=t,env_origins=xy.clone()))
reset_entry_xy(env,torch.arange(20000));rng=torch.get_rng_state().clone();fixture=verify_GPU_boundary_fixture(env);assert fixture['passed'] and not fixture['actual_bound_CUDA_state'] and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
base=json.loads(Path(FAILED_TOKEN,'reports/WAVE50_TARGET_CPU_PASSED.json').read_bytes());assert base['passed'] and base['actual_full_route_CPU_fixture_finite_tensors']==107 and len(base['strict_fullsave_rejections'])==10
own.wait_existing();assert own.D==D and own.CODE==D/'isaac/mod4' and own.s.D==D and 'native_e1_wave50_route_fixture_v2_scope_probe.py' in str(own.prior.native_contract.__code__.co_consts)
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=len(own.prior.read(own.R/'SOURCE_FREEZE.json')['sha256']),source_checkpoint=own.prior.inherited.fullsave(own.source()),actual_full_route_CPU_fixture_finite_tensors=107,strict_source_header_expert_route_parent_map_episode_CPU_proof_reused_exact=base,actual_same_fixture_function_CPU_passed=fixture,CPU_RNG_exact_no_CUDA=True,old440_math_runtime_command_reward_DR_clock_geometry_bytes_exact=True,GPU_SDK_native_PPO_fresh_formal_require_new_actual_pass=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.verify();print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('FAILED_TOKEN',repr(FAILED_ROOT)))
  save('FIXTURE_REVIEWED_TARGET_CPU_PASSED.json',proof)
  number=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())['number'];checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    found=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not found;checks.append(dict(host=host,path=path,matches=[]))
  save('FIXTURE_DISPATCH_REQUESTED.json',dict(epoch=time.time(),actual_CPU443_passed=True,unused_rechecked=checks,old440_once_and_failed_partial_scope_retained_not_replayed=True,new_independent_corrected_SDK_admission_required=True))
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_fixture_reviewed_once as own
own.verify();own.wait_existing();assert not (own.R/'E1_DISPATCH_STARTED.json').exists() and not (D/'controller.log').exists()
for p in (own.s.q.P/'autonomy_controller.lock',own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.s.q.base.PY,str(D/'supervise_wave50_route_fixture_reviewed_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.s.q.P)
v=dict(epoch=time.time(),root=str(D),source_count=len(own.prior.read(own.R/'SOURCE_FREEZE.json')['sha256']),controller=loc,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.prior.SOURCE_SHA,new_fixture_native_only_correction=True,old439_and440_source_preserved=True,new_route4m_scope_requires_all_actual_admissions_before_first300s=True,no_budget_extension=True)
(own.R/'PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('FIXTURE_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(dict(actual_dispatch=True,source_count=v['source_count'],controller=v['controller'],newSDK_native_actual_future_only=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('FIXTURE_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_unexecuted_substeps_continued_no_GPU_replay=True));raise
