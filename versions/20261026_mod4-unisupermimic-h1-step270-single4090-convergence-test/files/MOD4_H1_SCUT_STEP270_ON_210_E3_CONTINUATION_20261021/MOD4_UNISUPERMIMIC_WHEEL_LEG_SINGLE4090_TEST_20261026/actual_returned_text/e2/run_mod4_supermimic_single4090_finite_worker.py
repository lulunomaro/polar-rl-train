"""Finite offline core-method learning test. Never a production expert checkpoint."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import time
import traceback
import numpy as np
import torch
from mod4_supermimic_adapter import load_core, make_world_model

J = Path(__file__).resolve().parent
O = J / 'job0/production'

def put(name, value):
    p = O / name
    q = p.with_suffix(p.suffix + '.partial')
    q.write_text(json.dumps(value, indent=2), 'utf8')
    q.replace(p)

def save_model(name, wm, pi, wo, po, wm_steps, pi_steps):
    path = O / name
    value = dict(kind='UNISUPERMIMIC_MOD4_NATIVE30_ACTION6_OFFLINE_CORE_TEST_ONLY',
                 world_model={k:v.detach().cpu() for k,v in wm.state_dict().items()},
                 policy={k:v.detach().cpu() for k,v in pi.state_dict().items()},
                 world_optimizer=wo.state_dict(), policy_optimizer=po.state_dict(),
                 world_updates=wm_steps, policy_updates=pi_steps,
                 not_a_production_MoE_expert_or_complete_UniLab_checkpoint=True)
    torch.save(value, path)
    loaded = torch.load(path, map_location='cpu', weights_only=False)
    def finite(x):
        if torch.is_tensor(x):
            assert not x.is_floating_point() or torch.isfinite(x).all()
        elif isinstance(x, dict):
            for v in x.values(): finite(v)
        elif isinstance(x, (tuple, list)):
            for v in x: finite(v)
    finite(loaded)
    del loaded
    return dict(path=str(path), bytes=path.stat().st_size,
                SHA=hashlib.sha256(path.read_bytes()).hexdigest(),
                world_updates=wm_steps, policy_updates=pi_steps,
                full_saved_state_CPU_finite=True, not_production_source=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', type=int, required=True)
    parser.add_argument('--phase', required=True)
    args = parser.parse_args()
    assert args.job == 0 and args.phase == 'production'
    assert not O.exists()
    O.mkdir(parents=True)
    torch.set_num_threads(2)
    assert os.environ['CUDA_VISIBLE_DEVICES'] == 'GPU-16828f91-2b45-b646-8dc0-9481138e2842'
    assert torch.cuda.is_available() and torch.cuda.device_count() == 1
    device = torch.device('cuda:0')
    torch.manual_seed(20261026)
    torch.cuda.reset_peak_memory_stats()
    started = time.time()
    geo, nets = load_core(J)
    nets.AMP_DTYPE = None
    with np.load(J / 'artifacts/mod4_native30_action6_saved_transition_test.npz', allow_pickle=False) as z:
        data = {k: torch.from_numpy(z[k].copy()).to(device) for k in ('s', 's1', 'a', 'xi', 'held_out_env')}
    train = ~data['held_out_env']
    test = data['held_out_env']
    train_ids = torch.nonzero(train).flatten()
    st = geo.unflatten_state(data['s'])
    nt = geo.unflatten_state(data['s1'])
    context = torch.tanh(data['xi'])
    wm = make_world_model(nets).to(device)
    target = wm.targets(st, nt).detach()
    inputs = wm.inputs(st, data['a'], context).detach()
    wm.in_norm.update(inputs[train])
    wm.out_norm.update(target[train])
    standardized = (target - wm.out_norm.mean) / wm.out_norm.std()
    pi = nets.Policy(obs_dim=128, goal_dim=73, hist=10, z_dim=32, num_joints=6).to(device)
    wo = torch.optim.Adam(wm.parameters(), lr=2e-4)
    po = torch.optim.Adam(pi.parameters(), lr=2e-4, betas=(.9,.95))
    def metric(mask):
        with torch.no_grad():
            prediction = wm.net(wm.in_norm(inputs[mask]))
            return float((prediction - standardized[mask]).square().mean())
    before = dict(train_normalized_increment_MSE=metric(train), held_out_env_normalized_increment_MSE=metric(test))
    trace, wm_steps, pi_steps, gradients = [], 0, 0, []
    try:
        for step in range(200):
            ids = train_ids[torch.randint(len(train_ids), (256,), device=device)]
            wo.zero_grad(set_to_none=True)
            loss = (wm.net(wm.in_norm(inputs[ids])) - standardized[ids]).square().mean()
            assert torch.isfinite(loss)
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(wm.parameters(), 10, error_if_nonfinite=True)
            wo.step()
            wm_steps += 1
            if step % 25 == 0:
                trace.append(dict(update=wm_steps, loss=float(loss), gradnorm=float(norm)))
                put('latest_complete.json', dict(updates=wm_steps, phase='world_model_only_offline', not_production_E2=True))
            if (O / 'STOP_AFTER_SAVE.json').exists() or time.time() - started > 240:
                break
        assert wm_steps >= 20
        for parameter in wm.parameters():
            parameter.requires_grad_(False)
        # Test action derivatives through eight uses of the actual upstream integration.
        for update in range(5):
            ids = train_ids[:32]
            state = geo.unflatten_state(data['s'][ids])
            previous = data['a'][ids]
            ctx = context[ids]
            obs = torch.cat((geo.invariant_features(state), previous, ctx), -1)
            history = obs[:,None].expand(-1,10,-1).clone()
            goal = data['s1'][ids]
            pi.obs_norm.update(obs)
            pi.goal_norm.update(goal)
            po.zero_grad(set_to_none=True)
            tracking = 0
            for _ in range(8):
                raw = pi(history, goal)
                action = 6 * torch.tanh(raw / 6)
                state = wm.step(state, action, ctx)
                reference = geo.unflatten_state(goal)
                error = wm.state_error(state, reference) / wm.out_norm.std().clamp_min(.01)
                tracking = tracking + error.square().mean() + .001 * (action-previous).square().mean()
                obs = torch.cat((geo.invariant_features(state), action, ctx), -1)
                history = torch.cat((history[:,1:],obs[:,None]),1)
                previous = action
            assert torch.isfinite(tracking)
            tracking.backward()
            gradnorm = torch.nn.utils.clip_grad_norm_(pi.parameters(), 10, error_if_nonfinite=True)
            assert float(gradnorm) > 0
            po.step()
            pi_steps += 1
            gradients.append(dict(update=pi_steps, finite_loss=float(tracking), policy_gradient_norm=float(gradnorm)))
        torch.cuda.synchronize()
        after = dict(train_normalized_increment_MSE=metric(train), held_out_env_normalized_increment_MSE=metric(test))
        artifact = save_model('finite_test_full_state.pt', wm, pi, wo, po, wm_steps, pi_steps)
        result = dict(passed=True, test_scope='Real MOD4 selected saved transitions; offline WorldModel learning and eight-step differentiable policy-core test',
            upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',
            GPU_UUID=os.environ['CUDA_VISIBLE_DEVICES'], GPU_name=torch.cuda.get_device_name(0), visible_cuda_devices=1,
            torch_version=torch.__version__, FP32=True, full_default_world_hidden=[2048,2048,2048],
            native_joint_state_count=30, native_action_dim=6, input_dim=128, output_increment_dim=72,
            real_saved_transitions=int(train.sum()+test.sum()), held_out_env_transitions=int(test.sum()),
            before=before, after=after, world_updates=wm_steps, policy_updates=pi_steps,
            training_trace=trace, differentiable_policy_trace=gradients,
            peak_allocated_bytes=torch.cuda.max_memory_allocated(), peak_reserved_bytes=torch.cuda.max_memory_reserved(),
            actual_worker_elapsed_s=time.time()-started, final=artifact,
            no_online_simulator_or_new_robot_rollout=True, no_full_UniLab_learner_replay_critic_or_G1_reference_reproduction=True,
            context_incomplete_for_closed_loop_delay_DR=True,
            short_selected_sample_fit_not_generalization_or_physical_stability_or_step270_success=True,
            no_production_actor_STD_Adam_checkpoint_changed=True,
            own_original_writer_GO_to_terminal_cost_required=True)
        put('FINITE_TEST_RESULT_ACTUAL.json', result)
        put('FINAL.json', result)
        print(json.dumps(dict(passed=True, world_updates=wm_steps, policy_updates=pi_steps, peak_allocated_bytes=result['peak_allocated_bytes'])))
    except BaseException:
        error = traceback.format_exc()
        artifact = save_model('FAILED_PARTIAL_FULL_STATE.pt', wm, pi, wo, po, wm_steps, pi_steps)
        put('WORKER_ORIGINAL_ERROR.json', dict(epoch=time.time(), error=error, partial=artifact))
        put('FINAL.json', dict(passed=False, original_error=True, final=artifact))
        raise

if __name__ == '__main__':
    main()
