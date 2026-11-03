"""2026-11-03 second audit: boundary regressions, using CPU tensors only."""
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import torch

from .config import LEGS, observation_component, read_yaml, reward_config
from .validate import fixture
from .sdk import ScutBridge
from .train import ScutVecEnv
from .math_ops import quat_from_euler_xyz


class ReviewTests(unittest.TestCase):
    def test_all_26_enabled_base_terms_against_independent_numpy_equations(self):
        # No calls to the adapted math/helpers/raw_terms when building expected
        # values. This checks the selected saved recipe, not arbitrary profiles.
        n = 9
        r, robot, _ = fixture(n)
        c, d = r.cfg, robot.data
        rng = np.random.default_rng(270)
        def assign(name, value):
            getattr(d, name).copy_(torch.as_tensor(value, dtype=torch.float32))
        roll = np.linspace(-.25, .25, n)
        pitch = np.linspace(-.4, .4, n)
        yaw = np.linspace(-.6, .6, n)
        matrices = []
        for a,b,z in zip(roll,pitch,yaw):
            ca,sa,cb,sb,cz,sz = np.cos(a),np.sin(a),np.cos(b),np.sin(b),np.cos(z),np.sin(z)
            matrices.append([[cz*cb,cz*sb*sa-sz*ca,cz*sb*ca+sz*sa],
                             [sz*cb,sz*sb*sa+cz*ca,sz*sb*ca-cz*sa],[-sb,cb*sa,cb*ca]])
        rotation = np.array(matrices)
        q = quat_from_euler_xyz(*[torch.tensor(x,dtype=torch.float32) for x in (roll,pitch,yaw)])
        d.root_quat_w.copy_(q[:, [1,2,3,0]])
        gravity = np.einsum('nji,j->ni',rotation,np.array([0.,0.,-1.]))
        assign('projected_gravity_b',gravity)
        v, w = rng.normal(0,.4,(n,3)), rng.normal(0,.8,(n,3))
        assign('root_lin_vel_b',v); assign('root_ang_vel_b',w)
        jv, ja, jt = [rng.normal(0,scale,d.joint_vel.shape) for scale in (3.,5.,2.)]
        assign('joint_vel',jv); assign('joint_acc',ja); assign('applied_torque',jt)
        curr, prev, prevprev = [rng.normal(0,.4,(n,6)) for _ in range(3)]
        r._actions.copy_(torch.tensor(curr)); r._previous_actions.copy_(torch.tensor(prev))
        r._before_previous_actions.copy_(torch.tensor(prevprev))
        command = np.zeros((n,3)); command[:,0] = [0.,.05,-.6,.6,.8,-.9,.2,-.05,.5]
        command[:,2] = np.linspace(-.4,.4,n)
        # Compare the same float32 inputs at strict deadzone boundaries; numpy
        # linspace's float64 0.09999999999999998 is not the runtime float32 .1.
        command = command.astype(np.float32)
        r.command.copy_(torch.tensor(command))
        ground = np.array([0.,0.,.27,0.,.27,0.,.27,0.,0.])
        height = ground + np.linspace(.18,.42,n)
        d.root_pos_w[:,2] = torch.tensor(height)
        r.ground_z_est.copy_(torch.tensor(ground))
        r.ground_wheels.copy_(torch.tensor(ground[:,None]).expand(-1,2))
        wheel_b = rng.normal(0,.04,(n,2,3)); wheel_b[:,:,2] -= .28
        wheel_w = np.einsum('nij,nkj->nki',rotation,wheel_b)
        wheel_w += d.root_pos_w.numpy()[:,None,:]
        d.body_pos_w[:,r._wheel_link_idx] = torch.tensor(wheel_w,dtype=torch.float32)
        r.contact_sensor.data.net_forces_w_history.zero_()
        chassis = robot.body_names.index('chassis')
        r.contact_sensor.data.net_forces_w_history[2,1,chassis,2] = 10.
        r.reset_terminated[3] = True
        r._numerical_safety_reset_buf[4] = True
        r._invalidate_step_caches()
        leg, wheel, actuate = r._legs_act_idx, r._wheel_idx, r._actuate_idx
        ss = lambda x:np.sum(x*x,axis=-1)
        second = curr-2*prev+prevprev
        tracking = command.copy()
        still = np.abs(command[:,0]) < c.stand_still_deadzone_threshold
        tracking[still,0] = 0.
        tracking[np.abs(command[:,2]) < c.stand_still_deadzone_threshold,2] = 0.
        dx = tracking[:,0]-v[:,0]*np.cos(pitch)
        dyaw = tracking[:,2]-w[:,2]
        dh = height-ground-.25
        fork = wheel_b[:,0,0]-wheel_b[:,1,0]
        expected = dict(
            termination=np.arange(n)==3, leg_joint_acc=ss(ja[:,leg]), wheel_acc=ss(ja[:,wheel]),
            leg_joint_vel=ss(jv[:,leg]), wheel_vel=ss(jv[:,wheel]), joint_torque=ss(jt[:,actuate]),
            wheel_power=np.maximum(jt[:,wheel]*jv[:,wheel],0).sum(-1),
            lin_vel_z=v[:,2]**2, ang_vel_xy=ss(w[:,:2]), action_rate=ss(curr-prev),
            action_smoothness_leg=ss(second[:,:4]), action_smoothness_wheel=ss(second[:,4:]),
            flat_orientation_y_exp=np.exp(-gravity[:,0]**2/c.orientation_y_exp_sigma),
            flat_orientation_x_exp=np.exp(-gravity[:,1]**2/c.orientation_x_exp_sigma),
            flat_orientation_y_v=((c.orientation_y_A*np.exp(-command[:,0]**2/c.orientation_y_sigma)+c.orientation_y_bias)*gravity[:,0])**2,
            flat_orientation_x_v=((c.orientation_x_A*np.exp(-command[:,0]**2/c.orientation_x_sigma)+c.orientation_x_bias)*gravity[:,1])**2,
            track_lin_vel_xy=np.exp(-np.clip(dx,-c.lin_vel_err_constraint,c.lin_vel_err_constraint)**2/c.lin_vel_xy_sigma),
            track_lin_vel_xy_square=(dx*c.lin_vel_xy_square_sigma)**2,
            track_ang_vel_z=np.exp(-np.clip(dyaw,-c.ang_vel_err_constraint,c.ang_vel_err_constraint)**2/c.ang_vel_z_sigma),
            track_ang_vel_z_square=(dyaw*c.ang_vel_z_square_sigma)**2,
            stand_still_lin_vel=np.abs(v[:,:2]).sum(-1)*still,
            no_fork=np.abs(fork)>c.no_fork_distance, no_fork_square=(fork*c.no_fork_square_sigma)**2,
            track_height_square=(dh*c.height_square_sigma)**2,
            track_height_exp_tight=np.exp(-np.clip(dh,-c.height_err_constraint,c.height_err_constraint)**2/c.height_tight_sigma),
            undesired_contact=np.arange(n)==2)
        self.assertEqual(set(expected),{key for key,value in c.rewards.items() if value})
        reward = r.compute()
        for key,value in expected.items():
            torch.testing.assert_close(r.raw_terms[key].float(),torch.tensor(value,dtype=torch.float32),
                                       atol=2.e-5,rtol=2.e-5,msg=key)
        total = sum(c.rewards[key]*value*.02 for key,value in expected.items())
        total[4] = 0.
        torch.testing.assert_close(reward,torch.tensor(total,dtype=torch.float32),atol=2.e-5,rtol=2.e-5)

    def test_airborne_limit_keeps_upstream_l1_units(self):
        r, robot, contract = fixture(2)
        r.cfg.rear2_rear1_joint_limit_lower_boundary_ratio = .10
        r.cfg.rear2_rear1_joint_limit_upper_boundary_ratio = .20
        expected = 0.
        for name in LEGS:
            low, high = contract['joints'][name]['limits_si']
            robot.data.joint_pos[:, robot.joint_names.index(name)] = high + .01
            expected += (high-low)*.20 + .01
        actual, _, _ = r.motor_stop_terms(airborne=True)
        torch.testing.assert_close(actual, torch.full((2,), expected))

    def test_base_limit_uses_configured_boundary_ratio(self):
        r, robot, contract = fixture(2)
        r.cfg.rear2_rear1_joint_limit_boundary_ratio = .10
        for name in LEGS:
            low, high = contract['joints'][name]['limits_si']
            robot.data.joint_pos[:, robot.joint_names.index(name)] = high - .05*(high-low)
        actual, _, _ = r.motor_stop_terms()
        torch.testing.assert_close(actual, torch.ones(2))  # four * (0.05/0.10)^2

    def test_scan_state_is_advanced_after_current_reward(self):
        r, _, _ = fixture(2, profile='jump270')
        r.wheel_forward_prev_ground_z.zero_()
        r.wheel_forward_prev_ground_z_valid.fill_(True)
        r.wheel_forward_prev_direction_sign.fill_(1)
        r.wheel_forward_stair_prev_ground_z.zero_()
        r.wheel_forward_stair_prev_ground_z_valid.fill_(True)
        r.wheel_forward_stair_prev_direction_sign.fill_(1)
        hits = torch.zeros(2, 2, 3); hits[:, :, 2] = .27
        zero = torch.zeros(2, dtype=torch.bool)
        r.begin(torch.zeros(2, 6), torch.tensor([[.6, 0., 0.]]*2), torch.full((2,), .25),
                zero, zero, torch.ones(2, dtype=torch.long),
                torch.zeros(2, 3, len(r.robot.raw.body_names), 3),
                torch.zeros(2), torch.zeros(2, 2), hits, hits, hits, hits)
        self.assertFalse(bool(r.wheel_forward_stair_state.any()))
        r.compute()
        self.assertTrue(bool(r.wheel_forward_stair_state.all()))
        torch.testing.assert_close(r.state_terms['mod4_stair_height'], torch.zeros(2))
        torch.testing.assert_close(r.wheel_forward_stair_state_time, torch.full((2,), .02))
        # Upstream invokes _on_command_updated at reward tail AND observations.
        # Preserve its second hook; a scan cache avoids taking a new difference.
        r._on_command_updated()
        torch.testing.assert_close(r.wheel_forward_stair_state_time, torch.full((2,), .04))

    def test_repeated_observation_read_does_not_advance_lifecycle(self):
        calls = []
        env = SimpleNamespace(num_envs=2, device='cpu', max_episode_length=400, cfg={})
        bridge = SimpleNamespace(observations=lambda raw: (calls.append(1) or raw))
        raw = {'policy': torch.zeros(2, 35), 'critic': torch.zeros(2, 78)}
        vec = ScutVecEnv(env, bridge, raw)
        vec.get_observations(); vec.get_observations()
        self.assertEqual(len(calls), 1)
        vec.current = raw
        vec.get_observations()
        self.assertEqual(len(calls), 2)

    def test_observation_scaling_respects_stream_selection(self):
        cfg = reward_config()
        cfg.obs_input_scale_streams = ['policy']
        x = torch.tensor([2.])
        torch.testing.assert_close(observation_component(cfg, 'height_cmd', x, stream='critic'),
                                   torch.tensor([1.]))  # clip still happens; scale is disabled
        torch.testing.assert_close(observation_component(cfg, 'height_cmd', x, stream='policy'),
                                   torch.tensor([5.]))

    def test_ground_scan_matches_saved_reward_recipe(self):
        from .config import ground_scan_config
        cfg = ground_scan_config()
        original = read_yaml('trained_env')['height_scanner']
        self.assertEqual(cfg['resolution'], original['pattern_cfg']['resolution'])
        self.assertEqual(tuple(cfg['size']), tuple(original['pattern_cfg']['size']))
        self.assertEqual(tuple(cfg['offset']), tuple(original['offset']['pos']))
        # At an edge, replacing a 2cm grid by a 10cm grid changes mean ground_z.
        xs = torch.tensor([-.04, .01, .06])
        old_mean = (xs >= 0).float().mean()*.27
        actual_mean = (torch.tensor([0., .01, .02]) >= 0).float().mean()*.27
        self.assertGreater(float(actual_mean-old_mean), .08)

    def test_reset_clears_episode_clock_only_for_selected_env(self):
        r, _, _ = fixture(3)
        r.episode_length_buf[:] = torch.tensor([10, 20, 30])
        r.reset(torch.tensor([1]))
        self.assertEqual(r.episode_length_buf.tolist(), [10, 0, 30])

    def test_reset_scan_reseeds_new_pose_without_erasing_peer_delta(self):
        r, _, _ = fixture(3, profile='jump270')
        r.ground_z_est.fill_(.27)
        for prefix in ('wheel_forward', 'wheel_forward_stair'):
            getattr(r, prefix+'_prev_ground_z').fill_(.27)
            getattr(r, prefix+'_prev_ground_z_valid').fill_(True)
            setattr(r, '_cached_'+prefix+'_temporal_height_diffs', torch.full((3, 2), .27))
        ids = torch.tensor([1])
        r.reset(ids)
        bridge = ScutBridge.__new__(ScutBridge)
        bridge.reward = r
        bridge.reset_scan_pending = torch.tensor([False, True, False])
        bridge.env = SimpleNamespace(episode_length_buf=torch.tensor([10, 0, 30]),
            command_manager=SimpleNamespace(get_command=lambda name:torch.tensor([[.6, 0., 0.]]*3)))
        bridge.task = SimpleNamespace(height_cmd=lambda env:torch.full((3, 1), .25))
        calls = []
        def scans(selected):
            calls.append(selected.tolist())
            return (torch.zeros(1), torch.zeros(1, 2), *[torch.zeros(1, 2, 3) for _ in range(4)])
        bridge.read_reward_scans = scans
        # Isolate the sensor/cache lifecycle from state evolution (tested above).
        r._on_command_updated = lambda:None
        r.state_machine_manager = SimpleNamespace(on_observation_step=lambda env:None)
        bridge.refresh_observation_context()
        bridge.refresh_observation_context()
        self.assertEqual(calls, [[1]])
        torch.testing.assert_close(r.ground_z_est, torch.tensor([.27, 0., .27]))
        for prefix in ('wheel_forward', 'wheel_forward_stair'):
            actual = getattr(r, '_cached_'+prefix+'_temporal_height_diffs')
            torch.testing.assert_close(actual, torch.tensor([[.27, .27], [0., 0.], [.27, .27]]))
            torch.testing.assert_close(getattr(r, prefix+'_prev_ground_z')[1], torch.zeros(2))

    def test_saved_recipe_wheel_ground_uses_chassis_scan_and_invalid_fallback(self):
        r, _, _ = fixture(3)
        bridge = ScutBridge.__new__(ScutBridge)
        bridge.reward, bridge.tensor = r, lambda x:x
        hits = torch.zeros(3, 3, 3)
        hits[0, :, 2] = .27
        hits[1, :, 2] = float('inf')
        hits[2, :, 2] = torch.tensor([0., .27, float('inf')])
        class Scene(dict):
            env_origins = torch.tensor([[0., 0., 0.], [0., 0., .1], [0., 0., 0.]])
        bridge.env = SimpleNamespace(scene=Scene(scut_ground=SimpleNamespace(data=SimpleNamespace(ray_hits_w=hits))),
            command_manager=SimpleNamespace(get_command=lambda name:torch.tensor([[.6, 0., 0.]]*3)))
        bridge.raycast = lambda *args:self.fail('Disabled forward scanner must not raycast')
        ground, wheel_ground, *_ = bridge.read_reward_scans()
        expected = torch.tensor([.27, .1, .135])
        torch.testing.assert_close(ground, expected)
        torch.testing.assert_close(wheel_ground, expected[:, None].expand(-1, 2))

    def test_pd_privileged_fields_follow_named_action_order(self):
        r, robot, _ = fixture(2)
        r.cfg.obs_input_clip_cfg = {}
        r.cfg.obs_input_scale_enabled = False
        robot.root_view = SimpleNamespace(get_masses=lambda:torch.ones(2, len(robot.body_names)),
            get_material_properties=lambda:torch.ones(2, 2, 3))
        leg_order, wheel_order = [2, 0, 3, 1], [1, 0]
        pd = SimpleNamespace(leg_ids=[r._legs_act_idx[i] for i in leg_order],
            wheel_ids=[r._wheel_idx[i] for i in wheel_order],
            legs=SimpleNamespace(stiffness=torch.tensor([[30., 10., 40., 20.]]*2),
                                 damping=torch.tensor([[3., 1., 4., 2.]]*2)),
            wheels=SimpleNamespace(stiffness=torch.tensor([[60., 50.]]*2),
                                   damping=torch.tensor([[6., 5.]]*2)))
        bridge = ScutBridge.__new__(ScutBridge)
        bridge.reward, bridge.robot, bridge.n, bridge.device, bridge.tensor = r, robot, 2, 'cpu', lambda x:x
        bridge.refresh_observation_context = lambda:None
        bridge.wheel_material_ids = [[0], [1]]
        bridge.env = SimpleNamespace(_explicit_pd=pd,
            _feedback_delay_mild=SimpleNamespace(delay=torch.zeros(2)),
            _physics_action_delay=SimpleNamespace(queue=SimpleNamespace(groups={
                key:{'lag_steps':torch.zeros(2)} for key in ('legs', 'wheels')})),
            _mild_dr=SimpleNamespace(mass=torch.ones(2, len(robot.body_names))))
        obs = bridge.observations(dict(policy=torch.zeros(2, 35), critic=torch.zeros(2, 38)))['critic']
        torch.testing.assert_close(obs[:, 39:45], torch.tensor([[10.,20.,30.,40.,50.,60.]]*2))
        torch.testing.assert_close(obs[:, 45:51], torch.tensor([[1.,2.,3.,4.,5.,6.]]*2))

    def test_runner_uses_separate_actor_and_critic_dimensions(self):
        from .config import runner_config
        raw = read_yaml('trained_agent')
        raw['policy']['critic_hidden_dims'] = [32, 16]
        with patch('mod4v1_scut.config.read_yaml', return_value=raw):
            cfg = runner_config()
        self.assertEqual(cfg['critic']['hidden_dims'], [32, 16])
        self.assertEqual(cfg['actor']['hidden_dims'], raw['policy']['actor_hidden_dims'])

    def test_hard_mod4_failure_survives_wall_timeout_override(self):
        r, robot, _ = fixture(3, profile='jump270')
        r.wheel_forward_wall_reset.fill_(True)
        robot.data.root_lin_vel_b[1, 0] = 101.
        robot.data.root_ang_vel_b[2, 1] = float('nan')
        bridge = ScutBridge.__new__(ScutBridge)
        manager = SimpleNamespace(get_term=lambda key: torch.tensor([key == 'closure', False, False]))
        bridge.env = SimpleNamespace(termination_manager=manager)
        bridge.reward = r
        terminate, timeout = bridge.resolve_done(torch.ones(3, dtype=torch.bool),
                                                torch.zeros(3, dtype=torch.bool))
        self.assertEqual(terminate.tolist(), [True, True, True])
        self.assertEqual(r._numerical_safety_reset_buf.tolist(), [False, True, True])

    def test_reward_recipe_counts_are_explicit(self):
        original = read_yaml('trained_env')['rewards']
        trained = reward_config('trained_stair').rewards
        jump = reward_config('jump270').rewards
        self.assertEqual(trained, original)
        self.assertEqual(len(trained), 37)
        self.assertEqual(sum(v != 0 for v in trained.values()), 26)
        self.assertEqual(len(jump), 39)
        self.assertEqual(sum(v != 0 for v in jump.values()), 28)
        self.assertFalse(any('joint_pos_limits' in key for key in jump))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        raise FileExistsError('Keep the original audit result')
    torch.set_num_threads(2)
    torch.manual_seed(270)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ReviewTests))
    report = dict(passed=result.wasSuccessful(), tests=result.testsRun,
                  failures=len(result.failures), errors=len(result.errors), output=stream.getvalue(),
                  kind='CPU_BOUNDARY_REAUDIT_NOT_NATIVE_OR_SKILL',
                  production_PT_reads=0, physics_steps=0, GPU_training=0)
    args.report.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(stream.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
