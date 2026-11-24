"""One shared CPU control path for WASD, calibration, evaluation and video."""
from collections import deque
import json
import math
import numpy as np
import torch
import mujoco as mj
from fsm_paths import (HERE, E0_PATH, E0_SHA, JUMP_PATH, JUMP_SHA_PREFIX, R61_DIR,
                       STAIR_DONOR, donor_imports)
from fsm_io import sha256, put
from manual_fsm_model import SymmetricE0, StairExpert, effective_height, make_stair
from manual_fsm_core import ManualFSM, DetectorConfig, Phase, LABELS
from fsm_maps import reference

donor_imports()
legacy = reference.legacy
from jump380_r10_policy import load_policy as load_jump
from jump360_r3_policy import R3Control
from jump360_scene import JumpPlant

DT, SUBSTEPS = .0025, 8
CONTROL_DT = DT*SUBSTEPS
PPO_TO_NATIVE = np.array([0, 2, 1, 3, 4, 5])

def seed_stair(path=None, expert=2):
    path = Path(path) if path else HERE/f'weights/stair_seed_soft{expert}.pt'
    if path.exists():
        return path
    torch.manual_seed(11222026)
    model = StairExpert().warm_soft_expert(torch.load(STAIR_DONOR, map_location='cpu', weights_only=False), expert)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(dict(format='mod4v3_manual_fsm_stair_v1', stair=model.state_dict(),
                    donor_sha256=sha256(STAIR_DONOR), donor_expert=expert, optimizer_steps=0, ppo_updates=0), path)
    return path

from pathlib import Path

