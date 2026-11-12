"""Short native probe of height commands, ascent reset and reward; no PPO update."""
import torch
from tensordict import TensorDict

def run_probe(env,algorithm):
    algorithm.eval_mode();policy=algorithm.get_policy();before={k:v.clone() for k,v in algorithm.actor.state_dict().items()}
    obs=TensorDict(env._get_observations(),batch_size=[env.num_envs])
    start=env.terrain_summary();samples=[]
    for i in range(180):
        with torch.inference_mode():
            action=policy(obs,stochastic_output=False)
            raw,reward,term,timeout,_=env.step(action)
        assert torch.isfinite(reward).all(),'nonfinite reward'
        assert raw['policy'].shape==(env.num_envs,35) and raw['critic'].shape==(env.num_envs,78)
        obs=TensorDict(raw,batch_size=[env.num_envs])
        if i in (0,59,119,179):samples.append(dict(step=i+1,terrain=env.terrain_summary()['stair_lift'],numerical=env.done_totals.get('numerical'),closure=float(env.closure_error.max())))
    unchanged=all(torch.equal(v,algorithm.actor.state_dict()[k]) for k,v in before.items())
    assert unchanged,'probe changed actor'
    return dict(no_optimizer_update=True,actor_unchanged=True,steps=180,start=start,samples=samples,done_totals=env.done_totals)
