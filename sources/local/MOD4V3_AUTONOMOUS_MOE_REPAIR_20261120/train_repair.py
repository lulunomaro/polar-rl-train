# SPDX-License-Identifier: MIT
"""Bounded stage-2 PPO for E1/E2 and on-policy gate supervision for MOD4v3."""
from __future__ import annotations

import argparse
from collections import defaultdict
import copy
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import signal
import time

import numpy as np
import torch
from torch.nn import functional as F

from repair_envs import HERE, JUMP_ANCHOR, LEAP_PARENT, PARENT_WEIGHTS, JumpFixture, LeapFixture, StairFixture
from autonomous_stair_moe_model import AutonomousStairActorCritic, OBS_DIM, HIST_LEN
from moe_instant_jump_model import load_instant_jump_checkpoint

STAIR_PARENT = PARENT_WEIGHTS / 'model_autonomous_stair_moe_best.pt'
JUMP_PARENT = PARENT_WEIGHTS / 'model_instant_jump_best.pt'
EXPECTED_SHA = {
    'stair': 'f4185e24d4261870ed3bbab1789a0e32434b9cef305c558f83a2c4ab3e8bf4eb',
    'jump': 'e2d836573e6f89002a5769b1dcacc212f18cc9c24329ad9a13108607578b2c8c',
}
DWELL_CHECK = 300.0


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def save_json(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False, default=json_scalar) + '\n',
                   encoding='utf-8', newline='\n')
    tmp.replace(path)


def parent_model(role, checkpoint=None, leap=False):
    if leap:
        from moe_forward_leap_model import MoEForwardLeapActorCritic
        model = MoEForwardLeapActorCritic.load_from_checkpoint(checkpoint or LEAP_PARENT)
        model.history_frames = 12
        return model
    if role == 'jump':
        path = checkpoint or JUMP_PARENT
        if checkpoint is None and sha(path) != EXPECTED_SHA['jump']:
            raise ValueError('Unexpected E2 parent')
        return load_instant_jump_checkpoint(path)[0]
    path = checkpoint or STAIR_PARENT
    if checkpoint is None and sha(path) != EXPECTED_SHA['stair']:
        raise ValueError('Unexpected E1 parent')
    return AutonomousStairActorCritic.load_from_checkpoint(path)


def _worker(pipe, role, seed, measure_substeps, leap, stance_dr, leap_height_focus, stair_low_stance_focus,
            stair_high_slow_focus, leap_moving_focus, stair_restart_focus, instant_moving_focus, jump_top_support,
            stair_mid_stance_focus, touchdown_focus, high_takeoff_focus, sustained_high_jump, high_jump_apex_focus,
            parked_retake_focus, high_jump_impulse_focus, clean_jump_apex, min_landing_apex, varied_jump_runup,
            wasd_restart_focus, direct_jump_landing, jump_lip_focus, jump_airborne_height_focus, jump_loaded_push,
            stair_recovery_focus, jump_launch_energy, wasd_crouch_speed):
    try:
        env = LeapFixture(seed) if leap else JumpFixture(seed) if role == 'jump' else StairFixture(seed)
        if leap:
            env.height_focus = leap_height_focus
            env.moving_focus = leap_moving_focus
        if not leap and role == 'jump':
            env.moving_focus = instant_moving_focus
            env.require_top_support = jump_top_support
            env.touchdown_focus = touchdown_focus
            env.high_takeoff_focus = high_takeoff_focus
            env.sustained_high_jump = sustained_high_jump
            env.high_jump_apex_focus = high_jump_apex_focus
            env.high_jump_impulse_focus = high_jump_impulse_focus
            env.clean_jump_apex = clean_jump_apex
            env.min_landing_apex = min_landing_apex
            env.varied_jump_runup = varied_jump_runup
            env.direct_jump_landing = direct_jump_landing
            env.jump_lip_focus = jump_lip_focus
            env.jump_airborne_height_focus = jump_airborne_height_focus
            env.jump_loaded_push = jump_loaded_push
            env.jump_launch_energy = jump_launch_energy
            env.wasd_crouch_speed = wasd_crouch_speed
        if role != 'jump':
            env.restart_focus = stair_restart_focus
            env.parked_retake_focus = parked_retake_focus
            env.wasd_restart_focus = wasd_restart_focus
            env.stair_recovery_focus = stair_recovery_focus
            env.mid_stance_focus = stair_mid_stance_focus
            env.low_stance_focus = stair_low_stance_focus
        if role == 'stair':
            env.high_slow_focus = stair_high_slow_focus
        if leap:
            env.stance_dr = stance_dr
        if role != 'jump':
            env.measure_substeps = measure_substeps

        def state(packet):
            packet['permit'] = env.intent_ok if role != 'jump' else True
            packet['label'] = env.target() if role != 'jump' else False
            return packet

        while True:
            cmd, value = pipe.recv()
            if cmd == 'close':
                break
            if cmd == 'reset':
                pipe.send(state(env.sample(value, role)))
            elif cmd == 'step':
                action, effective, raw, dr = value
                if role == 'jump':
                    packet, reward, done, info = env.step(action)
                else:
                    packet, reward, done, info = env.step(action, effective, raw)
                packet = state(packet)
                terminal = packet if done and not info['fell_reason'] else None
                if done:
                    packet = state(env.sample(dr, role))
                pipe.send((packet, reward, done, terminal, info if done else None))
    except (EOFError, KeyboardInterrupt):
        pass
    except Exception:
        import traceback
        pipe.send({'error': traceback.format_exc()})
    finally:
        pipe.close()