class ManualPolicy:
    def __init__(self, checkpoint=None, detector=None, load_jumps=True):
        torch.set_num_threads(1)
        if sha256(E0_PATH) != E0_SHA:
            raise ValueError('SELECTED_E0 SHA mismatch')
        self.e0 = SymmetricE0().load_e0(torch.load(E0_PATH, map_location='cpu', weights_only=False)).eval()
        if (HERE/'E0_CALIBRATION.json').is_file():
            self.e0.load_calibration(json.loads((HERE/'E0_CALIBRATION.json').read_text(encoding='utf-8')))
        if checkpoint is None and (HERE/'CANDIDATE.json').is_file():
            manifest = json.loads((HERE/'CANDIDATE.json').read_text(encoding='utf-8'))
            checkpoint = HERE/manifest['checkpoint']
            if sha256(checkpoint) != manifest['sha256']:
                raise ValueError('Candidate SHA mismatch')
        self.checkpoint = Path(checkpoint) if checkpoint else seed_stair()
        payload = torch.load(self.checkpoint, map_location='cpu', weights_only=False)
        self.stair = make_stair(payload).eval()
        self.sha = sha256(self.checkpoint)
        if detector is None and (HERE/'DETECTOR.json').is_file():
            detector = json.loads((HERE/'DETECTOR.json').read_text(encoding='utf-8'))['config']
        self.config = DetectorConfig(**detector) if isinstance(detector, dict) else (detector or DetectorConfig())
        self.fsm = ManualFSM(config=self.config)
        self.moving_jump = self.stationary_jump = None
        self.jump_history_frames = 12
        self.jump_frames = 45
        if load_jumps:
            if not sha256(JUMP_PATH).startswith(JUMP_SHA_PREFIX):
                raise ValueError('jump380_r10 SHA mismatch')
            self.moving_jump = R3Control(load_jump(JUMP_PATH))
            donor, _, _ = legacy.load_manifest(R61_DIR/'CANDIDATE_R61_RAISED_READY.json')
            self.stationary_jump = donor.jump.eval()
            self.jump_history_frames = donor.jump_history_frames
            self.jump_frames = donor.jump_frames
        self.intent = dict(mode=False, forward=False, reverse=False, force=False, jump=False)
        self.reset_history()

    def reset_history(self):
        self.history = None
        self.stationary_history = deque(maxlen=max(40, self.jump_history_frames))
        self.fsm.reset()
        self.jump_ticks = 0
        self.jump_kind = None
        self.jump_seen_motion = False
        self.jump_stable_ticks = 0
        self.jump_handoff_ticks = 0
        self.last_climb = torch.zeros(1, 6)
        self.last_action = torch.zeros(1, 6)
        self.route = dict(e0=1., e1=0., e2=0.)
        if self.moving_jump is not None:
            self.moving_jump.reset_history()

    @torch.inference_mode()
    def act(self, obs):
        x = torch.as_tensor(obs, dtype=torch.float32).reshape(1, 35).clone()
        self.fsm.update(x, **self.intent)
        self.intent['force'] = self.intent['jump'] = False
        phase = Phase(int(self.fsm.phase[0]))
        if phase != Phase.JUMP_380MM:
            x[:, 3] = 5.*self.fsm.height
        x[:, 30] = 0.
        if self.history is None:
            self.history = x[:, None].expand(-1, 12, -1).clone()
        else:
            self.history = torch.cat((self.history[:, 1:], x[:, None]), 1)
        self.stationary_history.append(x.clone())
        base = self.e0(x)
        self.last_effective_height=float(self.e0.observation(x)[0,3]*.2)
        weight = float(self.fsm.stair_weight[0])
        if weight == 1.:
            action = self.stair(torch.cat((x, self.history.flatten(1)), -1)).clamp(-6., 6.)
            self.last_climb = action.clone()
        elif phase == Phase.TREAD_BRIDGE and weight > 0.:
            action = torch.lerp(base, self.last_climb, weight)
        else:
            action = base
        jump_weight = 0.
        if phase == Phase.JUMP_380MM:
            self.jump_ticks += 1
            x[:, 30] = float(self.jump_ticks <= (self.jump_hold_ticks if self.jump_kind == 'moving' else self.jump_frames))
            self.history[:, -1] = x
            self.stationary_history[-1] = x.clone()
            if self.jump_kind == 'moving':
                if self.moving_jump is None:
                    raise RuntimeError('Jump weights were not loaded')
                action = torch.from_numpy(self.moving_jump(None, x[0].numpy())).reshape(1, 6)
            else:
                frames = list(self.stationary_history)
                while len(frames) < self.jump_history_frames:
                    frames.insert(0, frames[0])
                hist = torch.stack(frames[-self.jump_history_frames:], 1).flatten(1)
                action = self.stationary_jump(x, hist).clamp(-6., 6.)
            self.jump_seen_motion |= bool(x[0, 16:20].abs().amax() > .7 or x[0, 5].abs() > .3)
            stable = bool(x[0, 7].abs() < .26 and x[0, 5].abs() < .35 and x[0, 16:20].abs().mean() < .35)
            self.jump_stable_ticks = self.jump_stable_ticks+1 if stable else 0
            # R10's own recent-key history controls jump/drive recovery. Return
            # after a stable proprioceptive window; a timeout is reported separately.
            ready = self.jump_ticks >= max(65, self.jump_frames+12) and self.jump_stable_ticks >= 10
            timeout = self.jump_ticks >= 150
            if ready or timeout or self.jump_handoff_ticks:
                self.jump_handoff_ticks += 1
                blend = min(1., self.jump_handoff_ticks/8.) if not timeout else 1.
                action = torch.lerp(action, base, blend)
                if blend >= 1.:
                    self.fsm.phase[0] = Phase.CRUISE_E0
                    self.fsm.age[0] = 0
                    self.jump_exit_timeout = timeout and not ready
            jump_weight = 1.
            weight = 0.
        # Feed the moving expert every pre-key observation, preserving its exact
        # R3Control history without allowing its actions into cruise.
        elif self.moving_jump is not None:
            self.moving_jump(None, x[0].numpy())
        self.last_model_obs = x[0].numpy().copy()
        self.last_action = action
        self.route = dict(e0=1.-max(weight, jump_weight), e1=weight, e2=jump_weight)
        return action[0].numpy().copy(), self.route.copy()

    def request_jump(self, obs):
        if self.fsm.phase[0] == Phase.JUMP_380MM:
            return False
        rolling = float(np.mean(obs[20:22])*.625)
        self.jump_kind = 'moving' if obs[0] >= .95 or rolling >= .85 else 'stationary'
        self.jump_hold_ticks = getattr(self, 'jump_hold_override', 31)
        self.jump_ticks = self.jump_stable_ticks = 0
        self.jump_handoff_ticks = 0
        self.jump_exit_timeout = False
        self.intent['jump'] = True
        return True

