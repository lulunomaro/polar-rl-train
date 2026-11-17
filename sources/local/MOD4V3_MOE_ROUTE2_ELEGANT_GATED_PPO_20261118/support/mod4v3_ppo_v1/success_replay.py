"""Phase-isolated E1-only native success replay; pinned v1 settle never evicts."""
from pathlib import Path
import hashlib
import json
import numpy as np
import torch

LOCKED_V1_SHA = 'a55eeaed11ed7c7471444e1369153824b3fe79544e59296c911a3235507bd7a4'


class SuccessReplayPool:
    """Four-phase isolated pool:
    0: settle_high (v_cmd==0, h_cmd>0.34) - pinned from frozen v1, never evicted
    1: approach    (v_cmd>0,  top_support==0) - dedicated FIFO
    2: top_climb   (v_cmd>0,  top_support>0)  - dedicated FIFO
    3: top_park    (v_cmd==0, h_cmd<=0.34, top_support==2) - dedicated FIFO
    """

    def __init__(self, max_frames=32768, seed=907, max_online_speed=0.78, strict_speed=0.60):
        self.max_frames = max_frames
        self.phase_caps = {
            0: max(4096, max_frames // 4),
            1: max(4096, max_frames * 3 // 8),
            2: max(4096, max_frames * 3 // 8),
            3: max(4096, max_frames // 4),
        }
        self.pinned_settle = []
        self.phase_chunks = {0: [], 1: [], 2: [], 3: []}
        self.phase_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        self.episodes = []
        self.frames = 0
        self.total_accepted = 0
        self.total_rejected_speed = 0
        self.strict_online_added = 0
        self.max_online_speed = max_online_speed
        self.strict_speed = strict_speed
        self.cache = None
        self.generator = torch.Generator(device='cpu').manual_seed(seed)

    def _classify_phases(self, frames, raw_phases):
        cmd = frames[:, 0]
        h_scaled = frames[:, 3]
        out = np.asarray(raw_phases, dtype=np.int64).copy()
        zero_cmd = np.abs(cmd) < 0.05
        out[zero_cmd & (h_scaled > 1.7)] = 0
        out[zero_cmd & (h_scaled <= 1.7) & (raw_phases == 2)] = 3
        out[zero_cmd & (h_scaled <= 1.7) & (raw_phases == 3)] = 3
        return out

    def _recompute_totals(self):
        pinned_n = sum(len(x) for x in self.pinned_settle)
        self.phase_counts[0] = pinned_n + sum(len(x) for x in self.phase_chunks[0])
        for p in (1, 2, 3):
            self.phase_counts[p] = sum(len(x) for x in self.phase_chunks[p])
        self.frames = sum(self.phase_counts.values())
        self.cache = None

    def _append_phase(self, phase, tensor_frames, pin=False):
        if not len(tensor_frames):
            return
        cap = self.phase_caps[phase]
        if len(tensor_frames) > cap:
            tensor_frames = tensor_frames[-cap:]
        if pin and phase == 0:
            self.pinned_settle.append(tensor_frames)
            return
        bucket = self.phase_chunks[phase]
        bucket.append(tensor_frames)
        total = sum(len(x) for x in bucket)
        while total > cap and len(bucket) > 1:
            removed = bucket.pop(0)
            total -= len(removed)

    def add(self, frames, phases, metadata):
        assert metadata['accepted_native_success'] and metadata['stable_hold_s'] >= 0.4 - 1e-6
        assert frames.ndim == 2 and frames.shape[1] == 461 and phases.shape == (len(frames),)
        assert np.isfinite(frames).all() and np.isin(phases, [0, 1, 2, 3]).all()
        metadata = metadata.copy()
        frozen_v1 = (
            bool(metadata.get('source_model_sha256'))
            and metadata.get('policy_update', 0) == 0
            and sum(len(x) for x in self.pinned_settle) < 500
        )
        typed_phases = self._classify_phases(frames, phases)

        if frozen_v1:
            settle_mask = typed_phases == 0
            if np.any(settle_mask):
                self._append_phase(0, torch.from_numpy(frames[settle_mask].copy()).float(), pin=True)
            obs = frames[:, :35]
            rim_start = float((np.abs(obs[50:min(90, len(obs)), 20:22]) * 10.0 * 0.0625).max()) if len(obs) > 55 else 0.0
            allow_motion = rim_start <= 0.72 or len(obs) <= 55
            if allow_motion:
                for p in (1, 2, 3):
                    m = typed_phases == p
                    if np.any(m):
                        self._append_phase(p, torch.from_numpy(frames[m].copy()).float(), pin=False)
            self.total_accepted += 1
            self.episodes.append((int(len(frames)), metadata))
            if len(self.episodes) > 256:
                self.episodes.pop(0)
            self._recompute_totals()
            return True

        ep_speed = metadata.get('episode_max_speed_m_s')
        active_cap = self.strict_speed if self.strict_online_added >= 8 else self.max_online_speed
        if ep_speed is not None and float(ep_speed) > active_cap + 1e-6:
            self.total_rejected_speed += 1
            return False

        # Exclude pre-command tall startup from non-v1 policies so settle stays 100% pure v1.
        keep_mask = typed_phases != 0
        kept_frames = frames[keep_mask]
        kept_phases = typed_phases[keep_mask]
        if not len(kept_frames):
            return False

        for p in (1, 2, 3):
            m = kept_phases == p
            if np.any(m):
                self._append_phase(p, torch.from_numpy(kept_frames[m].copy()).float(), pin=False)

        if ep_speed is not None and float(ep_speed) <= self.strict_speed + 1e-6:
            self.strict_online_added += 1
        self.total_accepted += 1
        self.episodes.append((int(len(kept_frames)), metadata))
        if len(self.episodes) > 256:
            self.episodes.pop(0)
        self._recompute_totals()
        return True

    def load_directory(self, directory):
        for path in sorted(Path(directory).glob('episode_*.npz')):
            with np.load(path, allow_pickle=False) as d:
                meta = json.loads(str(d['metadata_json']))
                self.add(d['frames'], d['phases'], meta)

    def _build_cache(self):
        built = {}
        s_list = self.pinned_settle + self.phase_chunks[0]
        built[0] = torch.cat(s_list, dim=0) if s_list else None
        for p in (1, 2, 3):
            built[p] = torch.cat(self.phase_chunks[p], dim=0) if self.phase_chunks[p] else None
        self.cache = built
        return built

    def sample(self, n, device):
        if not self.frames:
            return None
        built = self.cache if self.cache is not None else self._build_cache()
        has_park = built[3] is not None and len(built[3]) > 0
        if has_park:
            q0 = round(n * 0.20)
            q1 = round(n * 0.25)
            q2 = round(n * 0.35)
            q3 = n - q0 - q1 - q2
            quotas = [(0, q0), (1, q1), (2, q2), (3, q3)]
        else:
            q0 = round(n * 0.25)
            q1 = round(n * 0.30)
            q2 = n - q0 - q1
            quotas = [(0, q0), (1, q1), (2, q2)]

        available = [p for p in (0, 1, 2, 3) if built[p] is not None and len(built[p]) > 0]
        if not available:
            return None

        parts = []
        for p, count in quotas:
            if count <= 0:
                continue
            pool_p = built[p]
            if pool_p is None or len(pool_p) == 0:
                # Safe fallback: settle falls back only to settle/top_park, never to rushing approach if avoidable.
                fallback_p = 0 if (0 in available) else available[0]
                pool_p = built[fallback_p]
            idx = torch.randint(len(pool_p), (count,), generator=self.generator)
            parts.append(pool_p[idx])
        f = torch.cat(parts, dim=0).to(device)
        return dict(policy=f[:, :35], obs_history=f[:, 35:455], actions=f[:, 455:461])

    def checkpoint_state(self):
        return dict(
            max_frames=self.max_frames,
            phase_caps=self.phase_caps,
            pinned_settle=self.pinned_settle,
            phase_chunks=self.phase_chunks,
            phase_counts=self.phase_counts,
            frames=self.frames,
            total_accepted=self.total_accepted,
            total_rejected_speed=self.total_rejected_speed,
            strict_online_added=self.strict_online_added,
            generator_state=self.generator.get_state(),
        )

    def summary(self):
        counts = [int(self.phase_counts[i]) for i in (0, 1, 2, 3)]
        return dict(
            kept_episodes=len(self.episodes),
            kept_frames=int(self.frames),
            pinned_settle_frames=int(sum(len(x) for x in self.pinned_settle)),
            total_accepted=int(self.total_accepted),
            total_rejected_speed=int(self.total_rejected_speed),
            strict_online_added=int(self.strict_online_added),
            phase_frame_counts=counts,
            phases=['settle_high', 'approach', 'top_climb', 'top_park'],
            formal_or_fullDR_graduation=False,
        )


class NativeSuccessRecorder:
    def __init__(self, env, directory, source_sha256, pool=None, window=None):
        self.env = env
        self.ids = env.continuous_stair_mask.nonzero().flatten()
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.source_sha256 = source_sha256
        self.pool = pool or SuccessReplayPool()
        self.window = int(window or (env.max_episode_length + 1))
        self.cursor = 0
        self.frames = torch.zeros(self.window, len(self.ids), 461, device=env.device)
        self.phases = torch.zeros(self.window, len(self.ids), dtype=torch.int8, device=env.device)
        self.length = torch.zeros(len(self.ids), dtype=torch.long, device=env.device)
        self.saved = 0
        self.steps = 0
        self.policy_update = 0

    def push(self, observations, executed_actions, policy_update=0):
        self.frames[self.cursor] = torch.cat(
            [
                observations['policy'][self.ids],
                observations['obs_history'][self.ids],
                executed_actions[self.ids].clamp(-6, 6),
            ],
            1,
        ).detach()
        self.length += 1
        self.policy_update = policy_update

    def finish(self, done):
        env = self.env
        support = env.replay_top_support_count[self.ids]
        command = self.frames[self.cursor, :, 0]
        h_scaled = self.frames[self.cursor, :, 3]
        zero_cmd = command.abs() < 0.05
        phase_now = torch.where(
            zero_cmd & (h_scaled > 1.7),
            torch.zeros_like(support),
            torch.where(
                zero_cmd & (h_scaled <= 1.7) & (support == 2),
                torch.full_like(support, 3),
                torch.where(support > 0, torch.full_like(support, 2), torch.ones_like(support)),
            ),
        )
        self.phases[self.cursor] = phase_now.to(torch.int8)
        success = env.replay_success_now[self.ids]
        for local in success.nonzero().flatten().tolist():
            amount = min(int(self.length[local]), self.window)
            slots = torch.arange(self.cursor - amount + 1, self.cursor + 1, device=env.device) % self.window
            frames = self.frames[slots, local].detach().cpu().numpy()
            phases = self.phases[slots, local].detach().cpu().numpy()
            idx = int(self.ids[local])
            ep_max_spd = float(env.course_speed_max[idx])
            ep_entry_spd = float(env.course_entry_speed[idx])
            meta = dict(
                accepted_native_success=True,
                stable_hold_s=0.4,
                parked_hold_s=float(getattr(env, 'course_park_hold', torch.zeros(env.num_envs))[idx]),
                qualification='native training real bilateral climb hold + v=0 h=0.20 top park',
                formal_evaluation_pass=False,
                source_model_sha256=self.source_sha256,
                policy_update=self.policy_update,
                env_id=idx,
                episode_steps=int(self.length[local]),
                truncated=int(self.length[local]) > self.window,
                physics_dt_s=0.0025,
                policy_dt_s=0.02,
                history_H=12,
                teacher_assistance=False,
                actual_full_DR=bool(env.replay_actual_DR_at_step[idx]),
                speed_limit_m_s=float(env.replay_speed_limit_at_step[idx]),
                episode_max_speed_m_s=ep_max_spd,
                entry_speed_m_s=ep_entry_spd,
                strict_speed_qualified=bool(ep_max_spd <= 0.60 and ep_entry_spd <= 0.60),
            )
            admitted = self.pool.add(frames, phases, meta)
            meta['admitted_to_BC_pool'] = bool(admitted)
            self.saved += 1
            path = self.directory / f'episode_{self.saved:06d}.npz'
            pending = path.with_name(path.stem + '.partial.npz')
            np.savez_compressed(pending, frames=frames, phases=phases, metadata_json=np.asarray(json.dumps(meta)))
            pending.replace(path)
        self.length[done[self.ids]] = 0
        self.cursor = (self.cursor + 1) % self.window
        self.steps += 1
        if bool(success.any()):
            self.write_manifest()

    def write_manifest(self):
        files = {
            p.name: dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
            for p in self.directory.glob('episode_*.npz')
        }
        tmp = self.directory / 'MANIFEST.json.partial'
        tmp.write_text(
            json.dumps(
                dict(
                    **self.pool.summary(),
                    new_saved_episodes=self.saved,
                    source_model_sha256=self.source_sha256,
                    files=files,
                ),
                indent=2,
            )
            + '\n'
        )
        tmp.replace(self.directory / 'MANIFEST.json')

    def summary(self):
        return dict(**self.pool.summary(), new_saved_episodes=self.saved, recorded_policy_steps=self.steps)
