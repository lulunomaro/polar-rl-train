"""Focused CPU checks for v2 binding/reward selection and continuous targets."""
import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
import torch
from . import BINDINGS
from .config import model_contract, reward_config
from .hardware import adapter


class V2Tests(unittest.TestCase):
    def test_model_and_new_gas_target(self):
        c = model_contract(Path(BINDINGS['hardware_package']) / 'assets')
        self.assertEqual(c['joints']['left_hip']['limits_si'], [None, None])
        self.assertAlmostEqual(c['gas_springs']['left_gas_slide']['target_position_m'],
                               .1706394410901294)

    def test_source_reward_base_and_no_old_repairs(self):
        from .shared import load
        base = load('config').reward_config('trained_stair')
        cfg = reward_config()
        self.assertTrue(all(cfg.rewards[k] == value for k, value in base.rewards.items()))
        self.assertEqual(set(cfg.rewards) - set(base.rewards),
            {'scut_jump_push_height', 'scut_jump_push_velocity', 'scut_jump_peak'})
        self.assertFalse(any(k.startswith('jump200_') for k in cfg.rewards))
        self.assertFalse(cfg.jump_takeoff_state_machine_cfg['assist']['enabled'])

    def test_all_selected_reset_poses_meet_v2_hard_domain(self):
        bank = json.loads(Path(BINDINGS['reset_bank']).read_bytes())
        poses = [p for p in bank['poses'] if .24 <= p['root_height_m'] <= .272]
        self.assertEqual(len(poses), 74)
        for p in poses:
            for side in ('left', 'right'):
                adapter()._geometry().check_joint_limits({k[len(side)+1:]: v
                    for k, v in p['joint_pos'].items() if k.startswith(side+'_')},
                    side=side, tolerance=1e-7)

    def test_continuous_projection_preserves_source_scale_and_delay(self):
        class Base:
            def __init__(self, cfg, env):
                self.action_dim=4;self.calls=0;self._joint_ids=[0,1,2,3]
                self._asset=SimpleNamespace(data=SimpleNamespace(joint_pos=torch.tensor(
                    [[3.,3.,3.,3.], [7.,7.,7.,7.]])))
            @property
            def processed_actions(self): return self._processed_actions
            def process_actions(self, values): self.calls+=1;self._processed_actions=values.clone()
            def reset(self):return 'reset'
            def apply_actions(self):return 'apply'
        class Delay:
            def process_actions(self, values):super().process_actions(values)
        class Legacy(Delay,Base):
            def process_actions(self,values):raise RuntimeError('old projection called')
        task=SimpleNamespace(DelayedJointPositionAction=Legacy,_DelayMixin=Delay,
            mdp_actions=SimpleNamespace(JointPositionAction=Base),torch=torch,
            LEG_ORDER=('left_crank','left_hip','right_crank','right_hip'))
        action=adapter().make_mechanical_action_class(task)(
            SimpleNamespace(joint_names=task.LEG_ORDER,preserve_order=True),None)
        raw=torch.tensor([[-3.,3.,-3.,3.],[0.,0.,0.,0.]])
        action.process_actions(raw)
        self.assertEqual(action.calls,1)
        self.assertEqual(action.reset(),'reset');self.assertEqual(action.apply_actions(),'apply')
        self.assertAlmostEqual(float(action.processed_actions[0,0]-action.processed_actions[0,1]),
                               2*math.pi-6,places=6)
        self.assertGreater(float(action.processed_actions[1,1]),6.)
        torch.testing.assert_close(raw,torch.tensor([[-3.,3.,-3.,3.],[0.,0.,0.,0.]]))

    def test_checkpoint_has_new_v2_identity(self):
        from . import checkpoint
        self.assertEqual(checkpoint.FORMAT,'MOD4V2_SCUT_HW300N60_FULL_V1')
        self.assertIn('continuous',checkpoint.INTERFACE)

    def test_continuous_motor_stop_helper_has_no_finite_angle_cost(self):
        from .rewards import ScutRewards
        c=model_contract(Path(BINDINGS['hardware_package'])/'assets')
        obj=SimpleNamespace(contract=c,num_envs=2,device='cpu')
        for airborne in [False,True]:
            values=ScutRewards.motor_stop_terms(obj,airborne)
            self.assertTrue(all(torch.equal(v,torch.zeros(2))for v in values))


if __name__ == '__main__':unittest.main()
