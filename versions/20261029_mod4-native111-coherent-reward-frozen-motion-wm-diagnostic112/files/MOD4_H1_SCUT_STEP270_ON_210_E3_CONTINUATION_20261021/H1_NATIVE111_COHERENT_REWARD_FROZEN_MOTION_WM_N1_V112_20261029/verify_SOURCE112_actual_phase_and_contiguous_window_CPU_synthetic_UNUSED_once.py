from pathlib import Path
import hashlib,io,json,os,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;B=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27'
sys.path[:0]=[str(S/'code'),str(B/'source'),str(B/'source/sm_deps')]
def main():
 import torch
 from types import SimpleNamespace
 from fudan112_frozen_diag_driver_v1 import actual_phase_record,validate_actual_action_windows
 from supermimic_wheel_leg_v3.geometry import unflatten_state
 torch.set_num_threads(2);assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not torch.cuda.is_initialized()
 names=['left_wheel','right_wheel']+[str(i) for i in range(29)];last=dict(body_contact_force31=torch.zeros(31,3),root13_sdk_xyzw=torch.zeros(13),takeoff_count=0)
 last['root13_sdk_xyzw'][9]=.1;geom={'low':torch.tensor([[[0.,0.,.01],[0.,0.,.01]]])}
 a=actual_phase_record(last,geom,torch.tensor([200]),1,names);assert a['airborne_both_above5mm_and_unloaded'] and a['public_request_for_action']
 last['body_contact_force31'][:2,2]=2
 a=actual_phase_record(last,geom,torch.tensor([199]),1,names);assert not a['airborne_both_above5mm_and_unloaded'] and a['both_supported'] and not a['public_request_for_action']
 class WM:
  def step(self,state,action,context):
   p=state[0].clone();p[:,2]+=action[:,0]*.001;return (p,*state[1:])
 class MDP:
  def normalize_context(self,x):return x
  def wheel_geometry(self,state):
   low=state[0][:,None,:].expand(-1,2,-1).clone();low[:,:,2]-=.4;return dict(low=low)
 class Stream(io.StringIO):
  def close(self):pass
 class Sink:
  def __init__(self):self.stream=Stream()
  def __truediv__(self,name):return self
  def open(self,*a,**kw):return self.stream
 paired=[];phases=[]
 for i in range(40):
  s=torch.zeros(1,127);s[0,3]=1.;s[0,2]=.4+i*.001;s1=s.clone();s1[0,2]+=.001
  paired.append((s,torch.zeros(1,31),torch.ones(1,6),s1,torch.tensor([200+i]),torch.zeros(1,10,86),torch.zeros(1,6)))
  phases.append(dict(age_for_action=200+i,airborne_both_above5mm_and_unloaded=15<=i<22,both_supported=not(15<=i<22)))
 before=[x[0].clone() for x in paired];sink=Sink();validate_actual_action_windows(paired,phases,SimpleNamespace(mdp=MDP()),WM(),sink);v=json.loads(sink.stream.getvalue())
 assert {x['horizon'] for x in v['rows']}=={8,32} and any(x['grounded_start_then_air'] for x in v['rows']) and any(x['contains_air_to_supported'] for x in v['rows'])
 assert all(torch.equal(row[0],original) for row,original in zip(paired,before))
 error=max(abs(e) for row in v['rows'] for step in row['steps'] for e in step['wheel_bottom_abs_error2']);assert error<.00001
 broken=list(paired);x=list(broken[20]);x[4]=x[4]+2;broken[20]=tuple(x);sink2=Sink();validate_actual_action_windows(broken,phases,SimpleNamespace(mdp=MDP()),WM(),sink2);bad=json.loads(sink2.stream.getvalue());assert len(bad['rows'])<len(v['rows'])
 value=dict(passed_source_CPU_only=True,epoch=time.time(),synthetic_linear_dynamics_only=True,synthetic_phase_masks_only=True,helper_JSON_writes_captured_in_memory_not_saved_as_actual_case=True,actual_phase_geometry_force_request_boundary_checks=True,teacherforced8_32_closedform_max_abs_error=error,contiguous_windows=len(v['rows']),noncontiguous_windows_rejected=True,paired_input_states_literal_unchanged=True,actual_SDK_GPU_actor_WM_checkpoint_reads=0,not_actual108_case_or_skill=True)
 with (S/'reports/SOURCE108_PHASE_CONTIGUITY_8_32_CPU_SYNTHETIC_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 print(json.dumps(value))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (S/'reports'/('SOURCE108_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_actual_model_or_remote=True),f,indent=2)
  raise
