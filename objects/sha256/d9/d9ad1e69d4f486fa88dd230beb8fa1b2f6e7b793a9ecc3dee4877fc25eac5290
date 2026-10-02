"""Run posture shaping must not change stand, spin, jump or tunnel rewards."""
import ast
from pathlib import Path
from types import SimpleNamespace
import torch


def test_run_height_deficit_route_and_stand_mask():
    tree = ast.parse(Path(__file__).with_name('mod4_task.py').read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_height_deficit')
    target = torch.tensor([[.34], [.34], [.34], [.34]])
    height = torch.tensor([.19, .20, .20, .34])
    stand = torch.tensor([False, True, False, False])
    namespace = dict(torch=torch, skills=SimpleNamespace(_stand_mask=lambda env: stand),
                     height_cmd=lambda env: target, root_height_above_ground=lambda env: height)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), '<posture>', 'exec'), namespace)
    env = SimpleNamespace(num_envs=4, device='cpu', _mod4_mode_bit=torch.tensor([0, 0, 1, 4]))
    torch.testing.assert_close(namespace['run_height_deficit'](env), torch.tensor([.15, 0., 0., 0.]))
    delattr(env, '_mod4_mode_bit')
    torch.testing.assert_close(namespace['run_height_deficit'](env), torch.zeros(4))


def test_run_tilt_only_penalizes_moving_run():
    tree = ast.parse(Path(__file__).with_name('mod4_task.py').read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_tilt_l2')
    gravity = torch.tensor([[.3, .4, -.8], [.3, .4, -.8], [.3, .4, -.8], [.3, .4, -.8]])
    stand = torch.tensor([False, True, False, False])
    robot = SimpleNamespace(data=SimpleNamespace(projected_gravity_b=gravity))
    namespace = dict(torch=torch, skills=SimpleNamespace(_stand_mask=lambda env: stand))
    exec(compile(ast.Module(body=[fn], type_ignores=[]), '<tilt>', 'exec'), namespace)
    env = SimpleNamespace(num_envs=4, device='cpu', _mod4_mode_bit=torch.tensor([0, 0, 1, 4]), scene={'robot': robot})
    torch.testing.assert_close(namespace['run_tilt_l2'](env), torch.tensor([.25, 0., 0., 0.]))


def test_run_pose_reference_guides_balanced_stance_only_on_run():
    tree = ast.parse(Path(__file__).with_name('mod4_task.py').read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_pose_reference_l2')
    q = torch.tensor([[-.26, .45, -.26, .45]] * 3)
    robot = SimpleNamespace(joint_names=['left_crank', 'left_hip', 'right_crank', 'right_hip'],
                            data=SimpleNamespace(joint_pos=q))
    stand = torch.tensor([False, True, False])
    namespace = dict(torch=torch, skills=SimpleNamespace(_stand_mask=lambda env: stand),
                     LEG_ORDER=robot.joint_names, RUN_REF_CRANK=-.10, RUN_REF_HIP=.45)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), '<pose>', 'exec'), namespace)
    env = SimpleNamespace(num_envs=3, device='cpu', _mod4_mode_bit=torch.tensor([0, 0, 4]),
                          scene={'robot': robot})
    actual = namespace['run_pose_reference_l2'](env)
    torch.testing.assert_close(actual, torch.tensor([.0512, 0., 0.]))
    assert hasattr(env, '_mod4_run_pose_ctrl')
