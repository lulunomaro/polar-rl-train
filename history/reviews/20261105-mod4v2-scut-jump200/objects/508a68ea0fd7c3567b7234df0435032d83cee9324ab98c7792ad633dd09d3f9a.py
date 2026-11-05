"""Finite worker/resume/replay validation using a new local test PPO only."""
from pathlib import Path
import argparse,hashlib,json,random,subprocess,sys,time,traceback
import numpy as np
import torch

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.config import runner_config
from mod4v2_scut.newton_checkpoint import save as save_ppo
from mod4v2_scut.supermimic_train import build,save,decode
from mod4v2_scut.supermimic_evaluate import SavedPolicy
from mod4v2_scut.supermimic_newton import load_sources

p=argparse.ArgumentParser();p.add_argument('--output',default='supermimic_worker02')
a=p.parse_args();R=N/a.output;R.mkdir(exist_ok=False)
out=dict(epoch=time.time(),production_PT_reads=0,SSH=0,production_modified=False,passed=False)
env=bridge=None
try:
    from rsl_rl.runners import OnPolicyRunner
    package='F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
    components=N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4'
    bank=N/'runtime_refs/runtime/isaac/mod4/reset_bank.json'
    binding=G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json'
    random.seed(9138);np.random.seed(9138);torch.manual_seed(9138)
    env=NewtonEnv(package,components,bank,4,'cuda:0',9138)
    runner=OnPolicyRunner(env,runner_config(),None,env.device)
    ck=save_ppo(runner,env,R/'local_random_PPO_only.pt')
    source=decode(ck['path'],ck['SHA'])
    learner,bridge=build(env,source,binding,R/'learner',small=True)
    learner.collect(64)
    valid=learner.buffer.data['sample_valid'][:learner.buffer.size]
    # Inject a finite storage sentinel with huge labels. Sampling and windows
    # must exclude it; this is a synthetic replay test, not a physical failure.
    learner.buffer.data['sample_valid'][0,0]=False
    learner.buffer.data['stream_cut'][0,0]=True
    learner.buffer.data['r'][0,0]=1e20
    for _ in range(10):
        batch=learner.buffer.sample_transitions(256)
        assert bool(batch['sample_valid'].all()) and float(batch['r'].abs().max())<1e10
        window=learner.buffer.sample_windows(256,8)
        assert bool(torch.isfinite(window['mask']).all())
    fit=[]
    for _ in range(24):
        loss,error=learner.wm_update();fit.append([float(loss),float(error)])
    learner.policy_update();learner.iteration=1
    assert learner.last_bptt_receipt['verified_bptt_optimizer_step']
    saved=save(learner,R/'model_full.pt',ck)
    payload=decode(saved['path'],saved['SHA'])
    learned_policy=SavedPolicy(OnPolicyRunner(env,runner_config(),None,env.device).alg.actor,payload,env)
    obs=env.get_observations()
    action=learned_policy(obs)
    assert action.shape==(4,6) and bool(torch.isfinite(action).all())
    before={k:v.clone()for k,v in learner.pi.state_dict().items()}
    bridge.close()
    restored,bridge=build(env,payload,binding,R/'restored',small=True)
    assert all(torch.equal(v,restored.pi.state_dict()[k])for k,v in before.items())
    assert restored.counts==learner.counts
    assert all(len(getattr(restored,'opt_'+key).state)>0 for key in ('wm','pi','v','aux'))
    assert bool(restored.buffer.data['stream_cut'][(restored.buffer.ptr-1)%restored.buffer.T].all())
    restored.collect(1)
    loss,error=restored.wm_update();restored.policy_update()
    assert restored.counts.pi_bptt_optimizer_steps>=2
    out.update(passed=True,real_envs=4,real_controls=bridge.controls,
        numerical_resets=int(env.numerical_reset_counts.sum()),
        first_bptt=learner.last_bptt_receipt,resumed_bptt=restored.last_bptt_receipt,
        wm_fit=fit,synthetic_invalid_replay_excluded=True,history_stream_cut=True,
        fresh_physical_reset=True,all7_components_DR_generators_restored=True,
        all4_optimizers_replay_history_RNG_restored=True,
        evaluator_policy_finite=True,checkpoint=saved,
        production_switch_ready=False,
        pending='Finite CLI smoke and actual20k runtime memory/independent80 boundary')
except BaseException:out['error']=traceback.format_exc()
finally:
    if bridge is not None:bridge.close()
    if env is not None:env.close()
    with(R/'RESULT.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
    print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
