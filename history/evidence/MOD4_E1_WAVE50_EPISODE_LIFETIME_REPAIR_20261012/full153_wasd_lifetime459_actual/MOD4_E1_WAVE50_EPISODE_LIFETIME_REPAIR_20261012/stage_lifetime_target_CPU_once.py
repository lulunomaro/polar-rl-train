from pathlib import Path
import sys,os,json,time,hashlib,shlex,traceback,ast
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=D/'payload'
sys.path.insert(0,str(W/'MOD4_LOCAL_WASD_WAVE50_70_20261012'))
from build_linux_only_continuation_once import connect_linux_only
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012'
OLD='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(name,v):p=R/name;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
def run(n,s):
 _,o,e=n.exec_command(PY+' -c '+shlex.quote(s),timeout=240);b=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:save('REMOTE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(rc=rc,stdout=b.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_GPU=True));raise RuntimeError('Actual CPU stage refused, preserved')
 return json.loads(b)
BOUNDARY=r'''
from pathlib import Path
import sys,json,hashlib,torch,fcntl,time,shutil,subprocess
O=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);sys.path[:0]=[str(O),str(O/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_startup_resource_reviewed_once as old
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=j(O/'reports/e1_WAVE50_route_startup_resource_reviewed_observation_INDEPENDENT_POSTEXIT_PASSED.json');assert proof['passed'] and proof['closeout_ready']
for loc in (j(O/'reports/E1_STATE.json')['owner'],j(O/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=3374665,start_ticks=94934812)):
 a=old.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
assert not old.trainers();B=old.s.q.ctl.CANONICAL;before=B.read_bytes();b=j(B);assert b['active_segment'] is None and not j(old.s.q.ctl.STATE_PATH).get('active_training')
assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',old.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_fcntl_free=True))
f=j(O/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==449
for name,sha in f.items():assert h(O/name)==sha
ref=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012');whole=sum(p.stat().st_size for p in ref.rglob('*') if p.is_file());refsource=j(ref/'reports/SOURCE_FREEZE.json')['sha256'];sourcebytes=sum((O/k).stat().st_size for k in f);refsourcebytes=sum((ref/k).stat().st_size for k in refsource)
need=2*whole+2*1024**3+2*max(0,sourcebytes-refsourcebytes)+2*PAYLOAD_BYTES_TOKEN+2*1100000*20
free=shutil.disk_usage(O).free;mem=next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))
gpu=json.loads(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total','--format=csv,noheader,nounits']).decode().strip().replace(' ', '').join(['[',']'])) if False else subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total','--format=csv,noheader,nounits']).decode().strip()
assert free>need and mem>8*1024**3 and int(gpu.split(',')[0])>20000 and not D.exists(),dict(free=free,required=need,mem=mem,gpu=gpu)
source=Path(j(O/'reports/SOURCE_SELECTED.json')['path']);assert h(source)=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd';info=old.prior.inherited.fullsave(source);assert info['finite_tensors']==102
D.mkdir();(D/'reports').mkdir()
for name,sha in f.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json','COMPLETE149_DIRECTION_AXIS_DECISION.json','COMPLETE151_ROUTE_AXIS_DECISION.json','REUSED_ACTUAL_CONTRACTS.json'):shutil.copy2(O/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,old449_independent_fullsave_exit_unique_settled=True,oldfreeze=f,source=info,two_fcntl_free=locks,canonical_SHA=h(B),actual_resource=dict(durable_free_bytes=free,required_bytes=need,actual443_complete300_whole_bytes=whole,source_delta_bytes=sourcebytes-refsourcebytes,newpayload_bytes=PAYLOAD_BYTES_TOKEN,lifetime_state_double20_save_margin_bytes=2*1100000*20,available_RAM=mem,actual_GPU_memory_csv=gpu),no_GPU_or_budget_write=True)))
'''
CPU=r'''
from pathlib import Path
import sys,json,time,torch,copy,hashlib,types,ast,tempfile
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_lifetime_once as own
from wave50_entry_current_state_v2 import extend,identity,KEY as ENTRY_KEY
from wave50_entry_runtime_v2 import reset_entry_xy
from wave50_episode_direction_math import bind as bind_direction
from wave50_direction_state import PROFILE as DP,KEY as DK,validate as vd
from wave50_route_runtime import state_dict as route_dict
from wave50_route_state import KEY as RK,PROFILE as RP
from wave50_lifetime_state import KEY,PROFILE,validate,evaluate
import wave50_lifetime_runtime as runtime
from retention_command_state import same
own.wait_existing();source=own.prior.source();ck=torch.load(source,map_location='cpu',weights_only=False);sha=own.s.q.base.sha(source);assert sha==own.SOURCE_SHA
parent=json.loads((D/'reports/PARENT_TIMEOUT_SOURCE_ACTUAL.json').read_bytes());ns=dict(torch=torch,ManagerBasedRLEnv=object);exec(compile(parent['function_source'],'<actual-parent-time_out-CPU>','exec'),ns);runtime.PARENT=ns['time_out'];runtime.PARENT_SHA=parent['canonical_function_sha256']
nativepath=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012/WAVE50_NATIVE20K.json');native=json.loads(nativepath.read_bytes());rows=native['actual_generated_family_assignments'];orig=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2]
family=torch.full((40,40),-1,dtype=torch.long);bounds=torch.zeros((40,40,2,3));names=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
for a in rows:family[a['row'],a['column']]=names.index(a['family']);bounds[a['row'],a['column']]=torch.tensor(a['bounds'])
t=types.SimpleNamespace(retention_size=(9.,9.),retention_family=family,retention_bounds=bounds,retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256']);env=types.SimpleNamespace(num_envs=20000,device='cpu',step_dt=.01,max_episode_length=2000,episode_length_buf=torch.zeros(20000,dtype=torch.long),scene=types.SimpleNamespace(env_origins=orig.clone(),terrain=t));rng=torch.get_rng_state().clone()
xy=reset_entry_xy(env,torch.arange(20000));receipt=env._wave50_entry_map_receipt;mask,sign=bind_direction(xy.numpy(),rows,receipt['ten_wave_span_m']*.5,receipt['collision_sample_extent_xy'])
terrain=dict(native['E1_terrain_identity'],spawn_xy=xy.clone(),reset_expected_q=ck['E1_terrain_state']['reset_expected_q'].clone(),episode=ck['E1_terrain_state']['episode'].clone());terrain=extend(terrain,receipt);env._rough_spawn_xy=xy.clone();env._e1_episode=terrain['episode'].clone();route=route_dict(env,refresh=True)
direction=dict(version=1,profile=DP,num_envs=20000,assignment_sha256=receipt['actual_assignment_sha256'],entry_map_sha256=receipt['map_sha256'],entry_origin_sha256=receipt['actual_origin_sha256'],no_new_rng=True,no_live_position_or_heading_correction=True,wave_mask=torch.tensor(mask),entry_sign=torch.tensor(sign),bound_episode=terrain['episode'].clone(),reset_xy=xy.clone(),control_histogram=torch.zeros((2,3),dtype=torch.long));vd(direction,20000)
state=runtime.state_dict(env,refresh=True);fixture=runtime.verify_GPU_lifetime_fixture(env);assert fixture['passed'] and not fixture['actual_bound_CUDA_state'] and state['wave_mask'].sum()==2820
out=copy.deepcopy(ck);out['E1_terrain_state']=terrain;out[ENTRY_KEY]=identity(terrain);out[DK]=direction;out['E1_WAVE50_episode_direction_profile']=DP;out[RK]=route;out['E1_WAVE50_route_lifecycle_profile']=RP;out[KEY]=state;out['E1_WAVE50_episode_lifetime_profile']=PROFILE;out['E1_retained_flat_command_state']['assignment_sha256']=receipt['actual_assignment_sha256'];out['independent_terrain_expert']='E1_WAVE50';out['E1_WAVE50_initial_source_sha256']=sha
p=D/'reports/LIFETIME_FULLSTATE_CPU_FIXTURE.pt';assert not p.exists();torch.save(out,p);info=own.fullsave(p);assert info['finite_tensors']==110 and info['lifetime_state_verified'] and info['initial_source_and_expert_identity_exact']
rejects=[]
with tempfile.TemporaryDirectory() as tmp:
 q=Path(tmp)/'invalid.pt'
 for field in ('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_timeout_source_sha256','route_profile','bound_episode','limit_steps','wave_mask','initial_source_SHA','expert'):
  bad=copy.deepcopy(out)
  if field=='bound_episode':bad[KEY][field]+=1
  elif field=='limit_steps':bad[KEY][field][0]+=1
  elif field=='wave_mask':bad[KEY][field][0]=~bad[KEY][field][0]
  elif field=='initial_source_SHA':bad['E1_WAVE50_initial_source_sha256']='0'*64
  elif field=='expert':bad['independent_terrain_expert']='wrong'
  elif field in ('profile','route_profile'):bad[KEY][field]='wrong'
  else:bad[KEY][field]='0'*64
  torch.save(bad,q)
  try:own.fullsave(q)
  except AssertionError:rejects.append(field)
  else:raise AssertionError('Invalid lifetime accepted '+field)
 q=Path(tmp)/'state.pt';torch.save(state,q);loaded=torch.load(q,map_location='cpu',weights_only=False);runtime.load_state(env,loaded);assert same(runtime.state_dict(env),state)
env._e1_episode[torch.tensor([0,3,9])]+=1;after=runtime.bind(env);assert torch.equal(after['bound_episode'],env._e1_episode) and torch.equal(after['wave_mask'],state['wave_mask']) and torch.equal(after['limit_steps'],state['limit_steps'])
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();assert own.prior.D==D and own.prior.CODE==D/'isaac/mod4' and own.s.D==D
assert 'train_wave50_lifetime_resume_ppo.py' in str(own.prior.train.__code__.co_consts) and 'native_e1_wave50_lifetime_scope_probe.py' in str(own.prior.native_contract.__code__.co_consts) and 'train_wave50_lifetime_resume_ppo.py' in str(own.prior.guardian.__code__.co_consts)
for name in ('train_wave50_lifetime_resume_ppo.py','train_wave50_lifetime_fresh_preflight_ppo.py','probe_wave50_lifetime_fresh_process_full_resume.py'):
 tree=ast.parse((own.CODE/name).read_text())
 for n in ast.walk(tree):
  if isinstance(n,ast.For) and isinstance(n.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(n):
   for item in n.iter.elts:
    if isinstance(item,ast.Constant) and isinstance(item.value,str):assert (own.CODE/item.value).is_file(),item.value
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=len(own.read(own.R/'SOURCE_FREEZE.json')['sha256']),source_checkpoint=own.prior.inherited.fullsave(source),actual_full_lifetime_CPU_fixture_finite_tensors=110,source_finite_tensors=102,strict_fullsave_rejections=rejects,lifetime_CPU_disk_roundtrip_exact=True,actual20k_Wave2820_other17180_timeouts_exact=True,actual_same_function_CPU_fixture=fixture,parent_timeout_source_exact=parent,selected_episode_bind_exact=True,CPU_RNG_byteexact_no_CUDA=True,import_main_Popen_guardian_roots_exact=True,CPU_fixture_index=dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),not_GPU_or_usable_learning_weight=True),newscope_SDK_native_fullCUDA_PPO_fresh_formal_pending=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.verify();print(json.dumps(v))
'''
def main():
 assert not (R/'TARGET_STAGE_STARTED.json').exists();save('TARGET_STAGE_STARTED.json',dict(epoch=time.time(),new_lifetime_only=True))
 files={p.relative_to(P).as_posix():p.read_bytes() for p in P.rglob('*') if p.is_file()};assert len(files)==9
 for name,b in files.items():ast.parse(b)
 n,w=connect_linux_only()
 try:
  v=run(n,BOUNDARY.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('PAYLOAD_BYTES_TOKEN',str(sum(map(len,files.values())))));save('OLD449_FINAL_BOUNDARY_RESOURCE_ACTUAL.json',v);freeze=dict(v['oldfreeze'])
  with n.open_sftp() as f:
   for name,b in files.items():assert name not in freeze;f.open(ROOT+'/'+name,'wb').write(b);freeze[name]=hashlib.sha256(b).hexdigest()
   values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,all449_oldbytes_exact=True,only_episode_lifetime_axis=True,new_files=list(files)),'COMPLETE153_EPISODE_LIFETIME_AXIS_DECISION.json':json.loads((R/'SCOPE_DECISION_ACTUAL.json').read_bytes()),'PARENT_TIMEOUT_SOURCE_ACTUAL.json':json.loads((R/'PARENT_TIMEOUT_SOURCE_ACTUAL.json').read_bytes())}
   for name,value in values.items():
    b=json.dumps(value,ensure_ascii=False,indent=2).encode()
    with f.open(ROOT+'/reports/'+name,'wb') as out:out.write(b)
  save('SOURCE_FREEZE_ACTUAL.json',values['SOURCE_FREEZE.json'])
  proof=run(n,CPU.replace('ROOT_TOKEN',repr(ROOT)));save('LIFETIME_TARGET_CPU_PASSED.json',proof);print(json.dumps(dict(target_CPU_passed=True,source_count=proof['source_count'],finite_fixture=proof['actual_full_lifetime_CPU_fixture_finite_tensors'],dispatch_pending=True,resources=v['actual_resource'])))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:save('TARGET_STAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_actual_substeps_before_independent_continuation=True,no_GPU_yet=True));raise
