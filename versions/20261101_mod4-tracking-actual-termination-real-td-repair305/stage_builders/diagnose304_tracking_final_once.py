"""One necessary CPU read of new final300 for failure diagnosis, never training."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,importlib.util,io,json,sys,time,traceback
T=Path(__file__).resolve().parent;O=T/'REFERENCE_TRACKING_BPTT_V300_20261101';E=T/'REFERENCE_TRACKING300_POSTROUND_EVAL_V303_20261101'
N=T/'TRACKING300_FAILURE_DIAGNOSIS_V304_20261101';N.mkdir(exist_ok=False);R=N/'reports';R.mkdir()
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
try:
 put('CPU304_NEW_FINAL_DIAGNOSTIC_READ_CONSUMED.json',dict(epoch=time.time(),purpose='Final300 new failure causal diagnostics: reference/physical init and end mismatch, H32 WM trend, critic return dominance/action saturation; no archive-only read',model_reads_max=1,CUDA=False,SDK=0,optimizer_steps=0,GO=0))
 import numpy as np,torch
 torch.set_num_threads(8)
 sys.path[:0]=[str(O/'source'),str(O/'source/code'),str(O/'source/kernel')]
 from native_measured_depth_world_model50_v268 import MeasuredDepthTeacherWM50
 from measured_state224_v268 import MeasurementBinding268
 from tracking_reference300 import Reference300,tracking_cost300
 from tracking_wm300 import TrackingWM300
 from future_safe_wm_warm273 import FrozenTeacherContract273,context_from_start_anchor273
 from native_depth_world_model50_v255 import normalize_context40
 from teacher_student292 import model,forward,policy_obs,DEPTH_SCALE
 proof=json.loads((O/'reports/ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
 raw=Path(proof['path']).read_bytes();assert len(raw)==proof['bytes']and hashlib.sha256(raw).hexdigest()==proof['SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
 teacher=ck['teacher_full_PPO_state'];source=ck['world_model']['protocol']['binding']
 binding=MeasurementBinding268(tuple(source['joint_names']),tuple(source['body_names']),tuple(source['motor_ids_reward_order']),source['witness_kind'],source['witness_SHA'])
 task=ck['typed_TEACHER300_task'];target=ck['teacher_target_layout'];packed=ck['current_measured_state224'];phase=ck['reference_phase_steps'].long()
 wm=TrackingWM300(str(O/'source/kernel'),'cpu',teacher_contract=FrozenTeacherContract273(task['teacher_SHA'],task['teacher_whole_CPU_receipt_SHA'],True),binding=binding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512))
 wm.model.load_state_dict(ck['world_model']['world_model']);wm.updates=ck['total_WM_updates']
 ref=Reference300(O/'reference300.npz',task['reference'],binding.joint_names,'cpu',torch.zeros(2,3))
 # True hips from the exact runtime source are not needed for root/joint diagnostics.
 actor=model(103,True,'cpu');actor.load_state_dict(ck['student']['actor_state_dict']);critic=model(106,False,'cpu');critic.load_state_dict(ck['student']['critic_state_dict'])
 legs=[binding.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')];wheels=[binding.joint_names.index(n)for n in('left_wheel_spin','right_wheel_spin')]
 state=wm.measured_layout.unpack(packed)
 # Exact new final has no replay, so do not pretend a reconstructed observation
 # is the actual delayed policy observation. Evaluate clean modeled ABI only.
 policy=torch.zeros(80,35);policy[:,3]=1.25;policy[:,29]=1.;co=torch.zeros(80,38);co[:,3]=1.25;co[:,32]=1.
 z=torch.zeros(80);ctx=torch.cat((ck['current_static31'],torch.stack((target[:,0]-state[0][:,0],target[:,2],-state[0][:,1],z,z+2,z+3,z+1,z,z+1),-1)),-1)
 obs,cobs=policy_obs(state,ck['previous_clipped_action'],policy,co,ctx,legs,wheels);goals=ref.goals(state,phase,torch.arange(80),target)
 with torch.no_grad():
  raw_actions=forward(actor,torch.cat((obs,goals),-1));values=forward(critic,torch.cat((cobs,goals),-1)).flatten()
 wm_state=[];roll=state
 with torch.no_grad():
  for step in range(32):
   # This is diagnostic teacher-forced context construction from current scene
   # dimensions, not a valid newly observed packet and never policy training.
   cue=ctx.clone();cue[:,31]=target[:,0]-roll[0][:,0];cue[:,33]=-roll[0][:,1];cue[:,38]=step*.02
   po,pc=policy_obs(roll,ck['previous_clipped_action'],policy,co,cue,legs,wheels)
   goal=ref.goals(roll,phase+step,torch.arange(80),target);action=forward(actor,torch.cat((po,goal),-1)).clamp(-6,6)
   roll=wm.model.step(roll,action,normalize_context40(cue))
   if step in(0,3,7,15,31):wm_state.append(dict(step=step+1,mean_p=roll[0].mean(0).tolist(),mean_Rzz=float(roll[1][:,2,2].mean()),mean_speed=float(roll[2].norm(dim=-1).mean()),action_abs_max=float(action.abs().max())))
 traces=[]
 transfers=json.loads((E/'reports/ROOT303_SELECTED_REPLAY_TRANSFERS.json').read_bytes())
 for row in transfers['cases']:
  b=Path(row['local_path']).read_bytes();assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['SHA']
  with np.load(io.BytesIO(b),allow_pickle=False)as data:
   root=data['root13'].copy();root[:,:3]-=np.array(row['origin']);actions=data['action6'];depth=data['depth9']
   q=root[:,3:7];rzz=1-2*(q[:,0]**2+q[:,1]**2)
   traces.append(dict(env=row['env'],steps=len(root),firstroot=root[0].tolist(),lastroot=root[-1].tolist(),root_x_range=[float(root[:,0].min()),float(root[:,0].max())],root_z_range=[float(root[:,2].min()),float(root[:,2].max())],Rzz_range=[float(rzz.min()),float(rzz.max())],initial_action=actions[0].tolist(),final_action=actions[-1].tolist(),action_abs_max=np.abs(actions).max(0).tolist(),valid_depth=int((depth[:,8]==1).sum())))
 refstates=ref.states.numpy();qfirst=refstates[0];qend=refstates[-1];refroot=refstates[:,:3].copy();refroot[:,0]+=.8
 report=dict(epoch=time.time(),passed=True,source_final_SHA=proof['SHA'],model_reads=1,CUDA=torch.cuda.is_initialized(),SDK=0,GO=0,optimizer_steps=0,
  actual300=dict(Pi=ck['actual_new_Pi_updates'],critic=ck['actual_new_critic_updates'],WM=wm.updates,controls=ck['controls']),
  final_state_mean=dict(position=state[0].mean(0).tolist(),Rzz=float(state[1][:,2,2].mean()),phase_min=int(phase.min()),phase_max=int(phase.max()),virtualL=state[6][:,54:56].mean(0).tolist()),
  clean_reconstructed_ABI_only=dict(actor_max=raw_actions.abs().max(0).values.tolist(),saturated=(raw_actions.abs()>6).sum(0).tolist(),critic_min=float(values.min()),critic_max=float(values.max()),critic_mean=float(values.mean())),
  diagnostic_rollout_not_actual_recorded_anchor=wm_state,actual_recorded_traces=traces,
  reference=dict(firstposition=refroot[0].tolist(),lastposition=refroot[-1].tolist(),maxheight=float(refroot[:,2].max()),first_R=qfirst[3:12].reshape(3,3).tolist(),first_qlegs=qfirst[18:48][legs].tolist(),last_qlegs=qend[18:48][legs].tolist(),root_xy_range=[refroot[:,:2].min(0).tolist(),refroot[:,:2].max(0).tolist()],takeoffindices=np.where(ref.support.numpy().sum(-1)<.1)[0].tolist()),
  actual_eval=dict(success=0,cross=0,orientation=66,finished8s=14),
  limitation='No same-start actual+WM multi-step validation in original300 reports. ReconstructedcleanABI and syntheticcoursecontext are diagnostics only, not actual predictive-error estimates. Hipzeros not used for claimedlegtrackingerror.',
  source_defects=dict(soft_survival_Rzz_threshold=.45,actual_orientation_Rzz_threshold=float(np.cos(.75)),WM_supervision_uses_same_start_only=True,critic_trained_only_on_imagined_returns=True,actor_bootstrap_direct_gradient=True))
 put('CPU304_ACTUAL_FINAL300_FAILURE_DIAGNOSTIC.json',report)
 print(json.dumps(report),flush=True)
except BaseException:
 put('CPU304_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True));raise
