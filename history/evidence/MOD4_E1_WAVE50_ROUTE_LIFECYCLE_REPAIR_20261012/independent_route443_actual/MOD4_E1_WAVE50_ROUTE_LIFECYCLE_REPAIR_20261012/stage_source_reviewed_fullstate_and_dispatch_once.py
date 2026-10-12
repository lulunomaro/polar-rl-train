from route_GPU_io import *

def main():
 assert not (R/'GPU_STAGE_STARTED.json').exists();save('GPU_STAGE_STARTED.json',dict(epoch=time.time(),only_missing_source_header_CPU_contract_continued=True))
 before=json.loads((R/'ROUTE_LIFECYCLE_TARGET_CPU_PASSED.json').read_bytes());assert before['passed'] and before['source_count']==439
 source=D/'payload_source_reviewed/supervise_wave50_route_source_reviewed_once.py';raw=source.read_bytes();compile(raw,str(source),'exec')
 save('CPU439_SOURCE_HEADER_SCOPE_REVIEW.json',dict(epoch=time.time(),original_target_CPU_pass_preserved=True,CPU439_no_GPU_or_controller_dispatched=True,prepared_wrapper_added_parent_source_SHA_check_but_overrode_original_expert_initialsource_assertions=True,missing_negative_fullsave_source_header_test_before_GPU=True,old439_source_bytes_preserved=True,new_wrapper_only_restores_original_source_expert_assertions=True,not_physics_or_PPO_failure=True))
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,sys,hashlib,time,shutil,torch
P=Path(CPU_TOKEN);D=Path(ROOT_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=lambda p:json.loads(p.read_bytes());sys.path[:0]=[str(P),str(P/'isaac/mod4')]
import supervise_wave50_route_CPU_reviewed_once as cpu
cpu.verify();cpu.wait_existing();assert j(P/'reports/WAVE50_TARGET_CPU_PASSED.json')['passed'] and not (P/'reports/E1_DISPATCH_STARTED.json').exists()
f=j(P/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==439 and not D.exists()
for name,sha in f.items():assert h(P/name)==sha
resource=j(Path(OLD426_TOKEN)/'reports/SOURCE_FREEZE.json');ref=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_EPISODE_DIRECTION_REVIEWED_20261012');whole=sum(p.stat().st_size for p in ref.rglob('*') if p.is_file());ref_files=j(ref/'reports/SOURCE_FREEZE.json')['sha256'];size=sum((P/k).stat().st_size for k in f);refsize=sum((ref/k).stat().st_size for k in ref_files);required=2*whole+2*1024**3+2*max(0,size-refsize)+2*660000*20;free=shutil.disk_usage(P).free;assert free>required,dict(free=free,required=required)
D.mkdir();(D/'reports').mkdir()
for name,sha in f.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json','COMPLETE149_DIRECTION_AXIS_DECISION.json','COMPLETE151_ROUTE_AXIS_DECISION.json','REUSED_ACTUAL_CONTRACTS.json','CANDIDATE_JOB_UNUSED_ACTUAL.json'):shutil.copy2(P/'reports'/name,D/'reports'/name)
assert not torch.cuda.is_initialized();print(json.dumps(dict(epoch=time.time(),passed=True,all439_CPU_root_bytes_reused_exact=True,oldfreeze=f,previous_actual_CPU=j(P/'reports/WAVE50_TARGET_CPU_PASSED.json'),resources=dict(durable_free_bytes=free,required_bytes=required,actual_completed_initial300_fullpipeline_reference_bytes=whole),new_wrapper_pending_CPU_and_GPU=True)))
'''.replace('CPU_TOKEN',repr(CPU_ROOT)).replace('ROOT_TOKEN',repr(ROOT)).replace('OLD426_TOKEN',repr(OLD)))
  save('SOURCE_REVIEWED_CPU_ROOT_ACTUAL_REUSE.json',v);freeze=dict(v['oldfreeze']);freeze[source.name]=H(raw)
  with n.open_sftp() as f:
   io.put(f,ROOT+'/'+source.name,raw);io.put(f,ROOT+'/reports/SOURCE_FREEZE.json',json.dumps(dict(epoch=time.time(),sha256=freeze,all439_oldbytes_exact=True,only_source_expert_header_assertions_restored_newwrapper=True),indent=2).encode())
  fixture=run(n,r'''from pathlib import Path
import sys,json,time,torch,copy,hashlib,tempfile,types,ast
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_source_reviewed_once as own
from wave50_direction_state import PROFILE as DPROFILE,KEY as DKEY,validate as validate_direction
from wave50_entry_current_state_v2 import extend,identity,KEY as ENTRY_KEY
from wave50_entry_runtime_v2 import reset_entry_xy
from wave50_episode_direction_math import bind as bind_direction
from wave50_route_runtime import bind as bind_route,state_dict
from wave50_route_state import KEY,PROFILE,validate
own.wait_existing();source=own.source();sha=own.s.q.base.sha(source);ck=torch.load(source,map_location='cpu',weights_only=False)
nativepath=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012/WAVE50_NATIVE20K.json');native=json.loads(nativepath.read_bytes());rows=native['actual_generated_family_assignments'];orig=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2]
family=torch.full((40,40),-1,dtype=torch.long);bounds=torch.zeros((40,40,2,3));names=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
for a in rows:family[a['row'],a['column']]=names.index(a['family']);bounds[a['row'],a['column']]=torch.tensor(a['bounds'])
t=types.SimpleNamespace(retention_size=(9.,9.),retention_family=family,retention_bounds=bounds,retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256'])
env=types.SimpleNamespace(num_envs=20000,device='cpu',scene=types.SimpleNamespace(env_origins=orig.clone(),terrain=t))
xy=reset_entry_xy(env,torch.arange(20000));receipt=env._wave50_entry_map_receipt;mask,sign=bind_direction(xy.numpy(),rows,receipt['ten_wave_span_m']*.5,receipt['collision_sample_extent_xy'])
terrain=dict(native['E1_terrain_identity'],spawn_xy=xy.clone(),reset_expected_q=ck['E1_terrain_state']['reset_expected_q'].clone(),episode=ck['E1_terrain_state']['episode'].clone());terrain=extend(terrain,receipt)
env._rough_spawn_xy=xy.clone();env._e1_episode=terrain['episode'].clone();route=state_dict(env,refresh=True)
direction=dict(version=1,profile=DPROFILE,num_envs=20000,assignment_sha256=receipt['actual_assignment_sha256'],entry_map_sha256=receipt['map_sha256'],entry_origin_sha256=receipt['actual_origin_sha256'],no_new_rng=True,no_live_position_or_heading_correction=True,wave_mask=torch.tensor(mask),entry_sign=torch.tensor(sign),bound_episode=terrain['episode'].clone(),reset_xy=xy.clone(),control_histogram=torch.zeros((2,3),dtype=torch.long));validate_direction(direction,20000)
out=copy.deepcopy(ck);out['E1_terrain_state']=terrain;out[ENTRY_KEY]=identity(terrain);out[DKEY]=direction;out['E1_WAVE50_episode_direction_profile']=DPROFILE;out[KEY]=route;out['E1_WAVE50_route_lifecycle_profile']=PROFILE
out['E1_retained_flat_command_state']['assignment_sha256']=receipt['actual_assignment_sha256'];out['independent_terrain_expert']='E1_WAVE50';out['E1_WAVE50_initial_source_sha256']=own.prior.SOURCE_SHA
rejects=[]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'full_route_CPU_fixture.pt';torch.save(out,p);info=own.fullsave(p);assert info['finite_tensors']==107 and info['route_lifecycle_state_verified'] and info['parent_route_boundary_source_CPU_exact'] and info['initial_source_and_expert_identity_exact']
 for field in ('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_boundary_source_sha256','bound_episode','spawn_xy','inward_limit_m','initial_source_SHA','expert'):
  bad=copy.deepcopy(out)
  if field=='bound_episode':bad[KEY][field]+=1
  elif field=='spawn_xy':bad[KEY][field]+=.01
  elif field=='inward_limit_m':bad[KEY][field][0]+=1
  elif field=='initial_source_SHA':bad['E1_WAVE50_initial_source_sha256']='0'*64
  elif field=='expert':bad['independent_terrain_expert']='wrong'
  else:bad[KEY][field]='wrong' if field=='profile' else '0'*64
  torch.save(bad,p)
  try:own.fullsave(p)
  except AssertionError:rejects.append(field)
  else:raise AssertionError('Invalid full route state accepted '+field)
assert len(rejects)==10 and own.s.q.base.sha(source)==sha and not torch.cuda.is_initialized()
oldproof=json.loads(Path(CPU_TOKEN,'reports/WAVE50_TARGET_CPU_PASSED.json').read_bytes());assert oldproof['passed']
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=len(own.prior.read(own.R/'SOURCE_FREEZE.json')['sha256']),source_checkpoint=own.prior.inherited.fullsave(source),CPU439_route_component_proof_reused_exact=True,CPU439_proof_path=str(Path(CPU_TOKEN,'reports/WAVE50_TARGET_CPU_PASSED.json')),CPU439_proof_SHA=hashlib.sha256(Path(CPU_TOKEN,'reports/WAVE50_TARGET_CPU_PASSED.json').read_bytes()).hexdigest(),actual_full_route_CPU_fixture_finite_tensors=107,source_finite_tensors=102,strict_fullsave_rejections=rejects,source_expert_header_assertions_exact=True,independent_source_actorcriticoptimizer_storage=True,no_CUDA_initialized=True,CPU_fixtures_not_GPU_restore_or_physical_pass=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.verify();print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('CPU_TOKEN',repr(CPU_ROOT)))
  save('SOURCE_REVIEWED_FULLSTATE_TARGET_CPU_PASSED.json',fixture)
  number=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())['number'];checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    found=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not found;checks.append(dict(host=host,path=path,matches=[]))
  save('DISPATCH_REQUESTED.json',dict(epoch=time.time(),actual_target_CPU440_passed=True,unused_rechecked=checks,new_route_missing_SDK_native_small_big_fresh_then_first300s=True,no_oldscope_GPU_replay_or_budget_extension=True))
  dispatch=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_source_reviewed_once as own
own.verify();own.wait_existing();assert not (own.R/'E1_DISPATCH_STARTED.json').exists() and not (D/'controller.log').exists()
for p in (own.s.q.P/'autonomy_controller.lock',own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.s.q.base.PY,str(D/'supervise_wave50_route_source_reviewed_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.s.q.P)
v=dict(epoch=time.time(),root=str(D),source_count=len(own.prior.read(own.R/'SOURCE_FREEZE.json')['sha256']),controller=loc,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.prior.SOURCE_SHA,source35_b026_ancestor129_preserved=True,new_route_lifecycle_only=True,first_formal_seconds=300,no_new_budget_seconds=True,SDK_native_PPO_fresh_formal_require_own_actual_receipts=True)
(own.R/'PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('DISPATCH_ACTUAL_RECEIPT.json',dispatch);print(json.dumps(dict(passed=True,actual_dispatch=True,source_count=dispatch['source_count'],controller=dispatch['controller'],first_formal300_future_requires_all_newscope_passed=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('GPU_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_continue_unexecuted_admission_or_dispatch_no_GPU_replay=True));raise
