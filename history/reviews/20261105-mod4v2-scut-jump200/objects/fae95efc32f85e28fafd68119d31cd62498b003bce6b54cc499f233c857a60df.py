"""ABBA real Newton collect + WM/aux4 + H32/critic4; new random teacher."""
from pathlib import Path
from dataclasses import asdict
import argparse,copy,json,random,sys,time,traceback
import numpy as np
import torch
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.config import runner_config
from mod4v2_scut.newton_checkpoint import FORMAT,environment_state
from mod4v2_scut.supermimic_train import build,save,decode
from mod4v2_scut.newton_sampling import install_sampling
from mod4v2_scut.supermimic_speed import enable_fused_adam,enable_scripted_geometry
p=argparse.ArgumentParser();p.add_argument('--output',default='sampling_total_ABBA07')
p.add_argument('--scripted-geometry',action='store_true');args=p.parse_args()
R=N/args.output;R.mkdir(exist_ok=False)
out=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0,active_modified=False)
env=bridge=None
def cpu(value):
    if torch.is_tensor(value):return value.detach().cpu().clone()
    if isinstance(value,dict):return {k:cpu(v)for k,v in value.items()}
    if isinstance(value,list):return [cpu(v)for v in value]
    if isinstance(value,tuple):return tuple(cpu(v)for v in value)
    return copy.deepcopy(value)
try:
    from rsl_rl.runners import OnPolicyRunner
    random.seed(9194);np.random.seed(9194);torch.manual_seed(9194)
    env=NewtonEnv('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
        N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
        N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',128,'cuda:0',9194)
    runner=OnPolicyRunner(env,runner_config(),None,env.device)
    source=dict(**runner.alg.save(),**environment_state(env),format=FORMAT,reward_family='FUDAN_JUMP',
        num_envs=env.num_envs,iter=0,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
        python_rng=random.getstate(),numpy_rng=np.random.get_state())
    learner,bridge=build(env,source,G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json',R/'learner',residual_scale=.25)
    from supermimic_vendor_v2 import networks
    import ctx_reward_learner
    original_geometry={name:getattr(networks,name)for name in ('invariant_features','yaw_mat','so3_exp','so3_log')}
    original_critic_geometry=ctx_reward_learner.invariant_features
    del runner,source
    original=(env.closure_errors,env.acceptance.update_world,env.reward.compute)
    learner.collect(64)
    def round(steps):
        torch.cuda.synchronize();t=time.perf_counter();learner.collect(steps);torch.cuda.synchronize()
        c=time.perf_counter()-t
        for _ in range(4):learner.wm_update()
        learner.policy_update();torch.cuda.synchronize()
        row=dict(controls=steps,samples=steps*env.num_envs,collection_seconds=c,
            total_seconds=time.perf_counter()-t,counts=asdict(learner.counts),
            bptt=learner.last_bptt_receipt.copy())
        learner.iteration+=1
        return row
    round(2);round(3)
    snapshot=cpu(learner._checkpoint(True))
    rows=[]
    for arm in ('A','B','B','A'):
        env.closure_errors,env.acceptance.update_world,env.reward.compute=original
        for name,fn in original_geometry.items():setattr(networks,name,fn)
        ctx_reward_learner.invariant_features=original_critic_geometry
        learner.restore_full(snapshot)
        receipt=None
        if arm=='B':
            receipt=dict(sampling=install_sampling(env),optimizers=enable_fused_adam(learner))
            if args.scripted_geometry:receipt['geometry']=enable_scripted_geometry()
        else:
            for name in ('wm','pi','v','aux'):
                opt=getattr(learner,'opt_'+name);opt.defaults.update(fused=False,foreach=None)
                for group in opt.param_groups:
                    group.update(fused=False,foreach=None)
                    for param in group['params']:
                        state=opt.state.get(param)
                        if state and 'step'in state:state['step']=state['step'].cpu()
        for steps in (2,3):round(steps)
        timed=[round(steps)for steps in (2,3,2,3)]
        row=dict(arm=arm,execution=receipt,rounds=timed,
            samples=sum(x['samples']for x in timed),seconds=sum(x['total_seconds']for x in timed),
            collection_seconds=sum(x['collection_seconds']for x in timed))
        rows.append(row);print(json.dumps(dict(arm=arm,seconds=row['seconds'],collection=row['collection_seconds'])),flush=True)
    totals={}
    for arm in ('A','B'):
        samples=sum(x['samples']for x in rows if x['arm']==arm)
        seconds=sum(x['seconds']for x in rows if x['arm']==arm)
        collection=sum(x['collection_seconds']for x in rows if x['arm']==arm)
        totals[arm]=dict(samples=samples,seconds=seconds,collection_seconds=collection,
            total_steps_per_second=samples/seconds,collection_steps_per_second=samples/collection)
    # Save and resume the candidate through the exact production entry schema.
    install_sampling(env);enable_fused_adam(learner)
    if args.scripted_geometry:enable_scripted_geometry()
    saved=save(learner,R/'new_random_fixture_full.pt',dict(path='new_random_in_memory_teacher',iteration=0))
    payload=decode(saved['path'],saved['SHA']);before=asdict(learner.counts)
    learner.restore_full(payload);enable_fused_adam(learner);round(2)
    assert learner.counts.pi_bptt_optimizer_steps==before['pi_bptt_optimizer_steps']+1
    out.update(passed=True,GPU=torch.cuda.get_device_name(),num_envs=env.num_envs,rows=rows,totals=totals,
        total_speed_ratio=totals['B']['total_steps_per_second']/totals['A']['total_steps_per_second'],
        collection_speed_ratio=totals['B']['collection_steps_per_second']/totals['A']['collection_steps_per_second'],
        production_dimensions_and_update_ratios=True,production20k_speed_not_claimed=True,
        scripted_geometry=args.scripted_geometry,A_arms_restore_original_geometry=True,
        candidate_fullsave_resume_H32=True,checkpoint=saved,resumed_bptt=learner.last_bptt_receipt,
        numerical_resets=int(env.numerical_reset_counts.sum()),constraint_resets=int(env.constraint_reset_counts.sum()))
except BaseException:out['error']=traceback.format_exc()
finally:
    if bridge is not None:bridge.close()
    if env is not None:env.close()
    (R/'RESULT.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items()if k!='rows'}))
if not out['passed']:raise SystemExit(1)
