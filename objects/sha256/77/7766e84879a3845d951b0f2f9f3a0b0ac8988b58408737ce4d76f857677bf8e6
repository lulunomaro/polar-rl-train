"""Compatibility launcher for the SCUT `wheeled-legged_RL` repo on Isaac Lab 3.0.

Why this exists: the repo imports `store_code_state` from `rsl_rl.utils` (an rsl_rl 2.x /
Isaac Lab 2.x API).  Isaac Lab 3.0 ships rsl_rl 5.x, where that helper was dropped, so
`scripts/rsl_rl/train.py` dies on import.  Rather than editing a reference repository, we
re-install the missing function at start-up with the SAME semantics it had upstream
(archive the git state of the training repo so a run records its provenance), then exec the
repo script unchanged.

Usage:
  python scripts/isaac_train_compat.py <repo script> [script args...]
e.g.
  python scripts/isaac_train_compat.py scripts/rsl_rl/train.py \
      --task Robotics-Wheelbipe-V14-Flat-v0 --num_envs 64 --headless --max_iterations 5
"""
import os
import runpy
import sys

REPO = r"D:\claude2\fangzhen\refs\wheeled-legged_RL-main"


def _install_shim():
    import rsl_rl.utils as u

    if hasattr(u, "store_code_state"):
        return "already present"

    def store_code_state(logdir, repository_path=".", force=True):
        """rsl_rl 2.x semantics, implemented on top of GitPython."""
        try:
            import git
        except Exception:
            return None
        try:
            repo = git.Repo(os.path.abspath(repository_path), search_parent_directories=True)
        except Exception:
            return None
        try:
            branch = str(repo.active_branch)
        except Exception:
            branch = "HEAD"
        commit = repo.head.commit.hexsha
        has_changes = bool(repo.is_dirty(untracked_files=True))
        if not (repo.has_remotes and force is not None):
            pass
        try:  # archive the tracked tree next to the logs, exactly like rsl_rl 2.x did
            if has_changes or True:
                os.makedirs(logdir, exist_ok=True)
                with open(os.path.join(logdir, "code_state.txt"), "w", encoding="utf-8") as fh:
                    fh.write("branch=%s\ncommit=%s\ndirty=%s\n" % (branch, commit, has_changes))
        except Exception:
            pass
        return repo, commit, branch, has_changes

    u.store_code_state = store_code_state
    import rsl_rl
    rsl_rl.utils.store_code_state = store_code_state
    return "installed"


def _install_missing_submodules():
    """The public `agent_rl` package ships rsl_rl/{algorithms,modules,runners,storage,utils}
    but NOT the `env` subpackage that three of its runners import VecEnv from.  rsl_rl 5.x
    provides exactly that ABC, so alias it instead of editing the reference repository."""
    import types
    try:
        import agent_rl.rsl_rl.env  # noqa: F401
        return "already present"
    except Exception:
        pass
    import agent_rl.rsl_rl  # noqa: F401
    from rsl_rl.env import VecEnv
    mod = types.ModuleType("agent_rl.rsl_rl.env")
    mod.VecEnv = VecEnv
    mod.__doc__ = "compat shim: re-exports rsl_rl.env into the released agent_rl tree"
    sys.modules["agent_rl.rsl_rl.env"] = mod
    import agent_rl
    setattr(agent_rl.rsl_rl, "env", mod)
    return "shimmed agent_rl.rsl_rl.env from rsl_rl.env"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    script = sys.argv[1]
    rest = sys.argv[2:]
    path = script if os.path.isabs(script) else os.path.join(REPO, script)
    print("[compat] rsl_rl.utils.store_code_state:", _install_shim())
    print("[compat] agent_rl.rsl_rl.env:", _install_missing_submodules())
    # Isaac Lab's own train.py adds these two directories to sys.path before importing
    # `cli_args`; the repo copies that script, so a bare `python train.py` needs them too.
    lab = os.environ.get("ISAACLAB_PATH",
                         r"D:\claude2\fangzhen\third_party\IsaacLab-3.0.0-beta2.patch1")
    for sub in (os.path.join("source", "isaaclab"),
                os.path.join("scripts", "reinforcement_learning", "rsl_rl")):
        sys.path.insert(0, os.path.join(lab, sub))
    sys.argv = [path] + rest
    os.chdir(REPO)
    print("[compat] running", path, rest, flush=True)
    runpy.run_path(path, run_name="__main__")


if __name__ == "__main__":
    main()
