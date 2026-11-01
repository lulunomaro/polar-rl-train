import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,sys,time,traceback,types
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports';sys.path[:0]=[str(S),str(S/'code'),str(S/'kernel')]
def put(name,v):
    with (R/name).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
try:
    put('CPU296_NEW_TRACKING_ARCHITECTURE_PURPOSE_CONSUMED.json',dict(epoch=time.time(),purpose='Actual source actor103/moments goal expansion, NEW critic106 and synthetic H32 new tracking objective no-step; necessary new architecture admission',model_byte_reads_max=1,SDK=0,CUDA=False))
    import torch
    torch.set_num_threads(8);torch.manual_seed(296)
    from tracking_reference296 import Reference296,GOAL_DIM,tracking_cost296
    from tracking_learner296 import TrackingLearner296,ACTOR_DIM,CRITIC_DIM
    from future_safe_wm_warm273 import FutureSafeWarmWM273,FrozenTeacherContract273
    from measured_state224_v268 import MeasurementBinding268
    from teacher_student292 import forward,model,policy_obs
    proofpath=T/'LQR_MPC_DEPTH_TEACHER_STUDENT_V286_20261101/reports/ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
    proof=json.loads(proofpath.read_bytes());p=Path(proof['path']);raw=p.read_bytes();assert len(raw)==proof['bytes']and hashlib.sha256(raw).hexdigest()==proof['SHA']
    carrier=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
    b=carrier['world_model']['protocol']['binding'];binding=MeasurementBinding268(tuple(b['joint_names']),tuple(b['body_names']),tuple(b['motor_ids_reward_order']),b['witness_kind'],b['witness_SHA'])
    wm=FutureSafeWarmWM273(str(S/'kernel'),torch.device('cpu'),teacher_contract=FrozenTeacherContract273(carrier['teacher_source_SHA'],hashlib.sha256(proofpath.read_bytes()).hexdigest(),True),binding=binding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512))
    wm.model.load_state_dict(carrier['world_model']['world_model']);wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer']);wm.updates=7087
    refproof=json.loads((R/'REFERENCE296_PRODUCER.json').read_bytes());ref=Reference296(N/'reference296.npz',refproof,list(binding.joint_names),'cpu',torch.zeros(2,3))
    robot=types.SimpleNamespace(joint_names=list(binding.joint_names),body_names=list(binding.body_names))
    env=types.SimpleNamespace(scene={'robot':robot},target296=torch.tensor([[.8,0.,.27,0.]]).repeat(80,1))
    learner=TrackingLearner296(wm,carrier,ref,env,binding,hashlib.sha256(proofpath.read_bytes()).hexdigest(),lambda name,value:put('CPU_'+name,value));learner.batch=8
    packed=carrier['current_measured_state224'].clone();packed[:,:2]=0.;packed[:,2]=.3;packed[:,3:7]=torch.tensor([1.,0.,0.,0.]);packed[:,7:13]=0.
    state=wm.measured_layout.unpack(packed);context=torch.cat((carrier['current_static31'],torch.tensor([[.8,.27,0.,0.,2.,3.,1.,0.,1.]]).repeat(80,1)),-1)
    policy=torch.zeros(80,35);critic=torch.zeros(80,38);policy[:,3]=1.25;critic[:,3]=1.25;policy[:,29]=1.;critic[:,32]=1.
    p44,c47=policy_obs(state,torch.zeros(80,6),policy,critic,context,learner.legs,learner.wheels);policy=p44[:,:35].detach();critic=c47[:,:38].detach()
    source=model(35,True,'cpu');source.load_state_dict(carrier['teacher_full_PPO_state']['actor_state_dict'])
    with torch.no_grad():
        new=learner.action(policy,context[:,31:],packed,torch.zeros(80,dtype=torch.long));old=forward(source,policy).clamp(-6,6)
        assert torch.allclose(new,old,atol=1e-5,rtol=1e-5)
    for i in range(64):
        for name in('s','s1'):wm.buffer.data[name][i].copy_(packed)
        wm.buffer.data['xi'][i].copy_(context);wm.buffer.data['a'][i].copy_(new);wm.buffer.data['a_prev'][i].copy_(new)
        wm.anchors.data['valid_anchor'][i]=True;wm.anchors.data['static31_raw'][i].copy_(context[:,:31]);wm.anchors.data['environment_origins_world'][i]=0.
        wm.anchors.data['corners_world'][i].copy_(torch.tensor([[.8,-1.,.27],[3.8,-1.,.27],[3.8,1.,.27],[.8,1.,.27]]).expand(80,4,3))
        wm.anchors.data['step_height'][i]=.27;wm.anchors.data['confidence'][i]=1.;wm.anchors.data['initial_age'][i]=0.
        producer=types.SimpleNamespace(kind='LABELLED_SYNTHETIC_CPU_ONLY',plant='own_MOD4_live_USD',run_id='CPU296',generation='CPU296',source_admission_SHA='a'*64,sensor_id='synthetic',environment_ids=tuple(range(80)),episode_ids=(0,)*80)
        wm.anchors.scopes[i]=(producer,'synthetic_'+str(i));learner.add_metadata(i,policy,critic,torch.full((80,),i,dtype=torch.long))
    wm.buffer.ptr=0;wm.buffer.size=64
    before={k:v.detach().clone()for k,v in learner.actor.state_dict().items()};world={k:v.detach().clone()for k,v in wm.model.state_dict().items()}
    diagnostic=learner.update(apply_step=False)
    assert diagnostic and diagnostic['Pi_updates']==diagnostic['critic_updates']==0 and not diagnostic['Fudan_objective_used'] and diagnostic['critic_same_tracking_return']
    assert all(torch.equal(v,before[k])for k,v in learner.actor.state_dict().items());assert all(torch.equal(v,world[k])for k,v in wm.model.state_dict().items())
    assert not learner.critic_optimizer.state and all(int(v['step'])==42940 for v in learner.actor_optimizer.state.values())
    assert all(int(v['step'])==7087 for v in wm.optimizer.state.values())
    put('CPU296_ACTUAL_EXPANSION_AND_TRACKING_H32_NO_STEP.json',dict(passed=True,epoch=time.time(),source_carrier_SHA=proof['SHA'],model_reads=1,CUDA=torch.cuda.is_initialized(),SDK=0,optimizer_steps=0,actor_dim=ACTOR_DIM,critic_dim=CRITIC_DIM,goal_dim=GOAL_DIM,original_actor_and_STD_preserved_at_zero_goal_suffix=True,actor_Adam_offset42940=True,new_critic_Adam0=True,WM7087_preserved=True,synthetic_integration_not_world_accuracy=True,diagnostic=diagnostic))
    print(json.dumps(dict(passed=True,diagnostic=diagnostic)))
except BaseException:
    put('CPU296_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_consumed_read=True));raise
