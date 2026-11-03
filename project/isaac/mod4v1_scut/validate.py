"""Meaningful CPU integration tests. Synthetic tensors are never skill evidence."""
import ast
from copy import deepcopy
import io
import json
from pathlib import Path
import random
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np
import torch
from tensordict import TensorDict

from .config import (model_contract, reward_config, runner_config, LEGS, WHEELS,
                     observation_component, current_airborne_config)
from .acceptance import wheel_bounds, Strict270
from .math_ops import (quat_apply_inverse, quat_from_euler_xyz,
                       euler_xyz_from_quat, detect_sdk_quaternion_order)
from .rewards import ScutRewards, DataView, indices
from .upstream import source_path, state_classes, load_functions, BASE_METHODS

ASSETS = 'F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets'


def fixture(n=8, profile='trained_stair', order='xyzw'):
    contract = model_contract(ASSETS)
    joints = [k for k, v in contract['joints'].items() if v['type'] != 'ball']
    # Deliberately permuted names catch assumptions about PhysX order.
    joints = list(reversed(joints))
    bodies = list(reversed(contract['bodies']))
    j, b = len(joints), len(bodies)
    data = SimpleNamespace(joint_pos=torch.zeros(n,j), joint_vel=torch.zeros(n,j),
        joint_acc=torch.zeros(n,j), applied_torque=torch.zeros(n,j),
        root_pos_w=torch.tensor([[0.,0.,.34]]*n), root_lin_vel_w=torch.zeros(n,3),
        root_lin_vel_b=torch.zeros(n,3), root_ang_vel_b=torch.zeros(n,3),
        body_pos_w=torch.zeros(n,b,3), body_lin_vel_w=torch.zeros(n,b,3),
        body_ang_vel_w=torch.zeros(n,b,3),
        body_quat_w=(torch.tensor([0.,0.,0.,1.]) if order=='xyzw' else
                     torch.tensor([1.,0.,0.,0.])).expand(n,b,4).clone(),
        root_quat_w=torch.tensor([[0.,0.,0.,1.]]*n) if order=='xyzw' else torch.tensor([[1.,0.,0.,0.]]*n),
        projected_gravity_b=torch.tensor([[0.,0.,-1.]]*n), heading_w=torch.zeros(n))
    for i, name in enumerate(bodies):
        data.body_pos_w[:,i] = torch.tensor(contract['bodies'][name]['neutral_position_m'])+data.root_pos_w
    robot = SimpleNamespace(data=data, joint_names=joints, body_names=bodies)
    r = ScutRewards(robot, contract, n, 'cpu', profile=profile, quaternion_order=order)
    endpoint(r)
    return r, robot, contract


def endpoint(r, terminated=None, bad=None):
    n = r.num_envs
    r.begin(torch.randn(n,6)*.1, torch.tensor([[.6,0.,0.]]*n), torch.full((n,),.25),
        torch.zeros(n,dtype=torch.bool) if terminated is None else terminated,
        torch.zeros(n,dtype=torch.bool) if bad is None else bad,
        torch.full((n,),100,dtype=torch.long), torch.zeros(n,3,len(r.robot.raw.body_names),3),
        torch.zeros(n), torch.zeros(n,2), torch.zeros(n,2,3), torch.zeros(n,2,3),
        torch.zeros(n,2,3), torch.zeros(n,2,3))


