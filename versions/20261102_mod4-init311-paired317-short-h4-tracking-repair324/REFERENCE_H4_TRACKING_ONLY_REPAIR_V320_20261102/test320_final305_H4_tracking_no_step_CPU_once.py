"""One necessary final305 read for318 exactresume/EMA/H4 no-step repair admission, no step."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,sys,time,traceback,types
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports';sys.path[:0]=[str(S),str(S/'code'),str(S/'kernel')]
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
try:
 put('CPU320_FINAL305_H4_REPAIR_PURPOSE_CONSUMED.json',dict(epoch=time.time(),model_reads_max=1,optimizer_steps=0,SDK=0,GO=0,purpose='Necessary exactfinal305resume including originalEMAtarget/allAdam; newH4 policy/H32WM+heldrestlabel integratedCPUfixture no optimizer step'))
 import torch
 torch.set_num_threads(8);torch.manual_seed(305)
 from tracking_reference315 import Reference315 as Reference305
 from tracking_learner320 import TrackingLearner320 as TrackingLearner305
 from tracking_survival305 import matched_survival305
 from tracking_wm305 import TrackingWM305
 from future_safe_wm_warm273 import FrozenTeacherContract273
 from measured_state224_v268 import MeasurementBinding268
 from teacher_student292 import forward,policy_obs
 import math
 proofpath=T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json';proof=json.loads(proofpath.read_bytes())
 raw=Path(proof['path']).read_bytes();assert len(raw)==proof['bytes']and hashlib.sha256(raw).hexdigest()==proof['SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
 bb=ck['world_model']['protocol']['binding'];binding=MeasurementBinding268(tuple(bb['joint_names']),tuple(bb['body_names']),tuple(bb['motor_ids_reward_order']),bb['witness_kind'],bb['witness_SHA'])
 wm=TrackingWM305(str(S/'kernel'),torch.device('cpu'),teacher_contract=FrozenTeacherContract273(ck['teacher_source_SHA'],'a'*64,True),binding=binding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512))
 wm.model.load_state_dict(ck['world_model']['world_model']);wm.optimizer.load_state_dict(ck['world_model']['world_optimizer']);wm.updates=12468
 task=json.loads((T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/TASK305_FROZEN.json').read_bytes());ref=Reference305(N/'reference305.npz',task['reference'],binding.joint_names,'cpu',torch.zeros(2,3))
 env=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(joint_names=list(binding.joint_names),body_names=list(binding.body_names))},target305=torch.tensor([[.8,0.,.27,0.]]).repeat(80,1))
 learner=TrackingLearner305(wm,ck,ref,env,binding,hashlib.sha256(proofpath.read_bytes()).hexdigest(),lambda n,x:put('CPU_'+n,x));learner.batch=8
 assert all(torch.equal(v,ck['student']['actor_state_dict'][k])for k,v in learner.actor.state_dict().items())
 assert all(torch.equal(v,ck['student']['critic_state_dict'][k])for k,v in learner.critic.state_dict().items())
 assert all(torch.equal(v,ck['student']['target_critic_state_dict'][k])for k,v in learner.target_critic.state_dict().items())
 for scope,step in(('actor',48257),('critic',5317)):
  source=ck['student'][scope+'_optimizer'];actual=learner.optimizers[scope].state_dict()
  for pid,slots in source['state'].items():
   for k,v in slots.items():assert torch.equal(v,actual['state'][pid][k])if torch.is_tensor(v)else v==actual['state'][pid][k]
 packed=ck['current_measured_state224'].clone();state=wm.measured_layout.unpack(packed)
 ctx=torch.cat((ck['current_static31'],torch.tensor([[.8,.27,0.,0.,2.,3.,1.,0.,1.]]).repeat(80,1)),-1)
 policy=torch.zeros(80,35);critic=torch.zeros(80,38);policy[:,3]=1.25;critic[:,3]=1.25;policy[:,29]=1;critic[:,32]=1
 po,co=policy_obs(state,torch.zeros(80,6),policy,critic,ctx,learner.legs,learner.wheels);policy=po[:,:35].detach();critic=co[:,:38].detach()
 for i in range(64):
  for name in('s','s1'):wm.buffer.data[name][i].copy_(packed)
  wm.buffer.data['xi'][i].copy_(ctx);wm.buffer.data['a'][i]=0.;wm.buffer.data['a_prev'][i]=0.;wm.buffer.data['r'][i]=.6;wm.buffer.data['done'][i]=False
  wm.anchors.data['valid_anchor'][i]=True;wm.anchors.data['static31_raw'][i].copy_(ctx[:,:31]);wm.anchors.data['environment_origins_world'][i]=0.
  wm.anchors.data['corners_world'][i].copy_(torch.tensor([[.8,-1.,.27],[3.8,-1.,.27],[3.8,1.,.27],[.8,1.,.27]]).expand(80,4,3));wm.anchors.data['step_height'][i]=.27;wm.anchors.data['confidence'][i]=1.;wm.anchors.data['initial_age'][i]=0.
  producer=types.SimpleNamespace(kind='LABELLED_SYNTHETIC_CPU_ONLY',plant='own_MOD4_live_USD',run_id='CPU320',generation='CPU320',source_admission_SHA='a'*64,sensor_id='synthetic',environment_ids=tuple(range(80)),episode_ids=(0,)*80)
  wm.anchors.scopes[i]=(producer,'synthetic_'+str(i));learner.add_metadata(i,policy,critic,torch.full((80,),i,dtype=torch.long),critic,ctx[:,31:])
 wm.buffer.ptr=0;wm.buffer.size=64
 before={k:v.detach().clone()for k,v in learner.actor.state_dict().items()};cbefore={k:v.detach().clone()for k,v in learner.critic.state_dict().items()};targetbefore={k:v.detach().clone()for k,v in learner.target_critic.state_dict().items()}
 diag=learner.update(apply_step=False)
 assert diag and diag['policy_H']==4 and diag['WM_H']==32 and diag['H32']is False
 assert diag['actor_terminal_bootstrap']is False and diag['first_actual_gradient_components']['terminal_only']==0. and diag['terminal_loss']==0.
 assert diag['Pi_updates']==diag['critic_updates']==0 and diag['critic_target_source'].startswith('actual own transition')and abs(diag['actual_TD_reward_mean']-.6)<1e-6
 assert all(torch.equal(v,before[k])for k,v in learner.actor.state_dict().items())and all(torch.equal(v,cbefore[k])for k,v in learner.critic.state_dict().items())and all(torch.equal(v,targetbefore[k])for k,v in learner.target_critic.state_dict().items())
 # Force actual terminal labels: TD bootstrap must vanish even with a nonzero
 # inherited critic. The actor's imagined objective is unchanged in this probe.
 wm.buffer.data['done'][:]=True
 terminaldiag=learner.update(apply_step=False);assert abs(terminaldiag['actual_TD_target_mean']-.6)<1e-6 and terminaldiag['actual_terminal_fraction']==1.
 angle=torch.tensor([.5,.75,1.]);rot=torch.eye(3).repeat(3,1,1);rot[:,2,2]=angle.cos();survive=matched_survival305((torch.zeros(3,3),rot))
 assert survive[0]>.99 and abs(float(survive[1])-.5)<1e-5 and survive[2]<.001
 assert all(int(v['step'])in(42940,48257)for v in learner.actor_optimizer.state.values())and all(int(v['step'])==5317 for v in learner.critic_optimizer.state.values())
 report=dict(epoch=time.time(),passed=True,model_reads=1,optimizer_steps=0,CUDA=torch.cuda.is_initialized(),SDK=0,GO=0,source_final_SHA=proof['SHA'],actor103_critic106_STD_exact_restore=True,allAdamMoments_exact_restore=True,actoroffset48257=True,criticoffset5317=True,WM12468=True,synthetic_H4_no_step=diag,terminal_bootstrap_test=terminaldiag['actual_TD_target_mean'],survival_at_angles=survive.tolist(),physical_angle_unchanged=.75)
 put('CPU320_RESTORED305_H4_REPAIR_NO_STEP.json',report);print(json.dumps(report),flush=True)
except BaseException:
 put('CPU320_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True));raise
