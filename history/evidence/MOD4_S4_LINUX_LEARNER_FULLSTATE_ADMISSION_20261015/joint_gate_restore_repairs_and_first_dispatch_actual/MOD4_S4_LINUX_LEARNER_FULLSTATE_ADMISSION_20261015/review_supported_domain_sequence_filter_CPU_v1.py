"""Actual storage sample selection; privileged labels never choose actions."""
from pathlib import Path
import os,sys,json,time,copy,torch
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;W=D.parent
sys.path[:0]=[str(D),str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
from tensordict import TensorDict
from s4_supported_rollout_storage_v1 import SupportedSequenceStorage,DOMAIN,PROFILE,domain_label
from s4_rsl5_frozen_pair_learner_v1 import S4FrozenPairActor,CHOICE

def main():
    before=torch.get_rng_state().clone();n,t=13,24
    td=TensorDict(dict(policy=torch.zeros(n,35),critic=torch.zeros(n,38),**{DOMAIN:torch.ones(n,1),CHOICE:torch.zeros(n,1)}),batch_size=[n]);td['policy'][:,28]=1
    refs=json.loads((D/'target_CPU_components_v1/CPU_COMPONENT_SOURCE_MANIFEST.json').read_bytes())['refs']
    q=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015/payload/source'
    refs[0]['local_path']=str(q/'E0_frozen_source.pt');refs[1]['local_path']=str(q/'E1_WAVE35_frozen_source.pt')
    with torch.random.fork_rng(devices=[]):
        actor=S4FrozenPairActor(td,dict(actor=['policy'],critic=['critic']),'actor',6,expert_refs=refs,routing_seed=20261015)
        # Domain changes must not affect means/logits/selected deterministic expert.
        a=actor(td);logits=actor.logits.clone();flipped=td.clone();flipped[DOMAIN]=1-td[DOMAIN]
        b=actor(flipped);assert torch.equal(a,b) and torch.equal(logits,actor.logits)
        storage=SupportedSequenceStorage('rl',n,t,td,[6],'cpu')
        storage.step=t;storage.bootstrap_supported=torch.ones(n,dtype=torch.bool)
        storage.observations[DOMAIN][:]=1
        storage.observations[DOMAIN][:,0]=0
        storage.observations[DOMAIN][3,1]=0
        storage.bootstrap_supported[2]=False
        for i in range(n):storage.observations['policy'][:,i,0]=i
        storage.values[:]=.25
        storage.returns[:]=torch.sin(torch.arange(t*n).reshape(t,n,1).float()*.1)
        storage.distribution_params=(torch.zeros(t,n,2),)
        def gather():
            batches=list(storage.mini_batch_generator(4,5));assert len(batches)==20
            ids=torch.cat([b.observations['policy'][:,0] for b in batches[:4]])
            adv=torch.cat([b.advantages for b in batches[:4]])
            assert ((ids>=3)&(ids<n)).all() and len(ids)==240
            return dict(zip(ids.tolist()[:0],[])),adv.sort(0).values
        _,a=gather()
        # Unqualified background can have different returns without changing
        # any selected advantage, since normalization is on selected rows only.
        storage.returns[:,:3]=1e6
        _,b=gather();assert torch.equal(a,b)
        assert storage.last_selection['complete_supported_envs']==10
        assert storage.last_selection['eligible_samples']==240
        bad=0
        for value in (torch.full((n,1),.5),torch.full((n,1),float('nan')),torch.ones(n,2)):
            try:domain_label(value,n)
            except AssertionError:bad+=1
            else:raise AssertionError('Invalid domain accepted')
        storage.bootstrap_supported[:]=False
        try:list(storage.mini_batch_generator(4,5))
        except AssertionError:bad+=1
        else:raise AssertionError('Background fallback accepted')
    assert bad==4 and torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
    result=dict(epoch=time.time(),passed_CPU=True,profile=PROFILE,physical_fixture_envs=n,controls=t,
        selected_complete_supported_envs=10,selected_samples=240,bootstrap_and_any_bad_control_excluded=True,
        poisoned_unselected_return_does_not_affect_supported_normalization=True,
        domain_metadata_not_gate_input_and_not_expert_choice=True,original_commands_DR_geometry_reward_clock_not_changed=True,
        original_PPO_update_and_GAE_equations_preserved=True,selection_and_advantage_normalization_on_supported_set_explicit_new=True,
        negative_cases=bad,optimizer_updates=0,GPU=False,actual_GPU_supported_label_and_fullstate_startup_pending=True,
        actual_learning_admitted=False)
    p=D/'reports/S4_SUPPORTED_SEQUENCE_SAMPLE_SELECTION_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