class Fixtures:
    def __init__(self, role, count, seed, measure_substeps=False, leap=False, stance_dr=False,
                 leap_height_focus=False, stair_low_stance_focus=False, stair_high_slow_focus=False,
                 leap_moving_focus=False, stair_restart_focus=False, instant_moving_focus=False, jump_top_support=False,
                 stair_mid_stance_focus=False, touchdown_focus=0., high_takeoff_focus=False,
                 sustained_high_jump=False, high_jump_apex_focus=False, parked_retake_focus=False,
                 high_jump_impulse_focus=False, clean_jump_apex=False, min_landing_apex=0., varied_jump_runup=False,
                 wasd_restart_focus=False, direct_jump_landing=False, jump_lip_focus=False,
                 jump_airborne_height_focus=False, jump_loaded_push=False,
                 stair_recovery_focus=False, jump_launch_energy=False, wasd_crouch_speed=0.):
        self.pipes, self.workers = [], []
        ctx = mp.get_context('fork' if os.name != 'nt' else 'spawn')
        for index in range(count):
            leader, worker = ctx.Pipe()
            proc = ctx.Process(target=_worker, args=(worker, role, seed + 191 * index, measure_substeps, leap, stance_dr,
                                                     leap_height_focus, stair_low_stance_focus, stair_high_slow_focus,
                                                     leap_moving_focus, stair_restart_focus, instant_moving_focus,
                                                     jump_top_support, stair_mid_stance_focus, touchdown_focus, high_takeoff_focus,
                                                     sustained_high_jump, high_jump_apex_focus, parked_retake_focus,
                                                     high_jump_impulse_focus, clean_jump_apex, min_landing_apex,
                                                     varied_jump_runup, wasd_restart_focus, direct_jump_landing, jump_lip_focus,
                                                     jump_airborne_height_focus, jump_loaded_push,
                                                     stair_recovery_focus, jump_launch_energy, wasd_crouch_speed),
                               daemon=True)
            proc.start()
            worker.close()
            self.pipes.append(leader)
            self.workers.append(proc)

    def receive(self):
        replies = [pipe.recv() for pipe in self.pipes]
        for response in replies:
            if isinstance(response, dict) and 'error' in response:
                raise RuntimeError(response['error'])
        return replies

    def reset(self, dr):
        for pipe in self.pipes:
            pipe.send(('reset', dr))
        return self.receive()

    def step(self, actions, gate, raw, dr):
        for pipe, a, g, p in zip(self.pipes, actions, gate, raw, strict=True):
            pipe.send(('step', (a, float(g), float(p), dr)))
        return self.receive()

    def close(self):
        for pipe in self.pipes:
            try:
                pipe.send(('close', None))
            except OSError:
                pass
            pipe.close()
        for proc in self.workers:
            proc.join(timeout=2)
            if proc.is_alive():
                proc.terminate()
                proc.join()


def batch(packets, key, device, dtype=torch.float32):
    return torch.as_tensor(np.stack([p[key] for p in packets]), dtype=dtype, device=device)


def selected_history(model, history):
    return history[..., -getattr(model, 'history_frames', HIST_LEN) * OBS_DIM:]


def critic_value(model, obs, history, priv):
    return model.evaluate_value(obs, selected_history(model, history), priv)


def forward(model, role, obs, hist, permit, oracle=None):
    if role == 'jump':
        mean = model.act_deterministic(obs, selected_history(model, hist))
        std = model.action_std(obs).clamp(.008, .14)
        enabled = obs[:, 30] > .5
        return mean, std, enabled, enabled.float(), enabled.float(), None
    out = model.moe.compute_all_heads(obs, hist)
    slow_scale = getattr(model, 'slow_approach_scale', 1.)
    if slow_scale != 1.:
        approach = obs.clone()
        approach[:, 0] = torch.where(permit, approach[:, 0] * slow_scale, approach[:, 0])
        out['a_e0'] = model.moe.e0(approach)
    raw = out['g_prob']
    logits = out['g_logit'] if oracle is None else None
    gate = out['g_eff'] if oracle is None else oracle
    deployed_router = getattr(model, 'deployed_stair_router', None)
    if deployed_router is not None:
        with torch.no_grad():
            norm, features = deployed_router.encoder(obs, hist)
            raw = deployed_router.router.forward_logit(torch.cat((norm, features), dim=-1)).sigmoid().flatten()
            gate = ((raw - .05) / .95).clamp_min(0.)
        logits = None
    effective = torch.where(permit, gate, 0.)
    mean = torch.lerp(out['a_e0'], out['a_stair'], effective[:, None]).clamp(-6., 6.)
    std = model.stair_log_std.exp().clamp(.012, .14).expand_as(mean)
    enabled = (effective > .045) & permit
    return mean, std, enabled, effective, raw, logits


def balanced_gate(logits, labels, weights):
    positives = labels > .5
    loss = F.binary_cross_entropy_with_logits(logits, labels, reduction='none')
    if positives.any() and (~positives).any():
        return .45 * loss[positives].mean() + .55 * (loss * weights)[~positives].mean()
    return (loss * weights).mean()


