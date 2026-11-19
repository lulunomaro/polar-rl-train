# SPDX-License-Identifier: MIT
"""WASD intent arbitration and independent candidate loading for the MOD4v3 MoE."""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
import torch

from restart_router import RestartRouter, RestartSkillRouter, WINDOW as RESTART_WINDOW

HERE = Path(__file__).resolve().parent
PLAYER_DIR = HERE.parent / 'MOD4V3_AUTONOMOUS_MOE_ALL_MAPS_20261120'
sys.path.insert(0, str(PLAYER_DIR))
from autonomous_three_expert import AutonomousThreeExpert, SOURCE_SHA, load as load_parent, same_locomotion, stair, jump  # noqa: E402
from all_maps_runtime import CONTROL_DT, AutonomousMapSimulation, map_for, maps  # noqa: E402

maps.CACHE_DIR = HERE / 'runtime_cache' / f'player_{os.getpid()}'


class RepairedPolicy(AutonomousThreeExpert):
    def __init__(self):
        super().__init__()
        self.router_weights = None
        self.high_router_weights = None
        self.restart_router = None
        self.high_restart_router = None
        self.parked_restart_router = None
        self.restart_history = deque(maxlen=RESTART_WINDOW)
        self.stair_height_bank = ()
        self.slow_stair = None
        self.mid_stair = None
        self.rising_stair = None
        self.stair_driver_speed = None
        self.allow_stair = False
        self.jump_frames = jump.GATE_STEPS
        self.jump_history_frames = jump.HIST_LEN
        self.moving_jump = None
        self.moving_jump_frames = jump.GATE_STEPS
        self.moving_jump_history_frames = jump.HIST_LEN
        self.use_moving_jump = False
        self.jump_min_forward = 0.0
        self.stair_gate_floor = stair.GATE_DEADZONE
        self.stair_release_per_tick = 1.0
        self.restart_release_per_tick = 1.0
        self.high_restart_release_per_tick = 1.0
        self.stair_mix = 0.0
        self.handoff_mix = 0.0
        self.handoff_gains = None
        self.low_handoff_gains = None
        self.immediate_stair_stop = False
        self.handoff_duration = .44

    def reset_history(self):
        super().reset_history()
        self.restart_history.clear()
        self.stair_mix = 0.0
        self.handoff_mix = 0.0

    def set_handoff_gains(self, values, *, low_stance=False):
        if values is not None:
            gains = np.asarray(values, dtype=np.float32)
            if gains.shape not in ((6,), (12,)) or not np.isfinite(gains).all():
                raise ValueError('Expected six or twelve finite handoff gains')
            if low_stance:
                if gains.shape != (12,):
                    raise ValueError('Expected twelve low-stance handoff gains')
                self.low_handoff_gains = gains.reshape(4, 3)
            else:
                self.handoff_gains = gains.reshape(-1, 3)

    def handoff_action(self, obs, action, previous_mix, permit):
        self.handoff_mix = (0.0 if permit else
                            max(previous_mix, self.handoff_mix - CONTROL_DT / self.handoff_duration, 0.0))
        gains = self.handoff_gains
        if gains is None or self.handoff_mix <= 0.0:
            return action
        # Equal corrections on both sides leave the requested yaw differential intact.
        tilt = np.tanh(7. * obs[7] + .8 * obs[5])
        if self.low_handoff_gains is not None:
            if len(gains) != len(self.low_handoff_gains):
                raise ValueError('Height interpolation requires twelve gains at each end')
            low = float(np.clip((.36 - float(obs[3]) / 5.) / .04, 0., 1.))
            gains = gains + low * (self.low_handoff_gains - gains)
        if len(gains) == 2:
            height_scale = np.clip((float(obs[3]) / 5. - .37) / .05, 0., 1.)
            pair = height_scale * (gains[0] + tilt * gains[1])
        else:
            wheel_error = np.tanh(.7 * ((obs[20] + obs[21]) * .5 - 1.6 * obs[0]))
            folded_leg = np.tanh(1.6 * (obs[11] + obs[13]) * .5)
            pair = gains[0] + tilt * gains[1] + wheel_error * gains[2] + folded_leg * gains[3]
        return action + self.handoff_mix * pair[[0, 1, 0, 1, 2, 2]]

    def height_stair_outputs(self, current, history):
        if not self.stair_height_bank:
            return self.stair.compute_all_heads(current, history)
        height = float(current[0, 3]) / 5.
        bank = self.stair_height_bank
        by_height = [item[0] for item in bank]
        index = bisect_right(by_height, height)
        if index == 0:
            return bank[0][1].compute_all_heads(current, history)
        if index == len(bank):
            return bank[-1][1].compute_all_heads(current, history)
        low_h, low = bank[index - 1]
        high_h, high = bank[index]
        lower = low.compute_all_heads(current, history)
        if low is high:
            return lower
        blend = min(1., max(0., (height - low_h) / (high_h - low_h)))
        if blend < 1e-5:
            return lower
        upper = high.compute_all_heads(current, history)
        if blend > 1. - 1e-5:
            return upper
        for field in ('a_stair', 'h_virt', 'v_virt'):
            lower[field] = torch.lerp(lower[field], upper[field], blend)
        return lower

    def stair_outputs(self, current, history):
        out = self.height_stair_outputs(current, history)
        requested_height = float(current[0, 3]) / 5.
        if self.mid_stair is not None:
            # Keep the learned .36 m correction local to its training range.
            weight = float(np.clip((.009 - abs(requested_height - .36)) / .007, 0., 1.))
            if weight > 0.:
                middle = self.mid_stair.compute_all_heads(current, history)
                for name in ('a_stair', 'h_virt', 'v_virt'):
                    out[name] = torch.lerp(out[name], middle[name], weight)
        if self.rising_stair is not None and self.restart_history and requested_height > .40:
            recent_height = min(float(obs[3]) / 5. for obs in list(self.restart_history)[-68:])
            raised = float(np.clip((requested_height - recent_height) / .035, 0., 1.))
            tall = float(np.clip((requested_height - .40) / .02, 0., 1.))
            weight = raised * tall
            if weight > 0.:
                rising = self.rising_stair.compute_all_heads(current, history)
                for name in ('a_stair', 'h_virt', 'v_virt'):
                    out[name] = torch.lerp(out[name], rising[name], weight)
        if self.slow_stair is None:
            return out
        # The actuator receives the slewed command via obs[0]. Expert selection uses
        # the driver's speed setpoint because every restart briefly slews through low speed.
        requested_speed = self.stair_driver_speed if self.stair_driver_speed is not None else float(current[0, 0])
        tall = float(np.clip((requested_height - .36) / .040, 0., 1.))
        slow = float(np.clip((.72 - requested_speed) / .18, 0., 1.))
        weight = tall * slow
        if weight > 0.:
            alternative = self.slow_stair.compute_all_heads(current, history)
            for name in ('a_stair', 'h_virt', 'v_virt'):
                out[name] = torch.lerp(out[name], alternative[name], weight)
        return out

    @staticmethod
    def router_probability(model, current, history):
        norm, features = model.encoder(current, history)
        return float(model.router.forward_logit(torch.cat((norm, features), dim=-1)).sigmoid().item())

    def restart_outputs(self, router):
        if isinstance(router, RestartSkillRouter):
            return router.evaluate(self.restart_history)
        context, probability = router.probability(self.restart_history)
        return context, probability, np.zeros(3, dtype=np.float32)

    def parked_restart_outputs(self, height, baseline):
        """Use the learned low-stance restart gate after neutral forward release."""
        weight = float(np.clip((.35 - height) / .021, 0., 1.))
        if self.parked_restart_router is None or weight == 0.:
            return baseline
        recent_commands = list(self.restart_history)[-104:]
        if any(float(row[0]) < -.10 for row in recent_commands):
            return baseline
        context, probability, _ = self.parked_restart_router.evaluate(self.restart_history)
        contact_mix = float(np.clip(.5 + (probability - .76) / .10, 0., 1.))
        base_context, base_mix, base_delta = baseline
        return (base_context + weight * (context - base_context),
                base_mix + weight * (contact_mix - base_mix),
                (1. - weight) * base_delta)

    @torch.inference_mode()
    def act(self, obs: np.ndarray):
        x = torch.from_numpy(obs).reshape(1, stair.OBS_DIM)
        history = self.history.append(x)
        if self.restart_router is not None or self.rising_stair is not None:
            self.restart_history.append(obs.copy())
        if obs[jump.JUMP_MODE_BIT_INDEX] > 0.5:
            self.stair_mix = 0.0
            self.handoff_mix = 0.0
            expert = self.moving_jump if self.use_moving_jump else self.jump
            frames = self.moving_jump_history_frames if self.use_moving_jump else self.jump_history_frames
            jump_history = history.reshape(1, stair.HIST_LEN, stair.OBS_DIM)[:, -frames:]
            current = x
            if not self.use_moving_jump and self.jump_min_forward > 0. and obs[0] >= 0.:
                current = x.clone()
                current[:, 0] = current[:, 0].clamp_min(self.jump_min_forward)
                jump_history = jump_history.clone()
                commanded = jump_history[:, :, 30] > .5
                vx = jump_history[:, :, 0]
                jump_history[:, :, 0] = torch.where(commanded & (vx >= 0.), vx.clamp_min(self.jump_min_forward), vx)
            action = expert(current, jump_history.flatten(1)).clamp(-jump.ACTION_CLIP, jump.ACTION_CLIP)
            return action[0].numpy(), {'e0':0.0, 'e1':0.0, 'e2':1.0, 'g_prob':0.0}
        current = stair.canonicalize_normal_obs(x)
        h = stair.canonicalize_normal_obs(history.view(1, stair.HIST_LEN, stair.OBS_DIM)).flatten(1)
        out = self.stair_outputs(current, h)
        if self.router_weights is None:
            probability = float(out['g_prob'].item())
        else:
            # The separately trained router keeps its own encoder so E1 retraining cannot move its inputs.
            probability = self.router_probability(self.router_weights, current, h)
        if self.high_router_weights is not None:
            height = float(current[0, 3]) / 5.
            tall = min(1.0, max(0.0, (height - .325) / .010))
            if tall > 0.0:
                high_probability = self.router_probability(self.high_router_weights, current, h)
                probability += tall * (high_probability - probability)
        permit = self.allow_stair
        release = self.stair_release_per_tick
        restart_delta = None
        if permit and self.restart_router is not None:
            height = float(current[0, 3]) / 5.
            baseline = self.restart_outputs(self.restart_router)
            resumed, restart_probability, restart_delta = self.parked_restart_outputs(height, baseline)
            restart_release = self.restart_release_per_tick
            if self.high_restart_router is not None:
                tall = float(np.clip((height - .40) / .018, 0., 1.))
                if tall == 1.0:
                    resumed, restart_probability, restart_delta = self.restart_outputs(self.high_restart_router)
                    restart_release = self.high_restart_release_per_tick
                elif tall > 0.0:
                    high_context, high_probability, high_delta = self.restart_outputs(self.high_restart_router)
                    resumed += tall * (high_context - resumed)
                    restart_probability += tall * (high_probability - restart_probability)
                    restart_delta += tall * (high_delta - restart_delta)
                    restart_release += tall * (self.high_restart_release_per_tick - restart_release)
            authority = float(np.clip((resumed - .75) / .18, 0., 1.))
            probability += authority * (restart_probability - probability)
            release += authority * (restart_release - release)
        floor = self.stair_gate_floor
        proposed = max(0.0, (probability - floor) / (1.0 - floor))
        # A brief drop in confidence must not interrupt a committed lift. The
        # driver override still releases the stair branch on the current tick.
        previous_mix = self.stair_mix
        self.stair_mix = max(proposed, previous_mix - release) if permit else 0.0
        g = self.stair_mix
        action = torch.lerp(out['a_e0'], out['a_stair'], g)[0].numpy()
        if restart_delta is not None:
            action += g * authority * restart_delta[[0, 1, 0, 1, 2, 2]]
        action = self.handoff_action(obs, action, previous_mix, permit)
        action = np.clip(action, -stair.ACTION_CLIP, stair.ACTION_CLIP)
        return action, {'e0':1.0-g, 'e1':g, 'e2':0.0, 'g_prob':probability,
                                   'stair_permitted':float(permit), 'virtual_height':float(out['h_virt'].item()),
                                   'virtual_velocity':float(out['v_virt'].item())}


