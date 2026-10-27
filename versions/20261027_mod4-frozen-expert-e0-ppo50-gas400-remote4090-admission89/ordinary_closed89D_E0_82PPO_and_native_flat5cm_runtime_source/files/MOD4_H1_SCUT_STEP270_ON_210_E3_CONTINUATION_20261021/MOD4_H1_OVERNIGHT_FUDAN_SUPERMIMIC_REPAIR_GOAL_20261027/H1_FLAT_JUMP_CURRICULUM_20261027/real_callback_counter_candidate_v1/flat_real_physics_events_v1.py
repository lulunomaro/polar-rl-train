"""Independent flat-jump diagnostics from existing real physics callback tensors.

No actor, force, query, RNG, reward, reset, geometry or old270 goal modification.
Support truth is supplied by an admitted floor/contact provider, never an AABB.
"""
import math
import torch

class FlatRealPhysicsEvents:
 def __init__(self,n,device='cpu',height_m=.05):
  assert n>0 and height_m in (.05,.10,.20,.27)
  self.n=n;self.height_m=height_m;self.physics_dt_s=.0025;self.last_tick=None;self.callback_rows=0;self.tick_errors=0
  self.diagnostic_errors={}
  for k in ('attempt_generation','reset_generation','stable_ticks','air_ticks','landing_ticks'):
   setattr(self,k,torch.zeros(n,dtype=torch.long,device=device))
  for k in ('active','seen_ground','positive_vz','had_takeoff','height_met','landed','credited','previous_request','attempt_invalid'):
   setattr(self,k,torch.zeros(n,dtype=torch.bool,device=device))
  self.yaw_reference=torch.zeros(n,device=device)
  self.lifetime={k:torch.zeros(n,dtype=torch.long,device=device) for k in ('attempts','takeoffs','height_met','landings','recoveries','selected_resets','reset_censored_attempts','invalid_env_callbacks')}
 def _clear(self,mask):
  for k in ('active','seen_ground','positive_vz','had_takeoff','height_met','landed','credited','attempt_invalid'):
   getattr(self,k)[mask]=False
  for k in ('stable_ticks','air_ticks','landing_ticks'):getattr(self,k)[mask]=0
  self.yaw_reference[mask]=0
 def reset(self,ids):
  # Lifetime events are incremented at physics time and survive selected reset.
  self.lifetime['reset_censored_attempts'][ids]+=(self.active[ids]&~self.credited[ids]).long()
  self.lifetime['selected_resets'][ids]+=1;self.reset_generation[ids]+=1
  self._clear(ids);self.previous_request[ids]=False
 def note_error(self,error):
  key=type(error).__name__+': '+str(error);self.diagnostic_errors[key]=self.diagnostic_errors.get(key,0)+1
  self.attempt_invalid|=self.active;self.stable_ticks.zero_()
 def physical(self,*,physics_tick,request,wheel_bottom_m,wheel_N,wheel_floor_support,
              floor_basis_valid,all_min_clear_m,nonwheel_max_N,root_vz,
              root_planar_speed,roll,pitch,yaw,attempt_start=None):
  assert type(physics_tick)is int and physics_tick>=1
  vectors=(request,floor_basis_valid,all_min_clear_m,nonwheel_max_N,root_vz,root_planar_speed,roll,pitch,yaw)
  assert all(x.shape==(self.n,) for x in vectors)
  assert wheel_bottom_m.shape==wheel_N.shape==wheel_floor_support.shape==(self.n,2)
  assert request.dtype==floor_basis_valid.dtype==wheel_floor_support.dtype==torch.bool
  if self.last_tick is not None and physics_tick!=self.last_tick+1:
   self.tick_errors+=1;self.attempt_invalid|=self.active;self.stable_ticks.zero_()
  self.last_tick=physics_tick;self.callback_rows+=1
  fresh=(request&~self.previous_request) if attempt_start is None else attempt_start
  assert fresh.shape==(self.n,) and fresh.dtype==torch.bool
  self._clear(fresh);self.active|=fresh;self.attempt_generation+=fresh.long();self.lifetime['attempts']+=fresh.long()
  self.yaw_reference=torch.where(fresh,yaw,self.yaw_reference);self.previous_request.copy_(request)
  finite=torch.isfinite(wheel_bottom_m).all(-1)&torch.isfinite(wheel_N).all(-1)
  for x in vectors[2:]:finite&=torch.isfinite(x)
  valid=finite&floor_basis_valid
  self.lifetime['invalid_env_callbacks']+=(~valid).long();self.attempt_invalid|=self.active&~valid
  eligible=self.active&~self.attempt_invalid&valid
  clean=nonwheel_max_N<=1.
  floor=wheel_floor_support.all(-1)&clean&(all_min_clear_m>=-.001)
  self.seen_ground|=eligible&floor&~self.had_takeoff
  self.positive_vz|=eligible&(root_vz>.05)
  airborne=(wheel_N<=1.).all(-1)&(wheel_bottom_m>.005).all(-1)&(all_min_clear_m>0)&clean
  air=eligible&self.seen_ground&self.positive_vz&airborne
  self.air_ticks=torch.where(air,self.air_ticks+1,0)
  takeoff=air&(self.air_ticks>=16)&~self.had_takeoff;self.had_takeoff|=takeoff
  height=eligible&self.had_takeoff&airborne&(wheel_bottom_m>=self.height_m).all(-1)&~self.height_met
  self.height_met|=height
  self.landing_ticks=torch.where(eligible&self.had_takeoff&self.height_met&floor,self.landing_ticks+1,0)
  landing=(self.landing_ticks>=12)&~self.landed;self.landed|=landing
  dyaw=torch.atan2(torch.sin(yaw-self.yaw_reference),torch.cos(yaw-self.yaw_reference))
  stable=eligible&self.landed&floor&(root_vz.abs()<=.03)&(root_planar_speed<=.03)&(roll.abs()<math.radians(10))&(pitch.abs()<math.radians(10))&(dyaw.abs()<.2)
  self.stable_ticks=torch.where(stable,self.stable_ticks+1,0)
  recovery=(self.stable_ticks>=200)&~self.credited;self.credited|=recovery
  for k,event in (('takeoffs',takeoff),('height_met',height),('landings',landing),('recoveries',recovery)):self.lifetime[k]+=event.long()
  return dict(takeoff=takeoff,height_met=height,landing=landing,recovery=recovery)
 def snapshot(self):
  # Invoke only at normal report/save boundaries, not at each GPU callback.
  return dict(schema='mod4.flat_jump.real_physics_event_diagnostic.v1',height_m=self.height_m,physics_dt_s=self.physics_dt_s,
   callbacks=self.callback_rows,last_physics_tick=self.last_tick,tick_errors=self.tick_errors,
   lifetime={k:int(v.sum().detach().cpu()) for k,v in self.lifetime.items()},
   per_env_lifetime={k:v.detach().cpu().tolist() for k,v in self.lifetime.items()},
   diagnostic_errors=dict(self.diagnostic_errors),stable_required_callbacks=200,stable_required_s=.5,
   takeoff_callbacks=16,landing_callbacks=12,attempt_credit_cleared_on_new_attempt=True,
   lifetime_events_survive_selected_reset=True,not_270_goal_or_reward_or_skill_promotion=True)

