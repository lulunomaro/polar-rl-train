"""Optional FUTURE CPU/Torch test; NOT executed by this source-only review.
Requires the reviewed native bridge/vendor + RSL/TensorDict packages on PYTHONPATH.
--new-output must not exist. Creates only its OWN synthetic full checkpoint.
No SDK, learner, original mother checkpoint, GPU, physics, or evaluation claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import frozen_a1_raw35_v1 as h


def run(new_output):
    output=Path(new_output).resolve();h.need(not output.exists(),'fresh own CPU test output required');output.mkdir(parents=True)
    m=h._runtime_modules();t=m.t
    # Importing Torch is intentional ONLY when the parent runs THIS CPU fixture.
    with t.inference_mode(False),t.no_grad(),t.random.fork_rng(devices=[]):
        t.manual_seed(914)
        obs=m.TD(dict(policy=t.zeros(2,35),critic=t.zeros(2,38)),batch_size=[2])
        distribution=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar')
        teacher=m.MLP(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=distribution)
        ref=m.Wrapper(m.Policy(35,3,hist=10,z_dim=32,num_joints=6,hidden=(512,256,128)),teacher,0,scale=.05)
        ref.residual.dec[-1].weight.fill_(.02);ref.residual.dec[-1].bias.copy_(t.tensor([1.,-1.,2.,-2.,3.,-3.]))
        ref.obs_norm.mean.copy_(t.linspace(-.2,.2,35));ref.obs_norm.var.fill_(.7);ref.obs_norm.count.fill_(123.)
        ref.goal_norm.mean.copy_(t.tensor([.1,.2,-.3]));ref.goal_norm.var.fill_(.4);ref.goal_norm.count.fill_(81.)
        ref.eval().requires_grad_(False)
    counts={k:0 for k in h.COUNT_FIELDS};counts.update(policy_attempts=25,pi_optimizer_steps=24,pi_bptt_optimizer_steps=24,wm_optimizer_steps=40)
    teacher_receipt=dict(source_path='/OWN_SYNTHETIC_EMBEDDED_TEACHER_NEVER_OPEN.pt',source_SHA='a'*64,source_bytes=1,teacher_frozen=True)
    provenance=dict(role='E3',role_key='EXPLICIT_SYNTHETIC_ENTRY',run_id='SYNTHETIC_CPU_ONLY',actor_view=h.VIEW,algorithm_family=h.FAMILY,algorithm_variant='A1_RAW35_FRESH')
    root=dict(**provenance,pi=ref.state_dict(),wm={'unused':t.tensor([float('nan')])},critic={},opt_wm={},opt_pi={},opt_v={},iteration=24,
              args=dict(hist=10,z_dim=32,goal_frames=1,policy_hidden=(512,256,128),test_hidden_dims=None,amp='none',buffer_steps=128),
              new_algorithm_not_PPO_resume=True,asset_SHA='b'*64,contract_SHA='c'*64,bootstrap_teacher=teacher_receipt,
              context_reward_extension=dict(full_resume=True,counts=counts,aux={'unused':t.zeros(2)},opt_aux={},replay=dict(T=128,N=1024,data={}),
              obs_hist=t.zeros(1024,10,35),rng={'torch_cpu':t.get_rng_state(),'python':('NOT_RESTORED',)},environment={'NOT_RESTORED':True},
              contract=dict(schema='mod4v1.ctx_task_reward.v1',num_joints=30,action_dim=6,obs_dim=35,goal_frame_dim=3,context_dim=500,num_envs=1024,policy_dt_s=.02)))
    path=output/'production/checkpoints/synthetic_000024_complete.pt';path.parent.mkdir(parents=True);t.save(root,path)
    # Synthetic producer receipt creation is separate from the tested loader's
    # exactly-one own full checkpoint read/hash/CPU decode.
    raw=path.read_bytes();cp=dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),iteration=24,counts=counts,
        teacher_source=teacher_receipt,teacher_unchanged=True,full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
    final=dict(**provenance,kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3',passed_execution=True,teacher_unchanged=True,
               counts=counts,actual_BPTT_policy_steps=24,checkpoint=cp,teacher=teacher_receipt)
    before=t.get_rng_state().clone()
    cache=h.FrozenA1CheckpointCache(final,own_job_root=output,role='E3',role_key='EXPLICIT_SYNTHETIC_ENTRY',run_id='SYNTHETIC_CPU_ONLY',asset_SHA='b'*64,contract_SHA='c'*64)
    mean=cache.build_mean_policy('cpu',num_envs=80)
    assert t.equal(before,t.get_rng_state()),'CPU construction changed global RNG'
    assert t.equal(mean.pi.residual.dec[-1].bias,ref.residual.dec[-1].bias),'trained residual zeroed after strict load'
    generator=t.Generator(device='cpu');generator.manual_seed(83)
    history=t.zeros(80,10,35);maximum_error=0.
    for step in range(4):
        raw35=t.randn(80,35,generator=generator)
        fresh=t.zeros(80,dtype=t.bool)
        if step==0:fresh.fill_(True)
        if step==2:fresh[:2]=True  # Original terminated OR truncated two-env fixture.
        with t.inference_mode():
            shifted=t.cat((history[:,1:],raw35.unsqueeze(1)),1)
            history=t.where(fresh[:,None,None],raw35.unsqueeze(1).expand_as(history),shifted)
            expected=ref(history,raw35[:,:3]).clamp(-6.,6.)
        actual=mean.act(raw35,episode_start=fresh)
        error=float((expected-actual).abs().max());maximum_error=max(maximum_error,error)
        assert t.allclose(actual,expected,rtol=1e-6,atol=1e-6)
    assert t.equal(before,t.get_rng_state()),'mean inference drew RNG'
    receipt=mean.receipt();assert receipt['physical_byte_opens']==receipt['CPU_decodes']==receipt['SHA_calculations']==1
    assert receipt['mother_checkpoint_opens']==receipt['optimizer_updates']==receipt['normalization_updates']==0
    with t.no_grad():mean.pi.obs_norm.mean.add_(1.)
    try:mean.act(t.zeros(80,35),episode_start=t.zeros(80,dtype=t.bool))
    except ValueError:pass
    else:raise AssertionError('changed norm was not detected')
    assert mean._failed
    result=dict(kind='OWN_SYNTHETIC_CPU_TORCH_NOT_ORIGINAL_CHECKPOINT_OR_NATIVE_EVAL',passed=True,
                max_reference_error=maximum_error,CPU_mean_controls=4,source_bindings=m.source_bindings,receipt_before_negative_mutation=receipt,
                norm_mutation_detected=True,SDK_GPU_original_PT_optimizer_or_physics_operations=0,actual_frozen_evaluation=None)
    (output/'REMOTE_CPU_SYNTHETIC_RESULTS_V1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--new-output',required=True)
    run(parser.parse_args().new_output)