def load_jump_expert(raw, base_state):
    if raw.get('model_type') == 'MOD4v3_MoE_RL_HighMovingJump':
        sys.path.insert(0, str(HERE.parent / 'MOD4V3_RL_HIGH_MOVING_JUMP_20261118'))
        from moe_jump_model import HIST_LEN, PureNeuralJumpExpert
        weights = raw['state_dict']
        expert, history_frames, request_frames = PureNeuralJumpExpert(), HIST_LEN, 72
    elif raw.get('model_type') == 'MOD4v3_MoE_RL_ForwardLeap_StepJump':
        sys.path.insert(0, str(HERE.parent / 'MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118'))
        from moe_forward_leap_model import HIST_LEN, PureNeuralForwardLeapExpert
        weights = raw['state_dict']
        expert, history_frames, request_frames = PureNeuralForwardLeapExpert(), HIST_LEN, 95
    else:
        weights = raw['model_state_dict']
        expert, history_frames, request_frames = jump.InstantPureNeuralJumpExpert(), jump.HIST_LEN, jump.GATE_STEPS
    same_locomotion(base_state, weights, 'actor_body.e0.')
    same_locomotion(base_state, weights, 'actor_body.e_jump.loco_base.')
    prefix = 'actor_body.e_jump.'
    state = {k.removeprefix(prefix): value for k, value in weights.items() if k.startswith(prefix)}
    expert.load_state_dict(state, strict=True)
    return expert, history_frames, request_frames


