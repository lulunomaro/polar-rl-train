"""Property checks for reachable motor commands and the CAD relative stop."""
import ast
from pathlib import Path
import torch


def test_joint_and_relative_limits_for_large_asymmetric_policy_outputs():
    tree = ast.parse(Path(__file__).with_name('mod4_task.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_project_leg_motor_targets')
    ns = {'torch': torch}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<target-projection>', 'exec'), ns)
    fn = ns['_project_leg_motor_targets']
    torch.manual_seed(19)
    target = torch.randn(1024, 4) * 4
    limits = torch.tensor([[-1.2, .9], [-.5, .5], [-1.2, .9], [-.5, .5]]).repeat(1024, 1, 1)
    q = fn(target, limits, -1.0843, .85)
    assert torch.all(q >= limits[:, :, 0] - 1e-6)
    assert torch.all(q <= limits[:, :, 1] + 1e-6)
    differences = q[:, [0, 2]] - q[:, [1, 3]]
    assert torch.all(differences >= -1.0843 - 1e-6)
    assert torch.all(differences <= .85 + 1e-6)
    torch.testing.assert_close(fn(q, limits, -1.0843, .85), q)
    feasible = torch.tensor([[-.636, .45, -.636, .45]])
    torch.testing.assert_close(fn(feasible, limits[:1], -1.08632, .85), feasible)
