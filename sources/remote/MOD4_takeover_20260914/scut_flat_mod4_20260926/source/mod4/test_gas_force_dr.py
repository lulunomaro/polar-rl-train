"""Force units, gain invariance, reset isolation and within-episode consistency."""
import ast
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import torch


def test_gas_force_dr_stays_in_newtons_and_is_constant_inside_an_episode():
    tree = ast.parse(Path(__file__).with_name('skills_isaac.py').read_text())
    names = ('sample_gas_reference_force', 'gas_spring_preload')
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = dict(torch=torch, os=os, SceneEntityCfg=lambda name: SimpleNamespace(name=name))
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<gas-force>', 'exec'), ns)
    joints = ['left_gas_slide', 'right_gas_slide']
    motor = SimpleNamespace(joint_names=joints, stiffness=torch.tensor([[3150., 3850.]]).repeat(1024, 1))
    recorded = {}
    robot = SimpleNamespace(joint_names=joints, actuators={'gas_springs': motor},
                            set_joint_position_target=lambda values, joint_ids: recorded.update(target=values.clone()))
    env = SimpleNamespace(num_envs=1024, device='cpu', scene={'robot': robot})
    with patch.dict(os.environ, {'RM_DR_OFF': '0'}):
        ns['sample_gas_reference_force'](env, None, joint_names=joints)
        force = env._mod4_gas_force_ref_n.clone()
        assert float(force.min()) == 300 and float(force.max()) == 700
        assert torch.any(force[:, 0] != force[:, 1])
        for _ in range(2):
            ns['gas_spring_preload'](env, None, joint_names=joints, targets=[.2206, .2206])
            torch.testing.assert_close(motor.stiffness * recorded['target'], force)
        motor.stiffness *= 1.1
        ns['gas_spring_preload'](env, None, joint_names=joints, targets=[.2206, .2206])
        torch.testing.assert_close(motor.stiffness * recorded['target'], force)
        ns['sample_gas_reference_force'](env, torch.tensor([0, 3]), joint_names=joints)
        torch.testing.assert_close(env._mod4_gas_force_ref_n[4:], force[4:])
    with patch.dict(os.environ, {'RM_DR_OFF': '1'}):
        ns['sample_gas_reference_force'](env, None, joint_names=joints)
        torch.testing.assert_close(env._mod4_gas_force_ref_n, torch.full((1024, 2), 500.))
    with patch.dict(os.environ, {'RM_DR_OFF': '1', 'RM_GAS_FORCE_DR_ONLY': '1'}):
        ns['sample_gas_reference_force'](env, None, joint_names=joints)
        force = env._mod4_gas_force_ref_n
        assert float(force.min()) == 300 and float(force.max()) == 700
        assert torch.any(force[:, 0] != force[:, 1])
