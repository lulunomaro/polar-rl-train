"""Source-bound target CPU admission; no environment/GPU/training admission."""
from pathlib import Path
import hashlib, inspect, json, os, sys, time, copy
assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import torch
from tensordict import TensorDict
from rsl_rl.algorithms import PPO
from rsl_rl.storage import RolloutStorage
from s4_rsl5_frozen_pair_learner_v1 import S4RecordedChoicePPO, S4FrozenPairActor, S4NewSourceCritic, CHOICE

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def equal(a,b):
    if torch.is_tensor(a): return torch.equal(a,b)
    if isinstance(a,dict): return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)): return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b

def main():
    torch.set_num_threads(2)
    manifest=json.loads((ROOT/'CPU_COMPONENT_SOURCE_MANIFEST.json').read_bytes())
    assert manifest['approved_GPU'] is False and manifest['approved_PPO'] is False
    for name,h in manifest['files'].items():
        p=ROOT/name; assert p.resolve().is_relative_to(ROOT.resolve()) and sha(p)==h
    assert sha(inspect.getfile(PPO))==manifest['actual_target_PPO_SHA']
    assert S4RecordedChoicePPO.update is PPO.update and S4RecordedChoicePPO.compute_returns is PPO.compute_returns
    shared=torch.tensor(json.loads((ROOT/'actual_saved35_CPU_input_rows.json').read_bytes())['rows'],dtype=torch.float32)
    n,steps=13,24; groups=dict(actor=['policy'],critic=['critic'])
    def td(t):
        return TensorDict(dict(policy=shared[t*n:(t+1)*n].clone(),
            critic=torch.cos(torch.arange(n*38).reshape(n,38).float()*.01+t*.01)),batch_size=[n])
    def new():
        obs=td(0); seed=obs.clone(); seed[CHOICE]=torch.full((n,1),-1.)
        a=S4FrozenPairActor(obs,groups,'actor',6,expert_refs=manifest['refs'],routing_seed=20261015)
        c=S4NewSourceCritic(obs,groups,'critic',1,expert_refs=manifest['refs'])
        return S4RecordedChoicePPO(a,c,RolloutStorage('rl',n,steps,seed,[6],'cpu'),learning_rate=1e-4)
    before=torch.get_rng_state().clone(); intercepted=0
    with torch.random.fork_rng(devices=[]):
        alg=new(); parameters=copy.deepcopy(alg.save())
        with torch.inference_mode():
            for t in range(steps):
                actions=alg.act(td(t))
                assert torch.equal(alg.transition.observations[CHOICE][:,0],alg.actor.z.float())
                assert (actions.abs()>6).any()
                alg.process_env_step(td(t+1),torch.sin(torch.arange(n).float()+t*.1),torch.zeros(n),{'time_outs':torch.zeros(n)})
            alg.compute_returns(td(steps))
        private=alg.actor.generator().get_state().clone()
        def no_step(*a,**kw):
            nonlocal intercepted
            intercepted+=1
            p=list(alg.actor.parameters())+list(alg.critic.parameters())
            assert len(p)==14 and all(v.grad is not None and torch.isfinite(v.grad).all() for v in p)
            assert all(not list(e.parameters()) for e in alg.actor.experts)
        alg.optimizer.step=no_step
        loss=alg.update()
        assert intercepted==20 and not alg.optimizer.state and alg.storage.step==0
        assert torch.equal(private,alg.actor.generator().get_state())
        assert equal(parameters['actor_state_dict'],alg.actor.state_dict())
        assert equal(parameters['critic_state_dict'],alg.critic.state_dict())
        ck=copy.deepcopy(alg.save()); out=ROOT/'S4_TARGET_CPU_ALGORITHM_FIXTURE.pt'; assert not out.exists();torch.save(ck,out)
        resumed=new(); resumed.load(torch.load(out,map_location='cpu',weights_only=False)); assert equal(ck,resumed.save())
        with torch.inference_mode(): assert torch.equal(alg.act(td(24)),resumed.act(td(24)))
        assert alg.actor.verify_frozen()
    assert torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
    import importlib.metadata as m
    result=dict(epoch=time.time(),pid=os.getpid(),passed_target_CPU_component=True,
        root=str(ROOT),source_manifest_SHA=sha(ROOT/'CPU_COMPONENT_SOURCE_MANIFEST.json'),
        actual_versions={k:m.version(k) for k in ('torch','tensordict','rsl-rl-lib')},
        actual_installed_PPO_SHA=sha(inspect.getfile(PPO)),original_update_GAE_process_step_unchanged=True,
        actual_historical_storage_z_raw_and_old_logits=True,intercepted_gradient_steps=intercepted,
        optimizer_updates=0,gate_critic_gradient_ownership=True,expert_STD_weights_frozen=True,
        own_algorithm_disk_roundtrip_private_next_action_exact=True,CUDA_initialized=False,
        original_global_shuffle_test_confined_by_CPU_fork=True,
        fixture=dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out)),
        original_wholeW35_environment_fullrestore_GPU_not_yet_executed=True,
        gate_GPU_PPO_admitted=False,CPU_fixture_not_training_source=True)
    p=ROOT/'TARGET_S4_RSL5_COMPONENT_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

if __name__=='__main__': main()
