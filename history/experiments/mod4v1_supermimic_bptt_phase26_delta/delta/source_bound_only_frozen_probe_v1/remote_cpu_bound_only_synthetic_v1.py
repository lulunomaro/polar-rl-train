"""FUTURE parent CPU-only software fixture. Child does not run this script.

Only a NEW self-generated full synthetic checkpoint; no original input model arg,
SDK, GPU, subprocess, native environment or optimizer. Does not prove skill.
"""
import argparse
import hashlib
import json
from pathlib import Path
import bound_only_frozen_probe_v1 as p
from a1_frozen_eval_runtime_v2 import OriginalEpisodeBoundary


def run(new_output):
    output = Path(new_output).resolve(); assert not output.exists(); output.mkdir(parents=True)
    h = p.h; m = h._runtime_modules(); t = m.t
    before = t.get_rng_state().clone()
    with t.inference_mode(False), t.no_grad(), t.random.fork_rng(devices=[]):
        t.manual_seed(17035)
        obs = m.TD(dict(policy=t.zeros(2,35), critic=t.zeros(2,38)), batch_size=[2])
        distribution = dict(class_name='rsl_rl.modules.distribution:GaussianDistribution', init_std=1., std_type='scalar')
        teacher = m.MLP(obs, dict(actor=['policy'],critic=['critic']), 'actor', 6, [256,128,64], 'elu', distribution_cfg=distribution)
        original = m.Wrapper(m.Policy(35,3,hist=10,z_dim=32,num_joints=6,hidden=(512,256,128)), teacher, 0, scale=.05)
        original.residual.dec[-1].weight.fill_(.02)
        original.residual.dec[-1].bias.copy_(t.tensor([20.,-20.,2.,-2.,.1,-.1]))
        original.obs_norm.mean.copy_(t.linspace(-.2,.2,35)); original.obs_norm.var.fill_(.7); original.obs_norm.count.fill_(123.)
        original.goal_norm.mean.copy_(t.tensor([.1,.2,-.3])); original.goal_norm.var.fill_(.4); original.goal_norm.count.fill_(81.)
        original.eval().requires_grad_(False)
    assert t.equal(before,t.get_rng_state())
    counts = {k:0 for k in h.COUNT_FIELDS}
    counts.update(policy_attempts=25,pi_optimizer_steps=24,pi_bptt_optimizer_steps=24,wm_optimizer_steps=40)
    bootstrap = dict(source_path='/OWN_SYNTHETIC_NEVER_OPENED_MOTHER.pt',source_SHA='a'*64,source_bytes=1,teacher_frozen=True)
    provenance = dict(role='E3',role_key='OWN_SYNTHETIC_BOUND_PROBE',run_id='OWN_SYNTHETIC_BOUND_PROBE_CPU',
        actor_view=h.VIEW,algorithm_family=h.FAMILY,algorithm_variant='A1_RAW35_FRESH')
    root = dict(**provenance,pi=original.state_dict(),wm={'UNUSED':t.tensor([float('nan')])},critic={},
        opt_wm={},opt_pi={},opt_v={},iteration=24,new_algorithm_not_PPO_resume=True,asset_SHA='b'*64,contract_SHA='c'*64,
        bootstrap_teacher=bootstrap,args=dict(hist=10,z_dim=32,goal_frames=1,policy_hidden=(512,256,128),
            test_hidden_dims=None,amp='none',buffer_steps=128),
        context_reward_extension=dict(full_resume=True,counts=counts,aux={'UNUSED':t.zeros(2)},opt_aux={},
            replay=dict(T=128,N=1024,data={}),obs_hist=t.zeros(1024,10,35),
            rng={'torch_cpu':t.get_rng_state(),'python':('NOT_RESTORED',)},environment={'NOT_RESTORED':True},
            contract=dict(schema='mod4v1.ctx_task_reward.v1',num_joints=30,action_dim=6,obs_dim=35,
                goal_frame_dim=3,context_dim=500,num_envs=1024,policy_dt_s=.02)))
    def build_own_case(folder, *, statistics):
        path = folder/'production/checkpoints/own_synthetic_complete.pt'; path.parent.mkdir(parents=True)
        t.save(root,path)
        # Only the producer hashes its NEW output; tested cache has one own decode.
        raw = path.read_bytes()
        cp = dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),iteration=24,counts=counts,
            teacher_source=bootstrap,teacher_unchanged=True,full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
        final = dict(**provenance,kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3',passed_execution=True,
            teacher_unchanged=True,counts=counts,actual_BPTT_policy_steps=24,checkpoint=cp,teacher=bootstrap)
        cache = h.FrozenA1CheckpointCache(final,own_job_root=folder,role='E3',role_key=provenance['role_key'],
            run_id=provenance['run_id'],asset_SHA='b'*64,contract_SHA='c'*64)
        mean = p.build_bound_only_mean_policy(cache,'cpu',num_envs=80,expected_container_sha=cp['SHA'],
            collect_action_statistics=statistics,synthetic_only=True)
        return cache,mean,cp
    cache,mean,cp = build_own_case(output,statistics=True)
    assert mean.cache is cache and mean.act.__func__ is h.FrozenA1MeanPolicy.act
    assert type(mean.pi).__init__ is m.Wrapper.__init__
    assert t.equal(mean.pi.residual.dec[-1].bias,original.residual.dec[-1].bias)
    assert float(mean.pi.residual.dec[-1].bias.abs().max()) > 0.
    assert set(mean.pi.state_dict()) == set(root['pi'])
    assert all(t.equal(value,root['pi'][name]) for name,value in mean.pi.state_dict().items())
    assert cache.root['context_reward_extension']['counts'] == counts
    actor_calls = {'teacher':0,'residual':0}
    def count_teacher(module,args,result): actor_calls['teacher'] += 1
    def count_residual(module,args,result): actor_calls['residual'] += 1
    # READ-ONLY fixture-only hooks COUNT probe's actual subforwards, not alter output.
    hooks = [mean.pi.teacher.register_forward_hook(count_teacher),mean.pi.residual.register_forward_hook(count_residual)]
    caller = p.BoundOnlyPolicyCaller(mean,boundary=OriginalEpisodeBoundary(t,mean.device))
    generator=t.Generator(device='cpu'); generator.manual_seed(718)
    history=t.zeros(80,10,35); expected_error=0.; teacher_difference=0.; legacy_difference=0.
    for step in range(4):
        raw35=t.randn(80,35,generator=generator); start=caller.boundary.next_start.clone()
        with t.inference_mode():
            shifted=t.cat((history[:,1:],raw35.unsqueeze(1)),1)
            history=t.where(start[:,None,None],raw35.unsqueeze(1).expand_as(history),shifted)
            # Independent ORIGINAL software objects, NOT a second physical actor.
            base=original.teacher(m.TD(dict(policy=raw35),batch_size=[80]),stochastic_output=False)
            delta=original.residual(history,raw35[:,:3])
            expected=(base+.05*t.tanh(delta)).clamp(-6.,6.)
            legacy=(base+.05*delta).clamp(-6.,6.)
        action=caller(m.TD(dict(policy=raw35),batch_size=[80]),stochastic_output=False)
        assert t.equal(mean._history,history), 'original noisy35/current-frame padding/history changed'
        error=float((action-expected).abs().max()); expected_error=max(expected_error,error)
        assert t.allclose(action,expected,rtol=1e-6,atol=1e-6)
        teacher_difference=max(teacher_difference,float((action-base.clamp(-6.,6.)).abs().max()))
        legacy_difference=max(legacy_difference,float((action-legacy).abs().max()))
        assert teacher_difference <= .050001, 'float32 component bound vs CLIPPED TEACHER exceeded'
        terminated,truncated=t.zeros(80,dtype=t.bool),t.zeros(80,dtype=t.bool)
        if step==1: terminated[0]=True; truncated[1]=True
        caller.observe_transition(terminated,truncated)
    for handle in hooks: handle.remove()
    assert actor_calls == dict(teacher=4,residual=4)
    assert legacy_difference > .05, 'synthetic fixture failed to distinguish old unbounded mean'
    assert t.equal(before,t.get_rng_state()), 'bound probe advanced/restored caller RNG'
    receipt=caller.receipt()
    semantic=p.validate_bound_probe_receipt(receipt,expected_role='E3',expected_source_sha=cp['SHA'],expected_actor_calls=4)
    assert receipt['probe_optimizer_updates'] == dict(pi=0,wm=0,aux=0,critic=0)
    assert receipt['bound_probe_action_statistics']['forward_calls']==4
    assert receipt['bound_probe_action_statistics']['action_components']==4*80*6
    assert receipt['bound_probe_action_statistics']['extra_teacher_or_residual_forwards']==0
    assert cache.io_counts==dict(physical_byte_opens=1,SHA_calculations=1,CPU_decodes=1)
    cache.assert_unchanged(); mean.assert_frozen()
    # Negative ONE: original live teacher STD must remain part of whole pi guard.
    std_key=next(k for k in mean.pi.teacher.state_dict() if 'std' in k.lower())
    with t.no_grad(): mean.pi.teacher.state_dict()[std_key].add_(.125)
    try: mean.act(t.zeros(80,35),episode_start=t.ones(80,dtype=t.bool))
    except ValueError as exc:
        assert 'previously failed' not in str(exc); std_error=str(exc)
    else: raise AssertionError('teacher STD mutation escaped original whole mean guard')
    try: mean.act(t.zeros(80,35),episode_start=t.ones(80,dtype=t.bool))
    except ValueError as exc:
        assert 'previously failed' in str(exc); sticky=True
    else: raise AssertionError('bound probe continued after frozen-state failure')
    # Negative TWO: distinct own synthetic case, never rearm/rebuild existing cache.
    norm_cache,norm_mean,norm_cp=build_own_case(output/'ISOLATED_OWN_SYNTHETIC_NORM_NEGATIVE',statistics=False)
    with t.no_grad(): norm_mean.pi.obs_norm.mean.add_(.125)
    try: norm_mean.act(t.zeros(80,35),episode_start=t.ones(80,dtype=t.bool))
    except ValueError as exc:
        assert 'previously failed' not in str(exc); norm_error=str(exc)
    else: raise AssertionError('residual norm mutation escaped original whole mean guard')
    assert norm_cache.io_counts==dict(physical_byte_opens=1,SHA_calculations=1,CPU_decodes=1)
    assert t.equal(before,t.get_rng_state())
    result=dict(kind='OWN_SYNTHETIC_CPU_TORCH_BOUND_ONLY_ZERO_UPDATE_PROBE_V1',passed=True,
        actual_native_execution=None,original_model_PT_reads=0,actual_skill_or_training_effect=None,
        controls=4,num_envs=80,maximum_independent_bound_formula_error=expected_error,
        maximum_action_component_difference_vs_clipped_teacher=teacher_difference,
        maximum_action_component_difference_vs_legacy_unbounded_mean=legacy_difference,
        component_bound_float32_assert_tolerance=1e-6,
        full_strict_state_norm_and_teacher_values_match=True,constructor_zeroing_did_not_erase_loaded_weights=True,
        inherited_act_history_boundary_match=True,probe_subforwards=actor_calls,caller_RNG_unchanged=True,
        teacher_STD_guard_detected=True,teacher_STD_guard_error=std_error,sticky_failure_detected=sticky,
        isolated_residual_norm_guard_detected=True,isolated_residual_norm_guard_error=norm_error,
        isolated_negative_cache=norm_cache.receipt(),receipt_before_negative=receipt,semantic=semantic,
        source_bindings=m.source_bindings,probe_helper_source=p._source_binding(),
        no_SDK_GPU_actual_PT_raw_optimizer_or_native_operations=True)
    with (output/'REMOTE_CPU_BOUND_ONLY_RESULTS_V1.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False); stream.write('\n')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--new-output',required=True)
    run(parser.parse_args().new_output)
