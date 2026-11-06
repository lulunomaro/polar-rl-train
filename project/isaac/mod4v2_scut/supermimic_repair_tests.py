"""Regression tests for the reproduced semantics and checkpoint failures."""
from pathlib import Path
from types import SimpleNamespace
import argparse,json,sys,time,traceback
import torch


def run(output):
    from . import BINDINGS
    from .supermimic_newton import load_sources,warmstarted_learner,FudanPPOResidualPolicy
    from .supermimic_semantics import ClosedLoopMdp,CONTEXT_DIM,MID,SCHEMA,terrain
    from .supermimic_repaired import repaired_learner,migrate_v1
    from .supermimic_train import cleanup
    Base,Config=load_sources(Path(__file__).with_name('SUPERMIMIC_BINDINGS.json'))
    from supermimic_vendor_v2.geometry import unflatten_state
    torch.manual_seed(9138)
    env=SimpleNamespace(legs=[0,1,2,3],wheels=[4,5],device='cpu',num_envs=4)
    mdp=ClosedLoopMdp(env)
    flat=torch.zeros(4,73);flat[:,2]=.3;flat[:,3]=1
    flat[:,13:19]=torch.arange(6)*.01
    state=unflatten_state(flat)
    context=torch.zeros(4,CONTEXT_DIM);context[:,0]=.6;context[:,35]=.6
    context[:,106]=1;context[:,107:113]=.9;context[:,139:143]=1
    context[:,MID]=mdp.clean_sensors(state);context[:,172:176]=terrain(state)
    action=torch.full((4,6),.1)
    xi=context
    for j in range(32):xi=mdp.project(xi,torch.full_like(xi,.01),state,action,torch.full((4,),j+1),noisy=False)
    assert torch.equal(xi[:,:3],context[:,:3]) and torch.equal(xi[:,35:38],context[:,:3])
    assert torch.equal(xi[:,106:113],context[:,106:113])
    assert torch.equal(xi[:,139:156],context[:,139:156])
    assert torch.equal(xi[:,22:28],xi[:,57:63])
    assert bool((xi[:,14:16]==0).all()&(xi[:,49:51]==0).all())
    q=flat[:,13:43].clone().requires_grad_();st=(*state[:4],q,state[5])
    projected=mdp.project(context,torch.zeros_like(context),st,action,torch.ones(4,dtype=torch.long),noisy=False)
    grad,=torch.autograd.grad(projected[:,:35].sum(),q)
    assert bool(grad[:,:4].abs().sum()>0)
    moved=flat.clone();moved[:,0]+=.8
    assert not torch.equal(terrain(state),terrain(unflatten_state(moved)))
    frames=torch.arange(399)
    assert bool(mdp.valid_imagination_start(frames,32)[-1])
    assert bool(mdp.imagination_timeout(frames[-1:]+1,None).all())
    class Teacher(torch.nn.Module):
        def __init__(self):super().__init__();self.net=torch.nn.Linear(35,6)
        def forward(self,obs,stochastic_output=False):return self.net(obs['policy'])
    teacher=Teacher()
    env.supermimic_mdp=mdp
    env.state=SimpleNamespace(info={'supermimic_state':dict(s=flat,xi=context,a_prev=torch.zeros(4,6),
        f=torch.zeros(4,dtype=torch.long),ep_step=torch.zeros(4,dtype=torch.long))})
    env.export_supermimic_resume=lambda:dict(exact=False)
    cfg=Config(buffer_steps=64,horizon=32,hist=2,goal_frames=2,wm_window=32,wm_batch=4,
        pi_batch=4,wm_batches=4,critic_minibatches=2,wm_hidden=(16,16),policy_hidden=(16,8),
        critic_hidden=(16,8),compile=False,amp='none')
    cls=repaired_learner(warmstarted_learner(Base,teacher))
    learner=cls(env,cfg,output/'learner',aux_hidden=(16,16),aux_batch=4)
    learner.pi.base_clip_before_residual=True
    # Real-shaped synthetic labels are only a unit fixture. Actual plant smoke
    # runs separately and provides training readiness evidence.
    for j in range(64):
        s=flat.clone();s[:,0]+=.001*j
        s1=s.clone();s1[:,0]+=.001
        x=context.clone();x[:,172:176]=terrain(unflatten_state(s))
        x1=context.clone();x1[:,172:176]=terrain(unflatten_state(s1))
        x1[:,22:28]=action;x1[:,57:63]=action
        frame=torch.full((4,),j,dtype=torch.long)
        learner.buffer.add(dict(s=s,s1=s1,a=action,a_prev=action,xi=x,xi1=x1,xi1_valid=torch.ones(4,dtype=torch.bool),
            r=torch.full((4,),.01),f=frame,ep_step=frame.int(),done=torch.zeros(4,dtype=torch.bool),
            term=torch.zeros(4,dtype=torch.bool),trunc=torch.zeros(4,dtype=torch.bool),sample_valid=torch.ones(4,dtype=torch.bool)))
    loss,error=learner.wm_update()
    learner.calibration_updates=31
    learner.policy_update()
    assert learner.counts.pi_bptt_optimizer_steps==1
    payload=learner._checkpoint(True)
    restored=cls(env,cfg,output/'restored',aux_hidden=(16,16),aux_batch=4)
    restored.load_full_checkpoint(payload,allow_environment_reset=True);restored.restore_semantics(payload)
    assert restored.counts==learner.counts
    assert torch.equal(restored.value_mean,learner.value_mean) and torch.equal(restored.value_std,learner.value_std)
    assert all(len(getattr(restored,'opt_'+k).state)>0 for k in ('wm','pi','v','aux'))
    # Pending optimizer phase must never be labelled safe.
    learner.pending_iteration=dict(phase='wm',collect_left=0,wm_left=3)
    assert learner._checkpoint(True)['context_reward_extension']['update_boundary_safe'] is False
    learner.pending_iteration=None
    # Actual cleanup function with failing save must still close both resources.
    from . import supermimic_train as train
    original=train.save;closed=[]
    def fail(*args):raise OSError('INJECTED_SAVE_FAILURE')
    train.save=fail
    try:
        cleanup(learner,SimpleNamespace(close=lambda:closed.append('bridge')),
            SimpleNamespace(close=lambda:closed.append('env')),output,None,False,'original failure')
    finally:train.save=original
    assert closed==['bridge','env']
    # Preserve old output deadzone regression: clamp teacher before residual.
    from supermimic_vendor_v2.networks import Policy
    t=Teacher()
    with torch.no_grad():t.net.weight.zero_();t.net.bias.fill_(7)
    pi=FudanPPOResidualPolicy(Policy(35,6,hist=2,num_joints=6,hidden=(8,)),t,.25)
    pi.base_clip_before_residual=True
    with torch.no_grad():pi.residual.dec[-1].bias.fill_(-.1)
    predicted=pi(torch.zeros(4,2,35),torch.zeros(4,6))
    g,=torch.autograd.grad(predicted.sum(),pi.residual.dec[-1].bias)
    assert bool((g>0).all()) and bool((predicted<6).all())
    return dict(passed=True,CPU_fixture=True,production_PT_reads=0,physics_steps=0,
        command_DR_history_consistent_H32=True,observation_physical_gradient=True,
        terrain_distinguishable=True,finite_timeout_reachable=True,joint_autoregressive_update=True,
        verified_H32=learner.last_bptt_receipt,PopArt_full_resume=True,
        partial_optimizer_boundary_rejected=True,save_failure_cleanup=True,saturated_teacher_can_retreat=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(exist_ok=False)
    try:result=run(a.output)
    except BaseException:result=dict(passed=False,error=traceback.format_exc())
    result['epoch']=time.time();(a.output/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result))
    if not result['passed']:raise SystemExit(1)
