"""Verify the actual reward config retains a response to high tracking errors."""
import ast
import functools
from pathlib import Path
from types import SimpleNamespace
import torch


def test_reward_config_does_not_clip_dense_speed_correction():
    tree = ast.parse(Path(__file__).with_name('mod4_task.py').read_text())
    wrapper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_clip_reward_term')
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RewardsCfg')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__post_init__')
    class Term:
        def __init__(self, weight, func):
            self.weight, self.func = weight, func
    ns = dict(torch=torch, functools=functools, RewTerm=Term, REWARD_CLIP_MODE='safe',
              REWARD_CLIP=2.5, REWARD_CLIP_REPORT=[])
    exec(compile(ast.Module(body=[wrapper, method], type_ignores=[]), '<reward-config>', 'exec'), ns)
    err = torch.tensor([1., 1.2, 1.5, 2., 3.])
    cfg = SimpleNamespace(run_velocity_error=Term(-2., lambda env: err.square()),
                          other=Term(-1., lambda env: torch.tensor([20.])))
    ns['__post_init__'](cfg)
    actual = cfg.run_velocity_error.func(None) * cfg.run_velocity_error.weight
    torch.testing.assert_close(actual, -2. * err.square())
    assert torch.all(actual[1:] < actual[:-1])
    torch.testing.assert_close(cfg.other.func(None) * cfg.other.weight, torch.tensor([-2.5]))
