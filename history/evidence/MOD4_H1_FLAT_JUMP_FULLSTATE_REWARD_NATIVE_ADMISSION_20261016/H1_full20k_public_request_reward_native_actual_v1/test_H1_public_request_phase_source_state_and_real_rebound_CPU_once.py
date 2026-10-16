"""CPU candidate fixtures and existing real data rejection; not actual new native/PPO."""
from pathlib import Path
import torch,numpy as np,json,hashlib,time
from h1_public_request_phase_v1 import H1PublicRequestPhase,PROFILE
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016';R=D/'reports';R.mkdir(exist_ok=True)
def inputs(n=4):return dict(wheel_N=torch.full((n,2),5.),wheel_clear_m=torch.zeros((n,2)),all_min_clear_m=torch.zeros(n),nonwheel_max_N=torch.zeros(n),root_vz=torch.zeros(n),root_planar_speed=torch.zeros(n),roll=torch.zeros(n),pitch=torch.zeros(n),yaw=torch.full((n,),.27))
def main():
 rng=torch.get_rng_state().clone();p=H1PublicRequestPhase(4,'cpu');v=inputs();reward=torch.zeros(4)
 for i in range(100):
  assert not p.public_request().any();p.begin_control()
  for _ in range(4):reward+=p.physical(**v)['event_delta']
  p.finish_control_before_selected_reset()
 assert p.ready.all() and p.public_request().all() and not reward.any()
 p.begin_control();assert p.attempt.all();v['root_vz'].fill_(.1)
 for _ in range(4):reward+=p.physical(**v)['event_delta']
 p.finish_control_before_selected_reset();v['wheel_N'].zero_();v['wheel_clear_m'].fill_(.03);v['all_min_clear_m'].fill_(.03)
 for _ in range(4):
  p.begin_control()
  for _ in range(4):reward+=p.physical(**v)['event_delta']
  p.finish_control_before_selected_reset()
 assert p.launched.all() and (p.takeoff_count==1).all()
 v=inputs()
 for _ in range(53):
  p.begin_control()
  for _ in range(4):reward+=p.physical(**v)['event_delta']
  p.finish_control_before_selected_reset()
 assert p.landed.all() and p.recovered.all() and torch.equal(reward,torch.full((4,),7.))
 saved=p.state_dict();torch.save(saved,D/'H1_CPU_ONLY_SYNTHETIC_PHASE_ROUNDTRIP.pt');q=H1PublicRequestPhase(4,'cpu');q.load_state_dict(torch.load(D/'H1_CPU_ONLY_SYNTHETIC_PHASE_ROUNDTRIP.pt',map_location='cpu',weights_only=False));assert all(torch.equal(q.tensors()[k],x) for k,x in p.tensors().items());q.reset(torch.tensor([1,3]));assert all(torch.equal(q.tensors()[k][[0,2]],x[[0,2]]) and not q.tensors()[k][[1,3]].any() for k,x in p.tensors().items())
 # Contact truth must not choose the operator mode: identical clocks, different evidence.
 a=H1PublicRequestPhase(4,'cpu');b=H1PublicRequestPhase(4,'cpu');u=inputs();bad=inputs();bad['wheel_N'].zero_();bad['all_min_clear_m'].fill_(-.1)
 for i in range(240):
  assert torch.equal(a.public_mode(),b.public_mode());a.begin_control();b.begin_control()
  for _ in range(4):a.physical(**u);b.physical(**bad)
  a.finish_control_before_selected_reset();b.finish_control_before_selected_reset()
 assert not b.launched.any()
 # Actual corrected zero/default-PD motor calibration, all raw rows reused only on CPU.
 c=json.loads((OLD/'reports/H1_XYZW_FULLPOSE_COMPLETE_ACTUAL_BOUND_COLLECTION.json').read_bytes());ref=next(x['value'] for x in c['files'] if x['path'].endswith('/ACTUAL_AUTHORED_ALL_COLLIDER_REFERENCE.json'));non=[i for i,n in enumerate(ref['actual_contact_view_body_names']) if n not in ('left_wheel','right_wheel')];p=H1PublicRequestPhase(80,'cpu');last=None;rows=0;event=0.
 for r in c['complete_local_raw']:
  if not Path(r['path']).name.startswith('physics_'):continue
  with np.load(r['path'],allow_pickle=False) as z:
   for i in range(len(z['tick'])):
    ep=z['episode'][i];done=np.zeros(80,bool) if last is None else ep!=last;last=ep.copy();p.reset(torch.from_numpy(np.flatnonzero(done)));root=z['root13'][i]
    if rows%4==0:p.begin_control()
    v=dict(wheel_N=torch.from_numpy(np.linalg.norm(z['wheel_5ms_mean_force'][i],axis=-1)),wheel_clear_m=torch.from_numpy(z['wheel_clearance'][i]),all_min_clear_m=torch.from_numpy(z['all_shape_clearance'][i].min(-1)),nonwheel_max_N=torch.from_numpy(np.linalg.norm(z['all_body_contact_force'][i][:,non],axis=-1).max(-1)),root_vz=torch.from_numpy(root[:,9]),root_planar_speed=torch.from_numpy(np.linalg.norm(root[:,7:9],axis=-1)),roll=torch.from_numpy(z['roll'][i]),pitch=torch.from_numpy(z['pitch'][i]),yaw=torch.from_numpy(z['yaw'][i]));o=p.physical(**v);event+=float(o['event_delta'].sum());rows+=1
    if rows%4==0:p.finish_control_before_selected_reset()
 assert rows==896 and event==0 and not p.launched.any() and torch.equal(rng,torch.get_rng_state())
 report=dict(epoch=time.time(),passed_CPU_only=True,new_scope='H1 full20k external normal→jump→normal request with source actor',profile=PROFILE,actual_new_GPU_native_or_PPO=False,synthetic_fullcycle_reward_cap7=True,public_request_contact_truth_invariant=True,selectedreset_other_rows_exact=True,phase_CPU_diskroundtrip_literal_exact=True,zero_request_or_unknown_support_no_takeoff=True,real_corrected896_callbacks_reset_default_PD_rebound_reward0=True,actual_rebound_rows=rows,global_CPU_RNG_not_advanced=True,CUDA_optimizer_calls0=True,preparation_200ms_vz_point2_not_previous_unapproved500ms_point03_gate=True,recovery_500ms_point03_is_reward_bonus_not_training_release_line=True,yaw_reference='Own first physical episode yaw, zero yaw-rate command; not world heading correction or actor input',all_old_failed_observer_raw_and_false_reports_preserved=True)
 (R/'H1_PUBLIC_REQUEST_PHASE_FULLCYCLE_SAVE_RESET_AND_REAL_REBOUND_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_only=True,real_rebound_event_reward=event,source_future_GPU_unclaimed=True)),flush=True)
if __name__=='__main__':main()