def install_readonly_phase_hook(phase,cache_provider,*,height_m=.05):
 """Call old physical/reset once; provider reads only same-tick existing caches.

 cache_provider(phase, kw) -> physical() kwargs excluding request by default.
 It must provide qualified floor_basis_valid and true wheel_floor_support.
 It may not cast/query, fetch forces, run actor/FK, sample RNG or step physics.
 """
 assert not hasattr(phase,'_flat_real_physics_counter')
 counter=FlatRealPhysicsEvents(phase.n,phase.device,height_m);old_physical=phase.physical;old_reset=phase.reset
 def physical(**kw):
  result=old_physical(**kw)  # Original errors and return object are untouched.
  try:
   sample=cache_provider(phase,kw)
   sample.setdefault('request',phase.request_for_action)
   counter.physical(**sample)
  except Exception as error:counter.note_error(error)  # Diagnostic cannot replace old execution.
  return result
 def reset(ids):
  result=old_reset(ids)  # Preserve original selected-reset ordering and error.
  try:counter.reset(ids)
  except Exception as error:counter.note_error(error)
  return result
 phase.physical=physical;phase.reset=reset;phase._flat_real_physics_counter=counter
 return counter

def admitted_plane_cached_provider(phase,kw,*,admission):
 """Optional zero-query provider for an actually admitted floor-only z=0 scene.

 A cached net force or wheel AABB alone cannot certify its contact surface.
 Root must supply the real one-time scene/collision-domain admission receipt.
 No contact-pair/face-manifold identity claim is made by this provider.
 """
 assert admission['actual_admitted_flat_floor_only_collision_domain'] is True
 assert admission['floor_z_m']==0. and len(admission['actual_scene_admission_receipt_SHA'])==64
 env=phase.env;bottom=kw['wheel_clear_m']
 # This is the existing 5ms contact cache already updated before the callback.
 wheel_up=env._integrated_contact.history[:,0,:,2]
 support=(wheel_up>1.)&(bottom>=-.001)&(bottom<=.001)
 return dict(physics_tick=env.h1_callback_count+1,wheel_bottom_m=bottom,wheel_N=kw['wheel_N'],
  wheel_floor_support=support,floor_basis_valid=torch.ones_like(phase.request_for_action),
  **{k:kw[k] for k in ('all_min_clear_m','nonwheel_max_N','root_vz','root_planar_speed','roll','pitch','yaw')})

