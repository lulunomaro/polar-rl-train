"""Authentic old source tests plus actual new route functions on saved20k identities."""
from pathlib import Path
import torch,numpy as np,json,ast,types,copy,tempfile,hashlib
def verify(D,source):
 from test_wave50_direction_target_cpu import verify as original_verify
 from wave50_entry_runtime_v2 import reset_entry_xy
 import wave50_route_runtime as runtime
 from wave50_route_state import validate,evaluate_timeout,identity
 from retention_command_state import same
 previous=original_verify(D,source);assert previous['passed']
 nativepath=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012/WAVE50_NATIVE20K.json');native=json.loads(nativepath.read_bytes());xy=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2];rows=native['actual_generated_family_assignments']
 family=torch.full((40,40),-1,dtype=torch.long);bounds=torch.zeros((40,40,2,3));names=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
 for a in rows:family[a['row'],a['column']]=names.index(a['family']);bounds[a['row'],a['column']]=torch.tensor(a['bounds'])
 terrain=types.SimpleNamespace(retention_size=(9.,9.),retention_family=family,retention_bounds=bounds,retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256'])
 class Scene(dict):pass
 scene=Scene(robot=types.SimpleNamespace(data=types.SimpleNamespace(root_pos_w=xy.clone())));scene.terrain=terrain;scene.env_origins=xy.clone()
 env=types.SimpleNamespace(num_envs=20000,device='cpu',_e1_episode=torch.zeros(20000,dtype=torch.long),_rough_spawn_xy=xy.clone(),scene=scene)
 rng=torch.get_rng_state().clone();reset_entry_xy(env,torch.arange(20000));s=runtime.bind(env);assert s['wave_mask'].sum()==2820 and (~s['wave_mask']).sum()==17180
 original_text=(D/'isaac/mod4/e1_terrain_runtime.py').read_text();node=next(x for x in ast.parse(original_text).body if isinstance(x,ast.FunctionDef) and x.name=='boundary_timeout');ns=dict(torch=torch);exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual unchanged original2m boundary>','exec'),ns);original=ns['boundary_timeout']
 fixtures=[]
 for x,y in ((0.,0.),(2.,0.),(2.5,0.),(4.,0.),(4.001,0.),(-2.001,0.),(0.,2.001)):
  pose=xy.clone();pose[:,0]+=torch.where(s['wave_mask'],s['toward_sign'],torch.ones(20000))*x;pose[:,1]+=y;env.scene['robot'].data.root_pos_w=pose
  old=original(env);new=evaluate_timeout(pose,env._rough_spawn_xy,s,old);assert torch.equal(new[~s['wave_mask']],old[~s['wave_mask']])
  expected=x>4 or x < -2 or abs(y)>2;assert torch.equal(new[s['wave_mask']],torch.full_like(new[s['wave_mask']],expected));fixtures.append(dict(x=x,y=y,old_Wave=int(old[s['wave_mask']].sum()),new_Wave=int(new[s['wave_mask']].sum()),other17180_exact=True))
 rejects=[]
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'route.pt';torch.save(s,p);loaded=torch.load(p,map_location='cpu',weights_only=False);runtime.load_state(env,loaded);assert same(runtime.state_dict(env),s)
  for field in ('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_boundary_source_sha256','inward_limit_m'):
   bad=copy.deepcopy(s)
   if field=='profile':bad[field]='wrong'
   elif field=='inward_limit_m':bad[field][0]+=1.
   else:bad[field]='0'*64
   try:runtime.load_state(env,bad)
   except AssertionError:rejects.append(field)
   else:raise AssertionError('Wrong route state accepted '+field)
 runtime.load_state(env,s);env._e1_episode+=1;env.scene['robot'].data.root_pos_w=xy.clone();after=runtime.bind(env);assert torch.equal(after['bound_episode'],env._e1_episode) and torch.equal(after['spawn_xy'],xy)
 ids=torch.tensor([0,3,9,33]);original_episode=after['bound_episode'].clone();env._e1_episode[ids]+=1;after=runtime.bind(env);assert torch.equal(after['bound_episode'],env._e1_episode) and torch.equal(after['bound_episode'][torch.arange(20000)%3==1],original_episode[torch.arange(20000)%3==1])
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 # The parent config remains exact; the only changed manager declaration is its function.
 cfgsrc=(D/'isaac/mod4/wave50_route_runtime.py').read_text();configure=next(x for x in ast.parse(cfgsrc).body if isinstance(x,ast.FunctionDef) and x.name=='configure_retention');assign=[x for x in ast.walk(configure) if isinstance(x,ast.Assign)];assert len([x for x in assign if 'cfg.terminations' in ast.unparse(x)])==1
 return dict(passed=True,original_full_source102_and_D0D7_named_private_CPU_fixture=previous,actual_saved_native_path=str(nativepath),actual_saved_native_SHA=hashlib.sha256(nativepath.read_bytes()).hexdigest(),actual20k_Wave2820_nonWave17180_predicates_exact=True,fixtures=fixtures,strict_rejected_route_states=rejects,route_CPU_disk_roundtrip_exact=True,selected_episode_binding_exact=True,old_nonWave_outward_lateral2m_exact=True,new_Wave_inward4m_only=True,CPU_torch_RNG_byteexact_unchanged=True,production_old_boundary_source_SHA=hashlib.sha256(original_text.encode()).hexdigest(),no_CUDA_initialized=True,not_future_GPU_or_fullsave_pass=True)
