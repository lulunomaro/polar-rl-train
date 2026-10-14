"""Actual framework storage/update path, intercepted optimizer: zero learning."""
from pathlib import Path
import copy, hashlib, inspect, json, os, sys, time, traceback
os.environ['CUDA_VISIBLE_DEVICES'] = ''
D = Path(__file__).resolve().parent; W = D.parent
sys.path[:0] = [str(D), str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),
               str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
import numpy as np
import torch
from tensordict import TensorDict
from rsl_rl.algorithms import PPO
from rsl_rl.storage import RolloutStorage
from rsl_rl.models import MLPModel
from s4_rsl5_frozen_pair_learner_v1 import S4RecordedChoicePPO, S4FrozenPairActor, S4NewSourceCritic, CHOICE

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def equal(a, b):
    if torch.is_tensor(a): return torch.equal(a, b)
    if isinstance(a, dict): return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, (tuple, list)): return len(a) == len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a == b

def main():
    torch.set_num_threads(2)
    api = json.loads((D/'reports/LINUX_ORIGINAL_S4_LEARNER_API_SOURCE_ACTUAL_1792017483857895800.json').read_bytes())
    hashes = {c.__name__: sha(inspect.getfile(c)) for c in (PPO, RolloutStorage, MLPModel)}
    assert hashes['PPO'] == api['sources'][0]['sha256']
    assert hashes['RolloutStorage'] == api['sources'][4]['sha256']
    assert hashes['MLPModel'] == api['sources'][1]['sha256']
    assert S4RecordedChoicePPO.update is PPO.update and S4RecordedChoicePPO.compute_returns is PPO.compute_returns
    assert S4RecordedChoicePPO.process_env_step is PPO.process_env_step
    q = W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015'
    case = 's4_rule_original35_query35_native120_v2'
    receipt = json.loads(sorted((q/'reports').glob(case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes())
    raw = next(Path(r['local_path']) for r in receipt['collected_files'] if r['relative'].endswith('/S4_ROUTING_FULL_CONTROL_ACTUAL.npz'))
    with np.load(raw, allow_pickle=False) as z: saved = z['shared_obs'].copy()
    refs = json.loads((q/'payload/S4_PAIR_SOURCE_MANIFEST.json').read_bytes())['sources']
    for r in refs: r['local_path'] = str(q/'payload/source'/Path(r['local_path']).name)
    bad = 0; gradients = []; errors = []; initial = torch.get_rng_state().clone()
    # randperm in the original mini-batch generator really consumes global RNG.
    # Fork confines that original CPU-only test draw; it is not removed from production.
    with torch.random.fork_rng(devices=[]):
        n, steps = 13, 24
        def obs(t):
            x = torch.from_numpy(saved.reshape(-1,35)[80+t*n:80+(t+1)*n].copy())
            c = torch.cos(torch.arange(n*38).reshape(n,38).float()*.017+t*.01)
            return TensorDict(dict(policy=x, critic=c), batch_size=[n])
        groups = dict(actor=['policy'], critic=['critic'])
        def new():
            td = obs(0); extended = td.clone(); extended[CHOICE] = torch.full((n,1), -1.)
            actor = S4FrozenPairActor(td,groups,'actor',6,expert_refs=refs,routing_seed=20261015)
            critic = S4NewSourceCritic(td,groups,'critic',1,expert_refs=refs)
            storage = RolloutStorage('rl',n,steps,extended,[6],'cpu')
            return S4RecordedChoicePPO(actor,critic,storage,learning_rate=1e-4)
        alg = new(); frozen_before = copy.deepcopy(alg.actor.state_dict()); critic_before = copy.deepcopy(alg.critic.state_dict())
        assert not alg.optimizer.state
        with torch.inference_mode():
            for t in range(steps):
                td = obs(t); action = alg.act(td)
                assert CHOICE not in td.keys()
                z = alg.actor.z.clone(); logits = alg.actor.logits.clone()
                cat = torch.distributions.Categorical(logits=logits)
                normal = torch.distributions.Independent(torch.distributions.Normal(alg.actor.selected_mean, alg.actor.selected_std),1)
                independent = cat.log_prob(z)+normal.log_prob(action)
                errors.append(float((independent-alg.transition.actions_log_prob).abs().max()))
                assert errors[-1] < 2e-5
                assert torch.equal(alg.transition.actions,action) and (action.abs()>6).any()
                dones = torch.zeros(n,dtype=torch.long); dones[t%n] = int(t%5==0)
                rewards = torch.sin(torch.arange(n).float()+t*.1)
                alg.process_env_step(obs(t+1),rewards,dones,{'time_outs':torch.zeros(n)})
                assert torch.equal(alg.storage.observations[CHOICE][t,:,0],z.float())
                assert torch.equal(alg.storage.distribution_params[0][t],logits)
            alg.compute_returns(obs(steps))
        owned = alg.actor.generator().get_state().clone()
        calls = 0
        def intercepted_step(*a, **kw):
            nonlocal calls
            calls += 1
            parameters = list(alg.actor.parameters())+list(alg.critic.parameters())
            assert len(parameters)==14 and all(p.grad is not None and torch.isfinite(p.grad).all() for p in parameters)
            assert any(p.grad.abs().sum()>0 for p in alg.actor.gate.parameters())
            assert any(p.grad.abs().sum()>0 for p in alg.critic.parameters())
            assert all(not list(e.parameters()) for e in alg.actor.experts)
            gradients.append(float(sum(p.grad.square().sum() for p in parameters)))
        alg.optimizer.step = intercepted_step
        losses = alg.update()  # ORIGINAL update, including storage/timeout/GAE/KL/entropy path
        assert calls == 20 and len(gradients)==20 and alg.storage.step==0
        assert torch.equal(owned,alg.actor.generator().get_state()), 'Historical minibatches must not resample latent/action'
        assert equal(frozen_before,alg.actor.state_dict()) and equal(critic_before,alg.critic.state_dict())
        assert not alg.optimizer.state and alg.actor.verify_frozen()
        old = torch.tensor([[.2,-.2],[0.,0.]])
        kl = alg.actor.get_kl_divergence((old,),(old+torch.tensor([2.,-2.]),))
        independent_kl = torch.distributions.kl_divergence(torch.distributions.Categorical(logits=old),torch.distributions.Categorical(logits=old+torch.tensor([2.,-2.])))
        assert torch.allclose(kl,independent_kl,atol=1e-6,rtol=0) and (kl>0).all()
        # Save/load the actual algorithm-owned state, NOT an environment receipt.
        state = copy.deepcopy(alg.save())
        path = D/'S4_ACTUAL_RSL5_CPU_ALGORITHM_ROUNDTRIP_FIXTURE.pt'
        assert not path.exists(); torch.save(state,path)
        restored = new(); restored.load(torch.load(path,weights_only=False,map_location='cpu'))
        assert equal(state,restored.save())
        with torch.inference_mode():
            next_a = alg.act(obs(30)); next_b = restored.act(obs(30))
            assert torch.equal(next_a,next_b) and torch.equal(alg.actor.z,restored.actor.z)
        for mutation in ('source_sha','routing_device','missing_owned','frozen_weight','missing_z','fractional_z','oracle','raw_width','nonfinite'):
            victim = new(); ck = copy.deepcopy(state); td = obs(2)
            try:
                if mutation=='source_sha': ck['S4_owned_learning']['expert_sha'][0]='0'*64; victim.load(ck)
                elif mutation=='routing_device': ck['S4_owned_learning']['actor_owned']['routing_device']='cuda:0'; victim.load(ck)
                elif mutation=='missing_owned': del ck['S4_owned_learning']; victim.load(ck)
                elif mutation=='frozen_weight': ck['actor_state_dict']['frozen_std'][0,0]+=1; victim.load(ck)
                elif mutation in ('missing_z','fractional_z'):
                    td[CHOICE]=torch.full((n,1),-1. if mutation=='missing_z' else .5); victim.actor(td,stochastic_output=True)
                elif mutation=='oracle': td['policy'][:,29]=1; victim.actor(td)
                elif mutation=='raw_width': victim.actor(td,stochastic_output=True); victim.actor.get_output_log_prob(torch.zeros(n,5))
                elif mutation=='nonfinite': td['policy'][0,0]=float('nan'); victim.actor(td)
            except (AssertionError,KeyError): bad+=1
            else: raise AssertionError('Bad contract accepted: '+mutation)
    assert bad==9 and torch.equal(initial,torch.get_rng_state()) and not torch.cuda.is_initialized()
    import importlib.metadata as m
    report=dict(epoch=time.time(),passed=True,actual_RSL5_framework_source_SHA_equal=hashes,
        local_versions={k:m.version(k) for k in ('torch','tensordict','rsl-rl-lib')},target_versions=api['versions'],
        local_torch_tensordict_differ_target_GPU_not_claimed=True,actual_saved35_source=dict(path=str(raw),sha256=sha(raw)),
        synthetic_critic_reward_done_and_private_sampled_z_action_not_physical_rollout=True,
        rollout_controls=steps,num_CPU_fixture_rows=n,stored_z_old_gate_logits_raw_action=True,
        original_update_GAE_timeout_clip_adaptive_schedule_unchanged=True,
        original_minibatch_updates_intercepted_no_parameter_step=calls,optimizer_updates=0,
        gate_and_newcritic_gradient_ownership=True,frozen_expert_STD_unchanged=True,
        joint_logp_max_error=max(errors),joint_KL_includes_gate=True,historical_update_no_private_resampling=True,
        algorithm_gate_critic_optimizer_private_generator_disk_roundtrip_and_next_draw_exact=True,
        CPU_fixture=dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path)),negative_cases=bad,
        global_CPU_RNG_restored_after_fork_original_shuffle_consumption_disclosed=True,no_CUDA=True,
        environment_DR_globalnamed_privateCPUCUDA_and_GPU_native_fullstate_pending=True,actual_learning_admitted=False)
    p=D/'reports/S4_ACTUAL_RSL5_STORAGE_JOINT_UPDATE_GRADIENT_ONLY_CPU_ACTUAL.json'; assert not p.exists()
    p.write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(dict(passed=True,report=str(p),intercepted_update_steps=calls,optimizer_updates=0,negative_cases=bad)))

if __name__=='__main__':
    try: main()
    except Exception:
        p=D/'reports'/('S4_ACTUAL_RSL5_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
        p.write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),optimizer_updates_requested=0,GPU=False)),encoding='utf8')
        raise
