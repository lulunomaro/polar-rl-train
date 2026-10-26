# Frozen R2 entry static review

**Confirmed required fix: add source payload B root to sys.path. No additional
inevitable wiring failure was confirmed in this bounded static review.** The
R2 entry runs from HERE, whereas the production worker is itself under B and
therefore gets B on its initial Python path. B/source, B/lib and the runtime
directory do not make root-level h1_step270_sdk_runtime_candidate importable.
Keep the original EULA environment fix and existing primary-before-app-close
error receipts. No old entry or frozen directory was edited or executed.

Checks after the B-root fix:

- build_env sets cfg.scene.num_envs=args.num_envs. Replacing its Mod4Env/Mod4EnvCfg
  globals and wrapping scut.configure matches the production worker's pattern.
  R2 intentionally requests N1 and does not call main/learn or20k restore.
- The collected installed72 RslRlVecEnvWrapper source calls env.reset() in its
  constructor. R2 constructs it once and does not reset again. It provides the
  same unwrapped env and four-value step API used by production. This inspected
  wrapper is a saved installed-source reference, not a new actual SDK readback.
- PhysicalActionQueue starts with control_us10000 and reset does not change it.
  Setting the period before wrapper construction is consistent; no reset-driven
  period loss was found. A post-wrapper readback can retain the existing clock
  evidence without changing the reset protocol.
- H1Bridge(SimpleNamespace(env=vec),...) constructor uses runner.env only.
  current/pack use the env, native73 state and49 context. runner.alg is needed
  by before_action, which this driver does not call. The original correct
  quaternion reorder must remain intact.
- Native Policy construction matches learner._make_policy for the admitted
  hist10,goal_frames1,z_dim/hidden config,128 observations,73 goals and6 outputs.
  strict pi state loading includes RunningNorm buffers. Driver uses eval plus
  inference_mode and compares saved parameters/normalizers before/after. It
  does not call collect or any normalizer update.
- Current mod4_task.py explicitly sets **self.sim.physics=PhysxCfg(...)**.
  Therefore env.cfg.sim.physics.solver_type is the correct source path here;
  replacing it with a guessed sim.physx would introduce an unsupported change.
  robot.spawn.articulation_props and its solver position/velocity fields also
  match the inspected config. Keep source profiles'32/4 readback assertion.

Remaining runtime facts are pending, not new confirmed errors: N1 component and
scene support, fresh DR/reset readbacks,31-body/contact shapes, closure/mimic
readback and exact runtime objective SHA. R2's ordered30/contract checks stop
before actor forward if they differ. Do not weaken them to make a result pass.
The inherited witness IDs1,2,3 remain unsafe for N1 if original h1_capture is
enabled; R2 and the driver already keep it disabled. Driver's own read-only
capture replaces that optional path, not the physical event machine.

The single-attempt driver does not install the production training trace, so it
does not invoke preupdate saves or training reward flags. Its termination hook
captures pre-reset state; no new retry, action, phase or reset modification is
needed from this review. The new run remains a fresh deterministic native-policy
attempt, not an exact old training replay.

Only source/AST was read. No PT/model, actor, SDK, GPU, SSH or ledger operation
occurred. Guessed local source-path misses and the corrected searches are retained
in the JSON report. All files are frozen in the complete SHA index; root ordinary
supplement archival is pending.
