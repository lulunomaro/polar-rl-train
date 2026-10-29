"""NEW113 actual-action forward validation; no checkpoint I/O or physics in this module."""
from __future__ import annotations
import math
import torch

def require(v,msg):
 if not bool(v):raise ValueError(msg)
def tensor_rows(rows,key,width):
 out=torch.tensor([x[key] for x in rows],dtype=torch.float32)
 require(out.shape==(len(rows),width) and torch.isfinite(out).all(),key+" finite typed width")
 return out
def decode_records(rows,expected_count=2000):
 require(isinstance(rows,list) and len(rows)==expected_count,"actual complete row count")
 actions=[];ages=[];frames=[];done=[];stored_z=[]
 for i,x in enumerate(rows):
  require(x["control"]==i+1,"exact completed-control order")
  age=x["age_for_action"];require(isinstance(age,list) and age==[i],"exact action age before step")
  require(x["actual_phase_record"]["control"]==i+1 and x["actual_phase_record"]["age_for_action"]==i,"actual phase binding")
  require(x["task_relative_features7_for_action"][5]==float(200<=i<2000),"actual request clock")
  require(x["actor_obs86_for_action"][-2]==float(200<=i<2000),"actor request clock")
  require(x["actual_phase_record"]["public_request_for_action"]==(200<=i<2000),"public request clock")
  a=x["terminal_pre_reset"]["state"]["executed6"];require(len(a)==6,"actual executed6")
  actions.append(a);ages.append(i);frames.append(x["packed_frame_for_action"]);done.append(x["actual_original_done"])
  stored_z.append(x["frozen_WM_one_step"]["predicted_root_z"])
 require(done==[False]*(expected_count-1)+[True],"single episode only original final done")
 f=torch.tensor(frames,dtype=torch.long);require(f.ndim==1 and torch.equal(f[1:],f[:-1]+1),"contiguous exact private frames")
 s=tensor_rows(rows,"packed127_for_action",127);t=tensor_rows(rows,"terminal_packed127_same_point",127)
 xi=tensor_rows(rows,"xi31_for_action",31);a=torch.tensor(actions,dtype=torch.float32)
 require(a.shape==(expected_count,6) and torch.isfinite(a).all(),"finite executed actions")
 # No assumption that next current-state caches are bit-identical to pre-reset labels.
 # Report their domains; do not invent new physical reset/health tolerances.
 continuity=(s[1:]-t[:-1]).abs().amax(0) if len(rows)>1 else torch.zeros(127)
 return dict(s=s,t=t,a=a,xi=xi,frames=f,ages=torch.tensor(ages),done=torch.tensor(done),stored_root_z=torch.tensor(stored_z,dtype=torch.float32),continuity=continuity)

def valid_starts(frames,done,horizon):
 n=len(frames);result=[]
 for i in range(n-horizon+1):
  if bool(done[i:i+horizon-1].any()):continue
  if not torch.equal(frames[i:i+horizon],frames[i]+torch.arange(horizon)):continue
  result.append(i)
 return result

def evaluate_horizon(wm,unpack,normalize,data,horizon,batch_size=256,check_deadline=lambda:None):
 starts=valid_starts(data["frames"],data["done"],horizon)
 out=[]
 with torch.inference_mode():
  for offset in range(0,len(starts),batch_size):
   check_deadline()
   ids=torch.tensor(starts[offset:offset+batch_size],dtype=torch.long)
   initial=unpack(data["s"][ids]);predicted=tuple(x.clone() for x in initial)
   for k in range(horizon):
    check_deadline()
    predicted=wm.step(predicted,data["a"][ids+k],normalize(data["xi"][ids+k]))
    require(all(torch.isfinite(x).all() for x in predicted),"nonfinite predicted state")
   truth=unpack(data["t"][ids+horizon-1])
   for j,start in enumerate(ids.tolist()):
    row=dict(start_control=start+1,end_control=start+horizon,horizon=horizon,age_for_action=int(data["ages"][start]),
      request_for_action=bool(200<=int(data["ages"][start])<2000),
      input_position3=initial[0][j].tolist(),predicted_position3=predicted[0][j].tolist(),actual_position3=truth[0][j].tolist(),
      input_world_velocity3=initial[2][j].tolist(),predicted_world_velocity3=predicted[2][j].tolist(),actual_world_velocity3=truth[2][j].tolist(),
      predicted_minus_actual_position3=(predicted[0][j]-truth[0][j]).tolist(),
      predicted_minus_actual_world_velocity3=(predicted[2][j]-truth[2][j]).tolist(),
      predicted_displacement3=(predicted[0][j]-initial[0][j]).tolist(),actual_displacement3=(truth[0][j]-initial[0][j]).tolist(),
      actual_actions_at_every_offset=True,no_policy_action_resampling=True)
    if horizon==1:row["saved_GPU112_predicted_root_z"]=float(data["stored_root_z"][start])
    out.append(row)
 return out

def summary(rows):
 if not rows:return dict(windows=0)
 def stat(values):
  t=torch.tensor(values,dtype=torch.float32)
  return dict(mean=float(t.mean()),mean_abs=float(t.abs().mean()),rmse=float(t.square().mean().sqrt()),max_abs=float(t.abs().max()),p95_abs=float(torch.quantile(t.abs(),.95)))
 p=torch.tensor([r["predicted_minus_actual_position3"] for r in rows]);v=torch.tensor([r["predicted_minus_actual_world_velocity3"] for r in rows])
 qualified=[r for r in rows if abs(r["actual_world_velocity3"][0])>.02]
 result=dict(windows=len(rows),world_position_error={x:stat(p[:,i].tolist()) for i,x in enumerate("xyz")},
 world_velocity_error={x:stat(v[:,i].tolist()) for i,x in enumerate("xyz")},
 actual_world_vx_range=[min(r["actual_world_velocity3"][0] for r in rows),max(r["actual_world_velocity3"][0] for r in rows)],
 actual_dx_range=[min(r["actual_displacement3"][0] for r in rows),max(r["actual_displacement3"][0] for r in rows)],
 significant_vx_sign_subset=dict(actual_abs_vx_gt_m_s=.02,windows=len(qualified),opposite_sign=sum(r["actual_world_velocity3"][0]*r["predicted_world_velocity3"][0]<0 for r in qualified),
 threshold_scope="Reporting partition using original WM velocity error-floor units, not a physics/skill/admission gate"),
 positive_actual_dx_windows=sum(r["actual_displacement3"][0]>0 for r in rows),
 predicted_positive_dx_windows=sum(r["predicted_displacement3"][0]>0 for r in rows),
 zero_raw_action_replaced_or_generated=False,overlapping_windows_not_independent_trials=True)
 if rows[0]["horizon"]==1:
  result["CPU_vs_saved_GPU_one_step_root_z_max_abs"]=max(abs(r["predicted_position3"][2]-r["saved_GPU112_predicted_root_z"]) for r in rows)
 return result

