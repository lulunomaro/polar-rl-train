from pathlib import Path
import json,time,ast,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=D/'payload';C=P/'isaac/mod4'
B=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/immutable449_source'
def put(name,s):
 p=P/name;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
def save(name,v):p=R/name;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
def main():
 assert not P.exists();P.mkdir();C.mkdir(parents=True)
 save('COMPONENT_BUILD_STARTED.json',dict(epoch=time.time(),new_lifetime_only_axis=True,old449_bytes_unchanged=True))
 put('isaac/mod4/wave50_lifetime_state.py', '''import torch
PROFILE='WAVE50_birth_episode_timeout40s_nonWave20s_v1'
KEY='E1_WAVE50_episode_lifetime_state'
FIELDS=('wave_mask','bound_episode','limit_steps')
IDENTITY=('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_timeout_source_sha256','route_profile')
def identity(s):return tuple(s[k] for k in IDENTITY)
def validate(s,n):
 assert s['version']==1 and s['profile']==PROFILE and s['num_envs']==n and s['no_new_rng']
 assert s['step_dt_s']==.01 and s['Wave_seconds']==40. and s['other_seconds']==20.
 assert s['route_profile']=='WAVE50_legal_entry_inward4m_outward2m_lateral2m_v1'
 for k in ('assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_timeout_source_sha256'):assert isinstance(s[k],str) and len(s[k])==64
 assert s['wave_mask'].shape==(n,) and s['wave_mask'].dtype==torch.bool
 assert s['bound_episode'].shape==(n,) and s['bound_episode'].dtype==torch.long and (s['bound_episode']>=0).all()
 assert s['limit_steps'].shape==(n,) and s['limit_steps'].dtype==torch.long
 assert torch.equal(s['limit_steps'],torch.where(s['wave_mask'],4000,2000))
 return True
def evaluate(age,s,old):
 assert age.shape==old.shape==(s['num_envs'],) and age.dtype==torch.long and (age>=0).all()
 out=old.clone();mask=s['wave_mask'];out[mask]=age[mask]>=s['limit_steps'][mask];return out
''')
 put('isaac/mod4/wave50_lifetime_runtime.py', '''from pathlib import Path
import torch,json,hashlib,inspect,ast,copy
import wave50_route_runtime as previous
from wave50_lifetime_state import PROFILE,KEY,FIELDS,IDENTITY,validate,identity,evaluate
PARENT=None;PARENT_SHA=None
def source_sha(function):return hashlib.sha256(ast.unparse(ast.parse(inspect.getsource(function))).encode()).hexdigest()
def configure_retention(cfg):
 global PARENT,PARENT_SHA
 previous.configure_retention(cfg);assert cfg.episode_length_s==20.
 PARENT=cfg.terminations.time_out.func;PARENT_SHA=source_sha(PARENT)
 assert PARENT.__name__=='time_out' and cfg.terminations.time_out.time_out
 cfg.terminations.time_out.func=time_out
def bind(env):
 route=previous.bind(env);n=env.num_envs;device=env.device
 assert PARENT_SHA and abs(float(env.step_dt)-.01)<1e-12 and int(env.max_episode_length)==2000
 s=getattr(env,'_wave50_lifetime_state',None)
 metadata=dict(version=1,profile=PROFILE,num_envs=n,no_new_rng=True,step_dt_s=.01,Wave_seconds=40.,other_seconds=20.,route_profile=route['profile'],assignment_sha256=route['assignment_sha256'],entry_map_sha256=route['entry_map_sha256'],entry_origin_sha256=route['entry_origin_sha256'],parent_timeout_source_sha256=PARENT_SHA)
 if s is None:
  s=dict(metadata,wave_mask=torch.zeros(n,dtype=torch.bool,device=device),bound_episode=torch.full((n,),-1,dtype=torch.long,device=device),limit_steps=torch.full((n,),2000,dtype=torch.long,device=device));env._wave50_lifetime_state=s
 assert identity(s)==identity(metadata)
 changed=s['bound_episode']!=route['bound_episode'];s['wave_mask'][changed]=route['wave_mask'][changed];s['bound_episode'][changed]=route['bound_episode'][changed];s['limit_steps'][changed]=torch.where(s['wave_mask'][changed],4000,2000)
 validate(s,n);assert torch.equal(s['wave_mask'],route['wave_mask']) and torch.equal(s['bound_episode'],env._e1_episode);return s
def time_out(env):
 assert PARENT is not None
 old=PARENT(env);assert torch.equal(old,env.episode_length_buf>=env.max_episode_length)
 return evaluate(env.episode_length_buf,bind(env),old)
def state_dict(env,refresh=False):
 s=bind(env) if refresh else env._wave50_lifetime_state
 return {k:v.detach().clone().cpu() if isinstance(v,torch.Tensor) else copy.deepcopy(v) for k,v in s.items()}
def load_state(env,state):
 validate(state,env.num_envs);current=bind(env);assert identity(current)==identity(state)
 env._wave50_lifetime_state={k:v.detach().clone().to(env.device) if isinstance(v,torch.Tensor) else copy.deepcopy(v) for k,v in state.items()}
def audit(env):
 s=bind(env);return dict(profile=PROFILE,Wave_birth_environments=int(s['wave_mask'].sum()),other_birth_environments=int((~s['wave_mask']).sum()),Wave_seconds=40.,other_seconds=20.,parent_timeout_source_sha256=PARENT_SHA,episode_bound_exact=True,no_new_rng=True,only_time_out_function_changed=True,unchanged_initial_random_episode_age_draw=True,unchanged_clock_and_route_and_commands=True)
def verify_GPU_lifetime_fixture(env):
 before=env.episode_length_buf.clone();rng=torch.get_rng_state().clone();cuda_rng=torch.cuda.get_rng_state(env.device).clone() if str(env.device).startswith('cuda') else None;s=bind(env);rows=[]
 try:
  for age in (0,1999,2000,3999,4000):
   env.episode_length_buf.fill_(age);old=PARENT(env);new=time_out(env)
   assert torch.equal(new[~s['wave_mask']],old[~s['wave_mask']]);assert torch.equal(new[s['wave_mask']],torch.full_like(new[s['wave_mask']],age>=4000));rows.append(dict(age=age,Wave_timeouts=int(new[s['wave_mask']].sum()),other_timeouts=int(new[~s['wave_mask']].sum())))
 finally:env.episode_length_buf.copy_(before)
 assert torch.equal(before,env.episode_length_buf) and torch.equal(rng,torch.get_rng_state())
 if cuda_rng is not None:assert torch.equal(cuda_rng,torch.cuda.get_rng_state(env.device))
 return dict(passed=True,actual_bound_CUDA_state=cuda_rng is not None,fixtures=rows,actual_episode_length_buf_restored_exact=True,no_physical_step_or_reset_teleport_or_progress_credit=True,no_new_rng=True)
''')
 put('isaac/mod4/wave50_lifetime_full_checkpoint.py', '''from pathlib import Path
import json,hashlib,time,os,torch
import wave50_route_full_checkpoint as old
from wave50_lifetime_state import KEY,PROFILE,validate
from wave50_lifetime_runtime import bind,state_dict,load_state,audit
from retention_command_state import same
def install_e1_save_contract(runner,env):
 old.install_e1_save_contract(runner,env);original=runner.save
 def save(path,*a,**k):
  original(path,*a,**k);ck=torch.load(path,map_location='cpu',weights_only=False);ck[KEY]=state_dict(env,refresh=True);ck['E1_WAVE50_episode_lifetime_profile']=PROFILE;torch.save(ck,path)
  Path(path).parent.joinpath('WAVE50_LIFETIME_ACTUAL.json').write_text(json.dumps(audit(env),indent=2))
 runner.save=save
def resume_e1_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);sha=hashlib.sha256(Path(path).read_bytes()).hexdigest();new=KEY not in ck
 if new:assert sha==old.old.old.SOURCE_SHA;before=state_dict(env,refresh=True)
 else:validate(ck[KEY],env.num_envs);load_state(env,ck[KEY]);before=state_dict(env);assert same(before,ck[KEY])
 p=Path(log_dir)/'WAVE50_LIFETIME_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(before,p);loaded=torch.load(p,map_location='cpu',weights_only=False);load_state(env,loaded);assert same(state_dict(env),before)
 proof=old.resume_e1_new_episode(runner,env,path,log_dir);s=bind(env);assert torch.equal(s['bound_episode'],ck['E1_terrain_state']['episode'].to(env.device)+1)
 own=dict(epoch=time.time(),pid=os.getpid(),passed=True,source_sha256=sha,explicit_new_episode_lifetime_scope=new,predecessor_lifetime_state_restored_exact=not new,actual_CUDA_lifetime_disk_roundtrip_exact=True,saved_source_episode_plus_one_verified=True,no_new_rng=True,PhysX_exact_resume_claimed=False,lifetime_audit=audit(env))
 Path(log_dir,'E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(own,indent=2));return proof
''')
 put('isaac/mod4/wave50_lifetime_fullsave_cpu.py', '''from pathlib import Path
import json,torch
from wave50_route_fullsave_CPU_parent_reviewed import fullsave as old
from wave50_lifetime_state import KEY,PROFILE,validate
def fullsave(path,count=20000):
 info=old(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False);s=ck[KEY];validate(s,count);assert ck['E1_WAVE50_episode_lifetime_profile']==PROFILE
 route=ck['E1_WAVE50_route_lifecycle_state'];assert all(s[k]==route[k] for k in ('assignment_sha256','entry_map_sha256','entry_origin_sha256'))
 assert torch.equal(s['wave_mask'].cpu(),route['wave_mask'].cpu()) and torch.equal(s['bound_episode'].cpu(),ck['E1_terrain_state']['episode'].cpu())
 assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
 assert s['parent_timeout_source_sha256']==json.loads(Path(__file__).parents[2].joinpath('reports/PARENT_TIMEOUT_SOURCE_ACTUAL.json').read_bytes())['canonical_function_sha256']
 info['lifetime_state_verified']=True;info['initial_source_and_expert_identity_exact']=True;return info
''')
 modules=('wave50_lifetime_state.py','wave50_lifetime_runtime.py','wave50_lifetime_full_checkpoint.py','wave50_lifetime_fullsave_cpu.py')
 for oldname in ('train_wave50_route_resume_ppo.py','train_wave50_route_fresh_preflight_ppo.py','probe_wave50_route_fresh_process_full_resume.py'):
  name=oldname.replace('wave50_route','wave50_lifetime');s=(B/'isaac/mod4'/oldname).read_text();s=s.replace('from wave50_route_runtime import configure_retention','from wave50_lifetime_runtime import configure_retention').replace('from wave50_route_full_checkpoint import','from wave50_lifetime_full_checkpoint import')
  if name.startswith('train_'):
   anchor='    manifest["src_sha256"] = snapshot';assert s.count(anchor)==1
   s=s.replace(anchor,"    from wave50_lifetime_runtime import audit as audit_lifetime\n    manifest['actual_episode_lifetime']=audit_lifetime(env)\n    manifest['new_episode_lifetime_axis']=True\n    for name in "+repr(modules)+":\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n"+anchor)
   # Preserve the reviewed449 prePPO initialization exception exit; normal path unchanged.
   anchor='    try:\n\n        main()';
   if anchor in s:s=s.replace(anchor,'    try:\n\n        main()')
  else:
   anchor="    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']";assert anchor in s
   s=s.replace(anchor,"    lifetime=json.loads((log_dir/'E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json').read_text())\n    assert lifetime['passed'] and lifetime['predecessor_lifetime_state_restored_exact'] and not lifetime['explicit_new_episode_lifetime_scope'] and lifetime['actual_CUDA_lifetime_disk_roundtrip_exact'] and lifetime['saved_source_episode_plus_one_verified']\n"+anchor).replace('proof=proof,terrain=terrain,','proof=proof,terrain=terrain,lifetime=lifetime,')
  put('isaac/mod4/'+name,s)
 native=(B/'native_e1_wave50_route_fixture_v2_scope_probe.py').read_text().replace('from wave50_route_runtime import configure_retention','from wave50_lifetime_runtime import configure_retention')
 anchor=" Path(args.output).write_text(json.dumps(report,indent=2))";assert native.count(anchor)==1
 native=native.replace(anchor," from wave50_lifetime_runtime import audit as audit_lifetime,verify_GPU_lifetime_fixture\n report['episode_lifetime']=audit_lifetime(env)\n report['actual_lifetime_GPU_fixture']=verify_GPU_lifetime_fixture(env)\n"+anchor)
 put('native_e1_wave50_lifetime_scope_probe.py',native)
 controller='''from pathlib import Path
import ast,json,time,os,subprocess,argparse,traceback,torch
import supervise_wave50_route_lifecycle_once as prior
from wave50_lifetime_fullsave_cpu import fullsave
D=prior.D;R=prior.R;CODE=prior.CODE;s=prior.s;read=prior.read;identity=prior.identity
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012')
SOURCE_SHA=prior.SOURCE_SHA
def verify():
 prior_verify();f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==449 and all(f[k]==v for k,v in old.items())
 decision=read(R/'COMPLETE153_EPISODE_LIFETIME_AXIS_DECISION.json');assert decision['new_lifetime_axis_authorized_by_human_continue_and004005_bounded_diagnosis'] and decision['two_same_route_blocks_complete'] and decision['forward_complete']==13 and decision['reverse_complete']==23
 b=read(s.q.ctl.CANONICAL);assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>1020
 assert read(R/'WAVE50_TARGET_CPU_PASSED.json')['passed']
def wait_existing():
 proof=read(OLD/'reports/e1_WAVE50_route_startup_resource_reviewed_observation_INDEPENDENT_POSTEXIT_PASSED.json');assert proof['passed'] and proof['closeout_ready']
 for loc in (read(OLD/'reports/E1_STATE.json')['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=3374665,start_ticks=94934812)):
  actual=identity(loc['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
def trainers():
 rows=prior_trainers()
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   argv=[x.decode(errors='replace') for x in p.read_bytes().split(bytes([0]))]
   if any(Path(x).name in ('train_wave50_lifetime_resume_ppo.py','train_wave50_lifetime_fresh_preflight_ppo.py','native_e1_wave50_lifetime_scope_probe.py','probe_wave50_lifetime_fresh_process_full_resume.py','train_wave50_route_startup_resource_reviewed_ppo.py') for x in argv):rows.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return rows
prior_verify=prior.verify;prior_trainers=prior.trainers
prior.verify=verify;prior.wait_existing=wait_existing;prior.fullsave=fullsave;prior.trainers=trainers
prior.__file__=__file__
replacements={'train_wave50_route_resume_ppo.py':'train_wave50_lifetime_resume_ppo.py','train_wave50_route_fresh_preflight_ppo.py':'train_wave50_lifetime_fresh_preflight_ppo.py','probe_wave50_route_fresh_process_full_resume.py':'probe_wave50_lifetime_fresh_process_full_resume.py','native_e1_wave50_route_lifecycle_scope_probe.py':'native_e1_wave50_lifetime_scope_probe.py','e1_WAVE50_route_lifecycle_observation':'e1_WAVE50_episode_lifetime_observation','bounded_E1_WAVE50_route_lifecycle_learning':'bounded_E1_WAVE50_episode_lifetime_learning','E1_WAVE50_route_lifecycle_saved_review_ready':'E1_WAVE50_episode_lifetime_saved_review_ready','e1-wave50-route-lifecycle-repair':'e1-wave50-episode-lifetime-repair'}
for name in ('train','native_contract','fresh_resume','guardian','main','publish'):
 node=next(x for x in ast.parse((D/'supervise_wave50_route_lifecycle_once.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name==name)
 class Rename(ast.NodeTransformer):
  def visit_Constant(self,n):
   if isinstance(n.value,str):
    for a,b in replacements.items():n.value=n.value.replace(a,b)
   return n
 text=ast.unparse(Rename().visit(node))
 if name=='train':
  anchor="route = read(run / 'E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json')";assert anchor in text
  text=text.replace(anchor,"lifetime = read(run / 'E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json')\n        assert lifetime['passed'] and lifetime['explicit_new_episode_lifetime_scope'] and not lifetime['predecessor_lifetime_state_restored_exact'] and lifetime['actual_CUDA_lifetime_disk_roundtrip_exact'] and lifetime['saved_source_episode_plus_one_verified']\n        "+anchor)
 if name=='native_contract':
  anchor="audit_native_trace(outpath, v)";assert anchor in text
  text=text.replace(anchor,anchor+"\n        assert v['episode_lifetime']['Wave_seconds']==40. and v['episode_lifetime']['other_seconds']==20. and v['actual_lifetime_GPU_fixture']['passed'] and v['actual_lifetime_GPU_fixture']['actual_bound_CUDA_state']\n        write(label+'_LIFETIME_GPU_SCOPE_PASSED.json',dict(passed=True,audit=v['episode_lifetime'],fixture=v['actual_lifetime_GPU_fixture'],physical_callbacks=v['physical_callback_count']))")
 if name=='fresh_resume':
  anchor="assert proof['passed']";assert anchor in text
  text=text.replace(anchor,"assert proof['lifetime']['predecessor_lifetime_state_restored_exact'] and not proof['lifetime']['explicit_new_episode_lifetime_scope'] and proof['lifetime']['actual_CUDA_lifetime_disk_roundtrip_exact']\n    "+anchor)
 exec(compile(text,str(__file__)+'#new-lifetime-'+name,'exec'),vars(prior))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],original_failure_retained=True,no_blind_resume=True));raise
'''
 put('supervise_wave50_lifetime_once.py',controller)
 files={p.relative_to(P).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in P.rglob('*') if p.is_file()};assert len(files)==9
 save('COMPONENTS_PREPARED.json',dict(epoch=time.time(),passed=True,files=files,source449_allbytes_will_be_preserved_exact=True,new_scope='Only Wave-born physical episode time_out20to40seconds',target_fullstate_CPU_GPU_pending=True,no_oldonce_replayed=True))
 print(json.dumps(dict(prepared=True,components=len(files),new_source_count=449+len(files),GPU_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('BUILD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_target_root_or_GPU=True));raise
