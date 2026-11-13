"""Training-only action labels added to the installed native PPO loss."""
import ast
import inspect
from pathlib import Path
import textwrap
import types
import torch


class JumpGuidance:
    def __init__(self, spec):
        self.spec = spec
        self.elapsed = 0.
        self.values = []
        self.last = {}

    def compute(self, algorithm, observations):
        predicted = algorithm.actor(observations, stochastic_output=False).clamp(-6., 6.)
        target = observations['jump_target']
        mse = (predicted - target).square().mean()
        progress = min(self.elapsed / self.spec['decay_seconds'], 1.)
        coefficient = self.spec['initial'] + progress * (self.spec['final'] - self.spec['initial'])
        loss = coefficient * mse
        if not bool(torch.isfinite(loss)):
            raise ValueError('Nonfinite jump guidance loss')
        self.values.append((float(mse.detach()), float(loss.detach())))
        return loss

    def finish(self):
        n = len(self.values)
        if not n:
            raise ValueError('PPO update did not consume jump labels')
        self.last = dict(jump_bc_mse=sum(v[0] for v in self.values)/n,
                         jump_bc_loss=sum(v[1] for v in self.values)/n,
                         jump_bc_minibatches=n)
        self.values = []
        return self.last


def install(algorithm, spec, job):
    assert algorithm.symmetry is None and algorithm.rnd is None
    original = algorithm.update.__func__
    tree = ast.parse(textwrap.dedent(inspect.getsource(original)))
    fn = tree.body[0]
    losses = returns = 0
    for i, node in reversed(list(enumerate(fn.body))):
        if isinstance(node, ast.For):
            for j, item in reversed(list(enumerate(node.body))):
                if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'loss' for t in item.targets):
                    node.body[j+1:j+1] = ast.parse('loss = loss + self._jump_bc.compute(self, batch.observations)').body
                    losses += 1
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Name) and node.value.id == 'loss_dict':
            fn.body[i:i] = ast.parse('loss_dict.update(self._jump_bc.finish())').body
            returns += 1
    assert (losses, returns) == (1, 1), (losses, returns)
    ast.fix_missing_locations(tree)
    namespace = dict(original.__globals__)
    exec(compile(tree, '<native-rsl5-ppo-jump-guidance>', 'exec'), namespace)
    guidance = JumpGuidance(spec)
    algorithm._jump_bc = guidance
    algorithm.update = types.MethodType(namespace['update'], algorithm)
    (Path(job)/'PPO_UPDATE_WITH_JUMP_BC.py').write_text(ast.unparse(tree)+'\n')
    return guidance