class Tests(unittest.TestCase):
    def test_joint_names_and_motor_stop(self):
        r, robot, c = fixture()
        self.assertEqual([robot.joint_names[i] for i in r._actuate_idx], list(LEGS+WHEELS))
        self.assertEqual([robot.body_names[i] for i in r._wheel_link_idx], ['left_wheel','right_wheel'])
        self.assertFalse(any('roller' in robot.joint_names[i] or 'drive_' in robot.joint_names[i]
                             for i in r._actuate_idx))
        for joint in LEGS:
            robot.data.joint_pos[:, robot.joint_names.index(joint)] = c['joints'][joint]['limits_si'][1]+.01
        pos, _, _ = r.motor_stop_terms()
        self.assertTrue(bool((pos>0).all()))
        self.assertAlmostEqual(r.wheel_radius,.0625)

    def test_quaternion_boundary_rotated(self):
        n=7
        angles = torch.linspace(-.7,.7,n)
        q = quat_from_euler_xyz(angles, angles*.3, angles*.8)
        down=torch.zeros(n,3);down[:,2]=-1
        gravity=quat_apply_inverse(q,down)
        for order, raw in [('wxyz',q),('xyzw',q[:,[1,2,3,0]])]:
            data=SimpleNamespace(root_quat_w=raw, projected_gravity_b=gravity,
                                  heading_w=euler_xyz_from_quat(q)[2])
            self.assertEqual(detect_sdk_quaternion_order(data)[0], order)
            self.assertTrue(torch.equal(DataView(data,quaternion_order=order).root_quat_w,q))

    def test_reward_formula_and_one_dt(self):
        r, robot, _=fixture()
        generator=torch.Generator().manual_seed(270)
        robot.data.joint_vel.copy_(torch.randn(robot.data.joint_vel.shape,generator=generator)*.3)
        robot.data.joint_acc.copy_(torch.randn(robot.data.joint_acc.shape,generator=generator))
        robot.data.applied_torque.copy_(torch.randn(robot.data.applied_torque.shape,generator=generator))
        robot.data.root_lin_vel_b[:,0]=torch.linspace(.1,.8,r.num_envs)
        reward=r.compute()
        velocity=robot.data.root_lin_vel_b[:,0]
        expected=torch.exp(-(.6-velocity).square()/r.cfg.lin_vel_xy_sigma)
        self.assertTrue(torch.allclose(r.raw_terms['track_lin_vel_xy'],expected))
        expected=(robot.data.joint_acc[:,r._legs_act_idx].square()).sum(-1)
        self.assertTrue(torch.equal(r.raw_terms['leg_joint_acc'],expected))
        expected=sum(r.state_terms.get(k,torch.zeros(r.num_envs))*w*.02 for k,w in r.cfg.rewards.items())
        self.assertTrue(torch.allclose(reward,expected,atol=1.e-7))
        self.assertEqual(len(r.raw_terms),86)

    def test_termination_and_selected_reset(self):
        r, _, _=fixture()
        terminated=torch.zeros(r.num_envs,dtype=torch.bool);terminated[2]=True
        endpoint(r,terminated=terminated)
        r.compute()
        self.assertAlmostEqual(float(r._last_reward_terms['termination'][2]),-4.,places=6)
        r._previous_actions.fill_(3.)
        r._before_previous_actions.fill_(7.)
        r.reset(torch.tensor([2]))
        self.assertTrue(bool((r._previous_actions[2]==0).all()))
        self.assertTrue(bool((r._previous_actions[[0,1,3]]==3).all()))
        self.assertTrue(bool((r._before_previous_actions[[0,1,3]]==7).all()))

    def test_bad_reward_env_zero(self):
        r,_,_=fixture()
        bad=torch.zeros(r.num_envs,dtype=torch.bool);bad[3]=True
        endpoint(r,bad=bad)
        reward=r.compute()
        self.assertEqual(float(reward[3]),0.)
        self.assertTrue(bool(torch.isfinite(reward).all()))

    def test_stair_profile_and_detection(self):
        r,_,_=fixture(profile='jump270')
        self.assertTrue(r.cfg.wheel_forward_scan_cfg['detect']['step_height_min']<.27<r.cfg.wheel_forward_scan_cfg['detect']['step_height_max'])
        self.assertFalse(r.cfg.jump_takeoff_state_machine_cfg['assist']['enabled'])
        stair=next(m for m in r.state_machine_manager.machines if m.name=='stair')
        mask,anymask=stair._get_step_detect_masks(r,torch.full((r.num_envs,2),.27))
        self.assertTrue(bool(mask.all() and anymask.all()))
        r.wheel_forward_stair_state.fill_(True)
        r.wheel_forward_stair_reference_height.fill_(.27)
        reward=r.compute()
        self.assertTrue(torch.isfinite(reward).all())
        self.assertIn('mod4_stair_wheel_clearance',r.state_terms)

    def test_cylinder_bounds_and_strict_first_flight(self):
        c=model_contract(ASSETS)
        position=torch.tensor([[[.2,-.2,.34],[.2,.2,.34]]])
        q=torch.tensor([[[1.,0.,0.,0.],[1.,0.,0.,0.]]])
        low,high=wheel_bounds(position,q,c)
        self.assertTrue(torch.allclose(high-low,torch.tensor([[[.125,.02,.125]]]).expand(1,2,3),atol=1.e-7))
        angles=torch.full((1,2),torch.pi/2)
        rotated=quat_from_euler_xyz(angles,torch.zeros_like(angles),torch.zeros_like(angles))
        rl,rh=wheel_bounds(position,rotated,c)
        self.assertTrue(torch.allclose(rh-rl,torch.tensor([[[.125,.125,.02]]]).expand(1,2,3),atol=1.e-6))
        meter=Strict270(6,'cpu')
        zero=torch.zeros(6,2);wheel=torch.zeros(6,2,3)
        velocity=torch.zeros(6,3);orientation=torch.tensor([[1.,0.,0.,0.]]*6)
        active=torch.ones(6,dtype=torch.bool)
        def sample(rear,bottom,top=None,ground=None,load=None):
            lo=torch.zeros(6,2,3);hi=lo.clone()
            lo[...,0]=torch.as_tensor(rear).reshape(-1,1)
            lo[...,1]=torch.tensor([-.21,.19]);lo[...,2]=bottom
            hi.copy_(lo+torch.tensor([.125,.02,.125]))
            meter.update(lo,hi,zero if top is None else top,
                zero if ground is None else ground,wheel if load is None else load,
                torch.zeros(6),velocity,orientation,active)
        load=wheel.clone();load[:,:,2]=100
        # env1 starts unsupported on the platform: it must never earn flight success.
        load[1]=0
        sample([-.4,.1,-.4,-.4,-.4,-.4],.0,load=load)
        velocity[:,2]=.2
        sample([-.2,.1,-.2,-.2,-.2,-.2],.3)
        sample([.1,.1,.1,.1,.1,.1],.3)
        self.assertTrue(bool(meter.wholeclear[[0,2,3,4,5]].all()))
        self.assertFalse(bool(meter.wholeclear[1]))
        # env2 returns to floor, env3 returns behind edge; later top support cannot
        # undo either failure. env4 is too fast; env5 never has dual support.
        ground=zero.clone();ground[2,0]=100
        sample([.1,.1,.1,-.03,.1,.1],.3,ground=ground)
        velocity.zero_();velocity[4,0]=.031
        top=torch.full_like(zero,100);top[5,1]=0
        for _ in range(210):
            sample([.1]*6,.27,top=top,load=load)
        self.assertFalse(bool(meter.success.any()))
        sample([.1]*6,.27,top=top,load=load)
        self.assertEqual(meter.success.tolist(),[True,False,False,False,False,False])
        meter.reset(torch.tensor([0]))
        self.assertFalse(bool(meter.success[0] or meter.support_seen[0]))
        self.assertTrue(bool(meter.ground_return[2] and meter.edge_return[3]))

    def test_sdk_observation_fields_and_cache_reset(self):
        from .sdk import ScutBridge
        r,robot,_=fixture(4)
        robot.data.applied_torque.fill_(999.)
        robot.data.root_lin_vel_b.copy_(torch.tensor([[.3,.2,.1]]*4))
        material=torch.tensor([[[.8,.7,0.],[.9,.8,0.]]]*4)
        robot.root_view=SimpleNamespace(get_masses=lambda:torch.ones(4,len(robot.body_names)),
            get_material_properties=lambda:material)
        env=SimpleNamespace(command_manager=SimpleNamespace(get_command=lambda name:torch.tensor([[.6,0.,0.]]*4)),
            _explicit_pd=SimpleNamespace(legs=SimpleNamespace(stiffness=torch.full((4,4),150.),damping=torch.full((4,4),2.)),
                wheels=SimpleNamespace(stiffness=torch.zeros(4,2),damping=torch.full((4,2),.6))),
            _feedback_delay_mild=SimpleNamespace(delay=torch.ones(4)),
            _physics_action_delay=SimpleNamespace(queue=SimpleNamespace(groups={
                'legs':{'lag_steps':torch.ones(4)},'wheels':{'lag_steps':torch.full((4,),2.)}})),
            _mild_dr=SimpleNamespace(mass=torch.ones(4,len(robot.body_names))))
        bridge=ScutBridge.__new__(ScutBridge)
        bridge.env,bridge.reward,bridge.robot=env,r,robot
        bridge.n,bridge.tensor,bridge.device=4,lambda x:x,'cpu'
        bridge.wheel_material_ids=[[0],[1]]
        bridge.task=SimpleNamespace(height_cmd=lambda env:torch.full((4,1),.25))
        raw=dict(policy=torch.zeros(4,35),critic=torch.zeros(4,38))
        raw['policy'][:,10:14]=.11;raw['critic'][:,13:17]=.22
        before={k:v.clone() for k,v in raw.items()}
        result=bridge.observations(raw)
        self.assertEqual(result['policy'].shape,(4,35))
        self.assertEqual(result['critic'].shape,(4,78))
        self.assertTrue(torch.equal(result['policy'][:,10:14],torch.full((4,4),.11)))
        self.assertTrue(torch.equal(result['critic'][:,10:14],torch.full((4,4),.22)))
        self.assertTrue(torch.equal(result['critic'][:,35:38],robot.data.root_lin_vel_b))
        self.assertTrue(torch.equal(result['critic'][:,39:43],torch.full((4,4),100.)))
        self.assertTrue(torch.equal(result['critic'][:,51:57],torch.full((4,6),5.)))
        self.assertTrue(all(torch.equal(raw[k],before[k]) for k in raw))
        r.contact_sensor.data.net_forces_w_history.fill_(20.)
        r.reset(torch.tensor([2]))
        self.assertEqual(int(r.contact_sensor.data.net_forces_w_history[2].count_nonzero()),0)
        self.assertTrue(bool((r.contact_sensor.data.net_forces_w_history[1]==20).all()))

    def test_pre_reset_terminal_reward_hook(self):
        from .sdk import ScutBridge
        n=2
        bridge=ScutBridge.__new__(ScutBridge)
        terminated=torch.tensor([True,False]);timeout=torch.tensor([False,False])
        manager=SimpleNamespace(terminated=terminated,time_outs=timeout,
            _terminated_buf=terminated,_truncated_buf=timeout)
        env=SimpleNamespace(termination_manager=manager,
            scene=SimpleNamespace(update=lambda dt:None),reward_manager=SimpleNamespace(compute=lambda dt:None),
            extras={},max_episode_length_s=8.)
        bridge.env,bridge.ready=env,False
        events=[];state={'endpoint':7.}
        class Reward:
            reset_terminated=torch.zeros(n,dtype=torch.bool)
            state_machine_manager=SimpleNamespace(apply_done_masks=lambda r,t,o:(t,o),
                append_reset_logs=lambda r,log,ids:log.update({'State/scut_probe':2.}))
            _episode_sums={'probe':torch.tensor([8.,16.])}
            height_cmd=torch.zeros(n)
            def compute(self):events.append(('reward',state['endpoint']));return torch.full((n,),state['endpoint'])
            def reset(self,ids):events.append(('reset',ids.tolist()));state['endpoint']=0.
        bridge.reward=Reward()
        bridge.original_update=lambda dt:None
        bridge.original_done=lambda:terminated|timeout
        bridge.original_reward=lambda dt:None
        bridge.original_reset=lambda ids:env.extras.update(log={})
        bridge.top_force=torch.zeros(n,2);bridge.ground_force=bridge.top_force.clone()
        bridge.acceptance=Strict270(n,'cpu')
        bridge.task=SimpleNamespace(height_cmd=lambda env:torch.zeros(n,1))
        bridge.prepare_endpoint=lambda:events.append(('endpoint',state['endpoint']))
        bridge.snapshot=lambda t,o:{'endpoint':state['endpoint'],'terminated':t.clone()}
        bridge.completed_episodes=bridge.completed_strict=0
        bridge.ready=True
        bridge.install_hooks()
        self.assertTrue(bool(env.termination_manager.compute()[0]))
        reward=env.reward_manager.compute(.02)
        env._reset_idx(torch.tensor([0]))
        self.assertEqual(float(reward[0]),7.)
        self.assertEqual(bridge.terminal_snapshot['endpoint'],7.)
        self.assertEqual([row[0] for row in events],['endpoint','reward','reset'])
        self.assertEqual(float(env.extras['log']['Episode_Reward/scut_probe']),1.)
        self.assertEqual(env.extras['log']['State/scut_probe'],2.)
        bridge.close()

    def test_optional_current_config_is_separate(self):
        published=reward_config('trained_stair')
        current=current_airborne_config()
        self.assertFalse(published.enable_state_machines)
        self.assertTrue(current.airborne_state_machine_cfg['enabled'])
        self.assertIn('airborne_joint_pos_limits',current.rewards)

    def test_all_optional_reward_types_execute(self):
        classes=state_classes()
        self.branch_count=0
        for key in ('stair','jump_takeoff','airborne'):
            cls=classes[key]
            text=source_path(key).read_text(encoding='utf-8-sig')
            tree=ast.parse(text)
            fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='apply_reward_term_scales')
            kinds=[]
            for node in ast.walk(fn):
                if isinstance(node,ast.Compare) and isinstance(node.left,ast.Name) and node.left.id=='addition_type':
                    for other in node.comparators:
                        if isinstance(other,ast.Constant):kinds.append(other.value)
                        elif isinstance(other,(ast.Tuple,ast.List)):kinds.extend(x.value for x in other.elts)
            for kind in sorted(set(kinds)):
                with self.subTest(machine=key,kind=kind):
                    r,_,_=fixture(profile='jump270')
                    r.height_reward_airborne_state.fill_(True)
                    r.wheel_forward_stair_state.fill_(True)
                    r.jump_takeoff_phase.fill_(1)
                    r.airborne_wheel_contact_exit_time.fill_(.03)
                    r.airborne_base_contact_exit_time.fill_(.01)
                    r.airborne_entry_command=r.command.clone()
                    cfg=getattr(r.cfg,key+'_state_machine_cfg')
                    # Every branch sees non-empty robot tensors; optional defaults
                    # and named geometry are exercised without running physics.
                    addition=dict(type=kind,threshold=.3,value=1.,sigma=.02,
                        target=.25,force_threshold=1.,mode='l1')
                    if kind=='leg_retraction':addition['mode']='above_target'
                    if kind=='wheel_heading_x_centering':addition['mode']='exp'
                    cfg['reward_additions']={'probe':addition}
                    cfg['reward_scales']={}
                    cfg['reward_full']={}
                    if key=='jump_takeoff':
                        cfg['push']={'reward_additions':{}}
                        cfg['tuck']={'reward_additions':{}}
                    r.cfg.rewards={'probe':1.}
                    machine=cls()
                    if key=='airborne':
                        # Same explicit adaptation used in production subclass.
                        machine._get_rear2_rear1_joint_limit_terms=lambda env: (env.motor_stop_terms(True)[0],env.motor_stop_terms(True)[2])
                    terms=machine.apply_reward_term_scales(r,{})
                    self.assertEqual(terms['probe'].shape,(r.num_envs,))
                    self.assertTrue(bool(torch.isfinite(terms['probe']).all()))
                    self.branch_count+=1
        self.assertGreaterEqual(self.branch_count,45)

    def test_real_rsl_rollout_gae_update_save_restore(self):
        from .train import build_runner
        from .checkpoint import save,restore,COMPONENTS
        n=8
        class FixtureVec:
            num_envs=n;num_actions=6;device='cpu';max_episode_length=400;cfg={}
            episode_length_buf=torch.zeros(n,dtype=torch.long)
            def get_observations(self):
                return TensorDict(dict(policy=torch.randn(n,35)*.1,critic=torch.randn(n,78)*.1),batch_size=[n])
        runner=build_runner(FixtureVec(),None)
        self.assertEqual(runner.cfg['num_steps_per_env'],24)
        self.assertEqual(runner.alg.gamma,.99)
        self.assertEqual(runner.alg.lam,.95)
        original={key:val.clone() for key,val in runner.alg.actor.state_dict().items()}
        obs=FixtureVec().get_observations()
        with torch.inference_mode():
            for tick in range(24):
                actions=runner.alg.act(obs)
                rewards=1-actions.square().sum(-1)*.03
                done=torch.zeros(n,dtype=torch.bool)
                if tick==12:done[:2]=True
                obs=FixtureVec().get_observations()
                runner.alg.process_env_step(obs,rewards,done,{'time_outs':torch.zeros(n,dtype=torch.bool)})
            runner.alg.compute_returns(obs)
        # Independent GAE reconstruction, including the mid-rollout terminal mask.
        st=runner.alg.storage
        with torch.no_grad():
            tail=runner.alg.critic(obs)
            advantage=torch.zeros_like(tail)
            expected=torch.zeros_like(st.returns)
            for step in reversed(range(24)):
                nextv=tail if step==23 else st.values[step+1]
                alive=1-st.dones[step].float()
                delta=st.rewards[step]+.99*nextv*alive-st.values[step]
                advantage=delta+.99*.95*alive*advantage
                expected[step]=advantage+st.values[step]
            self.assertTrue(torch.allclose(st.returns,expected,atol=1.e-6))
        losses=runner.alg.update()
        self.assertTrue(all(np.isfinite(float(v)) for v in losses.values()))
        self.assertTrue(any(not torch.equal(v,original[k]) for k,v in runner.alg.actor.state_dict().items()))
        self.assertTrue(runner.alg.optimizer.state_dict()['state'])
        class State:
            def __init__(self):self.value=torch.tensor([5.]);self.rng=torch.Generator().manual_seed(4)
            def state_dict(self):return dict(value=self.value.clone(),rng=self.rng.get_state())
            def load_state_dict(self,data):self.value.copy_(data['value']);self.rng.set_state(data['rng'])
        component={key:State() for key in COMPONENTS}
        component['_physics_action_delay'].queue=SimpleNamespace(groups={
            'legs':{'last_apply_tick':torch.tensor([20])},'wheels':{'last_apply_tick':torch.tensor([20])}})
        physical=SimpleNamespace(generator=torch.Generator().manual_seed(8),
            factor=torch.ones(n),nominal=torch.ones(n,dtype=torch.bool),mu=torch.ones(n),
            reset_count=torch.ones(n,dtype=torch.long),output={'legs':torch.ones(n,4),'wheels':torch.ones(n,2)})
        command=SimpleNamespace(rng=torch.Generator().manual_seed(3),time_left=torch.full((n,),2.))
        reset_calls=[]
        env=SimpleNamespace(num_envs=n,command_manager=SimpleNamespace(get_term=lambda key:command),
                             _mild_dr=physical,reset=lambda:reset_calls.append(1))
        for k,v in component.items():setattr(env,k,v)
        r,_,_=fixture(n)
        bridge=SimpleNamespace(reward=r,physics_ticks=192)
        runner.current_learning_iteration=1
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.pt'
            save(runner,env,bridge,path,'trained_stair')
            saved={k:v.clone() for k,v in runner.alg.actor.state_dict().items()}
            with torch.no_grad():
                for p in runner.alg.actor.parameters():p.add_(1)
            command.time_left.zero_()
            restore(runner,env,bridge,path,'trained_stair')
            self.assertTrue(all(torch.equal(v,saved[k]) for k,v in runner.alg.actor.state_dict().items()))
            self.assertEqual(reset_calls,[1])
            self.assertTrue(torch.equal(command.time_left,torch.full((n,),2.)))
            self.assertTrue(all(group['last_apply_tick'].item()==-1 for group in component['_physics_action_delay'].queue.groups.values()))


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',required=True,type=Path)
    args=parser.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(20261103)
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    data=dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),
              errors=len(result.errors),output=stream.getvalue(),kind='CPU_SYNTHETIC_NOT_PHYSICS_OR_SKILL',
              production_checkpoint_reads=0,physics_steps=0,GPU_training=0)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    if args.report.exists():raise FileExistsError('Preserve previous validation report')
    args.report.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(stream.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':main()
