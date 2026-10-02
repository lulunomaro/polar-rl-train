import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT/'MOD4_RL_FIX_20260913_1500/overlay/isaac/mod4'
old = (ROOT/'snapshot/isaac/mod4/eval_terrain_mod4.py').read_text(encoding='utf8')
head = old[:old.index('def main() -> None:')]
head = head.replace('launcher = AppLauncher(args); app = launcher.app', '''# Nominal, episode-accounted acceptance only. Set before task import.
os.environ["RM_EPISODE_AUDIT"] = "1"
os.environ["RM_DR_OFF"] = "1"
os.environ["RM_ROUTE_CURRICULUM"] = "0"
os.environ["RM_JUMP_SCRIPT_PROB"] = "0"
os.environ["RM_TUNNEL_GOAL_X"] = "0"
os.environ["RM_TUNNEL_LEAD_M"] = "0"  # this variable ALSO shifts the spawn in current route_spawn
os.environ["RM_TUNNEL_SPAWN_DIST"] = "0"
os.environ["RM_ROUGH_SPEED_MAX"] = "0"
os.environ["RM_ROUTE_WEIGHTS"] = ""
launcher = AppLauncher(args); app = launcher.app''')
head = head.replace('keys.setdefault(k, v)', 'keys[k] = v')
main = '''def main() -> None:
    import hashlib
    from repair_contracts import EpisodeLedger, POLICY_TERMS
    if not args.report:
        raise ValueError("--report is required; use a new evidence path")
    dest = Path(args.report)
    if dest.exists():
        raise FileExistsError("refusing to overwrite an acceptance report: " + str(dest))
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    cfg.seed = args.seed
    if not mod4_task.attach_rmuc2026_terrain(cfg):
        raise ValueError("episode evaluator requires the delivered rmuc2026 arena")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    env = Mod4Env(cfg=cfg)
    try:
        vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
        policy = build_runner(vec, args.checkpoint)
        env.reset(seed=args.seed)
        obs = vec.get_observations()
        rc = env._mod4_routes
        ledger = EpisodeLedger(env.num_envs, [r["kind"] for r in rc.routes])
        for _ in range(args.steps):
            with torch.inference_mode():
                actions = policy(obs)
            if not bool(torch.isfinite(actions).all()):
                raise RuntimeError("nonfinite evaluation action")
            obs, rewards, dones, extras = vec.step(actions)
            if not bool(torch.isfinite(rewards).all()):
                raise RuntimeError("nonfinite evaluation reward")
            terminal = extras.get("repair_terminal_episodes")
            if terminal is None:
                raise RuntimeError("pre-reset episode snapshot hook is missing")
            if len(terminal) != int(dones.bool().sum()):
                raise RuntimeError("wrapper lost or duplicated a terminal episode")
            ledger.consume(terminal)
        digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
        # Runtime tensors establish what is actually active, not regex guesses of defaults.
        protocol = {
            "schema": "mod4_nominal_protocol_v1", "actor_class": _ACTOR_CLASS,
            "num_envs": env.num_envs, "step_dt": env.step_dt,
            "max_episode_length": env.max_episode_length,
            "requested_route_kinds": os.environ.get("RM_ROUTE_KINDS", ""),
            "usd_sha256": digest(mod4_task.ROBOT_USD),
            "route_table": rc.routes,
            "runtime_goals": rc.goals.detach().cpu().tolist(),
            "runtime_starts": rc.starts.detach().cpu().tolist(),
            "runtime_speeds": rc.speeds.detach().cpu().tolist(),
            "task_sha256": digest(HERE/"mod4_task.py"),
            "repair_sources": {p.name:digest(p) for p in sorted(HERE.glob('repair_*.py'))},
            "controller_sha256": digest(HERE/"mod4_env.py"),
            "reward_sha256": digest(HERE/"skills_isaac.py"),
            "route_adapter_sha256": digest(HERE/"route_isaac.py"),
            "sequence_sha256": digest(HERE/"mod4_sequence_model.py"),
            "observations": {k:[str(v) for v in vals] for k, vals in
                             env.observation_manager.active_terms.items()},
            "rm_env": {k:v for k,v in sorted(os.environ.items()) if k.startswith("RM_")
                and k not in {"RM_ACCEPT_TAG", "RM_INIT_STD", "RM_RETENTION_MIN"}},
        }
        encoded = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()
        report = {
            "schema": "mod4_episode_eval_v1", "status": "ROLLOUT_COMPLETE",
            "seed": args.seed, "steps_completed": args.steps,
            "checkpoint": str(Path(args.checkpoint).resolve()),
            "checkpoint_sha256": digest(args.checkpoint),
            "protocol": protocol, "protocol_sha256": hashlib.sha256(encoded).hexdigest(),
            "route_kinds": ledger.buckets(), "episodes": ledger.records,
            "censored_active_episodes": int((env.episode_length_buf > 0).sum()),
            "physical_clearance_verified": False,
            "clearance_note": "Root plus a constant is not a full articulated CAD envelope."
                " This report does not certify physical dog-hole clearance.",
            "closure_max_m": float(getattr(env, "_mod4_max_closure", float("nan"))),
            "mimic_max_rad": float(getattr(env, "_mod4_max_mimic", float("nan"))),
        }
        dest.parent.mkdir(parents=True, exist_ok=True)
        # No NaN or partial report may masquerade as a pass.
        payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
        with dest.open("x", encoding="utf8") as f:
            f.write(payload + "\\n")
        print("[episode-eval] wrote", str(dest), "completed episodes:", len(ledger.records), flush=True)
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        app.close()
'''
# Resolve the actual constant from current mod4_task.py, not an invented alias.
source = (ROOT/'snapshot/isaac/mod4/mod4_task.py').read_text(encoding='utf8')
assert 'USD_PATH' in source
main = main.replace('mod4_task.ROBOT_USD', 'mod4_task.USD_PATH')
(OUT/'eval_episodes_mod4.py').write_text(head + main, encoding='utf8')
print('built episode evaluator')
