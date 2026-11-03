"""Regression for the missing MOD4 E0 action wrapper; synthetic physics only."""
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import torch
from tensordict import TensorDict

from .checkpoint import check_interface, FORMAT, INTERFACE, LEGACY_FORMAT, LEGACY_INTERFACE
from .config import ACTION_CLIP, ACTION_INTERFACE, USD_SHA, CONTRACT_SHA
from .train import ScutVecEnv, build_runner
from .parity_tests import bridge_fixture


def spy_vec(n=8):
    bridge=SimpleNamespace(pending_actions=torch.zeros(n,6))
    env=SimpleNamespace(num_envs=n,device='cpu',max_episode_length=400,cfg={},
                        episode_length_buf=torch.zeros(n,dtype=torch.long),applied=[])
    def observations(raw):
        actor=torch.zeros(n,35)
        actor[:,22:28]=bridge.pending_actions
        return dict(policy=actor,critic=torch.zeros(n,78))
    bridge.observations=observations
    def step(action):
        env.applied.append(action.clone())
        env.episode_length_buf+=1
        reward=-action.square().mean(-1)
        return {},reward,torch.zeros(n,dtype=torch.bool),torch.zeros(n,dtype=torch.bool),{}
    env.step=step
    return ScutVecEnv(env,bridge,{}),env,bridge


class Tests(unittest.TestCase):
    def test_recorded_extreme_actions_clipped_before_physics_and_history_without_mutating_sample(self):
        vec,env,b=spy_vec(2)
        sampled=torch.tensor([[-74.81295,1.56447,-.29283,.88593,-1.58997,-1.74838],
                              [-150.,7.,-8.,3.,24.,-18.]])
        original=sampled.clone()
        obs,reward,done,info=vec.step(sampled)
        expected=torch.tensor([[-6.,1.56447,-.29283,.88593,-1.58997,-1.74838],
                               [-6.,6.,-6.,3.,6.,-6.]])
        torch.testing.assert_close(sampled,original,atol=0,rtol=0)
        torch.testing.assert_close(env.applied[0],expected)
        torch.testing.assert_close(b.pending_actions,expected)
        torch.testing.assert_close(obs['policy'][:,22:28],expected)

    def test_actual_rsl_rollout_keeps_sample_likelihood_and_twenty_adam_steps(self):
        vec,env,b=spy_vec()
        runner=build_runner(vec,None)
        with torch.no_grad():
            for p in runner.alg.actor.mlp.parameters():p.zero_()
            list(runner.alg.actor.mlp.parameters())[-1][0]=-75.
        obs=vec.get_observations()
        samples=[];logs=[]
        with torch.inference_mode():
            for _ in range(24):
                action=runner.alg.act(obs)
                samples.append(action.clone())
                logs.append(runner.alg.actor.get_output_log_prob(action).clone())
                obs,reward,done,extra=vec.step(action)
                runner.alg.process_env_step(obs,reward,done,extra)
            runner.alg.compute_returns(obs)
        torch.testing.assert_close(runner.alg.storage.actions,torch.stack(samples))
        torch.testing.assert_close(runner.alg.storage.actions_log_prob.squeeze(-1),torch.stack(logs))
        self.assertTrue(bool((runner.alg.storage.actions[:,:,0]<-6.).all()))
        self.assertEqual(float(torch.stack(env.applied).abs().max()),6.)
        losses=runner.alg.update()
        self.assertTrue(all(bool(torch.isfinite(torch.as_tensor(v))) for v in losses.values()))
        self.assertEqual({int(x['step']) for x in runner.alg.optimizer.state.values()},{20})

    def test_clipped_action_history_removes_observation_reset_but_keeps_real_outliers(self):
        b,r,robot,_=bridge_fixture(3)
        r.cfg.termination_duration_steps=20
        r._value_debug_enabled=True
        sample=torch.tensor([[-150.,0,0,0,0,0],[-6.,0,0,0,0,0],[0.,0,0,0,0,0]])
        for _ in range(11):
            r._debug_print_reward_and_state_stats()
            r.cache_raw_observations({'actions':sample},{'velocity':torch.zeros(3,1)})
        self.assertEqual(b.resolve_done()[0].tolist(),[True,False,False])
        r.cache_raw_observations({'actions':sample.clamp(-6.,6.)},
                                 {'velocity':torch.tensor([[0.],[0.],[121.]])})
        self.assertEqual(b.resolve_done()[0].tolist(),[False,False,True])

    def test_old_unclipped_checkpoint_requires_explicit_conversion(self):
        data=dict(format=LEGACY_FORMAT,interface=LEGACY_INTERFACE,profile='jump270',
                  usd_SHA=USD_SHA,contract_SHA=CONTRACT_SHA,actor_dim=35,critic_dim=78)
        with self.assertRaises(ValueError):check_interface(data,'jump270')
        self.assertTrue(check_interface(data,'jump270',True)['action_interface_repair'])
        data.update(format=FORMAT,interface=INTERFACE,action_clip=ACTION_CLIP,action_interface=ACTION_INTERFACE)
        self.assertFalse(check_interface(data,'jump270')['action_interface_repair'])
        data['critic_dim']=38
        with self.assertRaises(ValueError):check_interface(data,'jump270',True)

    def test_diagnostic_snapshot_retains_pre_reset_targets_and_reason_inputs(self):
        b,r,robot,_=bridge_fixture(2)
        robot.data.joint_pos_target=torch.ones_like(robot.data.joint_pos)*.4
        b.pending_actions=torch.ones(2,6)*6.
        b.top_force=b.ground_force=torch.zeros(2,2)
        b.physics_ticks=88
        b.acceptance=SimpleNamespace(success=torch.zeros(2,dtype=torch.bool),
            wholeclear=torch.zeros(2,dtype=torch.bool),leading=torch.zeros(2,dtype=torch.bool),
            stable_peak=torch.zeros(2),support_peak=torch.zeros(2))
        r._value_debug_step=11
        r._obs_raw_policy_max_abs[:]=torch.tensor([121.,6.])
        r._apply_termination_duration(torch.zeros(2,dtype=torch.bool))
        snap=b.snapshot(torch.tensor([True,False]),torch.zeros(2,dtype=torch.bool))
        r.reset(torch.tensor([0]));robot.data.joint_pos_target.zero_();b.pending_actions.zero_()
        torch.testing.assert_close(snap['joint_target'],torch.full((2,4),.4))
        torch.testing.assert_close(snap['applied_action'],torch.full((2,6),6.))
        self.assertEqual(snap['observation_outlier'].tolist(),[True,False])


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    if a.report.exists():raise FileExistsError(a.report)
    torch.set_num_threads(2);torch.manual_seed(270)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    a.report.write_text(json.dumps(dict(passed=result.wasSuccessful(),tests=result.testsRun,
        output=stream.getvalue(),production_PT_reads=0,physics=0,kind='CPU_ACTION_EXECUTION_AND_RSL_LIKELIHOOD_REGRESSION'),indent=2),encoding='utf8')
    print(stream.getvalue());raise SystemExit(0 if result.wasSuccessful() else 1)
