"""Actual measured-data H32 CUDA capacity/gradient admission, no optimizer step.

All fresh scratch parameters/norm buffers are restored exactly before return.
No old policy checkpoint, scene, physics, teacher/Pi/Critic forward is loaded.
"""
from pathlib import Path
import hashlib,io,json,os,sys,time,traceback
P=Path(__file__).resolve().parent;task=json.loads((P/'TASK274_ADMITTED.json').read_bytes());assert task['private_shared_EX_and_current_authority_admitted']and os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
def put(n,x):
 with(P/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
try:
 import numpy as np,torch
 sys.path[:0]=[str(P/'code'),str(P/'kernel')]
 from future_safe_wm_warm273 import FutureSafeWarmWM273,FrozenTeacherContract273
 from measured_state224_v268 import MeasurementBinding268,SCHEMA_ID
 from observed_support_context271 import Producer271,CurrentDepthPacket271,FRAME
 put('WORKER274_NEW272_RAW_PURPOSE_CONSUMED.json',dict(epoch=time.time(),dataset=task['dataset'],byte_opens_max=1,np_load_max=1,selected_members_each1=True,checkpoint_PT_reads=0,optimizer_steps_allowed=0))
 with Path(task['dataset']['path']).open('rb')as f:raw=f.read()
 assert len(raw)==task['dataset']['bytes']and hashlib.sha256(raw).hexdigest()==task['dataset']['SHA']
 needed=('s','s1','xi31','depth9','a','done','episode_id','physical_reward','physics_end_tick','depth_found','depth_time','control_time','visible_floor_z_m','sensor_pose_native13','environment_origins_world','T_world_heading')
 z=np.load(io.BytesIO(raw),allow_pickle=False);data={k:z[k]for k in needed};z.close();del raw
 assert data['s'].shape==data['s1'].shape==(64,80,224)
 assert np.array_equal(data['physics_end_tick'],np.arange(1,65)*8)
 device=torch.device('cuda:0');torch.cuda.reset_peak_memory_stats(device)
 original_rng=torch.random.get_rng_state().clone();cuda_rng=torch.cuda.get_rng_state(device).clone()
 b=task['actual_binding'];binding=MeasurementBinding268(tuple(b['joint_names']),tuple(b['body_names']),tuple(b['motor_ids']),'ACTUAL_OWN_MOD4_ROBOT_NAME_AND_MOTOR_ID_BINDING',task['binding_witness_SHA']);binding.validate()
 teacher=FrozenTeacherContract273(task['teacher_SHA'],task['teacher_whole_CPU_receipt_SHA'],True)
 wm=FutureSafeWarmWM273(str(P/'kernel'),device,teacher_contract=teacher,binding=binding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512),synthetic_CPU_test=False)
 initial={k:v.detach().clone()for k,v in wm.model.state_dict().items()};previous=torch.zeros(80,6,device=device);epstep=torch.zeros(80,dtype=torch.int32,device=device);rows=[]
 def tensor(k,i,dtype=torch.float32):return torch.as_tensor(data[k][i],device=device,dtype=dtype)
 for i in range(64):
  tick=int(data['physics_end_tick'][i]);xi=torch.cat((tensor('xi31',i),tensor('depth9',i)),-1);done=tensor('done',i,torch.bool)
  transition=dict(s=tensor('s',i),s1=tensor('s1',i),a=tensor('a',i),a_prev=previous.clone(),xi=xi,r=tensor('physical_reward',i),f=torch.full((80,),i,device=device,dtype=torch.int64),ep_step=epstep.clone(),done=done)
  p=Producer271('ACTUAL_OWN_MOD4_CURRENT_DEPTH263_PACKET','own_MOD4_live_USD',task['source_run_id'],task['source_generation'],task['source_actual_resource_admission_SHA'],'D435i_front_fixed',tuple(range(80)),tuple(int(x)for x in data['episode_id'][i]))
  st=torch.full((80,),float(data['depth_time'][i]),device=device);ct=torch.full((80,),float(data['control_time'][i]),device=device)
  packet=CurrentDepthPacket271(p,f"NEW272_REAL_PACKET:{i}",tensor('depth_found',i,torch.bool),tensor('depth9',i),tensor('visible_floor_z_m',i),st,ct,st.clone(),tensor('sensor_pose_native13',i),tensor('environment_origins_world',i),tensor('T_world_heading',i),FRAME,'native_wxyz')
  producer=dict(kind='ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER',plant='own_MOD4_live_USD',state_schema=SCHEMA_ID,binding_witness_SHA=binding.witness_SHA,measured_fields=['own_L0_theta4','contact_forces_BODY31x3'],s_physics_end_tick=tick-8,s1_physics_end_tick=tick,run_id=p.run_id,generation=p.generation,source_admission_SHA=p.source_admission_SHA,max_depth_age_seconds=float((ct-st).max()))
  rows.append(wm.add(transition,actual_anchor=packet,physics_end_tick=tick,physics_us=2500,feedback_samples=2,producer=producer))
  previous=transition['a'].clone();previous[done]=0;epstep=torch.where(done,0,epstep+1).to(torch.int32)
 assert wm.ready_for_update()and wm.updates==0 and len(wm.optimizer.state)==0
 batch=wm.sample();loss,prediction,context=wm.rollout_loss(batch,capture_context=True);wm.optimizer.zero_grad(set_to_none=True);loss.backward()
 grad=torch.nn.utils.clip_grad_norm_(wm.model.parameters(),1.)
 assert torch.isfinite(loss)and torch.isfinite(grad)and grad>0 and all(p.grad is None or torch.isfinite(p.grad).all()for p in wm.model.parameters())
 assert wm.updates==0 and len(wm.optimizer.state)==0
 scratch_norm_fits=wm.controls;wm.model.load_state_dict(initial,strict=True);wm.model.zero_grad(set_to_none=True)
 assert all(torch.equal(v,wm.model.state_dict()[k])for k,v in initial.items())
 assert torch.equal(original_rng,torch.random.get_rng_state())and torch.equal(cuda_rng,torch.cuda.get_rng_state(device))
 report=dict(passed=True,epoch=time.time(),source_data=task['dataset'],source_data_byte_opens=1,np_loads=1,selected_members_once=list(needed),physical_input_pairs=5120,controls=64,envs=80,world_state=224,WM_input=wm.model.in_dim,WM_output=wm.model.out_dim,horizon=32,batch=1024,hidden=[512,512,512],first_observed_anchor_only=True,supported_start_candidates=batch['supported_start_candidates'],supported_rows_total=sum(r['supported_current_anchors']for r in rows),scratch_normalizer_ingress_fits=scratch_norm_fits,loss=float(loss.detach()),preclip_grad_L2=float(grad),optimizer_steps=0,actual_WM_updates=0,actual_Pi_Critic_teacher_updates=0,checkpoint_PT_byte_reads=0,model_checkpoint_writes=0,scratch_params_and_norms_restored_exact=True,global_CPU_CUDA_RNG_unchanged=True,peak_owned_CUDA_bytes=torch.cuda.max_memory_allocated(device),context_shape=list(context.shape),no_SDK_or_physics_or_account=True,not_world_accuracy_policy_gradient_or_skill=True)
 put('ACTUAL274_NEW272_H32_CUDA_ADMISSION_RESULT.json',report);print(json.dumps(report),flush=True)
except BaseException:
 put('ORIGINAL274_WORKER_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True));raise