def load_candidate(stair_path=None, router_path=None, jump_path=None, *, keep_fast_moving_jump=False,
                   stair_height_bank=None, high_router_path=None, slow_stair_path=None, moving_jump_path=None,
                   restart_router_path=None, high_restart_router_path=None, parked_restart_router_path=None,
                   mid_stair_path=None, rising_stair_path=None):
    torch.set_num_threads(1)
    parent, parent_sha = load_parent()
    model = RepairedPolicy()
    model.load_state_dict(parent.state_dict(), strict=True)
    base_state = parent.stair.e0.state_dict()
    hashes = {'package': parent_sha}
    if keep_fast_moving_jump:
        model.moving_jump = parent.jump
        hashes['moving_jump'] = SOURCE_SHA['E2']
    for role, path in [('stair', stair_path), ('router', router_path), ('high_router', high_router_path),
                       ('slow_stair', slow_stair_path), ('mid_stair', mid_stair_path), ('rising_stair', rising_stair_path),
                       ('jump', jump_path), ('moving_jump', moving_jump_path)]:
        if path is None:
            continue
        path = Path(path)
        raw = torch.load(path, map_location='cpu', weights_only=True)
        hashes[role] = hashlib.sha256(path.read_bytes()).hexdigest()
        if role in ('jump', 'moving_jump'):
            expert, history_frames, request_frames = load_jump_expert(raw, base_state)
            setattr(model, role, expert)
            setattr(model, role + '_history_frames', history_frames)
            setattr(model, role + '_frames', request_frames)
        else:
            weights = raw['moe_state_dict']
            same_locomotion(base_state, weights, 'e0.')
            same_locomotion(base_state, weights, 'e1_stair.loco_base.')
            if role in ('router', 'high_router', 'slow_stair', 'mid_stair', 'rising_stair'):
                network = stair.AutonomousStairMoE()
                network.load_state_dict(weights, strict=True)
                setattr(model, role + '_weights' if role in ('router', 'high_router') else role, network)
            else:
                model.stair.load_state_dict(weights, strict=True)
    if stair_height_bank is not None:
        if router_path is None:
            raise ValueError('A shared router is required with the stair height bank')
        plan_file = Path(stair_height_bank).resolve()
        hashes['stair_height_bank'] = hashlib.sha256(plan_file.read_bytes()).hexdigest()
        plan = json.loads(plan_file.read_text(encoding='utf8'))
        experts = {}
        for point in plan:
            height = float(point['height_m'])
            path = (plan_file.parent / point['path']).resolve()
            if model.stair_height_bank and height <= model.stair_height_bank[-1][0]:
                raise ValueError('The stair height bank must use strictly increasing heights')
            if path not in experts:
                checkpoint = torch.load(path, map_location='cpu', weights_only=True)
                weights = checkpoint['moe_state_dict']
                same_locomotion(base_state, weights, 'e0.')
                same_locomotion(base_state, weights, 'e1_stair.loco_base.')
                network = stair.AutonomousStairMoE()
                network.load_state_dict(weights, strict=True)
                experts[path] = network.eval().requires_grad_(False)
            hashes[f'stair_height_{height:.3f}'] = hashlib.sha256(path.read_bytes()).hexdigest()
            model.stair_height_bank += ((height, experts[path]),)
    if restart_router_path is None and (high_restart_router_path is not None or parked_restart_router_path is not None):
        raise ValueError('Restart specializations require the primary restart model')
    for role, weight_file in (('restart_router', restart_router_path), ('high_restart_router', high_restart_router_path),
                              ('parked_restart_router', parked_restart_router_path)):
        if weight_file is None:
            continue
        path = Path(weight_file)
        raw = torch.load(path, map_location='cpu', weights_only=True)
        network = RestartSkillRouter() if raw.get('restart_action') else RestartRouter()
        network.load_state_dict(raw['state_dict'], strict=True)
        setattr(model, role, network)
        hashes[role] = hashlib.sha256(path.read_bytes()).hexdigest()
    model.provenance = hashes
    return model.eval().requires_grad_(False), hashes


