"""Prepare independent entry-axis sources. Never launches GPU or changes old sources."""
from pathlib import Path
import ast,json,hashlib,time
D=Path(__file__).resolve().parent;W=D.parent;P=D/'payload';R=D/'reports'
BASE=W/'MOD4_E1_WAVE50_INDEPENDENT_PREPARE_20261012/payload'
PREV=W/'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012'
def put(name,s):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(s.encode() if isinstance(s,str) else s)
 if p.suffix=='.py':ast.parse(p.read_text())
def text(name):return (BASE/name).read_text().replace('\r','')
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
NEW=['wave50_entry_v1_math.py','wave50_entry_runtime.py','wave50_entry_full_pose_reset.py','wave50_entry_current_state.py','wave50_entry_full_checkpoint.py','wave50_entry_fullsave_cpu.py','wave50_entry_sdk_placement.py','test_wave50_entry_target_cpu.py']
R.mkdir(exist_ok=True);assert not (R/'LOCAL_BUILD_PASSED.json').exists()
put('isaac/mod4/'+NEW[0],(PREV/'wave50_entry_cpu_component'/NEW[0]).read_bytes())
put('isaac/mod4/wave50_entry_runtime.py', '''"""Only reset XY changes; cache binds actual origins, assignment, bank and profile."""
from pathlib import Path
import hashlib,json,numpy as np,torch
from g4_retention_runtime import configure_retention as old_configure
from wave50_entry_v1_math import entry_map,PROFILE
A=Path(__file__).resolve().parent
PROFILE_SHA='995115310ad96d92a77865c04c736896c112b4b89c7d674ac7a6d4d19f249a5d'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reset_entry_xy(env,ids):
 origins=env.scene.env_origins[:,:2];rows=env.scene.terrain.retention_assignment
 assignment=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert assignment==env.scene.terrain.retention_assignment_sha
 profile=A/'g4_cad_profile.json';assert h(profile)==PROFILE_SHA
 bank=A/'MOD4_RESET_COLLISION_BANK.npz'
 static=(assignment,h(bank),h(A/'wave50_entry_v1_math.py'),h(A/'wave50_entry_full_pose_reset.py'),h(profile))
 if not hasattr(env,'_wave50_entry_xy') or static!=env._wave50_entry_static_identity or not torch.equal(origins,env._wave50_entry_origin_snapshot):
  with np.load(bank) as z:
   pick=int(np.argmin(abs(z['root_height']-.25)));points=z['points_root'][pick].copy()
  xy,receipt=entry_map(origins.detach().cpu().numpy(),rows,points,json.loads(profile.read_bytes())['span_m'])
  origin_sha=hashlib.sha256(origins.detach().cpu().numpy().astype('<f4').tobytes()).hexdigest()
  key=hashlib.sha256((origin_sha+json.dumps(static)).encode()).hexdigest()
  env._wave50_entry_xy=torch.as_tensor(xy,device=env.device,dtype=torch.float32)
  env._wave50_entry_origin_snapshot=origins.clone();env._wave50_entry_static_identity=static
  env._wave50_entry_cache_builds=getattr(env,'_wave50_entry_cache_builds',0)+1
  env._wave50_entry_map_receipt=dict(receipt,actual_origin_sha256=origin_sha,actual_assignment_sha256=assignment,
   complete_bank_sha256=static[1],math_sha256=static[2],full_pose_reset_sha256=static[3],geometry_profile_sha256=static[4],
   actual_input_identity_sha256=key,cache_builds=env._wave50_entry_cache_builds,actual_origin_bound=True)
 return env._wave50_entry_xy[ids].clone()
def configure_retention(cfg):
 from wave50_entry_full_pose_reset import full_reset
 r=old_configure(cfg);cfg.events.consistent_start.func=full_reset
 r['independent_WAVE50_reset_entry']=dict(profile=PROFILE,reset_XY_only=True,unchanged_command_RNG_reward_DR_geometry=True,
  full_sampled_footprint_front_support_min_m=.4,no_new_random_stream=True,original2m_training_route_unchanged=True)
 return r
''')
oldreset=(PREV/'own_final_actual_1791746783347133700/actual_src_snapshot/e1_full_pose_reset.py').read_text()
newreset=replace(oldreset,'xy=env.scene.env_origins[ids,:2].clone()',"from wave50_entry_runtime import reset_entry_xy\n xy=reset_entry_xy(env,ids)") if 'xy=env.scene.env_origins[ids,:2].clone()' in oldreset else replace(oldreset,'xy = env.scene.env_origins[ids,:2].clone()',"from wave50_entry_runtime import reset_entry_xy\n xy=reset_entry_xy(env,ids)")
put('isaac/mod4/wave50_entry_full_pose_reset.py',newreset)
put('isaac/mod4/wave50_entry_current_state.py','''"""Strict original G4 state plus deterministic reset-entry disk identity."""
from pathlib import Path
import hashlib,torch
import g4_current_state as old
from wave50_entry_v1_math import PROFILE as ENTRY_PROFILE
PROFILE='mod4_G4_CAD_derived_50mm_entry_v1'
KEY='E1_WAVE50_entry_reset_identity'
def validate(state,n):
 assert state['profile']==PROFILE and state['entry_profile']==ENTRY_PROFILE
 for k in ('entry_map_sha256','entry_origin_sha256','entry_assignment_sha256','entry_input_sha256','entry_math_sha256','entry_runtime_sha256','entry_full_pose_sha256'):
  assert isinstance(state[k],str) and len(state[k])==64
 assert state['entry_assignment_sha256'] and state['entry_origin_cache_bound'] and state['entry_reset_XY_only'] and state['entry_no_new_RNG']
 old.validate(dict(state,profile=old.PROFILE),n)
def extend(state,receipt):
 A=Path(__file__).resolve().parent
 s=dict(state,profile=PROFILE,entry_profile=ENTRY_PROFILE,entry_map_sha256=receipt['map_sha256'],
  entry_origin_sha256=receipt['actual_origin_sha256'],entry_assignment_sha256=receipt['actual_assignment_sha256'],entry_input_sha256=receipt['actual_input_identity_sha256'],
  entry_math_sha256=receipt['math_sha256'],entry_runtime_sha256=hashlib.sha256((A/'wave50_entry_runtime.py').read_bytes()).hexdigest(),
  entry_full_pose_sha256=receipt['full_pose_reset_sha256'],entry_origin_cache_bound=True,entry_reset_XY_only=True,entry_no_new_RNG=True)
 assert s['G4_profile_sha256']==receipt['geometry_profile_sha256'] and s['reset_bank_sha256']==receipt['complete_bank_sha256']
 validate(s,state['num_envs']);return s
def current_state(env):
 from wave50_entry_runtime import reset_entry_xy
 reset_entry_xy(env,torch.arange(env.num_envs,device=env.device))
 return extend(old.current_state(env),env._wave50_entry_map_receipt)
def identity(state):return old.identity(state)
def validate_complete_entry(ck,n):
 s=ck['E1_terrain_state'];validate(s,n);assert ck[KEY]==identity(s)
 assert hashlib.sha256(s['spawn_xy'].cpu().numpy().astype('<f4').tobytes()).hexdigest()==s['entry_map_sha256']
 assert ck['E1_retained_flat_command_state']['assignment_sha256']==s['entry_assignment_sha256']
''')
s=text('isaac/mod4/g4_full_checkpoint.py').replace('from g4_current_state import','from wave50_entry_current_state import').replace("verified_G3_to_independent_WAVE50","verified_G3_to_independent_WAVE50_entry")
s=replace(s,"ck['E1_terrain_state']=current_state(env)","ck['E1_terrain_state']=current_state(env)\n  from wave50_entry_current_state import KEY,validate_complete_entry\n  ck[KEY]=identity(ck['E1_terrain_state'])")
s=replace(s,'torch.save(ck,path);env.write_retention_trace',"validate_complete_entry(ck,env.num_envs)\n  torch.save(ck,path);env.write_retention_trace")
s=replace(s,"restore(env,state);term.load_state_retention(cmd);assert same(term.state_dict_retention(),cmd)","from wave50_entry_current_state import validate_complete_entry\n  validate_complete_entry(ck,env.num_envs)\n  restore(env,state);term.load_state_retention(cmd);assert same(term.state_dict_retention(),cmd)")
s=replace(s,"before=current_state(env);ct=term.state_dict_retention();tmp=Path(log_dir)/'WAVE50_FULL_STATE_ACTUAL_CUDA_ROUNDTRIP.pt'","before=current_state(env);ct=term.state_dict_retention();tmp=Path(log_dir)/'WAVE50_ENTRY_FULL_STATE_ACTUAL_CUDA_ROUNDTRIP.pt'")
s=replace(s,"same_tick_ground_query_cache_cleared=True,PhysX_exact_resume_claimed=False,terrain_identity=identity(current_state(env)))","same_tick_ground_query_cache_cleared=True,PhysX_exact_resume_claimed=False,terrain_identity=identity(current_state(env)),\n  entry_state_restored_exact=same_scope,explicit_new_entry_reset_scope=not same_scope,actual_origin_bound_entry_cache=True)")
s=replace(s,"return proof","entry=dict(epoch=time.time(),pid=os.getpid(),source_sha256=h,passed=True,same_entry_identity_restored_exact=same_scope,explicit_new_entry_scope=not same_scope,\n  actual_entry_terrain_command_CUDA_disk_roundtrip_exact=True,saved_source_episode_plus_one_verified=True,\n  current_identity=identity(current_state(env)),map_receipt=env._wave50_entry_map_receipt,reset_XY_only_no_new_RNG=True,not_PhysX_exactresume=True)\n Path(log_dir,'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json').write_text(json.dumps(entry,indent=2))\n return proof")
put('isaac/mod4/wave50_entry_full_checkpoint.py',s)
s=text('isaac/mod4/g4_fullsave_cpu.py')
s=replace(s,"validator=WAVE50_validate if", "from wave50_entry_current_state import validate as ENTRY_validate,PROFILE as ENTRY_PROFILE\n        validator=ENTRY_validate if ck['E1_terrain_state']['profile']==ENTRY_PROFILE else WAVE50_validate if")
s=replace(s,'    return info',"    if require_e1 and ck['E1_terrain_state']['profile']==ENTRY_PROFILE:\n        from wave50_entry_current_state import validate_complete_entry\n        validate_complete_entry(ck,count)\n    return info")
put('isaac/mod4/wave50_entry_fullsave_cpu.py',s)
s=text('isaac/mod4/g4_sdk_placement.py')
s=replace(s,'return dict(placement,reset_root_before_physics_exact=True',"assert env._wave50_entry_map_receipt['actual_origin_bound']\n assert env._wave50_entry_map_receipt['Wave_environments']==10\n return dict(placement,actual_origin_bound_entry_cache_verified=True,entry_map_receipt=env._wave50_entry_map_receipt,reset_root_before_physics_exact=True")
put('isaac/mod4/wave50_entry_sdk_placement.py',s)
for old,new in [('train_wave50_full_resume_ppo.py','train_wave50_entry_resume_ppo.py'),('train_wave50_fresh_preflight_ppo.py','train_wave50_entry_fresh_preflight_ppo.py'),('probe_wave50_fresh_process_full_resume.py','probe_wave50_entry_fresh_process_full_resume.py')]:
 s=text('isaac/mod4/'+old).replace('from g4_retention_runtime import','from wave50_entry_runtime import').replace('from g4_current_state import','from wave50_entry_current_state import').replace('from g4_full_checkpoint import','from wave50_entry_full_checkpoint import')
 if old.startswith('train'):
  s=replace(s,'    manifest["src_sha256"] = snapshot',"    for name in "+repr(tuple(NEW))+":\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n    manifest['entry_reset_XY_only']=True\n    manifest['entry_actual_origin_bound']=True\n    manifest[\"src_sha256\"] = snapshot")
 else:
  s=replace(s,"assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']","entry=json.loads((log_dir/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json').read_text())\n    assert entry['same_entry_identity_restored_exact'] and not entry['explicit_new_entry_scope']\n    assert entry['actual_entry_terrain_command_CUDA_disk_roundtrip_exact'] and entry['saved_source_episode_plus_one_verified']\n    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']")
 put('isaac/mod4/'+new,s)
