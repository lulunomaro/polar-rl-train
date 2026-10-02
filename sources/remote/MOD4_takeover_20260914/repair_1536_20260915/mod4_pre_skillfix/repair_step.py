"""Explicit phase hooks for the frozen MOD4 task. No simulator initialization here."""
from __future__ import annotations
import os
import torch

PRE = ("push_wrench", "leg_effort_noise", "wheel_effort_noise", "gas_spring_preload")
POST = ("ground_track", "skill_cmds", "route_cmd_term", "air_state", "jump_state",
        "landing_state", "tunnel_state")
ACCOUNT = ("route_stats", "plant_metrics")


class RepairStepMixin:
    def _repair_configure(self, cfg):
        names = set(PRE + POST + ACCOUNT)
        configured = set()
        for name in dir(cfg.events):
            term = getattr(cfg.events, name)
            if getattr(term, "mode", None) == "step":
                if name not in names:
                    raise ValueError("unclassified step event: " + name)
                # Unique modes retain EventManager's entity resolution and class handling.
                term.mode = "repair_" + name
                configured.add(name)
        required = set(POST + ACCOUNT + ("gas_spring_preload",))
        if required - configured:
            raise ValueError("missing required rmuc2026 events: " + str(sorted(required-configured)))
        self._repair_audit = os.environ.get("RM_EPISODE_AUDIT", "0") == "1"

    def _repair_apply(self, names):
        for name in names:
            mode = "repair_" + name
            if mode in self.event_manager.available_modes:
                self.event_manager.apply(mode=mode, dt=self.step_dt)

    def _repair_buffers(self):
        if not hasattr(self, "_repair_episode_id"):
            self._repair_episode_id = torch.full((self.num_envs,), -1, device=self.device, dtype=torch.long)
            self._repair_landed = torch.zeros(self.num_envs, device=self.device, dtype=torch.bool)

    def _repair_reset_buffers(self, env_ids):
        self._repair_buffers()
        self._repair_episode_id[env_ids] += 1
        self._repair_landed[env_ids] = False
        timer = getattr(self, "_mod4_land_timer", None)
        if timer is not None:
            timer[env_ids] = 0
        progress = getattr(self, "_mod4_route_progress", None)
        if isinstance(progress, dict):
            for v in progress.values():
                if isinstance(v, torch.Tensor) and v.ndim and v.shape[0] == self.num_envs:
                    v[env_ids] = 0

    def _perkind_account(self, iteration: int, out_dir: str) -> None:
        """Append one row per route kind: episodes attempted / succeeded so far.

        Episodes, not steps (audit 75): a kind's attempt count only increments when an env's
        episode id changes while it sits on that kind, so one 20 s episode counts once.
        """
        import csv
        import os
        ids = getattr(self, "_mod4_route_ids", None)
        prog = getattr(self, "_mod4_route_progress", None)
        if ids is None or not isinstance(prog, dict):
            return
        kinds = [r.get("kind") for r in getattr(getattr(self, "_mod4_routes", None), "routes", [])]
        if not kinds:
            return
        try:
            idl = ids.detach().to("cpu").tolist()
            succ = prog.get("success")
            succl = succ.detach().to("cpu").tolist() if succ is not None else [0.0] * len(idl)
            epid = getattr(self, "_repair_episode_id", None)
            epidl = epid.detach().to("cpu").tolist() if epid is not None else [0] * len(idl)
        except Exception:
            return
        ledger = getattr(self, "_perkind_ledger", None)
        if ledger is None:
            from repair_contracts import PerKindProgress
            ledger = self._perkind_ledger = PerKindProgress()
        try:
            st = ledger.update(idl, epidl, succl, kinds)
        except ValueError as exc:
            print("[perkind] rejected inconsistent live state: %s" % exc, flush=True)
            return
        path = os.path.join(out_dir, "perkind_progress.csv")
        new = not os.path.exists(path)
        with open(path, "a", newline="") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["iteration", "kind", "attempts", "successes", "rate"])
            for kind, rec in sorted(st.items()):
                rate = (rec["suc"] / rec["att"]) if rec["att"] else ""
                w.writerow([iteration, kind, rec["att"], rec["suc"],
                            ("%.4f" % rate) if rate != "" else ""])

    def _repair_publish_reference(self):
        """Pure command calculation: no elapsed/progress/flight counters advance."""
        rc = getattr(self, "_mod4_routes", None)
        if rc is None or not getattr(self, "_mod4_route_ready", False):
            return
        robot = self.scene["robot"]
        p = robot.data.root_pos_w - self.scene.env_origins
        q = robot.data.root_quat_w  # target build uses xyzw; version-bound by runtime manifest
        yaw = torch.atan2(2 * (q[:, 3] * q[:, 2] + q[:, 0] * q[:, 1]),
                          1 - 2 * (q[:, 1].square() + q[:, 2].square()))
        delta = rc.goals[rc.ids, :2] - p[:, :2]
        heading = torch.atan2(delta[:, 1], delta[:, 0])
        error = torch.atan2(torch.sin(heading-yaw), torch.cos(heading-yaw))
        term = self.command_manager.get_term("twist")
        cmd = term.command
        cmd[:, 0] = rc.speed * torch.cos(error).clamp(0, 1)
        cmd[:, 1] = 0
        cmd[:, 2] = (2 * error).clamp(-2, 2)
        kinds = rc.route_kinds[rc.ids]
        spin = kinds == rc.kind_ids["slope_spin"]
        jump = kinds == rc.kind_ids["jump_in_place"]
        cmd[spin, 0] = 0
        cmd[spin, 2] = rc.spin_speed[spin]
        cmd[jump] = 0
        cmd[rc.finished] = 0
        if hasattr(term, "time_left"):
            term.time_left[:] = 1e9
        if hasattr(term, "is_standing_env"):
            term.is_standing_env[:] = False
        # Height is initialized at reset and recomputed after physics. Recompute the
        # geometry-only tunnel command after reset too (no time accumulation).
        self._repair_apply(("tunnel_state",))

    def _repair_before_physics(self):
        self._repair_buffers()
        self._repair_apply(PRE)
        # Rewards must use the command the policy actually OBSERVED for this action.
        self._repair_old_twist = self.command_manager.get_term("twist").command.clone()
        h = getattr(self, "_mod4_height_cmd", None)
        self._repair_old_height = None if h is None else h.clone()

    def _repair_after_physics(self):
        rc = getattr(self, "_mod4_routes", None)
        if rc is None:
            raise RuntimeError("this repair overlay targets the rmuc2026 route task only")
        # Restore nominal height before computing temporary landing/tunnel overrides.
        # Previously the landing height could remain latched after its timer expired.
        table = getattr(self, "_mod4_route_height", None)
        h = getattr(self, "_mod4_height_cmd", None)
        if table is not None and h is not None:
            h[:, 0] = table[rc.ids]
        self._repair_apply(POST)
        self._repair_landed |= self._mod4_just_landed.bool()
        self._repair_next_twist = self.command_manager.get_term("twist").command.clone()
        self._repair_next_height = self._mod4_height_cmd.clone()
        self.command_manager.get_term("twist").command.copy_(self._repair_old_twist)
        if self._repair_old_height is not None:
            self._mod4_height_cmd.copy_(self._repair_old_height)

    def _repair_after_reward(self):
        # Curriculum/plant logs now read the physics transition and current termination.
        self._repair_apply(ACCOUNT)
        batch = self._repair_terminal_snapshot() if self._repair_audit else []
        self.command_manager.get_term("twist").command.copy_(self._repair_next_twist)
        self._mod4_height_cmd.copy_(self._repair_next_height)
        return batch

    def _repair_terminal_snapshot(self):
        """Only completed episodes; copied to CPU BEFORE _reset_idx clears their state."""
        ids = self.reset_buf.nonzero(as_tuple=False).flatten()
        if ids.numel() == 0:
            return []
        rc = self._mod4_routes
        rid = rc.ids[ids]
        def take(x):
            return x[ids].detach().cpu().tolist()
        terms = {name: take(self.termination_manager.get_term(name).bool())
                 for name in self.termination_manager.active_terms}
        data = {
            "env_id": ids.detach().cpu().tolist(), "episode_id": take(self._repair_episode_id),
            "route_id": rid.detach().cpu().tolist(),
            "duration_s": take(self.episode_length_buf * self.step_dt),
            "terminated": take(self.reset_terminated), "truncated": take(self.reset_time_outs),
            "goal_seen": take(rc.finished), "underpass_seen": take(rc.underpass_visited),
            "launched": take(rc.launched), "air_after_launch": take(rc.air_after_launch),
            "landed": take(self._repair_landed), "spin_deg": take(torch.rad2deg(rc.spin_angle)),
            "peak_rise_m": take((rc.peak_z - rc.starts[rc.ids, 2] - rc.base_height).clamp(min=0)),
            "max_air_time_s": take(rc.max_air_time),
        }
        return [{**{k: v[i] for k, v in data.items()},
                 "terms": {k: v[i] for k, v in terms.items()}}
                for i in range(len(data["env_id"]))]