def make_authored_preedge_cached_provider(phase):
 """Existing step scene: real floor-face ray + complete preedge footprint + Fz.

 The existing scene initializer already compares actual stage ordered triangles
 to the authored generator. That generator's first faces0,1 are floor z=0.
 AABB is used only for footprint/boundary position, not to invent face identity.
 SignedFz is the existing5ms contact mean, not an instantaneous manifold.
 """
 env=phase.env;receipt=env.step270_geometry_receipt;geometry=receipt['geometry']
 assert geometry==dict(height=.270,edge_x=.35,depth=.8,width=1.2)
 assert len(receipt['actual_stage_ordered_triangle_SHA'])==64
 origins=env.scene.env_origins
 floor_lower=origins[:,:2].amin(0)-2.5;floor_upper=origins[:,:2].amax(0)+2.5
 edge=origins[:,0,None]+geometry['edge_x']
 def provider(current,kw):
  assert current is phase
  cache=phase.last_measured;lo=cache['step_wheel_min'];hi=cache['step_wheel_max']
  face=cache['step_query_face'];height=cache['step_query_height'];bottom=kw['wheel_clear_m']
  # All these values were computed by the same original physical callback.
  floor_face=(face==0)|(face==1)
  on_floor_ray=floor_face&(height.abs()<=.001)
  complete_inside=((lo[:,:,:2]>=floor_lower)&(hi[:,:,:2]<=floor_upper)).all(-1)
  preedge=hi[:,:,0]<edge
  location=complete_inside&preedge&on_floor_ray
  signed_Fz_5ms=env._integrated_contact.history[:,0,:,2]
  support=location&(signed_Fz_5ms>1.)&(bottom>=-.001)&(bottom<=.001)
  return dict(physics_tick=env.h1_callback_count+1,wheel_bottom_m=bottom,wheel_N=kw['wheel_N'],
   wheel_floor_support=support,floor_basis_valid=location.all(-1),
   **{k:kw[k] for k in ('all_min_clear_m','nonwheel_max_N','root_vz','root_planar_speed','roll','pitch','yaw')})
 provider.floor_support_basis=dict(actual_scene_ordered_triangle_SHA=receipt['actual_stage_ordered_triangle_SHA'],
  authored_floor_face_ids=[0,1],authored_floor_z_m=0.,complete_wheel_footprint_before_edge=True,
  force_basis='existing integrated_contact.history[:,0,:,2] signedFz5ms mean >1N',
  instantaneous_contact_manifold_or_pair_ID_claimed=False,new_query_or_force_fetch=False)
 return provider