s=text('native_e1_wave50_scope_probe.py').replace('from g4_retention_runtime import','from wave50_entry_runtime import').replace('from g4_current_state import','from wave50_entry_current_state import').replace('from g4_sdk_placement import','from wave50_entry_sdk_placement import')
s=replace(s,"report['E1_reset_receipt']=env._rough_probe_reset_receipt;report['E1_same_tick_ground_query_updates']=env._rough_query_updates","report['E1_reset_receipt']=env._rough_probe_reset_receipt;report['E1_same_tick_ground_query_updates']=env._rough_query_updates\n report['actual_entry_map_receipt']=env._wave50_entry_map_receipt\n assert torch.equal(torch.tensor(initial_root,device=env.device,dtype=torch.float32)[:,:2],env._wave50_entry_xy)\n report['actual_all_reset_origins_equal_new_entry_map']=True")
s=replace(s,"selected_reset_audit=dict(selected_ids=ids.cpu().tolist(),other_bias_episode_exact=True,global_tick_unchanged=True)","assert torch.equal(robot.data.root_pos_w[ids,:2],env._wave50_entry_xy[ids])\n    selected_reset_audit=dict(selected_ids=ids.cpu().tolist(),other_bias_episode_exact=True,global_tick_unchanged=True,selected_entry_reset_exact=True)")
put('native_e1_wave50_entry_scope_probe.py',s)
put('wave50_entry_source_guard.py', '''"""005 authority remains unchanged; new entry scope pins approved diagnosis and own35 source."""
from pathlib import Path
from wave50_fullscope_source_guard import verify_original_records as old
def verify_original_records(q,D):
 old(q,D)
 d=q.w.read(D/'reports/COMPLETE147_ENTRY_AXIS_DECISION.json')
 assert d['candidate_forward_complete']==5 and d['candidate_reverse_complete']==25 and d['not_qualified50']
 assert d['new_entry_axis_approved'] and d['default_source_SHA']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
''')
s=text('supervise_wave50_independent_scope_once.py')
s=s.replace('from wave50_fullscope_source_guard import','from wave50_entry_source_guard import').replace("OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_SECOND_BOUNDED_20261011')","OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012')\nBASE=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012')")
s=replace(s,"f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==369", "f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(BASE/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==384")
s=replace(s,"decision=read(R/'FROZEN145_COMPLETE_SCOPE_DECISION.json');assert decision['actual_need_for_new_isolated50mm_learning'] and decision['checkpoint']['sha256']==SOURCE_SHA", "decision=read(R/'COMPLETE147_ENTRY_AXIS_DECISION.json');assert decision['new_entry_axis_approved'] and decision['default_source_SHA']==SOURCE_SHA")
s=replace(s,"st['phase']=='E1_WAVE35_second_bounded_saved_review_ready'", "st['phase']=='E1_WAVE50_second_bounded_saved_review_ready'")
s=replace(s,"p=read(OLD/'reports/e1_WAVE35_second_bounded_observation_PASSED.json');assert len(p['unique_completed_segment'])==1 and p['checkpoint']['sha256']==SOURCE_SHA", "p=read(OLD/'reports/e1_WAVE50_second_bounded_observation_PASSED.json');assert len(p['unique_completed_segment'])==1 and p['checkpoint']['sha256']=='a67b955f680dd101cc4480f19c2e95dd86c34423148302fad1d8e925e206d4df'")
s=s.replace('start_ticks=88740346','start_ticks=89922117').replace('verified_G3_to_independent_WAVE50','verified_G3_to_independent_WAVE50_entry')
s=s.replace('from g4_fullsave_cpu import','from wave50_entry_fullsave_cpu import')
for a,b in [('train_wave50_fresh_preflight_ppo.py','train_wave50_entry_fresh_preflight_ppo.py'),('train_wave50_full_resume_ppo.py','train_wave50_entry_resume_ppo.py'),('native_e1_wave50_scope_probe.py','native_e1_wave50_entry_scope_probe.py'),('probe_wave50_fresh_process_full_resume.py','probe_wave50_entry_fresh_process_full_resume.py')]:s=s.replace(a,b)
s=replace(s,"t['profile']=='mod4_G4_CAD_derived_50mm_v1'", "t['profile']=='mod4_G4_CAD_derived_50mm_entry_v1'")
s=replace(s,"assert v['PPO_update_count']==0 and not v['nonfinite']", "assert v['actual_all_reset_origins_equal_new_entry_map'] and v['actual_entry_map_receipt']['actual_origin_bound']\n        assert v['PPO_update_count']==0 and not v['nonfinite']")
s=replace(s,"assert v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact']", "assert v['sensor_sdk_audit']['selected_reset']['selected_entry_reset_exact'] and v['SDK_WAVE50_actual_assignment_placement']['actual_origin_bound_entry_cache_verified']\n            assert v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact']")
s=replace(s,"else:assert all(hist[1][i]>0 for i in (2,3,4,5))", "else:\n            assert all(hist[1][i]>0 for i in (2,3,4,5))\n            assert v['actual_entry_map_receipt']['map_sha256']=='f42f0b15333c9bedd903921e191940cc0a9e9d3042fd354053f74d5c1ee0eb0d'\n            assert v['actual_entry_map_receipt']['Wave_environments']==2820 and v['actual_entry_map_receipt']['other_environments_unchanged']==17180\n            audit_native_trace(outpath,v)")
s=replace(s,"cp=read(run/'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json');", "entryproof=read(run/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');assert entryproof['passed'] and entryproof['explicit_new_entry_scope'] and not entryproof['same_entry_identity_restored_exact'] and entryproof['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']\n        cp=read(run/'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json');")
s=s.replace("'e1_WAVE50_independent_observation'","'e1_WAVE50_entry_observation'").replace('E1_WAVE50_independent_saved_review_ready','E1_WAVE50_entry_saved_review_ready').replace("'-e1-wave50-independent'","'-e1-wave50-entry-repair'").replace("'e1-wave50-own-'","'e1-wave50-entry-own-'").replace('old369_own_PASSED','old386_own_PASSED')
insert='''def audit_native_trace(outpath,v):
 import numpy as np
 paths=list(outpath.parent.glob(outpath.stem+'_trace/retention_prefix_*.npz'));assert len(paths)==1
 with np.load(paths[0]) as z:
  root=z['root_before_physics'];cmd=z['command'];fam=z['family']
  assert len(cmd)==144 and cmd.shape[1:]==(20000,3) and np.isfinite(root).all() and np.isfinite(cmd).all()
  origins=np.array(v['reset_root_before_physics'])[:,:2];counts=[]
  rows=v['actual_generated_family_assignments']
  for side in (-1,1):
   mask=np.zeros(20000,dtype=bool)
   for a in rows:
    if a['family']!='random_uniform_for_rm':continue
    b=np.array(a['bounds']);center=(b[0,0]+b[1,0])*.5
    mask|=((origins>=b[0,:2])&(origins<b[1,:2])).all(1)&((origins[:,0]<center) if side<0 else (origins[:,0]>center))
   take=(fam==4)&mask[None,:];vx=cmd[:,:,0][take];vyaw=cmd[:,:,1:][take]
   c=dict(side=side,negative=int((vx<0).sum()),positive=int((vx>0).sum()),standing=int((vx==0).sum()),maxabs=float(abs(vx).max()))
   assert all(c[k]>0 for k in ('negative','positive','standing')) and c['maxabs']<=.300001 and np.max(abs(vyaw))==0
   counts.append(c)
 write('ENTRY_NATIVE_FULL_TRACE_REVIEW.json',dict(passed=True,path=str(paths[0]),bytes=paths[0].stat().st_size,sha256=s.q.base.sha(paths[0]),two_sides_signed_standing=counts,not_fullroute_contact_or_causal_certificate=True))

'''
s=replace(s,'def fresh_resume(big):',insert+'def fresh_resume(big):')
put('supervise_wave50_entry_scope_once.py',s)
# Target CPU tester keeps the real old strict command fixture, then adds cache/state rejection fixtures.
test=text('isaac/mod4/test_g4_fullstate_cpu.py').replace('def main(source):','def old_main(source):')
test=test[:test.index("if __name__=='__main__':")]
test+='''
def main(source):
 import contextlib,io,numpy as np
 from wave50_entry_runtime import reset_entry_xy
 from wave50_entry_current_state import extend,validate_complete_entry,identity,KEY
 buf=io.StringIO()
 with contextlib.redirect_stdout(buf):old_main(source)
 sourceproof=json.loads(buf.getvalue());D=Path(__file__).resolve().parents[2]
 native=json.loads((Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012')/'WAVE50_NATIVE20K.json').read_bytes())
 rows=native['actual_generated_family_assignments'];orig=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2]
 bank=D/'isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'
 with np.load(bank) as z:points=z['points_root'][int(np.argmin(abs(z['root_height']-.25)))].copy()
 env=SimpleNamespace(num_envs=20000,device='cpu',scene=SimpleNamespace(env_origins=orig.clone(),terrain=SimpleNamespace(retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256'])))
 ids=torch.arange(20000);xy=reset_entry_xy(env,ids);receipt=dict(env._wave50_entry_map_receipt)
 assert receipt['map_sha256']=='f42f0b15333c9bedd903921e191940cc0a9e9d3042fd354053f74d5c1ee0eb0d' and receipt['changed_environments']==2820
 assert torch.equal(reset_entry_xy(env,ids),xy) and env._wave50_entry_cache_builds==1
 env.scene.env_origins[0,1]+=.001;shifted=reset_entry_xy(env,ids)
 assert env._wave50_entry_cache_builds==2 and env._wave50_entry_map_receipt['actual_origin_sha256']!=receipt['actual_origin_sha256'] and shifted[0,1]==env.scene.env_origins[0,1]
 env.scene.env_origins.copy_(orig);assert torch.equal(reset_entry_xy(env,ids),xy)
 ck=torch.load(source,map_location='cpu',weights_only=False);state=dict(native['E1_terrain_identity'],spawn_xy=xy.clone(),reset_expected_q=ck['E1_terrain_state']['reset_expected_q'].clone(),episode=ck['E1_terrain_state']['episode'].clone())
 state=extend(state,env._wave50_entry_map_receipt);out=dict(ck,E1_terrain_state=state);out[KEY]=identity(state)
 validate_complete_entry(out,20000);rejects=[]
 for name in ('map','assignment','origin'):
  bad=copy.deepcopy(out);bad['E1_terrain_state']['entry_'+name+'_sha256']='e'*64
  try:validate_complete_entry(bad,20000)
  except AssertionError:rejects.append(name)
  else:raise AssertionError('Wrong identity accepted '+name)
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'entry_full_cpu_fixture.pt';torch.save(out,p);loaded=torch.load(p,weights_only=False)
  from wave50_entry_fullsave_cpu import fullsave
  assert fullsave(p)['finite_tensors']==102 and identity(loaded['E1_terrain_state'])==identity(state)
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(passed=True,source=sourceproof,strict_entry_map_assignment_origin_rejections=rejects,
   actual20k_native_origins_full1600assignments_CPU_fixture=True,entry_map=receipt,same_entry_CPU_disk_roundtrip_exact=True,
   actual_origin_mutation_cache_refresh_passed=True,full_source_D0D7_oldnamed_private_CPU_schema_strict=True,
   CUDA_SDK_native_PPO_fresh_formal_still_pending=True,no_CUDA_initialized=True)))
if __name__=='__main__':main(sys.argv[1])
'''
put('isaac/mod4/test_wave50_entry_target_cpu.py',test)
files={q.relative_to(P).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in P.rglob('*') if q.is_file()}
with (R/'LOCAL_BUILD_PASSED.json').open('x') as f:json.dump(dict(epoch=time.time(),files=files,all_compile_passed=True,source384_bytes_not_edited=True,new_target_CPU_and_GPU_not_yet_executed=True),f,indent=2)
print(json.dumps(dict(prepared=len(files),actual_target_CPU_pending=True)))
