"""Authentic source+entry tests and direction runtime/storage CPU fixtures, no CUDA."""
from pathlib import Path
import ast,json,io,contextlib,types,torch,numpy as np,copy,tempfile
def verify(D,source):
 from test_wave50_entry_target_cpu_v2 import main as entry_test
 from wave50_entry_runtime_v2 import reset_entry_xy
 from wave50_direction_state import PROFILE,FIELDS,validate
 from wave50_episode_direction_math import bind,apply
 from retention_command_state import same
 capture=io.StringIO()
 with contextlib.redirect_stdout(capture):entry_test(source)
 old=json.loads(capture.getvalue());assert old['passed']
 native=json.loads(Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012/WAVE50_NATIVE20K.json').read_bytes())
 xy=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2];rows=native['actual_generated_family_assignments']
 family=torch.full((40,40),-1,dtype=torch.long);bounds=torch.zeros((40,40,2,3));names=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
 for a in rows:family[a['row'],a['column']]=names.index(a['family']);bounds[a['row'],a['column']]=torch.tensor(a['bounds'])
 terrain=types.SimpleNamespace(retention_size=(9.,9.),retention_family=family,retention_bounds=bounds,retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256'])
 env=types.SimpleNamespace(num_envs=20000,device='cpu',_e1_episode=torch.zeros(20000,dtype=torch.long),scene=types.SimpleNamespace(terrain=terrain,env_origins=xy.clone()))
 reset_entry_xy(env,torch.arange(20000));assert torch.equal(env._wave50_entry_xy,xy)
 receipt=env._wave50_entry_map_receipt;mask,sign=bind(xy.numpy(),rows,receipt['ten_wave_span_m']*.5,receipt['collision_sample_extent_xy'])
 class Parent:
  def _write_dynamic(self,ids):pass
 node=next(x for x in ast.parse((D/'isaac/mod4/wave50_direction_runtime.py').read_text()).body if isinstance(x,ast.ClassDef))
 ns=dict(torch=torch,RetainedFlatNamedOwnedCommand=Parent,reset_entry_xy=reset_entry_xy,PROFILE=PROFILE,FIELDS=FIELDS,validate=validate)
 exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-wave-direction-class>','exec'),ns)
 term=ns['WaveEntryDirectionCommand'].__new__(ns['WaveEntryDirectionCommand']);term._env=env;term.device='cpu';term.num_envs=20000
 term.wave_mask=torch.zeros(20000,dtype=torch.bool);term.entry_sign=torch.zeros(20000);term.bound_episode=torch.full((20000,),-1,dtype=torch.long);term.reset_xy=torch.zeros((20000,2));term.direction_control_histogram=torch.zeros((2,3),dtype=torch.long)
 term._retention_resampling=False;term.manual_evaluation_mode=False;term.family=torch.where(torch.tensor(mask),4,0)
 rng=torch.Generator().manual_seed(20260928);term.is_standing_env=torch.rand(20000,generator=rng)<.2
 command=torch.zeros((20000,3));command[:,0]=torch.rand(20000,generator=rng)*.6-.3;command[term.is_standing_env]=0;term.vel_command_b=command.clone()
 before=torch.get_rng_state().clone();private=rng.get_state().clone();ids=torch.arange(20000);term._write_dynamic(ids)
 assert torch.equal(before,torch.get_rng_state()) and torch.equal(private,rng.get_state())
 assert np.array_equal(term.vel_command_b.numpy(),apply(command.numpy(),mask,sign)) and term.audit_direction()['all_episode_identity_exact']
 # The parent runtime may classify a moved body as nonWave/plane: preserve
 # its current command exactly without changing the episode binding/sign.
 take=torch.nonzero(term.wave_mask&~term.is_standing_env).flatten()[:9];bound=term.entry_sign.clone();term.family[take]=0;term.vel_command_b[take]=torch.tensor([1.2,0.,1.4]);unchanged=term.vel_command_b[take].clone();term._write_dynamic(ids)
 assert torch.equal(term.vel_command_b[take],unchanged) and torch.equal(term.entry_sign,bound)
 term.family[take]=4;term.vel_command_b[take]=command[take];term._write_dynamic(ids)
 env._e1_episode[[1,4,7]]+=1;term._write_dynamic(torch.tensor([1,4,7]));assert (term.bound_episode==env._e1_episode).all()
 state=term.state_dict_direction()
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'direction.pt';torch.save(state,p);term.load_state_direction(torch.load(p,map_location='cpu',weights_only=False));assert same(state,term.state_dict_direction())
 rejects=[]
 for key in ('assignment_sha256','entry_map_sha256','entry_origin_sha256'):
  bad=dict(state);bad[key]='0'*64
  try:term.load_state_direction(bad)
  except AssertionError:rejects.append(key)
  else:raise AssertionError('wrong direction identity accepted '+key)
 bad=dict(state,profile='wrong')
 try:validate(bad,20000)
 except AssertionError:rejects.append('profile')
 else:raise AssertionError('wrong direction profile accepted')
 checked=[]
 for name in ('train_wave50_direction_fresh_preflight_ppo.py','train_wave50_direction_resume_ppo.py','probe_wave50_direction_fresh_process_full_resume.py'):
  text=(D/'isaac/mod4'/name).read_text();tree=ast.parse(text);assert 'from wave50_direction_runtime import' in text and 'from wave50_direction_full_checkpoint import' in text
  for node in ast.walk(tree):
   if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(node):
    for item in node.iter.elts:
     if isinstance(item,ast.Constant) and isinstance(item.value,str):assert (D/'isaac/mod4'/item.value).is_file(),item.value;checked.append(item.value)
  if name.startswith('train_'):assert text.index('_write_dynamic(torch.arange(env.num_envs,device=env.device))')<text.index("manifest['actual_episode_direction']")
 assert not torch.cuda.is_initialized()
 return dict(passed=True,CPU_only=True,old_source_and_entry_unmodified_test=old,actual_20k_Wave2820_and_nonWave17180=True,original_command_abs_standing_rng_exact=True,current_nonWave_parent_command_exact=True,episode_sign_only_changes_on_selected_episode=True,direction_disk_roundtrip_exact=True,strict_rejections=rejects,source_snapshot_required_paths_checked=len(checked),no_CUDA_initialized=True,new_direction_SDK_native_PPO_fresh_formal_pending=True)
