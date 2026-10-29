from pathlib import Path
import os,json,time,sys
S=Path(__file__).resolve().parent;R=S/"reports";R.mkdir(exist_ok=True)
B=Path(json.loads((S/"PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json").read_bytes())["source_payload"]);sys.path[:0]=[str(S),str(B/"source")]
import torch
from actual_action_forward113_core_v1 import decode_records,evaluate_horizon,summary,valid_starts
from supermimic_wheel_leg_v3.geometry import unflatten_state
from compact_episode_static31_v1 import normalize_static31
def main():
 assert os.environ.get("CUDA_VISIBLE_DEVICES")==""
 torch.set_num_threads(2);assert not torch.cuda.is_initialized()
 n=384;rows=[];p=0.;last_v=0.
 neutral=[1.,.9]+[1.]*6+[0.]*3+[1.]*10+[1.]*2+[1.]*2+[1.]*2+[0.]*4
 assert torch.equal(normalize_static31(torch.tensor([neutral])),torch.zeros(1,31))
 for i in range(n):
  a=.3 if i%3==0 else -.15 if i%3==1 else .05
  s=[0.]*127;s[0]=p;s[3]=1.;s[7]=last_v
  t=s.copy();t[0]=p+a*.01;t[7]=a;p=t[0];last_v=a
  bit=float(i>=200);obs=[0.]*86;obs[-2]=bit;rel=[0.]*7;rel[5]=bit
  rows.append(dict(control=i+1,age_for_action=[i],packed_frame_for_action=i,actual_phase_record=dict(control=i+1,age_for_action=i,public_request_for_action=bool(bit)),task_relative_features7_for_action=rel,actor_obs86_for_action=obs,actual_original_done=i==n-1,packed127_for_action=s,terminal_packed127_same_point=t,xi31_for_action=neutral,terminal_pre_reset=dict(state=dict(executed6=[a,0,0,0,0,0])),frozen_WM_one_step=dict(predicted_root_z=0.)))
 d=decode_records(rows,n)
 class Model:
  def step(self,s,a,c):
   p=s[0].clone();p[:,0]+=a[:,0]*.01;v=s[2].clone();v[:,0]=a[:,0]
   return (p,s[1],v,*s[3:])
 allrows={h:evaluate_horizon(Model(),unflatten_state,normalize_static31,d,h,batch_size=31) for h in [1,8,32]}
 maximum=max(abs(e) for rs in allrows.values() for r in rs for k in ["predicted_minus_actual_position3","predicted_minus_actual_world_velocity3"] for e in r[k])
 assert maximum<1e-6 and [len(allrows[h]) for h in [1,8,32]]==[n,n-7,n-31]
 negatives=[]
 import copy
 for label,mutate in [
  ("wrong_control",lambda r:r[3].update(control=99)),
  ("wrong_age",lambda r:r[3].update(age_for_action=[44])),
  ("wrong_request",lambda r:r[220]["task_relative_features7_for_action"].__setitem__(5,0)),
  ("wrong_actor_request",lambda r:r[220]["actor_obs86_for_action"].__setitem__(-2,0)),
  ("wrong_phase_request",lambda r:r[220]["actual_phase_record"].update(public_request_for_action=False)),
  ("early_done",lambda r:r[12].update(actual_original_done=True)),
  ("noncontiguous",lambda r:r[12].update(packed_frame_for_action=999)),
  ("bad_xi",lambda r:r[12].update(xi31_for_action=[0]*30)),
  ("nonfinite_action",lambda r:r[12]["terminal_pre_reset"]["state"]["executed6"].__setitem__(0,float("nan"))),
  ("bad_state_width",lambda r:r[12].update(packed127_for_action=[0]*126))]:
  rr=copy.deepcopy(rows);mutate(rr)
  try:decode_records(rr,n)
  except (ValueError,RuntimeError):negatives.append(label)
  else:raise AssertionError(label)
 bad=d["done"].clone();bad[20]=True
 assert len(valid_starts(d["frames"],bad,32))<len(valid_starts(d["frames"],d["done"],32))
 class Nonfinite(Model):
  def step(self,s,a,c):
   x=super().step(s,a,c);x[0][:,0]=float("nan");return x
 try:evaluate_horizon(Nonfinite(),unflatten_state,normalize_static31,d,1)
 except ValueError:negatives.append("nonfinite_rollout")
 else:raise AssertionError("nonfinite")
 with (R/"SOURCE113_REAL_CORE_SYNTHETIC_ACTION_SEQUENCE_AND_NEGATIVES_CPU_ACTUAL.json").open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),passed_source_CPU_only=True,closed_form_nonconstant_action_sequence=True,world_state_rollout_not_policy=True,horizons=[1,8,32],synthetic_max_abs_error=maximum,negative_cases_rejected=negatives,midwindow_reset_excluded=True,checkpoint_model_raw_SDK_physics_or_GPU_reads=0,not_actual113_model_result=True),f,indent=2)
 print(json.dumps(dict(source_CPU_passed=True,negative_count=len(negatives),maximum_error=maximum,no_saved_model_or_raw=True)))
if __name__=="__main__":
 try:main()
 except BaseException:
  import traceback
  with (R/("SOURCE113_CPU_ORIGINAL_ERROR_"+str(time.time_ns())+".json")).open("x",encoding="utf8") as f:json.dump(dict(traceback=traceback.format_exc(),no_actual_model_or_raw=True),f,indent=2)
  raise

