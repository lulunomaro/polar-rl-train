"""New direction component CPU proof against original actual twenty-thousand reset map."""
from pathlib import Path
import ast,types,json,torch,numpy as np,hashlib,copy
def verify(D):
 C=D/'isaac/mod4';torch.set_num_threads(1)
 from curb20_entry_target_cpu import verify as old_verify
 from curb20_direction_state import bind_numpy,validate,PROFILE
 from retention_command_state import same
 result=old_verify(D)
 old=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_REPAIR_20261011')
 raw=old/'ENTRY_NATIVE20K.json';v=json.loads(raw.read_bytes());receipt=json.loads((old/'reports/ENTRY_NATIVE_SCOPE_PASSED.json').read_bytes())
 assert hashlib.sha256(raw.read_bytes()).hexdigest()==receipt['results']['ENTRY_NATIVE20K']['sha256']
 xy=np.array(v['reset_root_before_physics'],dtype='<f4')[:,:2];rows=v['actual_generated_family_assignments'];mask,sign=bind_numpy(xy,rows)
 assert len(xy)==20000 and mask.sum()==2820 and (sign>0).sum()>0 and (sign<0).sum()>0
 family=torch.full((40,40),-1,dtype=torch.long);bounds=torch.zeros((40,40,2,3))
 names=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
 for a in rows:family[a['row'],a['column']]=names.index(a['family']);bounds[a['row'],a['column']]=torch.tensor(a['bounds'])
 env=types.SimpleNamespace(num_envs=20000,device='cpu',_e1_episode=torch.zeros(20000,dtype=torch.long),
  _curb_entry_map_receipt=v['CURB_entry_map'],scene=types.SimpleNamespace(terrain=types.SimpleNamespace(retention_size=(9.,9.),retention_family=family,retention_bounds=bounds,retention_assignment_sha=v['command_retention']['assignment_sha256'])))
 class Base:
  def _write_dynamic(self,ids):pass
 tree=ast.parse((C/'curb20_direction_runtime.py').read_text());node=next(x for x in tree.body if isinstance(x,ast.ClassDef))
 ns=dict(torch=torch,RetainedFlatNamedOwnedCommand=Base,reset_entry_xy=lambda e,ids:torch.tensor(xy)[ids],PROFILE=PROFILE,FIELDS=('curb_mask','entry_sign','bound_episode','reset_xy','control_histogram'),validate=validate)
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(C/'curb20_direction_runtime.py'),'exec'),ns)
 cls=ns['CurbEntryDirectionCommand'];term=cls.__new__(cls);term._env=env;term.device='cpu';term.num_envs=20000
 term.curb_mask=torch.zeros(20000,dtype=torch.bool);term.entry_sign=torch.zeros(20000);term.bound_episode=torch.full((20000,),-1,dtype=torch.long);term.reset_xy=torch.zeros((20000,2));term.direction_control_histogram=torch.zeros((2,3),dtype=torch.long)
 term._retention_resampling=False;term.manual_evaluation_mode=False
 g=torch.Generator().manual_seed(20260928);term.is_standing_env=torch.rand(20000,generator=g)<.2
 command=torch.zeros((20000,3));command[:,0]=torch.rand(20000,generator=g)*.6-.3;command[term.is_standing_env]=0
 term.vel_command_b=command.clone();rng=g.get_state().clone();ids=torch.arange(20000)
 term._write_dynamic(ids);assert torch.equal(g.get_state(),rng)
 assert torch.equal(term.curb_mask,torch.tensor(mask)) and torch.equal(term.entry_sign,torch.tensor(sign))
 assert torch.equal(term.vel_command_b[~term.curb_mask],command[~term.curb_mask])
 assert torch.equal(term.vel_command_b[:,0].abs(),command[:,0].abs())
 assert term.audit_direction()['all_episode_identity_exact']
 # Move the live body elsewhere: the binding uses the original reset for the episode.
 before=term.entry_sign.clone();term._write_dynamic(ids);assert torch.equal(before,term.entry_sign)
 env._e1_episode[[1,4,7]]+=1;term._write_dynamic(torch.tensor([1,4,7]));assert (term.bound_episode==env._e1_episode).all()
 s=term.state_dict_direction();p=D/'reports/DIRECTION_COMPONENT_CPU_ROUNDTRIP.pt';assert not p.exists();torch.save(s,p);loaded=torch.load(p,map_location='cpu',weights_only=False)
 term.load_state_direction(loaded);assert same(term.state_dict_direction(),s)
 bad=dict(s,assignment_sha256='0'*64)
 try:term.load_state_direction(bad)
 except AssertionError:pass
 else:raise AssertionError('Wrong assignment was accepted')
 bad=dict(s,entry_map_sha256='0'*64)
 try:term.load_state_direction(bad)
 except AssertionError:pass
 else:raise AssertionError('Wrong entry identity was accepted')
 ck=torch.load(result['source_checkpoint']['path'],map_location='cpu',weights_only=False);a=copy.deepcopy(ck['model_state_dict']);b=copy.deepcopy(ck['model_state_dict'])
 tensors=[k for k in a if k.startswith(('actor','critic'))];assert len(tensors)==16
 for k in tensors:assert a[k].data_ptr()!=b[k].data_ptr()!=ck['model_state_dict'][k].data_ptr()
 first=tensors[0];prior=b[first].clone();a[first].add_(1);assert torch.equal(prior,b[first])
 checked=[]
 for name in ('train_curb20_direction_fresh_preflight_ppo.py','train_curb20_direction_resume_ppo.py','probe_curb20_direction_fresh_process_full_resume.py'):
  text=(C/name).read_text();tree=ast.parse(text);assert 'curb20_direction_runtime' in text and 'curb20_direction_full_checkpoint' in text
  for node in ast.walk(tree):
   if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(node):
    for item in node.iter.elts:
     if isinstance(item,ast.Constant) and isinstance(item.value,str):assert (C/item.value).is_file(),item.value;checked.append(item.value)
 assert not torch.cuda.is_initialized()
 return dict(passed=True,CPU_only=True,source_checkpoint=result['source_checkpoint'],actual_20000_fixture=True,actual_CURB2820=True,non_CURB17180_commands_exact=True,
  old_absolute_speed_standing_and_rng_exact=True,selected_episode_subset_exact=True,assignment_entry_wrong_identity_rejected=True,direction_disk_roundtrip_exact=True,
  independent_actor_critic_storage=True,snapshot_required_files_checked=len(checked),no_CUDA_initialized=True,new_SDK_native_PPO_formal_pending=True)
