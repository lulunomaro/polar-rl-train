"""Tiny synthetic event/hook lifecycle, not a native scene or skill result."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,json,os,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
from flat_real_physics_events_v1 import FlatRealPhysicsEvents,install_readonly_phase_hook,make_authored_preedge_cached_provider
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 report=HERE/'FLAT_REAL_CALLBACK_TINY_CPU_ACTUAL_V1.json';assert not report.exists()
 rng=torch.get_rng_state().clone();n=4;c=FlatRealPhysicsEvents(n);tick=0
 def frame(*,request=True,bottom=.0,force=10.,support=True,qualified=True,vz=0.):
  nonlocal tick
  tick+=1
  return dict(physics_tick=tick,request=torch.full((n,),request,dtype=torch.bool),wheel_bottom_m=torch.full((n,2),bottom),
   wheel_N=torch.full((n,2),force),wheel_floor_support=torch.full((n,2),support,dtype=torch.bool),
   floor_basis_valid=torch.full((n,),qualified,dtype=torch.bool),all_min_clear_m=torch.full((n,),min(bottom,.02)),
   nonwheel_max_N=torch.zeros(n),root_vz=torch.full((n,),vz),root_planar_speed=torch.zeros(n),roll=torch.zeros(n),pitch=torch.zeros(n),yaw=torch.zeros(n))
 for _ in range(250):c.physical(**frame())
 assert int(c.lifetime['recoveries'].sum())==0 and not c.had_takeoff.any()
 # A new real request starts a new attempt and cannot inherit standing time.
 c.physical(**frame(request=False));c.physical(**frame())
 for _ in range(16):c.physical(**frame(bottom=.06,force=0.,support=False,vz=.3))
 assert c.had_takeoff.all() and c.height_met.all()
 for _ in range(12):c.physical(**frame())
 assert c.landed.all() and (c.stable_ticks==1).all()
 for _ in range(198):c.physical(**frame())
 assert (c.stable_ticks==199).all() and int(c.lifetime['recoveries'].sum())==0
 c.physical(**frame());assert (c.stable_ticks==200).all() and (c.lifetime['recoveries']==1).all()
 for _ in range(5):c.physical(**frame())
 assert (c.lifetime['recoveries']==1).all()
 c.physical(**frame(request=False));c.physical(**frame())
 assert not c.had_takeoff.any() and not c.height_met.any() and not c.credited.any() and not c.stable_ticks.any()
 # COM/root velocity and only one high wheel do not satisfy both-wheel height.
 for _ in range(16):c.physical(**frame(bottom=.02,force=0.,support=False,vz=.5))
 one=frame(bottom=.06,force=0.,support=False,vz=.5);one['wheel_bottom_m'][:,1]=.049;c.physical(**one)
 for _ in range(230):c.physical(**frame())
 assert not c.height_met.any() and (c.lifetime['recoveries']==1).all()
 before={k:v.clone() for k,v in c.lifetime.items()};c.reset(torch.tensor([0,2]))
 assert torch.equal(before['recoveries'],c.lifetime['recoveries']) and c.reset_generation.tolist()==[1,0,1,0]
 assert not c.active[[0,2]].any() and c.active[[1,3]].all()
 # Unqualified floor identity cannot provide a recovery or even trusted ground.
 d=FlatRealPhysicsEvents(n);tick=0
 for _ in range(230):d.physical(**frame(qualified=False))
 assert not d.seen_ground.any() and not d.credited.any() and d.attempt_invalid.all()
 # Hook preserves original invocation/result/errors and reset ordering.
 calls=[];result=object();p=SimpleNamespace(n=n,device='cpu',request_for_action=torch.ones(n,dtype=torch.bool))
 def original(**kw):calls.append(('physical',kw));return result
 def reset(ids):calls.append(('reset',ids));return result
 p.physical=original;p.reset=reset;tick=0
 def provider(phase,kw):
  calls.append(('provider',kw));return frame()
 hooked=install_readonly_phase_hook(p,provider)
 value=torch.arange(n);assert p.physical(original_input=value) is result
 assert calls[0][0]=='physical' and calls[1][0]=='provider' and calls[0][1]['original_input'] is value
 ids=torch.tensor([1]);assert p.reset(ids) is result and calls[-1]==('reset',ids) and hooked.reset_generation.tolist()==[0,1,0,0]
 def failure(**kw):raise RuntimeError('SYNTHETIC_ORIGINAL_PHYSICAL_ERROR')
 broken=SimpleNamespace(n=n,device='cpu',request_for_action=p.request_for_action,physical=failure,reset=reset)
 bc=install_readonly_phase_hook(broken,provider)
 try:broken.physical()
 except RuntimeError as e:assert str(e)=='SYNTHETIC_ORIGINAL_PHYSICAL_ERROR'
 else:raise AssertionError('Original error swallowed')
 assert bc.callback_rows==0 and not bc.diagnostic_errors
 # Diagnostic provider error is recorded without replacing the original result.
 bad=SimpleNamespace(n=n,device='cpu',request_for_action=p.request_for_action,physical=original,reset=reset)
 def missing(*a):raise KeyError('SYNTHETIC_MISSING_FLOOR_BASIS')
 badc=install_readonly_phase_hook(bad,missing);assert bad.physical() is result and badc.diagnostic_errors
 # Reuse the exact cached signedFz/query-face/preedge interface; no query method.
 origins=torch.zeros(n,3);lo=torch.zeros(n,2,3);hi=torch.zeros(n,2,3);lo[:,:,:2]=-.1;hi[:,:,:2]=.1
 history=torch.zeros(n,3,2,3);history[:,0,:,2]=10.
 env=SimpleNamespace(scene=SimpleNamespace(env_origins=origins),_integrated_contact=SimpleNamespace(history=history),h1_callback_count=0,
  step270_geometry_receipt=dict(geometry=dict(height=.270,edge_x=.35,depth=.8,width=1.2),actual_stage_ordered_triangle_SHA='SYNTHETIC'+'0'*55))
 floor_phase=SimpleNamespace(env=env,request_for_action=torch.ones(n,dtype=torch.bool),last_measured=dict(step_wheel_min=lo,step_wheel_max=hi,
  step_query_face=torch.zeros(n,2,dtype=torch.long),step_query_height=torch.zeros(n,2)))
 provider=make_authored_preedge_cached_provider(floor_phase);kw={k:v for k,v in frame().items() if k in ('wheel_N','all_min_clear_m','nonwheel_max_N','root_vz','root_planar_speed','roll','pitch','yaw')};kw['wheel_clear_m']=torch.zeros(n,2)
 assert provider(floor_phase,kw)['wheel_floor_support'].all()
 history[0,0,0,2]=0.;floor_phase.last_measured['step_query_face'][1,0]=2;hi[2,0,0]=.35
 support=provider(floor_phase,kw)
 assert not support['wheel_floor_support'][0,0] and not support['floor_basis_valid'][1] and not support['floor_basis_valid'][2]
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 source=HERE/'flat_real_physics_events_v1.py';ast.parse(source.read_bytes())
 value=dict(epoch=time.time(),passed=True,source=dict(path=str(source),SHA=H(source)),synthetic_envs=n,
  standing_no_credit=True,real_takeoff_then_both_height_then_landing_then_200_stable_required=True,
  stable199_rejected_200_credited=True,one_wheel_or_root_COM_velocity_no_height_credit=True,
  new_attempt_credit_cleared=True,selected_reset_keeps_lifetime_and_only_clears_selected=True,
  unqualified_floor_basis_no_credit=True,original_result_object_input_RNG_error_and_reset_order_preserved=True,
  authored_preedge_cached_force_face_and_full_footprint_provider_positive_and_negatives=True,
  signed_Fz_is_5ms_mean_not_instantaneous_manifold=True,
  diagnostic_failure_nonblocking_and_saved=True,no_new_queries_Actor_SDK_GPU_remote_PT_or_ledger=True,
  actual_floor_scene_admission_provider_and_native_integration_pending=True,not_actual_jump_or_skill_result=True,
  original_reader_errors=[dict(tool_chunk='3f363c',error='rg guessed nonexistent h1_step270_phase_runtime_candidate.py; actual phase is Step270Phase in h1_step270_sdk_runtime_candidate.py.'),
   dict(tool_chunk='c85b4e',error='Get-Content optional nonexistent h1_collider_clearance.py returned1; actual source h1_authored_full_collider_plane_reference_v1.py located and read.')],
  Git_status='ordinary_supplement_pending_root')
 with report.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 print(json.dumps(dict(passed=True,report=str(report),SHA=H(report),source_SHA=H(source),actual_native_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=HERE/('TINY_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(traceback=traceback.format_exc(),no_actual_native_or_GPU=True),indent=2),encoding='utf8');raise
