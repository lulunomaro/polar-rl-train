"""Line-parity regressions: source lifecycle, exact fields and episode boundaries."""
import ast
from copy import deepcopy
import io
import json
import inspect
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import torch

from .commands import RewardTailCommand
from .config import command_recipe, read_yaml, reward_config
from .math_ops import quat_from_euler_xyz, wrap_to_pi
from .sdk import ScutBridge
from .train import ScutVecEnv, initialize_episode_lengths
from .upstream import load_functions, source_path
from .validate import fixture


def bridge_fixture(n=4, profile='trained_stair'):
    r, robot, contract = fixture(n, profile)
    r.episode_length_buf.zero_()
    b = ScutBridge.__new__(ScutBridge)
    b.reward, b.robot, b.n, b.device, b.tensor = r, robot, n, 'cpu', lambda x: x
    b.env = SimpleNamespace(termination_manager=SimpleNamespace(
        get_term=lambda name: torch.zeros(n, dtype=torch.bool)))
    return b, r, robot, contract


class ParityTests(unittest.TestCase):
    def test_source_done_body_and_duration_loaded_without_body_edits(self):
        r, _, _ = fixture(1)
        for name in ('_get_dones', '_apply_termination_duration', '_clear_termination_duration_buffers'):
            original = load_functions('base_env', [name])[name]
            self.assertEqual(getattr(r, name).__func__.__code__.co_code, original.__code__.co_code)
            self.assertEqual(getattr(r, name).__func__.__code__.co_firstlineno, original.__code__.co_firstlineno)

    def test_contact_and_orientation_need_twenty_consecutive_controls(self):
        b, r, robot, _ = bridge_fixture()
        chassis = robot.body_names.index('chassis')
        r.contact_sensor.data.net_forces_w[0, chassis, 2] = 1.001
        r.contact_sensor.data.net_forces_w[1, chassis, 2] = 1.0
        q = quat_from_euler_xyz(torch.deg2rad(torch.tensor([0.,0.,40.1,39.9])), torch.zeros(4), torch.zeros(4))
        robot.data.root_quat_w.copy_(q[:, [1,2,3,0]])
        for _ in range(19):
            terminated, _ = b.resolve_done()
            self.assertFalse(bool(terminated.any()))
        self.assertEqual(b.resolve_done()[0].tolist(), [True, False, True, False])
        r.contact_sensor.data.net_forces_w.zero_()
        robot.data.root_quat_w[:] = torch.tensor([0.,0.,0.,1.])
        self.assertFalse(bool(b.resolve_done()[0].any()))
        self.assertEqual(r._termination_duration_counter.tolist(), [0]*4)

    def test_duration_reset_is_per_environment_and_hard_guards_are_immediate(self):
        b, r, robot, _ = bridge_fixture(3)
        chassis = robot.body_names.index('chassis')
        r.contact_sensor.data.net_forces_w[:, chassis, 2] = 2.
        for _ in range(19): b.resolve_done()
        r.reset(torch.tensor([1]))
        self.assertEqual(b.resolve_done()[0].tolist(), [True, False, True])
        r.reset(torch.arange(3))
        r.cfg.termination_duration_steps = 20
        robot.data.root_lin_vel_b[1,0] = 101.
        robot.data.root_pos_w[2,0] = float('nan')
        b.env.termination_manager.get_term = lambda name:torch.tensor([name=='closure',False,False])
        self.assertEqual(b.resolve_done()[0].tolist(), [True,True,True])

    def test_timeout_uses_original_maximum_minus_one_and_wall_is_not_failure(self):
        b, r, _, _ = bridge_fixture(3, 'jump270')
        r.episode_length_buf[:] = torch.tensor([398,399,400])
        terminate, timeout = b.resolve_done()
        self.assertEqual(timeout.tolist(), [False,True,True])
        self.assertFalse(bool(terminate.any()))
        r.wheel_forward_wall_reset[0] = True
        terminate, timeout = b.resolve_done()
        self.assertTrue(bool(timeout[0]))
        self.assertFalse(bool(terminate[0]))

    def test_raw_observation_outliers_before_clip_reset_after_warmup(self):
        b, r, _, _ = bridge_fixture(3)
        for _ in range(11):
            r.cache_raw_observations({'actions':torch.tensor([[121.],[0.],[0.]])},
                                     {'root_lin_vel_b':torch.tensor([[0.],[float('nan')],[120.]])})
        self.assertEqual(b.resolve_done()[0].tolist(), [True,True,False])

    def test_source_timeout_bootstrap_with_task_failure_but_not_mandatory_reset(self):
        b,r,robot,_=bridge_fixture(3,'jump270')
        r.episode_length_buf.fill_(399)
        r.contact_sensor.data.net_forces_w[:,robot.body_names.index('chassis'),2]=2.
        for _ in range(19): b.resolve_done()
        b.env.termination_manager.get_term=lambda name:torch.tensor([False,name=='closure',False])
        terminated,timeout=b.resolve_done()
        self.assertEqual(terminated.tolist(),[True,True,True])
        self.assertEqual(timeout.tolist(),[True,False,True])
        env=SimpleNamespace(num_envs=3,device='cpu',max_episode_length=400,cfg={},
            step=lambda action:({},torch.zeros(3),terminated,timeout,{}))
        bridge=SimpleNamespace(pending_actions=torch.zeros(3,6),
            observations=lambda raw:{'policy':torch.zeros(3,35),'critic':torch.zeros(3,78)})
        vec=ScutVecEnv(env,bridge)
        _,_,done,info=vec.step(torch.zeros(3,6))
        self.assertTrue(bool(done.all()))
        torch.testing.assert_close(info['time_outs'],timeout)

    def test_real_reward_tail_uses_old_command_then_advances_once_and_samples_height(self):
        r, robot, _ = fixture(2)
        r.cfg.height_range = (.31,.31)
        calls = []
        term = SimpleNamespace(command=torch.tensor([[.6,0.,0.]]*2), command_counter=torch.zeros(2,dtype=torch.long))
        def advance(dt):
            calls.append(dt);term.command[:,0]=1.2;term.command_counter[0]+=1
        r.command_generator = RewardTailCommand(term, advance)
        r.command_counter.zero_()
        r._actions.fill_(2.);r._previous_actions.fill_(1.);r._before_previous_actions.zero_()
        r.compute()
        expected = torch.exp(torch.tensor(-.6**2/r.cfg.lin_vel_xy_sigma))
        torch.testing.assert_close(r.raw_terms['track_lin_vel_xy'], expected.expand(2))
        self.assertEqual(calls, [.02])
        torch.testing.assert_close(r.command[:,0], torch.full((2,),1.2))
        torch.testing.assert_close(r.height_cmd,torch.tensor([.31,.25]))
        torch.testing.assert_close(r._previous_actions,torch.ones(2,6))
        r.finish_observation()
        torch.testing.assert_close(r._previous_actions,torch.full((2,6),2.))
        torch.testing.assert_close(r._before_previous_actions,torch.ones(2,6))

    def test_v13_inherited_hook_syncs_state_override_into_generator(self):
        r,_,_=fixture(2)
        term=SimpleNamespace(command=torch.zeros(2,3))
        r.command_generator=RewardTailCommand(term,lambda dt:None)
        r.state_machine_manager.on_command_updated=lambda env:None
        r.state_machine_manager.apply_command_overrides=lambda env:env.command[:,0].fill_(.8)
        r._on_command_updated()
        torch.testing.assert_close(term.command[:,0],torch.full((2,),.8))
        self.assertEqual(r._sync_command_generator_command.__func__.__code__.co_filename,str(source_path('parent_env')))

    def test_critic_slot_order_and_sanitize_match_source_lines_3262_3295(self):
        b, r, robot, _ = bridge_fixture(2)
        r.cfg.obs_input_clip_cfg={};r.cfg.obs_input_scale_enabled=False
        r.command.fill_(2.);r.height_cmd.fill_(.25);r._actions.fill_(9.)
        b.env.command_manager=SimpleNamespace(get_command=lambda name:torch.full((2,3),2.))
        b.env.episode_length_buf=torch.zeros(2,dtype=torch.long)
        b.task=SimpleNamespace(height_cmd=lambda env:torch.full((2,1),.25))
        b.reset_scan_pending=torch.zeros(2,dtype=torch.bool)
        r.state_machine_manager.on_observation_step=lambda env:env.height_cmd.fill_(.5)
        r._get_ctrl_mode_obs_raw=lambda:torch.arange(7).expand(2,-1).float()+50
        robot.data.root_lin_vel_b[:]=torch.tensor([11.,12.,13.])
        robot.root_view=SimpleNamespace(get_masses=lambda:torch.ones(2,len(robot.body_names)),
            get_material_properties=lambda:torch.ones(2,2,3))
        b.wheel_material_ids=[[0],[1]]
        b.env._explicit_pd=SimpleNamespace(leg_ids=r._legs_act_idx,wheel_ids=r._wheel_idx,
            legs=SimpleNamespace(stiffness=torch.ones(2,4),damping=torch.ones(2,4)),
            wheels=SimpleNamespace(stiffness=torch.ones(2,2),damping=torch.ones(2,2)))
        b.env._feedback_delay_mild=SimpleNamespace(delay=torch.zeros(2))
        b.env._physics_action_delay=SimpleNamespace(queue=SimpleNamespace(groups={
            k:{'lag_steps':torch.zeros(2)} for k in ('legs','wheels')}))
        b.env._mild_dr=SimpleNamespace(mass=torch.ones(2,len(robot.body_names)))
        raw={'policy':torch.arange(35).expand(2,-1).float().clone(),
             'critic':torch.arange(38).expand(2,-1).float().clone()}
        raw['policy'][1,4]=float('nan')
        before={k:v.clone() for k,v in raw.items()}
        out=b.observations(raw)
        torch.testing.assert_close(out['policy'][0,28:35],torch.arange(7).float()+50)
        torch.testing.assert_close(out['critic'][0,28:31],torch.tensor([11.,12.,13.]))
        self.assertAlmostEqual(float(out['critic'][0,31]),.34,places=6)
        # Height is captured before on_observation_step, whereas mode is after it.
        self.assertAlmostEqual(float(r.height_cmd[0]),.5,places=6)
        torch.testing.assert_close(out['policy'][:,3],torch.full((2,),.25))
        torch.testing.assert_close(out['critic'][:,3],torch.full((2,),.25))
        torch.testing.assert_close(r._previous_actions,torch.full((2,6),9.))
        torch.testing.assert_close(out['critic'][0,32:39],torch.arange(7).float()+50)
        torch.testing.assert_close(out['policy'][:,22:28],torch.full((2,6),9.))
        self.assertTrue(bool(torch.isfinite(out['policy']).all()))
        self.assertTrue(bool(r._obs_raw_policy_has_nonfinite[1]))
        for k in raw: torch.testing.assert_close(raw[k],before[k],equal_nan=True)

    def test_v14_subclass_guide_contact_override_reaches_reward_and_strict_support(self):
        b,r,robot,_=bridge_fixture(6)
        names=['guide_roller_00','left_wheel','chassis','left_thigh','left_gas_barrel','left_drive_hip']
        force=float(r.cfg.undesired_contact_force_threshold)+1.
        for i,name in enumerate(names):
            r.contact_sensor.data.net_forces_w_history[i,0,robot.body_names.index(name),2]=force
        r.compute()
        torch.testing.assert_close(r.raw_terms['undesired_contact'],torch.tensor([1.,0.,1.,1.,1.,1.]))
        self.assertEqual(len(r._undesired_contact_link_idx),29)
        self.assertEqual(len(r._nonwheel_contact_link_idx),29)
        self.assertEqual(len(r._reset_contact_link_idx),9)
        self.assertFalse(r.cfg.use_gimbal)
        # The base alone excludes guides; the final selected V14 constructor
        # overrides that list. Both source assignments are checked explicitly.
        for key,expect in [('base_env',False),('current_env',True)]:
            tree=ast.parse(source_path(key).read_text(encoding='utf-8-sig'))
            assignment=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Attribute) and t.attr=='_undesired_contact_link_idx' for t in n.targets))
            self.assertEqual('.*_guide_link' in ast.literal_eval(assignment.value.args[0]),expect)
        for _ in range(19):self.assertFalse(bool(b.resolve_done()[0].any()))
        self.assertEqual(b.resolve_done()[0].tolist(),[True,False,True,False,False,False])
        captured=[]
        b.acceptance=SimpleNamespace(update=lambda *args:captured.append(args))
        b.env.scene=SimpleNamespace(env_origins=torch.zeros(6,3))
        b.current_sensor=SimpleNamespace(data=SimpleNamespace(net_forces_w=r.contact_sensor.data.net_forces_w_history[:,0]))
        b.current_contact_order=list(range(len(robot.body_names)))
        b.top_force=b.ground_force=torch.zeros(6,2)
        b.measure_acceptance()
        torch.testing.assert_close(captured[0][5],torch.tensor([force,0.,force,force,force,force]))

    def test_original_command_distribution_not_fixed_point_six_for_saved_recipe(self):
        raw=read_yaml('trained_env')['commands']
        self.assertEqual(command_recipe('trained_stair'),raw)
        self.assertEqual(reward_config('trained_stair').height_range,[.2,.42])
        self.assertEqual(reward_config('trained_stair').episode_length_s,20.)
        self.assertEqual(command_recipe('jump270')['ranges']['lin_vel_x'],(.6,.6))
        self.assertEqual(reward_config('jump270').episode_length_s,8.)

    def test_original_random_episode_clock_only_for_saved_training_profile(self):
        env=SimpleNamespace(num_envs=128,device='cpu',max_episode_length=1000,cfg={},episode_length_buf=torch.zeros(128,dtype=torch.long))
        vec=ScutVecEnv(env,None)
        initialize_episode_lengths(vec,'jump270')
        self.assertEqual(int(env.episode_length_buf.sum()),0)
        initialize_episode_lengths(vec,'trained_stair')
        self.assertGreater(int(env.episode_length_buf.max()),0)
        self.assertLess(int(env.episode_length_buf.max()),1000)

    def test_angle_endpoint_preserves_positive_and_negative_pi(self):
        x=torch.tensor([torch.pi,-torch.pi,0.])
        torch.testing.assert_close(wrap_to_pi(x),x)

    def test_math_boundary_matches_installed_isaac_function_bodies(self):
        import importlib.util
        from . import math_ops
        root=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
        path=root/'utils/math.py'
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        names={'wrap_to_pi','quat_inv','quat_apply','quat_apply_inverse','quat_conjugate'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        for n in nodes:n.decorator_list=[]
        ns={'torch':torch}
        exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(path),'exec'),ns)
        q=torch.randn(4,4);q=q/q.norm(dim=-1,keepdim=True)*1.0001
        v=torch.randn(4,3)
        for name in ('quat_apply','quat_apply_inverse'):
            torch.testing.assert_close(getattr(math_ops,name)(q,v),ns[name](q,v),rtol=0,atol=0)
        torch.testing.assert_close(math_ops.quat_inv(q),ns['quat_inv'](q),rtol=0,atol=0)
        x=torch.tensor([-3*torch.pi,-torch.pi,0.,torch.pi,3*torch.pi])
        torch.testing.assert_close(math_ops.wrap_to_pi(x),ns['wrap_to_pi'](x),rtol=0,atol=0)

    def test_forward_scan_is_lazy_at_first_use_and_keeps_resampled_direction(self):
        r, _, _ = fixture(2,'jump270')
        r._invalidate_step_caches()
        calls=[]
        def scan(stair):
            calls.append((stair,r.command[:,0].clone()))
            return torch.zeros(2,2,3),torch.zeros(2,2,3)
        r.forward_scan_provider=scan
        r.command[:,0]=-1.
        r._get_wheel_forward_scan_points()
        r.command[:,0]=1.
        r._get_wheel_forward_scan_points()
        r._get_wheel_forward_stair_scan_points()
        self.assertEqual(len(calls),2)
        torch.testing.assert_close(calls[0][1],torch.full((2,),-1.))
        torch.testing.assert_close(r._cached_wheel_forward_scan_direction_sign,torch.full((2,),-1.))
        torch.testing.assert_close(r._cached_wheel_forward_stair_scan_direction_sign,torch.ones(2))

    def test_original_command_class_and_sdk_parent_methods_on_cpu(self):
        # No simulator or import stubs execute. The SCUT class body is unchanged;
        # original installed SDK sampling/timing method ASTs use tensor fixtures.
        import importlib.util
        from . import math_ops
        sdkroot=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
        ns=dict(torch=torch,math_utils=math_ops)
        def methods(path,clsname,names):
            tree=ast.parse(path.read_text(encoding='utf-8-sig'))
            cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==clsname)
            nodes=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in names]
            unit=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),*nodes],type_ignores=[])
            exec(compile(ast.fix_missing_locations(unit),str(path),'exec'),ns)
            return {n.name:ns[n.name] for n in nodes}
        class Base:
            def __init__(self,cfg,env):
                self.cfg,self._env,self.robot=cfg,env,env.scene['robot']
                self.num_envs,self.device=env.num_envs,env.device
                self.vel_command_b=torch.zeros(self.num_envs,3)
                self.heading_target=torch.zeros(self.num_envs)
                self.is_heading_env=torch.zeros(self.num_envs,dtype=torch.bool)
                self.is_standing_env=self.is_heading_env.clone()
                self.time_left=torch.zeros(self.num_envs)
                self.command_counter=torch.zeros(self.num_envs,dtype=torch.long)
                self.metrics={k:torch.zeros(self.num_envs) for k in ('error_vel_xy','error_vel_yaw')}
        for name,method in methods(sdkroot/'envs/mdp/commands/velocity_command.py','UniformVelocityCommand',
                                   ['_resample_command','_update_metrics','command']).items():setattr(Base,name,method)
        for name,method in methods(sdkroot/'managers/command_manager.py','CommandTerm',
                                   ['compute','reset','_resample']).items():setattr(Base,name,method)
        class Mode(SimpleNamespace):pass
        class FakeDict:pass
        class FakeList:pass
        cls=load_functions('commands',class_name='SpecialModeUniformVelocityCommand',extra=dict(
            UniformVelocityCommand=Base,SpecialModeEntryCfg=Mode,DictConfig=FakeDict,ListConfig=FakeList,
            Real=__import__('numbers').Real,math_utils=math_ops))['SpecialModeUniformVelocityCommand']
        raw=command_recipe('trained_stair')
        cfg=SimpleNamespace(**{k:v for k,v in raw.items() if k not in ('ranges','special_modes')},
            ranges=SimpleNamespace(**raw['ranges']),special_modes=tuple(
                Mode(**{k:v for k,v in m.items() if k!='ranges'},ranges=SimpleNamespace(**m['ranges']))
                for m in raw['special_modes']))
        _,r,robot,_=bridge_fixture(64)
        env=SimpleNamespace(scene={'robot':robot},num_envs=64,device='cpu',step_dt=.02,
            episode_length_buf=torch.zeros(64,dtype=torch.long),_get_training_iteration=lambda:0)
        c=cls(cfg,env)
        ids=torch.arange(64);c.reset(ids);c.compute(.02)
        self.assertTrue(bool((c.special_mode_id==-1).all())) # minimum episode time 5s
        self.assertTrue(bool((c.time_left>=4.98).all() and (c.time_left<=15.).all()))
        env.episode_length_buf.fill_(300);c.time_left.zero_();c.compute(.02)
        self.assertTrue(bool((c.command_counter==2).all()))
        self.assertTrue(bool((c.special_mode_id>=0).any()))
        c.is_standing_env.zero_();c.is_heading_env.fill_(True)
        c.special_mode_id[:3]=torch.tensor([-1,0,1]);c.is_standing_env[2]=True
        c.heading_target[0]=.4;c.vel_command_b[:3,2]=torch.tensor([0.,8.,9.]);c._update_command()
        torch.testing.assert_close(c.command[:3,2],torch.tensor([2.,8.,0.]))
        previous=c.command.clone();counter=c.command_counter.clone();c.reset(torch.tensor([7]))
        torch.testing.assert_close(c.command[:7],previous[:7])
        self.assertEqual(int(c.command_counter[7]),1)
        torch.testing.assert_close(c.command_counter[:7],counter[:7])
        spans=c._normalize_range_spec([[-3.,-2.],[2.,3.]])
        values=c._sample_range_spec(spans,256,'cpu')
        self.assertTrue(bool(((values.abs()>=2.)&(values.abs()<=3.)).all()))
        self.assertEqual(c._update_command.__func__.__code__.co_filename,str(source_path('commands')))


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--report',required=True,type=Path);a=p.parse_args()
    if a.report.exists():raise FileExistsError(a.report)
    torch.set_num_threads(2);torch.manual_seed(270)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ParityTests))
    a.report.write_text(json.dumps(dict(passed=result.wasSuccessful(),tests=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),output=stream.getvalue(),
        kind='SOURCE_LINE_PARITY_CPU_SYNTHETIC',production_PT_reads=0,physics_steps=0,GPU_training=0),indent=2)+'\n',encoding='utf-8')
    print(stream.getvalue());raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':main()
