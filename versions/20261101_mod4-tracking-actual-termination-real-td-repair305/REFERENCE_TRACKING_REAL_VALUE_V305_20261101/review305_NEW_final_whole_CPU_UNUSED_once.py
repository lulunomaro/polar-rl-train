import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
sys.path.insert(0,str(N));from tracking_task305 import validate_final,validate_task
def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2)
try:
    assert not(R/'CPU305_NEW_FINAL_CONSUMED.json').exists()
    complete=json.loads((R/'ROOT305_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert complete['passed_collection']and complete['owner_closed']['canonical_None']and complete['owner_closed']['shared_locks_free']
    formal=complete['formals']['jump_72'];role=complete['roles']['jump_72'];task=json.loads((N/'TASK305_FROZEN.json').read_bytes());validate_task(task)
    assert role['qualified_formal']and role['private_EX_free']and formal['transfers']==1 and formal['two_host_SHA_equal']
    validate_final(role['final'],task,role['final']['original_finite_owner_GO'])
    put('CPU305_NEW_FINAL_CONSUMED.json',dict(epoch=time.time(),purpose='NEW final tracking103/106/fullthreeoptimizers/teacher/fullstate/phase once',modelreads_max=1,CUDA=False))
    import torch
    raw=Path(formal['path']).read_bytes();assert len(raw)==formal['bytes']and hashlib.sha256(raw).hexdigest()==formal['SHA']
    ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
    assert ck['kind']=='REFERENCE_TRACKING_BPTT305_COMPLETE'
    count=[0]
    def finite(x):
        if torch.is_tensor(x):
            count[0]+=1
            if x.is_floating_point():assert torch.isfinite(x).all()
        elif isinstance(x,dict):
            for v in x.values():finite(v)
        elif isinstance(x,(list,tuple)):
            for v in x:finite(v)
    finite(ck);s=ck['student'];pi=ck['actual_new_Pi_updates'];wm=ck['total_WM_updates']
    assert pi==ck['actual_new_critic_updates']==s['Pi_updates']==s['critic_updates']>0
    assert wm==9712+ck['actual_new_WM_updates']
    assert s['actor_state_dict']['mlp.0.weight'].shape==(128,103)and s['critic_state_dict']['mlp.0.weight'].shape==(128,106)
    teacher=ck['teacher_full_PPO_state'];assert teacher['iter']==2135 and all(int(v['step'])==42940 for v in teacher['optimizer_state_dict']['state'].values())
    assert torch.equal(s['actor_state_dict']['distribution.std_param'],teacher['actor_state_dict']['distribution.std_param'])
    for scope,offset in(('actor',45533),('critic',2593)):
        optimizer=s[scope+'_optimizer'];bindings=s['identity']['targets'][scope]['parameter_bindings'];ids={v['optimizer_id']:v['state_key']for v in bindings}
        assert len(optimizer['state'])==(9 if scope=='actor'else 8)
        for pid,v in optimizer['state'].items():
            key=ids[pid];assert int(v['step'])==(42940 if key=='distribution.std_param'else offset+pi)
            assert v['exp_avg'].shape==v['exp_avg_sq'].shape==s[scope+'_state_dict'][key].shape
    assert all(int(v['step'])==wm for v in ck['world_model']['world_optimizer']['state'].values())
    assert 'target_critic_state_dict'in s and s['actor_Adam_offset']==45533 and s['critic_Adam_offset']==2593
    assert not s['old_Fudan_return']and s['critic_same_tracking_return']and s['goal_dim']==59
    assert ck['reference_phase_steps'].shape==(80,)and not ck['mixed_ground_JUMP_state']['flat_mask'].any()
    assert set(ck['target_DR_state']['components'])=={'sensor','feedback','physics_action_queue','spring','damping','COM','PD'}
    row=dict(passed=True,epoch=time.time(),path=formal['path'],SHA=formal['SHA'],bytes=formal['bytes'],finite_tensors=count[0],Pi=pi,critic=pi,totalWM=wm,newWM=wm-9712,actor103=True,critic106=True,goal59=True,three_optimizers=True,teacher_full17Adam42940=True,Fudan_used=False,critic_same_tracking_return=True,CUDA=torch.cuda.is_initialized(),modelreads=1,strict270success_not_inferred=True)
    put('ROOT305_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json',row);print(json.dumps(row))
except BaseException:
    put('CPU305_NEW_FINAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True));raise
