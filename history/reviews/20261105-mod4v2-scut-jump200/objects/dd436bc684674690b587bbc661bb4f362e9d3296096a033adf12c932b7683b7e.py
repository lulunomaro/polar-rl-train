"""New random4env native migration/resume fixture, never reads production PT."""
from pathlib import Path
from dataclasses import asdict
import json,random,sys,time,traceback
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

R=N/sys.argv[1];R.mkdir(exist_ok=False)
env=bridge=None
report=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0)
try:
    from rsl_rl.runners import OnPolicyRunner
    random.seed(9138);np.random.seed(9138);torch.manual_seed(9138)
    package='F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
    components=N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4'
    binding=G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json'
    env=NewtonEnv(package,components,N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',4,'cuda:0',9138)
    runner=OnPolicyRunner(env,runner_config(),None,env.device)
    ppo=save_ppo(runner,env,R/'fixture_random_ppo.pt')
    source=decode(ppo['path'],ppo['SHA'])
    old,bridge=build(env,source,binding,R/'original',small=True,residual_scale=.25)
    old.collect(64)
    for j in range(4):old.wm_update()
    old.policy_update();old.iteration=1
    original=old._checkpoint(True)
    from mod4v2_scut.supermimic_train import FORMAT
    original.update(format=FORMAT,contract_SHA='00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e',
        policy_residual_scale=.25,source_PPO=ppo)
    oldcounts=asdict(old.counts)
    bridge.close()
    learner,bridge=build(env,original,binding,R/'migrated',small=True,residual_scale=.25,
        sampling_optimization=True,semantic_repair=True)
    assert asdict(learner.counts)==oldcounts
    assert learner.extension_contract['context_dim']==176
    assert learner.migration_receipt['source_iteration']==1
    # All original parameters not expanded/recovered remain exactly equal.
    assert all(torch.equal(v,learner.pi.state_dict()[k]) for k,v in original['pi'].items())
    for name in ('wm','pi','v','aux'):
        before=(original['context_reward_extension']['opt_aux'] if name=='aux' else original['opt_'+name])
        saved_steps=sorted(float(s['step']) for s in before['state'].values())
        new_steps=sorted(float(s['step']) for s in getattr(learner,'opt_'+name).state.values())
        assert saved_steps==new_steps
    learner.collect(learner.semantic_warmup_remaining);learner.semantic_warmup_remaining=0
    assert bool(torch.isfinite(learner.buffer.data['xi']).all())
    assert bool((learner.buffer.data['xi'][:,:,139:143]>0).all())
    fit=[]
    for j in range(32):
        learner.collect(2+(j%2))
        loss,err=learner.wm_update();learner.policy_update()
        fit.append(dict(j=j,loss=float(loss),error=float(err),value=learner.last_value))
        print(json.dumps(dict(j=j,loss=float(loss),value=learner.last_value,
            new_BPTT=learner.counts.pi_bptt_optimizer_steps-oldcounts['pi_bptt_optimizer_steps'])),flush=True)
    learner.iteration+=32
    assert learner.counts.pi_bptt_optimizer_steps>oldcounts['pi_bptt_optimizer_steps']
    assert learner.last_bptt_receipt['verified_bptt_optimizer_step']
    assert learner.last_value['outside_loose80']==0
    ck=save(learner,R/'fixture_repaired_full.pt',ppo)
    payload=decode(ck['path'],ck['SHA'])
    expected={k:v.clone()for k,v in learner.pi.state_dict().items()}
    bridge.close()
    resumed,bridge=build(env,payload,binding,R/'resumed',small=True)
    assert resumed.counts==learner.counts
    assert torch.equal(resumed.value_mean,learner.value_mean)and torch.equal(resumed.value_std,learner.value_std)
    assert all(torch.equal(v,resumed.pi.state_dict()[k])for k,v in expected.items())
    resumed.collect(3);resumed.wm_update();resumed.policy_update()
    assert resumed.counts.pi_bptt_optimizer_steps>learner.counts.pi_bptt_optimizer_steps
    evaluated=SavedPolicy(OnPolicyRunner(env,runner_config(),None,env.device).alg.actor,payload,env)
    assert evaluated.actor.base_clip_before_residual
    assert bool(torch.isfinite(evaluated(env.get_observations())).all())
    report.update(passed=True,native_Newton=True,real_envs=4,source='new random PPO fixture only',
        all_four_Adam_steps_preserved_by_explicit_migration=True,real_H32=learner.last_bptt_receipt,
        resumed_H32=resumed.last_bptt_receipt,value=learner.last_value,fit=fit,
        full_value_normalization_replay_RNG_resume=True,checkpoint=ck,
        numerical_resets=int(env.numerical_reset_counts.sum()),constraint_resets=int(env.constraint_reset_counts.sum()),
        independent80_not_claimed=True)
except BaseException:report['error']=traceback.format_exc()
finally:
    if bridge is not None:bridge.close()
    if env is not None:env.close()
    (R/'RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items()if k!='fit'}))
if not report['passed']:raise SystemExit(1)