def train_jump_seed(model, optimizer, device, steps, seed):
    if steps == 0:
        return None
    if not JUMP_ANCHOR.exists():
        raise FileNotFoundError(JUMP_ANCHOR)
    pool = torch.load(JUMP_ANCHOR, map_location=device, weights_only=True)
    obs, act = pool['obs'], pool['act']
    short = pool['hist'].reshape(-1, 12, OBS_DIM)
    history = torch.cat((short[:, :1].expand(-1, HIST_LEN - 12, -1), short), dim=1).flatten(1)
    # Oversample the stationary group since it is the primary failure of e2d83657.
    stationary = torch.where(obs[:, 0].abs() < .09)[0]
    random = torch.Generator(device=device).manual_seed(seed)
    previous = None
    for i in range(steps):
        indices = torch.cat((stationary[torch.randint(len(stationary), (192,), generator=random, device=device)],
                             torch.randint(len(obs), (192,), generator=random, device=device)))
        pred = model.act_deterministic(obs[indices], history[indices])
        loss = F.smooth_l1_loss(pred, act[indices], beta=.4)
        if i == 0:
            previous = float(loss.detach())
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.actor_body.e_jump.parameters(), 1.0)
        optimizer.step()
    return {'optimizer_steps': steps, 'seed_frames': len(obs), 'first_loss': previous, 'last_batch_loss': float(loss.detach())}


def save_weights(model, role, path, meta, actor_opt, critic_opt):
    delta = model.verify_zero_e0_drift()
    tmp = path.with_suffix('.tmp')
    if role == 'jump':
        if hasattr(model, 'history_frames'):
            content = {'model_type': 'MOD4v3_MoE_RL_ForwardLeap_StepJump', 'state_dict': model.state_dict()}
        else:
            content = {'model_state_dict': model.state_dict()}
    else:
        content = {'moe_state_dict': model.moe.state_dict(), 'state_dict': model.state_dict()}
    content.update(metadata=meta | {'max_frozen_e0_difference': delta}, format='MOD4V3_AUTONOMOUS_MOE_REPAIR_V1',
                   optimizer_actor=actor_opt.state_dict(), optimizer_critic=critic_opt.state_dict() if critic_opt else None)
    torch.save(content, tmp)
    tmp.replace(path)
    return sha(path)


def summary(episodes):
    stats = defaultdict(lambda: defaultdict(float))
    for ep in episodes:
        acc = stats[ep['profile']]
        acc['episodes'] += 1
        acc['falls'] += int(bool(ep['fell_reason']))
        if 'support_0p4' in ep:
            acc['supported'] += int(ep['support_0p4'])
            acc['recovered'] += int(ep['recovered'])
            acc['direct_completions'] += int(ep['recovered'] and ep['backtrack_m'] <= .075)
            acc['backtrack_m'] += ep['backtrack_m']
            acc['invalid_gate_peak'] = max(acc['invalid_gate_peak'], ep['invalid_gate_max'])
            if ep.get('restart_backtrack_m') is not None:
                acc['resumed'] += 1
                acc['renewed_contact'] += int(ep['restart_contact'])
                acc['restart_backtrack_m'] += ep['restart_backtrack_m']
        else:
            acc['landed'] += int(ep['landed'])
            acc['clearance_m'] += ep['clearance_m']
            acc['backtrack_m'] += ep['backtrack_m']
            if 'held_top_s' in ep:
                acc['held_top_0p4'] += int(ep['held_top_s'] >= .40 and not ep['fell_reason'])
            acc['preflight_face_hit'] += int(ep.get('preflight_face_hit', False))
            if 'direct_held_top' in ep:
                acc['direct_held_top'] += int(ep['direct_held_top'] and not ep['fell_reason'])
            support_ok = ep.get('held_top_s', .40) >= .40 and ep.get('direct_held_top', True)
            acc['qualified'] += int(support_ok and ep['landed'] and not ep['fell_reason'] and ep['clearance_m'] >= .30
                                     and ep['backtrack_m'] <= .07 and ep['landing_pitch_deg'] <= 16.0
                                     and not ep.get('preflight_face_hit', False))
    return {k: dict(v) for k, v in stats.items()}