class RepairedSimulation(AutonomousMapSimulation):
    def __init__(self, policy, sha, *, show_viewer=True, jump_stance_prep=False):
        self.jump_stance_prep = jump_stance_prep
        self.jump_height = None
        self.jump_pending = False
        self.jump_prepare_frames = 0
        super().__init__(policy, sha, show_viewer=show_viewer)

    def reset_at_spawn(self, spawn_idx=None):
        self.jump_height = None
        self.jump_pending = False
        self.jump_prepare_frames = 0
        return super().reset_at_spawn(spawn_idx)

    def request_jump(self):
        if self.jump_pending or self.jump_rem:
            return False
        if self.jump_stance_prep and self.target_h > .305:
            self.jump_height = self.target_h if self.jump_height is None else self.jump_height
            self.jump_pending = True
            self.jump_prepare_frames = 0
            self.jump_launch_gz = self.ground_z(*self.d.qpos[:2])  # Telemetry only.
            return True
        return self.start_jump()

    def start_jump(self):
        if not super().request_jump():
            return False
        # Select once at the keypress from the driver's commanded speed. The mode and
        # history stay coherent through landing, even if W is released while in the air.
        self.unified.use_moving_jump = self.unified.moving_jump is not None and abs(self.cmd_vx) >= .15
        self.jump_rem = self.unified.moving_jump_frames if self.unified.use_moving_jump else self.unified.jump_frames
        return True

    def update_jump_height(self, pressed):
        if self.jump_pending:
            # Explicit reverse cancels a queued launch while the wheels are on the ground.
            if 's' in pressed or ('a' in pressed) != ('d' in pressed):
                self.jump_pending = False
                return
            self.jump_height = max(.28, self.jump_height - .28 * CONTROL_DT)
            if self.jump_height <= .280001:
                self.jump_prepare_frames += 1
                if self.jump_prepare_frames >= 10:
                    self.jump_pending = False
                    self.start_jump()
        elif self.jump_height is not None and not self.jump_rem:
            delta = float(np.clip(self.target_h - self.jump_height, -.12 * CONTROL_DT, .12 * CONTROL_DT))
            self.jump_height += delta
            if abs(self.jump_height - self.target_h) < 1e-6:
                self.jump_height = None

    def _observe(self, jump_requested):
        obs = super()._observe(jump_requested)
        if self.jump_height is not None:
            obs[3] = self.jump_height * 5.
        return obs

    def telemetry(self):
        status = super().telemetry()
        status['source_sha256'] = {**SOURCE_SHA, **self.unified.provenance}
        status['jump_pending'] = self.jump_pending
        status['effective_target_h'] = self.target_h if self.jump_height is None else self.jump_height
        return status

    def step(self, pressed):
        if self.paused:
            return
        forward = int('w' in pressed) - int('s' in pressed)
        explicit_turn = ('a' in pressed) != ('d' in pressed)
        # Raw operator intent arrives before the command slew or history. It is independent of obstacle detection.
        self.update_jump_height(pressed)
        self.unified.allow_stair = forward > 0 and not explicit_turn and not self.jump_pending
        self.unified.stair_driver_speed = self.max_vx if self.unified.allow_stair else None
        stopping_stair = (
            self.unified.immediate_stair_stop and forward == 0 and self.cmd_vx > 0.0
            and (self.unified.stair_mix > 0.0 or self.unified.handoff_mix > 0.0)
        )
        if stopping_stair or forward * self.cmd_vx < 0:
            self.cmd_vx = 0.0
        super().step(pressed)


