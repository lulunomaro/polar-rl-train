"""Portable target-API test, optimizer intercepted and all source weights unchanged."""
from pathlib import Path
import copy,json,torch
from tensordict import TensorDict
from rsl_rl.storage import RolloutStorage
from rsl_rl.algorithms import PPO
from s4_rsl5_frozen_pair_learner_v1 import S4FrozenPairActor,S4NewSourceCritic,CHOICE
from s4_supported_rollout_storage_v1 import SupportedDomainPPO,DOMAIN
from s4_owned_rollout_audit_v1 import install_rollout_audit

def check(root,refs):
    root=Path(root);initial=torch.get_rng_state().clone();count=0;n,t=13,24
    data=torch.tensor(json.loads((root/'actual_saved35_CPU_input_rows.json').read_bytes())['rows'],dtype=torch.float32)
    def obs(i):
        label=torch.ones(n,1);label[0]=0
        if i==5:label[1]=0
        if i==24:label[2]=0
        return TensorDict(dict(policy=data[i*n:(i+1)*n].clone(),critic=torch.cos(torch.arange(n*38).reshape(n,38).float()*.01+i*.01),**{DOMAIN:label}),batch_size=[n])
    with torch.random.fork_rng(devices=[]):
        groups=dict(actor=['policy'],critic=['critic']);td=obs(0);seed=td.clone();seed[CHOICE]=torch.full((n,1),-1.)
        actor=S4FrozenPairActor(td,groups,'actor',6,expert_refs=refs,routing_seed=20261015)
        critic=S4NewSourceCritic(td,groups,'critic',1,expert_refs=refs)
        alg=SupportedDomainPPO(actor,critic,RolloutStorage('rl',n,t,seed,[6],'cpu'),learning_rate=1e-4,entropy_coef=.005,value_loss_coef=2.)
        a=copy.deepcopy(actor.state_dict());c=copy.deepcopy(critic.state_dict())
        with torch.inference_mode():
            for i in range(t):alg.act(obs(i));alg.process_env_step(obs(i+1),torch.sin(torch.arange(n).float()+i),torch.zeros(n),{'time_outs':torch.zeros(n)})
            alg.compute_returns(obs(t))
        private=actor.generator().get_state().clone()
        def no_step(*a,**k):
            nonlocal count
            count+=1;parameters=list(actor.parameters())+list(critic.parameters())
            assert len(parameters)==14 and all(p.grad is not None and torch.isfinite(p.grad).all() for p in parameters)
        alg.optimizer.step=no_step
        folder=root/'CPU_SHADOW_ROLLOUT_AUDIT_NOT_PHYSICS';assert not folder.exists();folder.mkdir()
        assert SupportedDomainPPO.update is PPO.update
        install_rollout_audit(alg,folder,refs[1]['sha256']);alg.update()
        index=json.loads((folder/'S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json').read_bytes())
        assert len(index['rows'])==1 and index['rows'][0]['optimizer_update_complete'] is True
        assert index['rows'][0]['selection']['eligible_samples']==240
        assert count==20 and not alg.optimizer.state
        assert all(torch.equal(v,a[k]) for k,v in actor.state_dict().items()) and all(torch.equal(v,c[k]) for k,v in critic.state_dict().items())
        assert torch.equal(private,actor.generator().get_state())
    assert torch.equal(initial,torch.get_rng_state()) and not torch.cuda.is_initialized()
    return dict(passed=True,actual_framework_original_update_gradient_steps_intercepted=count,optimizer_updates=0,
        source_weights_STD_gate_critic_unchanged=True,selected_supported_samples=240,
        original_rollout_buffers_durable_before_update=True,audit_no_extra_private_sampling=True,
        CPU13_fixture_not_physical20k=True,no_CUDA=True,actual_GPU_learning_not_inferred=True)