def collect(model, role, env, packet, hist, horizon, device, dr, sample_actions, end, oracle_stair=False):
    store = defaultdict(list)
    complete = []
    for _ in range(horizon):
        if end():
            break
        obs = batch(packet, 'obs', device)
        priv = batch(packet, 'priv', device)
        permit = batch(packet, 'permit', device, torch.bool)
        label = batch(packet, 'label', device)
        flat_history = hist.flatten(1)
        with torch.no_grad():
            mean, std, exploration, gate, raw, _ = forward(model, role, obs, flat_history, permit, label if oracle_stair else None)
            dist = torch.distributions.Normal(mean, std)
            raw_action = torch.where(exploration[:, None], dist.sample(), mean) if sample_actions else mean
            value = critic_value(model, obs, flat_history, priv) if role != 'router' else torch.zeros(len(obs), device=device)
            lp = dist.log_prob(raw_action).sum(-1)
            replies = env.step(raw_action.clamp(-6., 6.).cpu().numpy(), gate.cpu().numpy(), raw.cpu().numpy(), dr)
        next_packet, rewards, dones, terminals, infos = list(zip(*replies, strict=True))
        if not np.isfinite(rewards).all():
            raise RuntimeError('Non-finite reward in closed-loop rollout')
        complete.extend(info for info in infos if info is not None)
        next_obs = batch(next_packet, 'obs', device)
        done = torch.tensor(dones, dtype=torch.bool, device=device)
        timeout_bootstrap = torch.zeros(len(dones), device=device)
        good = [i for i, terminal in enumerate(terminals) if terminal is not None]
        if role != 'router' and good:
            terminal_packet = [terminals[i] for i in good]
            to = batch(terminal_packet, 'obs', device)
            tp = batch(terminal_packet, 'priv', device)
            th = torch.cat((hist[good, 1:], to[:, None]), dim=1).flatten(1)
            with torch.no_grad():
                timeout_bootstrap[good] = critic_value(model, to, th, tp)
        for key, val in [('obs', obs), ('hist', flat_history), ('priv', priv), ('action', raw_action), ('logp', lp),
                         ('value', value), ('permit', permit), ('exploration', exploration), ('label', label),
                         ('done', done), ('timeout', timeout_bootstrap), ('rew', torch.tensor(rewards, device=device, dtype=torch.float32))]:
            store[key].append(val)
        hist = torch.cat((hist[:, 1:], next_obs[:, None]), dim=1)
        hist = torch.where(done[:, None, None], next_obs[:, None, :], hist)
        packet = next_packet
    if not store:
        return None, packet, hist, complete
    data = {key: torch.stack(val) for key, val in store.items()}
    if role != 'router':
        with torch.no_grad():
            bootstrap = critic_value(model, batch(packet, 'obs', device), hist.flatten(1), batch(packet, 'priv', device))
            adv = torch.zeros_like(data['rew'])
            residual = torch.zeros_like(bootstrap)
            for t in reversed(range(len(data['rew']))):
                mask = ~data['done'][t]
                nv = bootstrap if t + 1 == len(data['rew']) else data['value'][t + 1]
                delta = data['rew'][t] + .99 * (nv * mask + data['timeout'][t]) - data['value'][t]
                residual = delta + (.99 * .95) * mask * residual
                adv[t] = residual
            data['ret'] = adv + data['value']
            active = data['exploration']
            if active.sum() > 2:
                adv = (adv - adv[active].mean()) / adv[active].std().clamp_min(1e-5)
            data['adv'] = adv
    return {k: v.flatten(0, 1) for k, v in data.items()}, packet, hist, complete


