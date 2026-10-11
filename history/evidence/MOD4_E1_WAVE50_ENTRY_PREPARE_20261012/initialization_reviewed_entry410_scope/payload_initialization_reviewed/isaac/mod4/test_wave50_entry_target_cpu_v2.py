"""Actual source schema/storage and original strict-loader migration fixture; no CUDA."""
from pathlib import Path
import ast,copy,hashlib,json,sys,tempfile,torch
from types import SimpleNamespace
from retention_command_state import FIELDS,validate,same
from g4_command_migration import restore_source_then_bind_WAVE50

def old_main(source):
 torch.set_num_threads(1);p=Path(source);h=hashlib.sha256(p.read_bytes()).hexdigest()
 assert h=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
 ck=torch.load(p,map_location='cpu',weights_only=False)
 import supervise_e1_command_retention_episode_reviewed_once as inherited
 info=inherited.fullsave(p);assert info['finite_tensors']==102
 assert ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1'
 saved=ck['E1_retained_flat_command_state'];validate(saved,20000)
 other=copy.deepcopy(ck);checked=0
 for group in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
  def tensors(v):
   if torch.is_tensor(v):yield v
   elif isinstance(v,dict):
    for x in v.values():yield from tensors(x)
   elif isinstance(v,(list,tuple)):
    for x in v:yield from tensors(x)
  for a,b in zip(tensors(ck[group]),tensors(other[group])):assert a.data_ptr()!=b.data_ptr() and torch.equal(a,b);checked+=1
 a=next(iter(other['actor_state_dict'].values()));a.add_(1);assert h==hashlib.sha256(p.read_bytes()).hexdigest()
 # CPU fixture uses authentic fields, with a CPU-format RNG in place of CUDA bytes.
 # CUDA format/state equality is reserved for actual simulator startup, never inferred here.
 s=copy.deepcopy(saved);s.update(rng_device_type='cpu',rng=torch.Generator().manual_seed(93811).get_state())
 tree=ast.parse(Path(__file__).with_name('retention_flat_runtime.py').read_text())
 cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='RetainedFlatCommand')
 methods=[x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name in ('state_dict_retention','load_state_retention')]
 ns=dict(torch=torch,PROFILE=s['profile'],FIELDS=FIELDS,validate=validate)
 for fn in methods:exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<exact-old-loader>','exec'),ns)
 class Fixture:pass
 for fn in methods:setattr(Fixture,fn.name,ns[fn.name])
 f=Fixture();f.device='cpu';f.num_envs=20000;f._retention_rng=torch.Generator().manual_seed(4)
 f._env=SimpleNamespace(num_envs=20000,device='cpu',scene=SimpleNamespace(terrain=SimpleNamespace(retention_assignment_sha='f'*64)))
 for k in FIELDS:setattr(f,k,torch.zeros_like(s[k]))
 f.world_direction=torch.zeros(20000);f.is_moving_spin=torch.zeros(20000,dtype=torch.bool);f.vel_command_b=torch.zeros((20000,3))
 try:f.load_state_retention(s);raise RuntimeError('Original wrong assignment must reject')
 except AssertionError:pass
 proof=restore_source_then_bind_WAVE50(f,s,s['assignment_sha256'])
 assert f._env.scene.terrain.retention_assignment_sha=='f'*64
 assert same(f.state_dict_retention(),dict(s,assignment_sha256='f'*64))
 try:restore_source_then_bind_WAVE50(f,s,'e'*64);raise RuntimeError('Wrong source identity must reject')
 except AssertionError:pass
 with tempfile.TemporaryDirectory() as tmp:
  q=Path(tmp)/'slope_command.pt';torch.save(f.state_dict_retention(),q)
  f.load_state_retention(torch.load(q,weights_only=False));assert same(f.state_dict_retention(),dict(s,assignment_sha256='f'*64))
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(passed=True,source=info,CPU_only=True,no_CUDA_initialized=True,
  actor_critic_optimizer_independent_storage_tensors=checked,source_bytes_preserved=True,
  original_strict_wrong_assignment_rejected=True,wrong_source_identity_rejected=True,
  source_command_identity_view_exact_then_new_assignment_binding_CPU_fixture=proof,
  same_assignment_full_command_disk_restore_CPU_fixture_exact=True,
  authentic_CUDA_source_state_schema_validated_only=True,actual_CUDA_migration_episode_fullresume_PPO_pending=True)))

def main(source):
 import contextlib,io,numpy as np
 from wave50_entry_runtime_v2 import reset_entry_xy
 from wave50_entry_current_state_v2 import extend,validate_complete_entry,identity,KEY
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
 state=extend(state,env._wave50_entry_map_receipt);out=dict(ck,E1_terrain_state=state);out[KEY]=identity(state);out['E1_retained_flat_command_state']=dict(ck['E1_retained_flat_command_state'],assignment_sha256=state['entry_assignment_sha256'])
 validate_complete_entry(out,20000);rejects=[]
 for name in ('map','assignment','origin'):
  bad=copy.deepcopy(out);bad['E1_terrain_state']['entry_'+name+'_sha256']='e'*64
  try:validate_complete_entry(bad,20000)
  except AssertionError:rejects.append(name)
  else:raise AssertionError('Wrong identity accepted '+name)
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'entry_full_cpu_fixture.pt';torch.save(out,p);loaded=torch.load(p,weights_only=False)
  from wave50_entry_fullsave_cpu_v2 import fullsave
  assert fullsave(p)['finite_tensors']==102 and identity(loaded['E1_terrain_state'])==identity(state)
 from wave50_entry_runtime_v2 import initialization_safe_map
 small=orig[:10].numpy();smallxy,smallreceipt=initialization_safe_map(small,rows,points,json.loads((D/'isaac/mod4/g4_cad_profile.json').read_bytes())['span_m'],10)
 assert np.array_equal(small,smallxy) and smallreceipt['Wave_environments']==0 and smallreceipt['changed_environments']==0
 try:initialization_safe_map(np.repeat(small[:1],20000,axis=0),rows,points,2.4064227271861266,20000)
 except AssertionError:pass
 else:raise AssertionError('Empty production20k Wave scope must reject')
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(passed=True,source=sourceproof,strict_entry_map_assignment_origin_rejections=rejects,
   actual20k_native_origins_full1600assignments_CPU_fixture=True,entry_map=receipt,same_entry_CPU_disk_roundtrip_exact=True,
   actual_origin_mutation_cache_refresh_passed=True,small_preplacement_no_Wave_identity_exact=True,empty_production20k_strict_rejected=True,full_source_D0D7_oldnamed_private_CPU_schema_strict=True,
   CUDA_SDK_native_PPO_fresh_formal_still_pending=True,no_CUDA_initialized=True)))
if __name__=='__main__':main(sys.argv[1])
