"""Actual whole20k source state and selected-reset math; no GPU/worker adoption."""
from pathlib import Path
import json,time,hashlib,traceback,copy,torch,numpy as np
import wave50_birth_bodyframe_CPU_component_v1 as m
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):
 h=hashlib.sha256()
 def feed(x):
  h.update(type(x).__name__.encode()+b'\0')
  if torch.is_tensor(x):h.update(str(x.dtype).encode());h.update(str(tuple(x.shape)).encode());h.update(x.cpu().contiguous().numpy().tobytes())
  elif isinstance(x,np.ndarray):h.update(str(x.dtype).encode());h.update(str(x.shape).encode());h.update(x.tobytes())
  elif isinstance(x,dict):
   for k in sorted(x,key=repr):feed(k);feed(x[k])
  elif isinstance(x,(list,tuple)):
   for y in x:feed(y)
  else:h.update(repr(x).encode())
 feed(v);return h.hexdigest()

def main():
 out=R/'WAVE50_WHOLE20K_BIRTH_BODYFRAME_LOGICAL_CPU_PREPARED_ACTUAL.json';assert not out.exists()
 try:
  p=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/left_second_ownsave_actual_1791963199228502100/0_model_32825.pt';assert H(p)==m.SOURCE
  source=torch.load(p,map_location='cpu',weights_only=False);before=digest(source);rng=torch.get_rng_state().clone()
  d=source['E1_WAVE50_episode_direction_state'];route=source['E1_WAVE50_route_lifecycle_state'];life=source['E1_WAVE50_episode_lifetime_state'];terrain=source['E1_terrain_state'];commands=source['E1_retained_flat_command_state']
  assert terrain['num_envs']==20000 and torch.equal(d['wave_mask'],route['wave_mask']) and torch.equal(d['wave_mask'],life['wave_mask'])
  assert torch.equal(d['entry_sign'],route['toward_sign']) and torch.equal(d['bound_episode'],terrain['episode'])
  identity={k:d[k] for k in ('assignment_sha256','entry_map_sha256','entry_origin_sha256')};identity.update(parent_boundary_source_sha256=route['parent_boundary_source_sha256'],parent_timeout_source_sha256=life['parent_timeout_source_sha256'])
  state=m.from_strict_source(m.SOURCE,d['wave_mask'],d['entry_sign'],terrain['episode'],identity)
  episodes=terrain['episode']+1;allids=torch.arange(20000);first=m.bind_selected_births(state,allids,episodes,identity)
  counts={}
  for sign in (-1.,1.):
   mask=first['wave_mask']&(first['world_toward_sign']==sign);n=int(mask.sum());flipped=int(first['flip_pi'][mask].sum());assert abs(flipped-(n-flipped))<=1
   counts[str(sign)]=dict(actual_source_births=n,pi_births=flipped,unrotated_births=n-flipped)
  original=commands['BODY_command'].clone();family=commands['family'].clone();standing=(original==0).all(-1)
  actual=m.command_from_original(original,family,standing,first);active=first['wave_mask']&(family==4)&~standing
  assert torch.equal(actual[active,0]*first['BODY_coefficient'][active],original[active,0])
  assert torch.equal(actual[~first['wave_mask']],original[~first['wave_mask']]) and torch.equal(actual[standing],original[standing])
  selected=torch.nonzero(first['wave_mask'],as_tuple=False).flatten()[::197];next_episode=episodes.clone();next_episode[selected]+=1
  second=m.bind_selected_births(first,selected,next_episode,identity);untouched=torch.ones(20000,dtype=torch.bool);untouched[selected]=False
  for k in ('bound_episode','flip_pi','BODY_coefficient'):
   assert torch.equal(second[k][untouched],first[k][untouched])
  assert torch.equal(second['flip_pi'][selected],~first['flip_pi'][selected])
  base=json.loads((W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json').read_bytes())
  q=torch.tensor(base['initial']['root'],dtype=torch.float32)[:,3:7];flip=torch.arange(80)%2==0;rotated=m.rotate_birth_xyzw(q,flip)
  assert torch.allclose(rotated.square().sum(-1),q.square().sum(-1),atol=1e-6,rtol=0)
  negatives=[]
  tests=[]
  for field,value in [('profile','wrong'),('source_SHA','0'*64),('num_envs',128),('new_entry_pose',False),('new_BODY_direction_identity',False),('Wave_inward_limit_m',3.),('Wave_seconds',20.),('new_RNG_draws',True),('live_heading_position_correction',True),('actual_GPU_fullrestore_verified',True)]:
   bad=copy.deepcopy(first);bad[field]=value;tests.append((field,lambda bad=bad:m.validate(bad,identity)))
  tests += [('wrong_identity',lambda:m.validate(first,dict(identity,entry_map_sha256='0'*64))),('same_episode_live_rebind',lambda:m.bind_selected_births(first,selected,episodes,identity)),('duplicate_reset_IDs',lambda:m.bind_selected_births(first,torch.tensor([0,0]),episodes+1,identity)),('wrong_quaternion_norm',lambda:m.rotate_birth_xyzw(q*2,flip))]
  for name,fn in tests:
   try:fn()
   except AssertionError:negatives.append(name)
   else:raise AssertionError('Bad scope admitted: '+name)
  assert digest(source)==before and H(p)==m.SOURCE and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
  report=dict(epoch=time.time(),passed_logical_CPU_proposal=True,source=dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),whole_tree_before_after_SHA=before),actual_saved_envs20000=True,actual_wave_birth_side_counts=counts,source_bindings=identity,old_actorcriticstdAdam_allD0D7_globalnamed_private_CPUCUDA_and_all_other_saved_fields_exact_unchanged=True,
   strict_old_fullstate_must_restore_before_declared_new_entry_direction=True,new_identity=dict(profile=m.PROFILE,new_geometry=False,new_entry_pose=True,new_BODY_direction_identity=True,new_world_route_or_lifetime=False),
   original_absolute_command_draws_and_standing20percent_unchanged=True,actual_saved_command_world_heading_product_exact=True,nonWave_and_standing_saved_commands_exact=True,no_live_heading_position_input_or_correction=True,no_new_RNG=True,selected_reset_nonselected_rows_exact=True,per_environment_birth_orientation_alternates_only_with_episode=True,
   current_family4_and_static_bornWave_masks_separate=True,current_source_command_phase_not_claimed_new_physics=True,
   actual80_saved_pose_xyzw_math_only=True,actual20k_native_root_ABI_NOT_verified=True,physical_all25200point_safe_Z_newreset_NOT_implemented_or_admitted=True,
   negative_cases_rejected=negatives,no_modified_or_new_policy_checkpoint=True,newproduction_worker_exists=False,new_target_ROOT_CPU_or_GPU_passed=False,SDK_native_fullrestore_PPO_or_budget_admitted=False,
   remaining=['Integrate independent Linux reset wrapper after original fullreset and strict source restore, verify actual native quaternion ABI before writing poses','Recompute original full collision-footprint safeZ and capture native setter/q30/XY readback, selected reset and all other fields actual exact; no cached ground fallback','Explicit new entry/direction metadata and own per-env state must be fullsaved/validated. World route/timing and production DR/reward/LR/clock/hardware unchanged. Original direction-audit BODY sign predicate must be independently versioned rather than bypassed','Actual histogram of BODY signs, WORLD signs and effective physical exposure; deterministic birth allocation does not claim50/50controltime','Own sourcefreeze/resource/budget/native/fullstate scoped admission before any first bounded repair PPO; not third duration-only old-axis block'],
   component_SHA=H(A/'wave50_birth_bodyframe_CPU_component_v1.py'),reader_SHA=H(__file__),Git_pending=True)
  out.write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode());print(json.dumps(dict(passed_CPU_only=True,source20k=m.SOURCE,birth_side_counts=counts,negative_cases=len(negatives),source_unchanged=True,GPU_or_PPO_admitted=False)))
 except BaseException:
  p=R/('BODYFRAME_LOGICAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_not_changed=True,no_GPU_PPO_or_budget=True),indent=2).encode());raise

if __name__=='__main__':main()
