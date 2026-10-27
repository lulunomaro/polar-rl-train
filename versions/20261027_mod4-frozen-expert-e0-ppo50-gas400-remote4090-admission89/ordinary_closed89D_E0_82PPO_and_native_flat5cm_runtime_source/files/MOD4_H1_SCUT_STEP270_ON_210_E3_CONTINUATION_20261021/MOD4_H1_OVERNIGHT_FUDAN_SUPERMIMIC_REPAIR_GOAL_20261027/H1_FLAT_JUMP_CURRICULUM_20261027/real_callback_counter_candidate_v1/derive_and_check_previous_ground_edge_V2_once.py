"""Preserve V1; minimal same-episode previous-floor witness for request-air edge."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 old=HERE/'flat_real_physics_events_v1.py';new=HERE/'flat_real_physics_events_v2.py';assert not new.exists()
 before=old.read_text('utf8');assert H(old)=='aa27da21284af05de5a406e438b762330c8788d67e2653486434e5a64bdf7399'
 replacements=[
  ("'credited','previous_request','attempt_invalid'):","'credited','previous_request','attempt_invalid','previous_ground'):") ,
  ('self._clear(ids);self.previous_request[ids]=False','self._clear(ids);self.previous_request[ids]=False;self.previous_ground[ids]=False'),
  ('  self._clear(fresh);self.active|=fresh;', '  ground_before=self.previous_ground&fresh\n  self._clear(fresh);self.active|=fresh;'),
  ('  self.seen_ground|=eligible&floor&~self.had_takeoff','  self.seen_ground|=eligible&(floor|ground_before)&~self.had_takeoff\n  self.previous_ground.copy_(valid&floor)')]
 after=before
 for a,b in replacements:assert after.count(a)==1;after=after.replace(a,b,1)
 inverse=after
 for a,b in reversed(replacements):assert inverse.count(b)==1;inverse=inverse.replace(b,a,1)
 assert inverse==before;new.write_bytes(after.encode());ast.parse(after)
 import torch
 rng=torch.get_rng_state().clone();spec=importlib.util.spec_from_file_location('flat_real_V2_edge',new);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 c=m.FlatRealPhysicsEvents(2);tick=0
 def row(ground,request):
  nonlocal tick
  tick+=1;support=torch.full((2,2),ground,dtype=torch.bool);support[1]=False
  return dict(physics_tick=tick,request=torch.full((2,),request,dtype=torch.bool),wheel_bottom_m=torch.full((2,2),0. if ground else .06),
   wheel_N=torch.full((2,2),10. if ground else 0.),wheel_floor_support=support,floor_basis_valid=torch.ones(2,dtype=torch.bool),
   all_min_clear_m=torch.full((2,),0. if ground else .02),nonwheel_max_N=torch.zeros(2),root_vz=torch.full((2,),0. if ground else .3),
   root_planar_speed=torch.zeros(2),roll=torch.zeros(2),pitch=torch.zeros(2),yaw=torch.zeros(2))
 c.physical(**row(True,False))
 assert c.previous_ground.tolist()==[True,False] and not c.active.any() and not c.credited.any()
 # First requested callback is already airborne. Only actual preceding support arms.
 for _ in range(16):c.physical(**row(False,True))
 assert c.had_takeoff.tolist()==c.height_met.tolist()==[True,False]
 for _ in range(211):c.physical(**row(True,True))
 assert c.lifetime['recoveries'].tolist()==[1,0]
 c.reset(torch.tensor([0]));assert not c.previous_ground[0] and not c.credited[0] and c.lifetime['recoveries'][0]==1
 for _ in range(16):c.physical(**row(False,True))
 assert not c.had_takeoff[0] and not c.height_met[0] and c.lifetime['recoveries'][0]==1
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 p=HERE/'PREVIOUS_GROUND_REQUEST_EDGE_V2_CPU_ACTUAL.json'
 with p.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,V1_SHA=H(old),V2_SHA=H(new),
  exact_inverse_V1_bytes=True,only_four_source_replacements=replacements,
  prior_same_episode_floor_support_can_arm_request_first_callback_air=True,unseen_ground_env_cannot_credit=True,
  selected_reset_clears_previous_ground_but_preserves_lifetime=True,first_standing_callback_never_credits=True,
  V1_other_behavior_fixtures_not_reexecuted=True,no_PT_Actor_SDK_GPU_remote_or_ledger=True,actual_native_pending=True),f,indent=2)
 print(json.dumps(dict(passed=True,V2_SHA=H(new),report_SHA=H(p),only_new_boundary_tiny_CPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=HERE/('V2_EDGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
