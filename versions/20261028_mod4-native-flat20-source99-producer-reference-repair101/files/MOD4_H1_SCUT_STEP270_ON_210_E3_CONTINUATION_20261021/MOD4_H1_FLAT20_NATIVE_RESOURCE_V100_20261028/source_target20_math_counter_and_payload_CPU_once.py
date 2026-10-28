from pathlib import Path
import json,sys,time,os,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();results={}
 for mode in ['seed27','seed28']:
  B=N/'payloads'/mode
  for name,m in list(sys.modules.items()):
   p=getattr(m,'__file__',None)
   if p and Path(p).is_relative_to(N/'payloads'):sys.modules.pop(name,None)
  sys.path[:]=[x for x in sys.path if not any(x==str(N/'payloads'/old/sub) for old in ['seed27','seed28'] for sub in ['.','source','source/sm_deps','job0/runtime/isaac/mod4'])]
  sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'job0/runtime/isaac/mod4')]
  from native_flat90_source_guard_v1 import check_payload
  payload=check_payload(B,verify_model_bytes=False)
  from native_flat_jump_adapter_v1 import OwnFlatJumpReference,encode_frame
  from flat95_task_focused_starts_v1 import focused_mask,CONTRACT
  from flat_real_physics_events_v3_original_support import FlatRealPhysicsEvents
  task=payload['task'];doc=json.loads((B/task['native_reference_relative']).read_bytes());provider=OwnFlatJumpReference(doc);ages=torch.tensor([200,220,241]);value,mask=provider.query(encode_frame(ages,torch.zeros(3,dtype=torch.long)));target=provider.phase.targets(ages,torch.zeros_like(ages))
  assert provider.phase.height_m==CONTRACT['height_m']==task['flat_jump_target_m']==.20 and abs(float(target['height'][1])-.20)<.00005
  assert (mask[:,13:73]==0).all() and value[1,2]>.58 and provider.phase.targets(ages,torch.zeros_like(ages))['nominal_flight_s']>.40
  assert focused_mask(torch.tensor([180,200,240])).all() and not focused_mask(torch.tensor([179,241,500])).any()
  counter=FlatRealPhysicsEvents(2,height_m=.20);tick=0
  def physical(flight,request):
   nonlocal tick
   tick+=1
   return counter.physical(physics_tick=tick,request=torch.full((2,),request,dtype=torch.bool),wheel_bottom_m=torch.tensor([[.06,.06],[.201,.201]]) if flight else torch.zeros(2,2),wheel_N=torch.zeros(2,2) if flight else torch.full((2,2),5.),wheel_floor_support=torch.full((2,2),not flight,dtype=torch.bool),floor_basis_valid=torch.ones(2,dtype=torch.bool),all_min_clear_m=torch.full((2,),.05) if flight else torch.zeros(2),nonwheel_max_N=torch.zeros(2),root_vz=torch.full((2,),.3) if flight else torch.zeros(2),root_planar_speed=torch.zeros(2),roll=torch.zeros(2),pitch=torch.zeros(2),yaw=torch.zeros(2))
  physical(False,False);physical(False,False)
  for _ in range(25):physical(True,True)
  for _ in range(220):physical(False,False)
  snap=counter.snapshot();assert snap['lifetime']['takeoffs']==2 and snap['lifetime']['height_met']==1 and snap['lifetime']['landings']==1 and snap['lifetime']['recoveries']==1 and snap['per_env_lifetime']['recoveries']==[0,1]
  results[mode]=dict(passed=True,source_inventory_passed_no_model_bytes_read=True,physical_initial_seed=task['native_seed'],saved_learning_seed=task['native_learning_seed'],target_m=.20,body_apex_cue_m=float(value[1,2]),analytic_apex_clearance_m=float(target['height'][1]),nominal_ballistic_flight_s=target['nominal_flight_s'],six_cm_rejected_as_twenty_cm=True,twenty_cm_landing200stable_source_trace_credited=True,synthetic_source_trace_not_physics_or_learned_success=True)
 assert not torch.cuda.is_initialized()
 with (R/'TARGET20_MATH_REALCOUNTER_AND_EXACT_PAYLOAD_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,epoch=time.time(),results=results,no_saved_model_actor_WM_forward_GPU_SDK_or_remote=True,actual_target_source_CPU_and_GO_pending=True),f,indent=2)
 print(json.dumps(dict(passed=True,target20_source_CPU=True,not_training=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'TARGET20_LOCAL_SOURCE_CPU_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_model_read=True),f,indent=2)
  raise