def read_candidate(path):
    candidate_file = Path(path).resolve()
    manifest = json.loads(candidate_file.read_text(encoding='utf8'))
    paths = {k: candidate_file.parent / v for k, v in manifest['checkpoints'].items()}
    return manifest, paths


def load_manifest(path):
    manifest, paths = read_candidate(path)
    settings = manifest['settings']
    model, hashes = load_candidate(paths.get('stair'), paths.get('router'), paths.get('jump'),
                                   stair_height_bank=paths.get('stair_height_bank'),
                                   high_router_path=paths.get('high_router'), slow_stair_path=paths.get('slow_stair'),
                                   moving_jump_path=paths.get('moving_jump'),
                                   keep_fast_moving_jump=settings.get('keep_fast_moving_jump', False),
                                   restart_router_path=paths.get('restart_router'),
                                   high_restart_router_path=paths.get('high_restart_router'),
                                   parked_restart_router_path=paths.get('parked_restart_router'),
                                   mid_stair_path=paths.get('mid_stair'), rising_stair_path=paths.get('rising_stair'))
    if hashes != manifest['sha256']:
        raise RuntimeError('The loaded policy does not match the validated candidate hashes')
    model.jump_min_forward = float(settings.get('jump_min_forward', 0.0))
    model.stair_gate_floor = float(settings.get('gate_floor', stair.GATE_DEADZONE))
    model.stair_release_per_tick = float(settings.get('gate_release', 1.0))
    model.restart_release_per_tick = float(settings.get('restart_release', model.stair_release_per_tick))
    model.high_restart_release_per_tick = float(settings.get('high_restart_release', model.restart_release_per_tick))
    model.set_handoff_gains(settings.get('handoff_gains'))
    model.set_handoff_gains(settings.get('low_handoff_gains'), low_stance=True)
    model.immediate_stair_stop = bool(settings.get('immediate_stair_stop', False))
    model.handoff_duration = float(settings.get('handoff_duration', .44))
    if not np.isfinite(model.handoff_duration) or model.handoff_duration <= 0.:
        raise ValueError('Handoff duration must be positive and finite')
    executable_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    identity = {'weights': hashes, 'settings': settings, 'player': executable_sha}
    if model.restart_router is not None:
        identity['restart_router_source'] = hashlib.sha256((HERE / 'restart_router.py').read_bytes()).hexdigest()
    model.runtime_sha = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return model, hashes, bool(settings.get('jump_stance_prep', False))


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--candidate', type=Path)
    args.add_argument('--stair-height-bank', type=Path)
    args.add_argument('--high-router', type=Path)
    for name in ('stair', 'router', 'jump'):
        args.add_argument(f'--{name}', type=Path)
    args.add_argument('--keep-fast-moving-jump', action='store_true')
    args.add_argument('--jump-stance-prep', action='store_true')
    args.add_argument('--jump-min-forward', type=float, default=0.0)
    args.add_argument('--gate-floor', type=float, default=stair.GATE_DEADZONE)
    args.add_argument('--gate-release', type=float, default=1.0)
    cli = args.parse_args()
    if cli.candidate:
        model, hashes, stance_prep = load_manifest(cli.candidate)
    else:
        model, hashes = load_candidate(cli.stair, cli.router, cli.jump, keep_fast_moving_jump=cli.keep_fast_moving_jump,
                                       stair_height_bank=cli.stair_height_bank, high_router_path=cli.high_router)
        model.jump_min_forward = cli.jump_min_forward
        model.stair_gate_floor = cli.gate_floor
        model.stair_release_per_tick = cli.gate_release
        stance_prep = cli.jump_stance_prep
    import tkinter as tk
    import play_autonomous_all_maps as play
    play.STATUS_PATH = HERE / 'PLAYER_STATUS.json'
    play.ERROR_PATH = HERE / 'PLAYER_ERROR.txt'
    identity = getattr(model, 'runtime_sha', None) or hashlib.sha256(repr(hashes).encode()).hexdigest()
    root = tk.Tk()
    sim = RepairedSimulation(model, identity, show_viewer=True, jump_stance_prep=stance_prep)
    class StepPlayer(play.AutonomousPlayer):
        def apply_suite_selection(self, initial=False):
            if initial and cli.candidate:
                self.suite_cb.current(4)
                self.sub_cb.configure(values=play.STAIR_SCENES, state='readonly')
                self.sub_var.set('20 cm 单阶')
            return super().apply_suite_selection(initial=initial)

    StepPlayer(root, sim)
    root.title(f'MOD4v3 自动 MoE · 修复试验 · {identity[:8]}')
    root.mainloop()


if __name__ == '__main__':
    main()
