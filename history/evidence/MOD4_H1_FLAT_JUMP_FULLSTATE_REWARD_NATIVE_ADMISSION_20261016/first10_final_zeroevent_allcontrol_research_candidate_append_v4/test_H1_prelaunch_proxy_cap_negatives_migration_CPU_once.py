"""CPU candidate only: preserve original event truth and prevent unbounded shaping."""
from pathlib import Path
import os,sys,json,time,io,copy
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;sys.path[:0]=[str(D),str(D/'payload'),str(D/'payload/job0/runtime/isaac/mod4')]
from h1_public_request_phase_v1 import H1PublicRequestPhase
from h1_takeoff_progress_phase_v2_candidate import H1TakeoffProgressPhaseV2,EXTRA
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq
torch.set_num_threads(2)
def args(n=8,vz=0.,support=True):
 return dict(wheel_N=torch.full((n,2),10. if support else 0.),wheel_clear_m=torch.full((n,2),0. if support else .03),all_min_clear_m=torch.full((n,),0. if support else .03),nonwheel_max_N=torch.zeros(n),root_vz=torch.full((n,),float(vz)),root_planar_speed=torch.zeros(n),roll=torch.zeros(n),pitch=torch.zeros(n),yaw=torch.zeros(n))
def prepare(p,old):
 for _ in range(100):
  p.begin_control();old.begin_control()
  for __ in range(4):
   a=p.physical(**args());b=old.physical(**args());assert eq(a['event_delta'],b['event_delta']) and not p.progress_control.any()
  p.finish_control_before_selected_reset();old.finish_control_before_selected_reset()
 assert p.ready.all() and torch.equal(p.public_mode(),old.public_mode())
def main():
 report=D/'reports/H1_PRELAUNCH_PROXY_V2_CAP_NEGATIVES_MIGRATION_CPU_ACTUAL.json';assert not report.exists();rng=torch.get_rng_state().clone();p=H1TakeoffProgressPhaseV2(8,'cpu');old=H1PublicRequestPhase(8,'cpu');prepare(p,old);p.begin_control();old.begin_control();total=torch.zeros(8)
 for speed in (.1,.2,.5,2.,.1,2.,0.,2.):
  a=p.physical(**args(vz=speed));b=old.physical(**args(vz=speed));total+=a['prelaunch_proxy_delta'];assert eq(a['event_delta'],b['event_delta']) and (total<=.500001).all() and not p.launched.any()
 assert torch.allclose(total,torch.full((8,),.5)) and not p.event_control.any()
 for _ in range(16):a=p.physical(**args(vz=.3,support=False));b=old.physical(**args(vz=.3,support=False));assert eq(a['event_delta'],b['event_delta']) and not a['prelaunch_proxy_delta'].any()
 for _ in range(212):a=p.physical(**args());b=old.physical(**args());assert eq(a['event_delta'],b['event_delta'])
 assert p.takeoff_count.eq(1).all() and p.landing_count.eq(1).all() and p.recovery_count.eq(1).all();saved=p.state_dict();buf=io.BytesIO();torch.save(saved,buf);buf.seek(0);clone=H1TakeoffProgressPhaseV2(8,'cpu');clone.load_state_dict(torch.load(buf,map_location='cpu',weights_only=False));assert eq(clone.state_dict(),saved);keep=torch.ones(8,dtype=torch.bool);keep[[1,4]]=False;clone.reset(torch.tensor([1,4]));assert all(torch.equal(v[keep],saved['tensors'][k][keep]) and not v[~keep].any() for k,v in clone.tensors().items())
 migrate=H1TakeoffProgressPhaseV2(8,'cpu');migrate.load_state_dict(old.state_dict());assert all(eq(migrate.tensors()[k],v) for k,v in old.tensors().items()) and all(not migrate.tensors()[k].any() for k in EXTRA)
 negative=0
 for case in ('not_prepared','no_public_request','unsupported','nonwheel_contact','penetrating','tilted','horizontal_motion','downward','already_launched'):
  x=H1TakeoffProgressPhaseV2(8,'cpu');x.age_control.fill_(100);x.ready.fill_(True)
  if case=='not_prepared':x.ready.zero_()
  if case=='no_public_request':x.age_control.zero_()
  x.begin_control();kw=args(vz=.5)
  if case=='unsupported':kw['wheel_N'].zero_()
  if case=='nonwheel_contact':kw['nonwheel_max_N'].fill_(2.)
  if case=='penetrating':kw['all_min_clear_m'].fill_(-.002)
  if case=='tilted':kw['roll'].fill_(.5)
  if case=='horizontal_motion':kw['root_planar_speed'].fill_(1.)
  if case=='downward':kw['root_vz'].fill_(-1.)
  if case=='already_launched':x.launched.fill_(True)
  mode=x.public_mode().clone();out=x.physical(**kw);assert not out['prelaunch_proxy_delta'].any() and torch.equal(mode,x.public_mode()),case;negative+=1
 bad=copy.deepcopy(saved);bad['tensors']['progress_peak'].fill_(float('nan'))
 try:clone.load_state_dict(bad)
 except AssertionError:negative+=1
 else:raise AssertionError('Nonfinite phase source accepted')
 assert not torch.cuda.is_initialized() and torch.equal(rng,torch.get_rng_state());r=dict(epoch=time.time(),passed_CPU_candidate_only=True,original_takeoff_landing_recovery_event_deltas_exact=True,original_strict_air16_landing12_recovery200_callbacks_unchanged=True,bounded_prelaunch_proxy_credit_per_attempt=.5,no_cycle_hover_oscillation_credit_farming=True,pre_request_reset_rebound_credit0=True,rejected_negative_cases=negative,selectedreset_other_rows_exact=True,new_V2_phase_CPU_disk_roundtrip_exact=True,original_V1_phase_all_typed_fields_migrated_literal_exact_three_new_fields0=True,no_actor_mode_action_force_reset_or_RNG_mutation=True,global_CPU_RNG_unchanged_0CUDA0optimizer=True,not_actual_SDK_native_or_new_PPO_pass=True)
 report.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r))
if __name__=='__main__':main()