class ManualSimulation(legacy.AutonomousMapSimulation):
    def __init__(self, policy, *, show_viewer=False):
        super().__init__(policy, policy.sha, show_viewer=show_viewer)
        self.max_vx = 1.2
        self.max_wz = 1.8
        self.target_h = .35
        self.mode_latched = False
        self.raw_keys = set()
        self.physics_observer = None
        self.dr = None

    def reset_at_spawn(self, spawn_idx=None):
        result = super().reset_at_spawn(spawn_idx)
        self.mode_latched = False
        self.raw_keys = set()
        self.unified.intent = dict(mode=False, forward=False, reverse=False, force=False, jump=False)
        return result

    def toggle_stair_mode(self):
        self.mode_latched = not self.mode_latched
        return self.mode_latched

    def request_jump(self):
        if self.m is None:
            return False
        accepted=self.unified.request_jump(self._observe(False))
        if accepted:self.mode_latched=False
        return accepted

    def step(self, pressed, command=None):
        if self.paused:
            return
        keys = set(pressed)
        rising = keys-self.raw_keys
        if 'c' in rising:
            self.toggle_stair_mode()
        if 'v' in rising:
            if 'f' not in keys:
                self.mode_latched = True
            self.unified.intent['force'] = True
        if 'space' in rising or 'j' in rising:
            self.request_jump()
        if '1' in rising:
            self.max_vx = 1.2
        if '2' in rising:
            self.max_vx = 2.8
        self.raw_keys = keys
        if command is None:
            forward = int('w' in keys)-int('s' in keys)
            turn = int('a' in keys)-int('d' in keys)
            self.target_h = float(np.clip(self.target_h+('e' in keys)*.0024-('q' in keys)*.0024, .24, .42))
            vx_goal = forward*self.max_vx
            wz_goal = turn*self.max_wz
        else:
            vx_goal, wz_goal = command
        self.cmd_vx += (vx_goal-self.cmd_vx)/12.
        self.cmd_wz += (wz_goal-self.cmd_wz)/12.
        self.unified.intent.update(mode=self.mode_latched or 'f' in keys, forward='w' in keys,
                                   reverse='s' in keys)
        obs = self._observe(False)
        if self.dr is not None:
            obs=self.dr.observe(obs)
        self.last_obs = obs.copy()
        action, self.route = self.unified.act(obs)
        if not np.isfinite(action).all():
            raise RuntimeError('Non-finite policy action')
        native = torch.from_numpy(action[PPO_TO_NATIVE]).reshape(1, 6)
        for sub in range(SUBSTEPS):
            if self.dr is not None:
                tau=self.dr.torque(action[PPO_TO_NATIVE],jump=bool(self.route['e2']) and self.unified.jump_kind=='moving')
            elif self.route['e2'] and self.unified.jump_kind=='moving':
                # R10 was validated with JumpPlant's target unwrap, which
                # relies on the pinned MJCF travel limits. The legacy map
                # player's extra target-difference clamp clips its push stroke.
                # Reuse the released jump motor mapping without editing the
                # plant, gains, frequency or voltage/torque envelope.
                if not hasattr(self.env, 'default_leg_q'):
                    self.env.default_leg_q=self.env.default_q[self.env.leg_ids].numpy().astype(np.float32)
                    self.env.kp_scale=np.ones(4,dtype=np.float32)
                    self.env.kd_scale=np.ones(4,dtype=np.float32)
                    self.env.kv_scale=np.ones(2,dtype=np.float32)
                    self.env.effort_scale=np.ones(6,dtype=np.float32)
                tau = JumpPlant._compute_motor_torque(self.env, native.numpy()[0])
            else:
                tau = self.env._torque(native).numpy().reshape(-1)
            if sub % 4 == 0:
                self.d.ctrl[self.env.act_ids[:4]] = tau[:4]
            self.d.ctrl[self.env.act_ids[4:]] = tau[4:]
            mj.mj_step(self.m, self.d)
            if self.dr is not None:
                self.dr.sample_sensors(self._observe(False))
            if self.physics_observer is not None:
                self.physics_observer(self)
        self.prev_a = action.copy()
        self.steps += 1
        self.closure_mm = 1000.*max(float(np.linalg.norm(self.d.site_xpos[a]-self.d.site_xpos[b])) for a,b in self.pairs)
        # Evaluation never silently resets or substitutes a successful episode.
        if not np.isfinite(self.d.qpos).all() or not np.isfinite(self.d.qvel).all():
            raise RuntimeError('Non-finite plant state')

