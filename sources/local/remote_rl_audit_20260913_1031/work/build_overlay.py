"""Build a version-bound review overlay; never touches the remote tree."""
import ast, hashlib, pathlib, textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'MOD4_RL_FIX_20260913_1500/overlay/isaac/mod4'

def replace_func(path, name, replacement):
    s = path.read_text(encoding='utf8')
    node = next(n for n in ast.parse(s).body if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = s.splitlines(keepends=True)
    path.write_text(''.join(lines[:node.lineno-1]) + textwrap.dedent(replacement).strip() + '\n' + ''.join(lines[node.end_lineno:]), encoding='utf8')

replace_func(OUT/'mod4_curriculum.py', 'accumulate_route_stats', '''
def accumulate_route_stats(env, env_ids=None):
    """Called AFTER termination/reward, BEFORE reset: count completed episodes by kind."""
    if os.environ.get("RM_ROUTE_CURRICULUM", "0").strip() != "1":
        return
    import torch
    from repair_contracts import episode_counts
    rc = getattr(env, "_mod4_routes", None)
    if rc is None:
        raise RuntimeError("route curriculum needs route controller")
    st = _state(env)
    attempts, successes = episode_counts(
        rc.ids, [r["kind"] for r in rc.routes], list(ROUTE_KINDS),
        env.reset_buf, rc.finished, env.reset_terminated)
    for key, value in (("attempts", attempts), ("successes", successes)):
        prior = st[key]
        if not isinstance(prior, torch.Tensor):
            prior = torch.as_tensor(prior, dtype=value.dtype, device=value.device)
        st[key] = prior + value
''')

replace_func(OUT/'train_mod4_ppo.py', '_load_partial', '''
def _load_partial(runner, path: str, actor_dim: int) -> None:
    """Only a COMPLETE new encoder may be absent; actor head and critic must match."""
    from repair_contracts import validate_warmstart
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    partial = os.environ.get("RM_PARTIAL_WARMSTART", "1").strip() == "1"
    missing = validate_warmstart(runner.alg.actor.state_dict(),
                                runner.alg.critic.state_dict(), checkpoint, partial)
    if missing:
        print("[repair] deliberate encoder initialization: " + ", ".join(missing), flush=True)
    if partial:
        runner.load(path, load_cfg={"actor": True, "critic": True,
                    "optimizer": False, "iteration": False}, strict=not missing)
    else:
        runner.load(path, strict=True)
''')

replace_func(OUT/'train_mod4_ppo.py', '_partial_warm_start', '''
def _partial_warm_start(path: str, frame_dim: int, out_dim: int) -> str:
    """Allow exactly the known frame->frame+latent upgrade. Never hide load errors."""
    import tempfile
    if os.environ.get("RM_PARTIAL_WARMSTART", "1").strip() != "1":
        return path
    ck = torch.load(path, map_location="cpu", weights_only=False)
    sd = ck.get("actor_state_dict") or {}
    w = sd.get("mlp.0.weight")
    if w is None:
        raise ValueError("checkpoint has no actor first layer")
    if w.ndim != 2:
        raise ValueError("checkpoint actor first layer must be a matrix")
    if int(w.shape[1]) == int(out_dim):
        return path
    if int(w.shape[1]) != int(frame_dim) or out_dim <= frame_dim:
        raise ValueError("unsupported warm-start input layout")
    if any(k.startswith("encoder.") for k in sd):
        raise ValueError("encoder checkpoint cannot be treated as a plain-policy upgrade")
    sd["mlp.0.weight"] = torch.cat([w, w.new_zeros(w.shape[0], out_dim-frame_dim)], dim=1)
    ck.pop("optimizer_state_dict", None)
    fd, out = tempfile.mkstemp(prefix="mod4_partial_", suffix=".pt")
    os.close(fd)
    torch.save(ck, out)
    print("[repair] warm-start copy: " + out, flush=True)
    return out
''')

# Update misleading ordering documentation without changing observation layout itself.
path = OUT/'mod4_sequence_model.py'
s = path.read_text(encoding='utf8')
start, end = s.index('History ordering ('), s.index('What is deliberately NOT copied')
s = s[:start] + '''History ordering (corrected against the installed ObservationManager)
----------------------------------------------------------------------
Isaac keeps history PER TERM, then concatenates terms. The 175 numbers are
[commands history, height history, ..., mode history]. Taking the last 35
does not give the current frame. latest_indices gathers each term's newest
sample. The encoder retains the term-major 175-D input; export uses the same
gather. Previously trained sequence checkpoints have different semantics and
must not be silently reused under this layout. A plain 35-D policy is the
controlled warm-start baseline. Shape equality alone is insufficient.

''' + s[end:]
path.write_text(s, encoding='utf8')

# Derive the engine loop from the exact installed runtime, with four small hooks.
base = (ROOT/'snapshot/runtime/manager_based_rl_env.py').read_text(encoding='utf8')
cls = next(n for n in ast.parse(base).body if isinstance(n, ast.ClassDef) and n.name == 'ManagerBasedRLEnv')
node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'step')
method = ''.join(base.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
method_hash = hashlib.sha256(ast.dump(ast.parse(textwrap.dedent(method)), include_attributes=False).encode()).hexdigest()
method = method.replace('        # process actions\n', '        self._repair_before_physics()\n        # process actions\n', 1)
method = method.replace('        # -- check terminations\n', '        self._repair_after_physics()\n        # -- check terminations\n', 1)
method = method.replace('        if len(self.recorder_manager.active_terms) > 0:', '        terminal_snapshot = self._repair_after_reward()\n\n        if len(self.recorder_manager.active_terms) > 0:', 1)
method = method.replace('        # -- compute observations\n', '        self._repair_publish_reference()\n        self.extras["repair_terminal_episodes"] = terminal_snapshot\n        # -- compute observations\n', 1)
header = '''"""MOD4 phase-correct environment bound to the audited Isaac Lab step implementation.

The physics/renderer/recorder/reset flow is copied from the installed base step;
only explicit phase hooks are inserted. No package/site runtime is modified.
"""
from __future__ import annotations
import os, ast, hashlib, inspect, textwrap
import torch
from isaaclab.envs import ManagerBasedRLEnv
from repair_step import RepairStepMixin

class Mod4Env(RepairStepMixin, ManagerBasedRLEnv):
    def __init__(self, cfg, *args, **kwargs):
        actual = hashlib.sha256(ast.dump(ast.parse(textwrap.dedent(
            inspect.getsource(ManagerBasedRLEnv.step))), include_attributes=False).encode()).hexdigest()
        if actual != "EXPECTED":
            raise RuntimeError("Isaac base step changed: review the version-bound repair loop")
        if float(os.environ.get("RM_JUMP_SCRIPT_PROB", "0")) != 0:
            raise ValueError("scripted action replacement is incompatible with this PPO training path")
        self._repair_configure(cfg)
        super().__init__(cfg, *args, **kwargs)

    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        self._repair_reset_buffers(env_ids)
        self._repair_publish_reference()

'''.replace('EXPECTED', method_hash)
(OUT/'mod4_env.py').write_text(header + method + '\n', encoding='utf8')
print('overlay generated; base step AST sha256:', method_hash)
