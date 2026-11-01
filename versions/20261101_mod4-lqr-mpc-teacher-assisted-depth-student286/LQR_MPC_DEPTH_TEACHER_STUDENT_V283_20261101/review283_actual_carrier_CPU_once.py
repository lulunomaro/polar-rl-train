"""One necessary carrier decode: actual migration + labelled synthetic H32 no-step."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,sys,time,traceback,types
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports'
sys.path[:0]=[str(S),str(S/'code'),str(S/'kernel')]
def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

try:
    put('CPU283_CARRIER_PURPOSE_CONSUMED_BEFORE_READ.json',dict(epoch=time.time(),
      purpose='new teacher student actual optimizer identity and H32 no-step integration',
      maximum_carrier_byte_hash_decode=1,old_teacher_raw_reads=0,CUDA=False,optimizer_steps=0))
    import numpy as np,torch
    torch.set_num_threads(8)
    torch.manual_seed(283)
    from teacher_student283 import TeacherStudent283,forward,policy_obs
    from future_safe_wm_warm273 import FutureSafeWarmWM273,FrozenTeacherContract273
    from measured_state224_v268 import MeasurementBinding268
    from reference283 import Reference283
    from literal_imagination259 import RewardMemory
    from native_depth_world_model50_v255 import normalize_context40
    OLD=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101'
    receipt=OLD/'reports/ROOT281_NEW_WM_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json'
    proof=json.loads(receipt.read_bytes());assert proof['passed']
    p=Path(proof['path']);raw=p.read_bytes();assert len(raw)==proof['bytes'] and hashlib.sha256(raw).hexdigest()==proof['SHA']
    carrier=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
    assert carrier['actual_new_WM_updates']==4719 and not torch.cuda.is_initialized()
    binding_metadata=carrier['world_model']['protocol']['binding']
    binding=MeasurementBinding268(tuple(binding_metadata['joint_names']),tuple(binding_metadata['body_names']),
      tuple(binding_metadata['motor_ids_reward_order']),binding_metadata['witness_kind'],binding_metadata['witness_SHA'])
    wm=FutureSafeWarmWM273(str(S/'kernel'),torch.device('cpu'),teacher_contract=FrozenTeacherContract273(
      carrier['teacher_source_SHA'],H(receipt),True),binding=binding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512))
    wm.model.load_state_dict(carrier['world_model']['world_model'],strict=True)
    wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer']);wm.updates=4719
    wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'].cpu())
    references=json.loads((T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V282_20261101/REFERENCE282_PRODUCER.json').read_bytes())
    reference=Reference283(N/'reference283.npz',references,list(binding.joint_names),'cpu')
    # This batch is explicitly synthetic, initialized from the saved final own
    # state. It proves executable gradients and identity, not world accuracy.
    env=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(joint_names=list(binding.joint_names))},
      target283=torch.tensor([[1.,0.,.27,0.]]).repeat(80,1),_mixed209_flat=torch.arange(80)%10==0)
    learner=TeacherStudent283(wm,carrier,reference,env,binding,H(receipt),lambda n,v:put('CPU_'+n,v))
    learner.batch=16
    packed=carrier['current_measured_state224'].clone()
    packed[:,:2]=0.;packed[:,2]=.34;packed[:,3:7]=torch.tensor([1.,0.,0.,0.])
    packed[:,7:13]=0.
    state=wm.measured_layout.unpack(packed)
    policy=torch.zeros(80,35);critic=torch.zeros(80,38);policy[:,3]=.675;critic[:,3]=.675
    policy[:,29]=1.;critic[:,32]=1.
    rawcontext=torch.cat((carrier['current_static31'],torch.tensor([[1.,.27,0.,0.,2.,3.,1.,0.,1.]]).repeat(80,1)),-1)
    policy44,critic47=policy_obs(state,torch.zeros(80,6),policy,critic,rawcontext,learner.leg_ids,learner.wheel_ids)
    policy=policy44[:,:35].detach();critic=critic47[:,:38].detach()
    orig=carrier['teacher_full_PPO_state']
    from teacher_student283 import model
    actor=model(35,True,'cpu');actor.load_state_dict(orig['actor_state_dict'])
    value=model(38,False,'cpu');value.load_state_dict(orig['critic_state_dict'])
    with torch.no_grad():
        a0=forward(actor,policy);a1=learner.action(policy,rawcontext[:,31:])
        c0=forward(value,critic);c1=forward(learner.critic,torch.cat((critic,rawcontext[:,31:]),-1))
        assert torch.allclose(a0.clamp(-6,6),a1,atol=1e-5,rtol=1e-5)
        assert torch.allclose(c0,c1,atol=1e-5,rtol=1e-5)
    for i in range(64):
        for name in ('s','s1'):wm.buffer.data[name][i].copy_(packed)
        wm.buffer.data['xi'][i].copy_(rawcontext)
        wm.buffer.data['a'][i].copy_(a0.clamp(-6,6));wm.buffer.data['a_prev'][i].copy_(a0.clamp(-6,6))
        wm.anchors.data['valid_anchor'][i]=True
        wm.anchors.data['static31_raw'][i].copy_(rawcontext[:,:31])
        wm.anchors.data['environment_origins_world'][i]=0.
        wm.anchors.data['corners_world'][i].copy_(torch.tensor([[1.,-1.,.27],[4.,-1.,.27],[4.,1.,.27],[1.,1.,.27]]).expand(80,4,3))
        wm.anchors.data['step_height'][i]=.27;wm.anchors.data['confidence'][i]=1.;wm.anchors.data['initial_age'][i]=0.
        producer=types.SimpleNamespace(kind='LABELLED_SYNTHETIC_CPU_ONLY',plant='own_MOD4_live_USD',run_id='CPU283',
          generation='CPU283',source_admission_SHA=H(receipt),sensor_id='synthetic',environment_ids=tuple(range(80)),episode_ids=(0,)*80)
        wm.anchors.scopes[i]=(producer,'synthetic_CPU283_'+str(i))
        memory=RewardMemory(torch.zeros(80),torch.zeros(80,2,dtype=torch.bool),torch.zeros(80,6,2))
        learner.add_metadata(i,policy,critic,torch.tensor([[1.4,0.,.135,0.]]).repeat(80,1),memory,torch.zeros(80,3))
    wm.buffer.size=64;wm.buffer.ptr=0
    before={k:v.detach().clone() for k,v in learner.actor.state_dict().items()}
    norms={k:v.detach().clone() for k,v in wm.model.state_dict().items()}
    diagnostic=learner.update(apply_step=False)
    assert diagnostic and not diagnostic['optimizer_steps_applied']
    assert diagnostic['Pi_updates']==diagnostic['critic_updates']==0
    assert all(torch.equal(v,before[k]) for k,v in learner.actor.state_dict().items())
    assert all(torch.equal(v,norms[k]) for k,v in wm.model.state_dict().items())
    assert all(int(v['step'])==42940 for opt in learner.optimizers.values() for v in opt.state.values())
    assert all(int(v['step'])==4719 for v in wm.optimizer.state.values())
    report=dict(passed=True,epoch=time.time(),purpose='actual restored carrier migration + synthetic H32 gradient integration',
      carrier_SHA=proof['SHA'],actual_source_optimizer_identity=True,actual_target_split_adam_identity=True,
      actor35to44_critic38to47_zero_suffix_equivalent=True,source_full17_Adam_partition=[9,8],
      source_Adam_step=42940,inherited_WM_step=4719,CUDA_initialized=torch.cuda.is_initialized(),
      optimizer_steps=0,actual_plant_SDK_runs=0,actual_world_accuracy_not_measured=True,
      teacher_reference_not_WM_transitions=True,diagnostic=diagnostic,
      actual_live_H32_gradient_and_WM_loss_required_before_first_student_step=True)
    put('CPU283_ACTUAL_CARRIER_MIGRATION_AND_H32_NO_STEP.json',report)
    print(json.dumps(report))
except BaseException:
    put('CPU283_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay=True))
    raise