def stair_reference_loss(model, role, anchor):
    # Sample the active skill separately so adjacent cruise frames do not drown out first contact.
    pick = lambda ids, count: ids[torch.randint(len(ids), (count,), device=ids.device)]
    groups = anchor.get('positive_groups', (anchor['positive'],))
    positive = torch.cat([pick(ids, max(1, 192 // len(groups))) for ids in groups])
    if role == 'stair':
        if 'impact_indices' in anchor:
            positive = torch.cat((positive, pick(anchor['impact_indices'], 64)))
        out = model.moe.compute_all_heads(anchor['obs'][positive], anchor['hist'][positive])
        act = out['a_stair'].clamp(-6., 6.)
        error = F.smooth_l1_loss(act, anchor['act'][positive], beta=.25)
        error += .10 * F.smooth_l1_loss(out['v_virt'], anchor['cmd'][positive, 0], beta=.16)
        error += .35 * F.smooth_l1_loss(out['h_virt'], anchor['cmd'][positive, 1], beta=.025)
        return error
    parts = [positive, pick(anchor['negative'], 224)]
    if 'hard_indices' in anchor:
        parts.append(pick(anchor['hard_indices'], 112))
    ids = torch.cat(parts)
    out = model.moe.compute_all_heads(anchor['obs'][ids], anchor['hist'][ids])
    loss = balanced_gate(out['g_logit'], anchor['gate'][ids], torch.ones_like(out['g_logit']))
    hard_pool = anchor.get('hard_negatives')
    if hard_pool is not None:
        hard_ids = pick(hard_pool['indices'], 192)
        hard_obs, hard_hist = hard_pool['obs'][hard_ids], hard_pool['hist'][hard_ids]
        norm, encoded = model.moe.encoder(hard_obs, hard_hist)
        hard_logit = model.moe.router.forward_logit(torch.cat((norm, encoded), dim=-1))
        loss = loss + .85 * F.softplus(hard_logit).mean()
    return loss


def warm_stair(model, role, optimizer, anchor, steps, end):
    progress = {'steps': 0}
    for step in range(steps):
        if end():
            break
        loss = stair_reference_loss(model, role, anchor)
        if not torch.isfinite(loss):
            raise RuntimeError('Non-finite stair reference loss')
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(optimizer.param_groups[0]['params'], .8, error_if_nonfinite=True)
        optimizer.step()
        if step == 0:
            progress['initial_loss'] = float(loss.detach())
        progress['steps'] += 1
        progress['last_loss'] = float(loss.detach())
    return progress


def train_iter(model, args, data, opt_actor, opt_critic, end, anchor=None, critic_only=False, jump_ref=None):
    n = len(data['obs'])
    loss_sum = defaultdict(float)
    steps = defaultdict(int)
    for _ in range(3):
        for ids in torch.randperm(n, device=data['obs'].device).split(512):
            if end():
                return dict(steps), dict(loss_sum)
            d = {k: a[ids] for k, a in data.items()}
            oracle = d['label'] if anchor is not None and args.role == 'stair' else None
            mean, std, _, _, _, logits = forward(model, args.role, d['obs'], d['hist'], d['permit'], oracle)
            do_actor = not critic_only and (args.role == 'router' or d['exploration'].any() or logits is not None)
            if do_actor:
                if logits is not None:
                    classification = balanced_gate(logits, d['label'], torch.where(d['permit'], 1., 1.6))
                    loss = classification * (1.0 if args.role == 'router' else .13)
                    loss_sum['gate'] += float(classification.detach())
                else:
                    loss = mean.sum() * 0.
                if args.role != 'router' and d['exploration'].any():
                    action_mask = d['exploration']
                    dist = torch.distributions.Normal(mean, std)
                    new = dist.log_prob(d['action']).sum(-1)[action_mask]
                    old = d['logp'][action_mask]
                    adv = d['adv'][action_mask]
                    ratio = (new - old).clamp(-15, 15).exp()
                    pg = -torch.minimum(ratio * adv, ratio.clamp(.86, 1.14) * adv).mean()
                    loss = loss + pg
                    loss_sum['ppo'] += float(pg.detach())
                    if jump_ref is not None:
                        with torch.no_grad():
                            base_action = jump_ref.act_deterministic(d['obs'][action_mask], selected_history(model, d['hist'][action_mask]))
                        reference = F.mse_loss(mean[action_mask], base_action)
                        loss = loss + args.anchor_weight * reference
                        loss_sum['reference'] += float(reference.detach())
                if anchor is not None:
                    ref_loss = stair_reference_loss(model, args.role, anchor)
                    loss = loss + args.anchor_weight * ref_loss
                    loss_sum['reference'] += float(ref_loss.detach())
                opt_actor.zero_grad(set_to_none=True)
                if not torch.isfinite(loss):
                    raise RuntimeError('Non-finite actor loss')
                loss.backward()
                torch.nn.utils.clip_grad_norm_(opt_actor.param_groups[0]['params'], .8, error_if_nonfinite=True)
                opt_actor.step()
                steps['actor'] += 1
            if opt_critic is not None:
                value = critic_value(model, d['obs'], d['hist'], d['priv'])
                c_loss = F.smooth_l1_loss(value, d['ret'], beta=2.0)
                opt_critic.zero_grad(set_to_none=True)
                c_loss.backward()
                torch.nn.utils.clip_grad_norm_(opt_critic.param_groups[0]['params'], 1., error_if_nonfinite=True)
                opt_critic.step()
                steps['critic'] += 1
                loss_sum['critic'] += float(c_loss.detach())
    return dict(steps), dict(loss_sum)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', choices=('router', 'stair', 'jump'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--num-envs', type=int, default=16)
    parser.add_argument('--seconds', type=int, default=2340)
    parser.add_argument('--iters', type=int, default=90)
    parser.add_argument('--horizon', type=int, default=144)
    parser.add_argument('--jump-bc', type=int, default=1600)
    parser.add_argument('--seed', type=int, default=20261120)
    parser.add_argument('--resume', type=Path)
    parser.add_argument('--stair-anchor', type=Path)
    parser.add_argument('--deployed-stair-router', type=Path, help='Use this frozen recognition model for E1 PPO rollouts.')
    parser.add_argument('--anchor-steps', type=int, default=1500)
    parser.add_argument('--anchor-weight', type=float)
    parser.add_argument('--router-negatives', type=Path)
    parser.add_argument('--fit-router-encoder', action='store_true')
    parser.add_argument('--dr-0-updates', type=int, default=8)
    parser.add_argument('--dr-partial-updates', type=int, default=10)
    parser.add_argument('--actor-lr', type=float)
    parser.add_argument('--leap', action='store_true')
    parser.add_argument('--stance-dr', type=int, choices=(0, 1), default=0)
    parser.add_argument('--leap-height-focus', action='store_true')
    parser.add_argument('--stair-low-stance-focus', action='store_true')
    parser.add_argument('--stair-high-slow-focus', action='store_true')
    parser.add_argument('--slow-approach-scale', type=float, default=1.)
    parser.add_argument('--stair-mid-stance-focus', action='store_true')
    parser.add_argument('--leap-moving-focus', action='store_true')
    parser.add_argument('--instant-moving-focus', action='store_true')
    parser.add_argument('--jump-top-support', action='store_true')
    parser.add_argument('--touchdown-focus', type=float, default=0.)
    parser.add_argument('--high-takeoff-focus', action='store_true')
    parser.add_argument('--sustained-high-jump', action='store_true')
    parser.add_argument('--high-jump-apex-focus', action='store_true')
    parser.add_argument('--high-jump-impulse-focus', action='store_true')
    parser.add_argument('--clean-jump-apex', action='store_true')
    parser.add_argument('--min-landing-apex', type=float, default=0.)
    parser.add_argument('--varied-jump-runup', action='store_true')
    parser.add_argument('--direct-jump-landing', action='store_true')
    parser.add_argument('--jump-lip-focus', action='store_true')
    parser.add_argument('--jump-airborne-height-focus', action='store_true')
    parser.add_argument('--jump-loaded-push', action='store_true')
    parser.add_argument('--jump-launch-energy', action='store_true')
    parser.add_argument('--wasd-crouch-speed', type=float, default=0.)
    parser.add_argument('--stair-recovery-focus', action='store_true')
    parser.add_argument('--stair-restart-focus', action='store_true')
    parser.add_argument('--parked-retake-focus', action='store_true')
    parser.add_argument('--wasd-restart-focus', action='store_true')
    parser.add_argument('--cpu', action='store_true')
    parser.add_argument('--probe', action='store_true')
    args = parser.parse_args()
    if args.anchor_weight is None:
        args.anchor_weight = {'router': .6, 'stair': 2., 'jump': 3.}[args.role]
    torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    stop = False

    def request_stop(_sig, _frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    if args.leap and args.role != 'jump':
        parser.error('--leap requires --role jump')
    if (args.leap_height_focus or args.leap_moving_focus) and not args.leap:
        parser.error('Leap focus options require --leap')
    if args.instant_moving_focus and (args.role != 'jump' or args.leap):
        parser.error('--instant-moving-focus requires the instant jump expert')
    if not 0. < args.slow_approach_scale <= 1. or (args.slow_approach_scale != 1. and not args.stair_high_slow_focus):
        parser.error('--slow-approach-scale requires --stair-high-slow-focus and a scale in (0, 1]')
    if args.sustained_high_jump and not (args.high_takeoff_focus and args.instant_moving_focus and args.jump_top_support):
        parser.error('--sustained-high-jump requires the matched takeoff fixture with top-support measurement')
    if args.wasd_crouch_speed and not (args.role == 'jump' and args.high_takeoff_focus
                                       and 0. < args.wasd_crouch_speed <= 1.):
        parser.error('--wasd-crouch-speed requires the high-stance takeoff fixture')
    if args.jump_launch_energy and not (args.role == 'jump' and args.jump_airborne_height_focus):
        parser.error('--jump-launch-energy requires the airborne height objective')
    if args.deployed_stair_router and args.role != 'stair':
        parser.error('--deployed-stair-router requires --role stair')
    if args.stair_recovery_focus and not (args.role != 'jump' and args.wasd_restart_focus):
        parser.error('--stair-recovery-focus requires the WASD stair fixture')
    if args.jump_loaded_push and not (args.jump_airborne_height_focus and args.high_jump_impulse_focus):
        parser.error('--jump-loaded-push requires airborne height and loaded impulse measurements')
    if args.jump_airborne_height_focus and not args.jump_lip_focus:
        parser.error('--jump-airborne-height-focus requires --jump-lip-focus')
    if args.jump_lip_focus and not (args.role == 'jump' and args.direct_jump_landing and args.varied_jump_runup):
        parser.error('--jump-lip-focus requires the varied direct jump landing fixture')
    if args.parked_retake_focus and (args.role == 'jump' or not (args.stair_restart_focus and args.stair_low_stance_focus)):
        parser.error('--parked-retake-focus requires the low-stance restart fixture')
    if args.wasd_restart_focus and not args.parked_retake_focus:
        parser.error('--wasd-restart-focus requires --parked-retake-focus')
    if args.high_jump_impulse_focus and not args.high_jump_apex_focus:
        parser.error('--high-jump-impulse-focus requires --high-jump-apex-focus')
    if args.clean_jump_apex and not (args.high_jump_impulse_focus and args.sustained_high_jump):
        parser.error('--clean-jump-apex requires the sustained flight and loaded stroke rewards')
    if not 0. <= args.min_landing_apex <= .22 or args.min_landing_apex and not args.clean_jump_apex:
        parser.error('--min-landing-apex must be in [0, .22] and positive values require --clean-jump-apex')
    if args.direct_jump_landing and not (args.varied_jump_runup and args.jump_top_support):
        parser.error('--direct-jump-landing requires varied run-up and top support measurement')
    if args.varied_jump_runup and not (args.clean_jump_apex and args.min_landing_apex > 0.):
        parser.error('--varied-jump-runup requires the clean jump credit and a main-flight clearance')
    if args.high_jump_apex_focus and not args.sustained_high_jump:
        parser.error('--high-jump-apex-focus requires sustained high jump')
    if not np.isfinite(args.touchdown_focus) or args.touchdown_focus < 0. or (args.touchdown_focus and not args.instant_moving_focus):
        parser.error('--touchdown-focus requires --instant-moving-focus and a nonnegative weight')
    if args.role == 'jump':
        (LeapFixture if args.leap else JumpFixture)(args.seed)
    else:
        # Build the shared XML before forking. Each subprocess gets independent MjData.
        StairFixture(args.seed)
    anchor_on = args.stair_anchor is not None and args.role != 'jump'
    env = Fixtures(args.role, args.num_envs, args.seed, measure_substeps=anchor_on, leap=args.leap,
                   stance_dr=bool(args.stance_dr), leap_height_focus=args.leap_height_focus,
                   stair_low_stance_focus=args.stair_low_stance_focus, stair_high_slow_focus=args.stair_high_slow_focus,
                   leap_moving_focus=args.leap_moving_focus, stair_restart_focus=args.stair_restart_focus,
                   instant_moving_focus=args.instant_moving_focus, jump_top_support=args.jump_top_support,
                   stair_mid_stance_focus=args.stair_mid_stance_focus, touchdown_focus=args.touchdown_focus,
                   high_takeoff_focus=args.high_takeoff_focus, sustained_high_jump=args.sustained_high_jump,
                   high_jump_apex_focus=args.high_jump_apex_focus, parked_retake_focus=args.parked_retake_focus,
                   high_jump_impulse_focus=args.high_jump_impulse_focus, clean_jump_apex=args.clean_jump_apex,
                   min_landing_apex=args.min_landing_apex, varied_jump_runup=args.varied_jump_runup,
                   wasd_restart_focus=args.wasd_restart_focus, direct_jump_landing=args.direct_jump_landing,
                   jump_lip_focus=args.jump_lip_focus, jump_airborne_height_focus=args.jump_airborne_height_focus,
                   jump_loaded_push=args.jump_loaded_push, stair_recovery_focus=args.stair_recovery_focus,
                   jump_launch_energy=args.jump_launch_energy, wasd_crouch_speed=args.wasd_crouch_speed)
    try:
        device = torch.device('cpu' if args.cpu else 'cuda')
        model = parent_model(args.role, args.resume, args.leap).to(device)
        model.slow_approach_scale = args.slow_approach_scale
        if args.deployed_stair_router:
            reference = parent_model('router', args.deployed_stair_router).moe.to(device).eval().requires_grad_(False)
            # Keep the externally pinned router out of the trained expert state dict.
            object.__setattr__(model, 'deployed_stair_router', reference)
        jump_ref = copy.deepcopy(model).requires_grad_(False).eval() if args.leap or args.instant_moving_focus else None
        if args.role == 'router':
            model.requires_grad_(False)
            model.moe.router.requires_grad_(True)
            params = list(model.moe.router.parameters())
            if args.fit_router_encoder:
                model.moe.encoder.requires_grad_(True)
                params += list(model.moe.encoder.parameters())
        elif args.role == 'stair':
            if anchor_on or args.deployed_stair_router:
                model.moe.router.requires_grad_(False)
            params = [p for p in model.moe.parameters() if p.requires_grad] + [model.stair_log_std]
        else:
            params = [p for p in model.actor_body.e_jump.parameters() if p.requires_grad] + [model.ejump_log_std]
        actor_lr = args.actor_lr if args.actor_lr is not None else {'router': 1.3e-4, 'stair': 2.e-5, 'jump': 4.e-5}[args.role]
        opt_actor = torch.optim.Adam(params, lr=actor_lr, eps=1e-5)
        opt_critic = None if args.role == 'router' else torch.optim.Adam(model.critic.parameters(), lr=3.e-4, eps=1e-5)
        start = time.monotonic()

        def end():
            return stop or (out / 'REQUEST_STOP').exists() or time.monotonic() - start >= args.seconds

        ident = {'role': args.role, 'device': str(device), 'gpu': torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU',
                 'visible_device': os.environ.get('CUDA_VISIBLE_DEVICES', ''), 'pid': os.getpid(), 'started_epoch': time.time(),
                 'budget_seconds': args.seconds, 'actor_lr': actor_lr, 'anchor_weight': args.anchor_weight,
                 'leap_height_focus': args.leap_height_focus, 'stair_low_stance_focus': args.stair_low_stance_focus,
                 'stair_high_slow_focus': args.stair_high_slow_focus, 'slow_approach_scale': args.slow_approach_scale,
                 'leap_moving_focus': args.leap_moving_focus, 'touchdown_focus': args.touchdown_focus,
                 'stair_restart_focus': args.stair_restart_focus, 'instant_moving_focus': args.instant_moving_focus,
                 'jump_top_support': args.jump_top_support, 'stair_mid_stance_focus': args.stair_mid_stance_focus,
                 'high_takeoff_focus': args.high_takeoff_focus, 'sustained_high_jump': args.sustained_high_jump,
                 'high_jump_apex_focus': args.high_jump_apex_focus, 'parked_retake_focus': args.parked_retake_focus,
                 'high_jump_impulse_focus': args.high_jump_impulse_focus, 'clean_jump_apex': args.clean_jump_apex,
                 'min_landing_apex': args.min_landing_apex, 'varied_jump_runup': args.varied_jump_runup,
                 'wasd_restart_focus': args.wasd_restart_focus,
                 'direct_jump_landing': args.direct_jump_landing,
                 'jump_lip_focus': args.jump_lip_focus,
                 'jump_airborne_height_focus': args.jump_airborne_height_focus,
                 'jump_loaded_push': args.jump_loaded_push, 'jump_launch_energy': args.jump_launch_energy,
                 'stair_recovery_focus': args.stair_recovery_focus, 'wasd_crouch_speed': args.wasd_crouch_speed,
                 'deployed_stair_router_sha256': sha(args.deployed_stair_router) if args.deployed_stair_router else None,
                 'parent': sha(args.resume) if args.resume else sha(LEAP_PARENT) if args.leap else EXPECTED_SHA[
                     'jump' if args.role == 'jump' else 'stair']}
        save_json(out / 'STARTED.json', ident)
        packet = env.reset(0.)
        hist = batch(packet, 'obs', device)[:, None].expand(-1, HIST_LEN, -1).clone()
        if args.probe:
            data, _, _, episodes = collect(model, args.role, env, packet, hist, args.horizon, device, 0., False, end)
            report = {'zero_updates': True, 'frames': len(data['obs']), 'closed_loop': summary(episodes),
                      'finite': all(bool(torch.isfinite(data[k]).all()) for k in ('rew', 'obs', 'hist', 'action')),
                      'frozen_E0': model.verify_zero_e0_drift()}
            save_json(out / 'PROBE.json', report)
            print(json.dumps(report), flush=True)
            if not report['finite'] or report['frozen_E0'] != 0:
                raise RuntimeError('Failed zero-update probe')
            return
        bc = None
        anchor = None
        if anchor_on:
            anchor = torch.load(args.stair_anchor, map_location=device, weights_only=True)
            anchor['positive'] = torch.where(anchor['gate'] > .5)[0]
            anchor['negative'] = torch.where(anchor['gate'] <= .5)[0]
            if args.role == 'stair' and 'impact' in anchor and anchor['impact'].any():
                anchor['impact_indices'] = torch.where(anchor['impact'])[0]
            if 'hard' in anchor and anchor['hard'].any():
                anchor['hard_indices'] = torch.where(anchor['hard'])[0]
            height_edges = anchor['obs'].new_tensor([.30, .34, .37, .39, .41])
            skill_rows = anchor['positive']
            buckets = torch.bucketize(anchor['obs'][skill_rows, 3].contiguous() / 5., height_edges)
            by_height = tuple(skill_rows[buckets == i] for i in range(len(height_edges) + 1))
            anchor['positive_groups'] = tuple(rows for rows in by_height if len(rows))
            if sum(map(len, anchor['positive_groups'])) != len(skill_rows):
                raise RuntimeError('Some active stair rows were not assigned to a height group')
            if args.router_negatives is not None:
                negatives = torch.load(args.router_negatives, map_location=device, weights_only=True)
                negatives['indices'] = torch.arange(len(negatives['obs']), device=device)
                anchor['hard_negatives'] = negatives
            warm_opt = torch.optim.Adam(params, lr=1.5e-4, eps=1e-5)
            bc = warm_stair(model, args.role, warm_opt, anchor, args.anchor_steps, end)
            bc['examples'] = len(anchor['obs'])
            bc['active'] = len(anchor['positive'])
            bc['active_height_counts'] = [len(ids) for ids in anchor['positive_groups']]
            if 'hard_indices' in anchor:
                bc['post_probe_wall_frames'] = len(anchor['hard_indices'])
            if 'impact_indices' in anchor:
                bc['targeted_impact_frames'] = len(anchor['impact_indices'])
            if args.router_negatives is not None:
                bc['hard_negative_frames'] = len(anchor['hard_negatives']['obs'])
                bc['hard_negative_sha'] = sha(args.router_negatives)
            bc['sha256'] = sha(args.stair_anchor)
            save_json(out / 'STAIR_ANCHOR.json', bc)
            save_weights(model, args.role, out / 'model_warm.pt', ident | {'seed_fit': bc}, opt_actor, opt_critic)
        if args.role == 'jump' and not args.resume and not args.leap:
            warm_opt = torch.optim.Adam(params, lr=2.0e-4, eps=1e-5)
            bc = train_jump_seed(model, warm_opt, device, args.jump_bc, args.seed)
            if bc:
                save_json(out / 'JUMP_ANCHOR.json', bc)
        progress = {'iteration': 0, 'frames': 0, 'actor_updates': 0, 'critic_updates': 0, 'seed_fit': bc}
        recent = []
        last_saved = 0.
        for iteration in range(1, args.iters + 1):
            if end():
                break
            dr = (0.0 if iteration <= args.dr_0_updates else
                  .35 if iteration <= args.dr_0_updates + args.dr_partial_updates else 1.)
            model.eval()
            data, packet, hist, complete = collect(model, args.role, env, packet, hist, args.horizon, device, dr, True, end,
                                                 oracle_stair=anchor_on and args.role == 'stair')
            recent.extend(complete)
            if data is None or end():
                break
            model.train()
            updates, loss = train_iter(model, args, data, opt_actor, opt_critic, end, anchor=anchor,
                                       critic_only=(anchor_on and args.role == 'stair' or jump_ref is not None) and iteration <= 5, jump_ref=jump_ref)
            progress.update(iteration=iteration, frames=progress['frames'] + len(data['obs']), dr=dr,
                            actor_updates=progress['actor_updates'] + updates.get('actor', 0),
                            critic_updates=progress['critic_updates'] + updates.get('critic', 0),
                            total_episodes=len(recent), recent=summary(recent[-128:]), loss=loss,
                            gate_positive_frames=int(data['label'].sum()), exploration_frames=int(data['exploration'].sum()),
                            elapsed_s=round(time.monotonic() - start, 3))
            if iteration == 1 or (time.monotonic() - start) - last_saved >= DWELL_CHECK or iteration % 8 == 0:
                checkpoint = out / f'model_{iteration:04d}.pt'
                progress['checkpoint'] = checkpoint.name
                progress['checkpoint_sha256'] = save_weights(model, args.role, checkpoint, ident | progress, opt_actor, opt_critic)
                last_saved = time.monotonic() - start
            save_json(out / 'LATEST.json', progress)
            print(json.dumps(progress, allow_nan=False), flush=True)
        checkpoint = out / 'model_final.pt'
        progress['checkpoint'] = checkpoint.name
        progress['checkpoint_sha256'] = save_weights(model, args.role, checkpoint, ident | progress, opt_actor, opt_critic)
        save_json(out / 'EPISODES.json', recent)
        save_json(out / 'FINISHED.json', ident | progress | {'closed_epoch': time.time()})
    finally:
        env.close()


if __name__ == '__main__':
    main()
