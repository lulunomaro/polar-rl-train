"""Original PPO update with supported storage, all optimizer steps intercepted."""
from pathlib import Path
import os,sys,json,time,copy,torch
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;W=D.parent
sys.path[:0]=[str(D),str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
from tensordict import TensorDict
from rsl_rl.storage import RolloutStorage
from rsl_rl.algorithms import PPO
from s4_rsl5_frozen_pair_learner_v1 import S4FrozenPairActor,S4NewSourceCritic,CHOICE
from s4_supported_rollout_storage_v1 import SupportedDomainPPO,DOMAIN
def main():
    torch.set_num_threads(2);n,t=13,24;initial=torch.get_rng_state().clone()
    data=torch.tensor(json.loads((D/'target_CPU_components_v1/actual_saved35_CPU_input_rows.json').read_bytes())['rows'])
    refs=json.loads((D/'target_CPU_components_v1/CPU_COMPONENT_SOURCE_MANIFEST.json').read_bytes())['refs']
    q=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015/payload/source'
    refs[0]['local_path']=str(q/'E0_frozen_source.pt');refs[1]['local_path']=str(q/'E1_WAVE35_frozen_source.pt')
    def obs(i):
        label=torch.ones(n,1);label[0]=0
        if i==5:label[1]=0
        if i==24:label[2]=0
        return TensorDict(dict(policy=data[i*n:(i+1)*n].clone(),critic=torch.cos(torch.arange(n*38).reshape(n,38).float()*.01+i*.01),**{DOMAIN:label}),batch_size=[n])
    groups=dict(actor=['policy'],critic=['critic']);count=0
    with torch.random.fork_rng(devices=[]):
        td=obs(0);seed=td.clone();seed[CHOICE]=torch.full((n,1),-1.)
        actor=S4FrozenPairActor(td,groups,'actor',6,expert_refs=refs,routing_seed=20261015)
        critic=S4NewSourceCritic(td,groups,'critic',1,expert_refs=refs)
        storage=RolloutStorage('rl',n,t,seed,[6],'cpu')
        alg=SupportedDomainPPO(actor,critic,storage,learning_rate=1e-4,entropy_coef=.005,value_loss_coef=2.0)
        before={k:v.clone() for k,v in actor.state_dict().items()};cbefore={k:v.clone() for k,v in critic.state_dict().items()}
        with torch.inference_mode():
            for i in range(t):
                alg.act(obs(i));alg.process_env_step(obs(i+1),torch.sin(torch.arange(n).float()+i),torch.zeros(n),{'time_outs':torch.zeros(n)})
            alg.compute_returns(obs(t))
        private=actor.generator().get_state().clone()
        def no_step(*a,**kw):
            nonlocal count
            count+=1;p=list(actor.parameters())+list(critic.parameters())
            assert len(p)==14 and all(x.grad is not None and torch.isfinite(x.grad).all() for x in p)
        alg.optimizer.step=no_step
        assert SupportedDomainPPO.update is PPO.update
        result=alg.update();assert count==20 and alg.storage.last_selection['complete_supported_envs']==10
        assert all(torch.equal(v,before[k]) for k,v in actor.state_dict().items())
        assert all(torch.equal(v,cbefore[k]) for k,v in critic.state_dict().items())
        assert not alg.optimizer.state and torch.equal(private,actor.generator().get_state())
        state=alg.save();assert state['S4_supported_training_exposure']['last_selection']['eligible_samples']==240
    assert torch.equal(initial,torch.get_rng_state()) and not torch.cuda.is_initialized()
    report=dict(epoch=time.time(),passed_CPU=True,original_update_20_gradient_steps_intercepted=count,
        optimizer_updates=0,production_loss_coefficients=dict(value_loss=2.0,entropy=.005),
        selected_supported24_bootstrap_samples=240,all13_physical_fixture_rows_sampled_without_privileged_action_selection=True,
        actual_saved35_fixed_inputs_plus_synthetic_critic_rewards_labels=True,
        domain_metadata_not_policy_input=True,original_GAE_and_PPO_update_unchanged=True,
        source_STD_and_expert_gate_critic_weights_unchanged=True,private_RNG_no_redraw_during_update=True,
        target_GPU_supported_metadata_and_source_bound_startup_pending=True,gate_learning_admitted=False)
    p=D/'reports/S4_SUPPORTED_ACTUAL_PPO_GRADIENT_ONLY_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
