from pathlib import Path
import json

probe = Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/scut_rough_v0_22cap_1h_20261109_r2/full_dr_probe_20261110_r1')
base = probe.parent
plan = json.loads((base / 'PLAN_LOCAL.json').read_text())

for name, support in [('base', probe/'support_base'), ('scut', probe/'support_scut_solver')]:
    p = dict(plan)
    p['support'] = str(support)
    (probe / f'PLAN_{name}.json').write_text(json.dumps(p, indent=2) + '\n')

    env_path = support / 'mod4v3_ppo_v1' / 'scut_flat_env.py'
    s = env_path.read_text()
    if 'import json, os, math' not in s:
        s = s.replace('import math\n', 'import json, os, math\n', 1)
    anchor = '        r._numerical_safety_reset_buf.copy_(self.numeric)\n'
    block = r'''        if os.environ.get("FULL_DR_PROBE_LOG", "0") == "1":
            logged = getattr(self, "_probe_numeric_logged", None)
            if logged is None:
                logged = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
                self._probe_numeric_logged = logged
            bad = self.numeric & ~logged
            if bool(bad.any()):
                d = self.view.data
                bad_ids = bad.nonzero(as_tuple=False).flatten()[:16]
                names = [self.robot.joint_names[i] for i in self.active_ids]
                full_dr = getattr(self, 'full_dr', None)
                ext_force = getattr(self, '_external_force', None)
                ext_torque = getattr(self, '_external_torque', None)
                ext_timer = getattr(self, '_external_timer', None)
                ext_hold = getattr(self, '_external_hold', None)
                action_delay = getattr(self, '_action_delay_steps', None)
                obs_delay = getattr(self, '_obs_delay_steps', None)
                for idx_t in bad_ids:
                    idx = int(idx_t.item())
                    joint_vels = {name: float(v) for name, v in zip(names, d.joint_vel[idx, self.active_ids].detach().cpu())}
                    row = {
                        'env': idx,
                        'step': int(self.episode_length_buf[idx].item()),
                        'command': self.command[idx].detach().cpu().tolist(),
                        'height_cmd': float(self.height[idx].detach().cpu()),
                        'root_pos': d.root_pos_w[idx].detach().cpu().tolist(),
                        'root_quat': d.root_quat_w[idx].detach().cpu().tolist(),
                        'root_lin_vel_b': d.root_lin_vel_b[idx].detach().cpu().tolist(),
                        'root_ang_vel_b': d.root_ang_vel_b[idx].detach().cpu().tolist(),
                        'joint_vel': joint_vels,
                        'closure_m': float(self.closure_error[idx].detach().cpu()),
                        'mimic_m': float(self.mimic_error[idx].detach().cpu()),
                        'mass_scale': None if full_dr is None else full_dr.mass_scale[idx].detach().cpu().tolist(),
                        'material_mu': None if full_dr is None else float(full_dr.material_mu[idx].detach().cpu()),
                        'gas_target': self.gas_targets[idx].detach().cpu().tolist(),
                        'external_force': None if ext_force is None else ext_force[idx].detach().cpu().tolist(),
                        'external_torque': None if ext_torque is None else ext_torque[idx].detach().cpu().tolist(),
                        'external_timer': None if ext_timer is None else float(ext_timer[idx].detach().cpu()),
                        'external_hold': None if ext_hold is None else int(ext_hold[idx].detach().cpu()),
                        'action_delay_steps': None if action_delay is None else int(action_delay[idx].detach().cpu()),
                        'obs_delay_steps': None if obs_delay is None else int(obs_delay[idx].detach().cpu()),
                    }
                    print('PROBE_NUMERIC ' + json.dumps(row, default=str), flush=True)
                logged[bad] = True
'''
    if anchor not in s:
        raise SystemExit(f'anchor missing in {env_path}')
    if 'FULL_DR_PROBE_LOG' not in s:
        s = s.replace(anchor, anchor + block, 1)
    env_path.write_text(s)

    train_path = support / 'mod4v3_ppo_v1' / 'scut_flat_train.py'
    t = train_path.read_text()
    if '--fixed-probe-steps' not in t:
        t = t.replace("    parser.add_argument('--iterations',type=int,default=100000)\n",
                      "    parser.add_argument('--iterations',type=int,default=100000)\n    parser.add_argument('--fixed-probe-steps',type=int,default=0)\n", 1)
    old_loop = '            while not bool(counts.all()) and steps<501:\n'
    new_loop = '            probe_limit = args.fixed_probe_steps if args.fixed_probe_steps > 0 else 501\n            while (steps < probe_limit) if args.fixed_probe_steps > 0 else (not bool(counts.all()) and steps < 501):\n'
    if old_loop not in t:
        raise SystemExit(f'loop missing in {train_path}')
    t = t.replace(old_loop, new_loop, 1)
    train_path.write_text(t)

    if name == 'scut':
        s = env_path.read_text()
        s = s.replace('solver_position_iteration_count=32,solver_velocity_iteration_count=4',
                      'solver_position_iteration_count=12,solver_velocity_iteration_count=6')
        s = s.replace('max_position_iteration_count=255 if rough else 32,max_velocity_iteration_count=255 if rough else 4',
                      'max_position_iteration_count=255,max_velocity_iteration_count=255')
        env_path.write_text(s)

print('PATCHED', probe)
