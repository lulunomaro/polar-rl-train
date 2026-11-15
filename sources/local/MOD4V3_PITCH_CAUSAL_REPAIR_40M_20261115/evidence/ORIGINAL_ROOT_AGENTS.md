# Agent rules for this workspace (RM2026 wheel-legged robot)

Read this before you touch the robot model, launch training, or export a policy.
These rules exist because 2026-09-10 two AI runs trained on a retired plant and on a
plant that did not match the deployment firmware.

## 1. The only live robot plant is MOD4

* MuJoCo / mjlab plant: `incoming/rm2025_mod4/robot_hifi.xml`, pinned by
  `incoming/rm2025_mod4/PLANT_PROVENANCE.json` (sha256 `e91ce284..`).
* Isaac Lab / PhysX asset: `incoming/chassis_mod4_mjcf_usd_20260910/chassis_mod4/isaac/robot.usd`
  plus the `import_contract.json` next to it. Do NOT regenerate that USD with a generic
  MJCF importer - the closed loops and the 1:1 chain couplings are authored into it.
* **Everything under `incoming/rm2025_fixed/` is RETIRED (0908 and 0910).** There is no
  `robot_hifi.xml` there any more; the 0910 file was renamed to `robot_hifi_0910.xml` so
  nothing can select it by default. Read `incoming/rm2025_fixed/DO_NOT_USE.md` before you
  even think about it, and never wire it back into `names.py`. If something asks for
  `incoming/rm2025_fixed/robot_hifi.xml`, the correct answer is "that plant is retired",
  not "restore the file".
* `train/rmvehicle/src/rmvehicle/robot_cfg.py` raises for any plant path that resolves
  inside `rm2025_fixed/`; `scripts/check_model_identity.py` refuses to train when the
  plant hash or a pinned number disagrees with the provenance file.

## 2. Entry points

| purpose | entry point |
|---|---|
| production RL (mjlab, MuJoCo-Warp, MOD4 MJCF) | `migration/linux/run_closed_chain_training.sh` |
| plant identity gate | `scripts/check_model_identity.py --task RM2025-Later-CC-Flat-v0` |
| Isaac Lab training (PhysX, MOD4 USD) | `isaac/mod4/train_mod4_ppo.py` |
| Isaac Lab physics acceptance | `incoming/chassis_mod4_mjcf_usd_20260910/chassis_mod4/isaac/smoke_test.py` (must print `PASS_RUNTIME_BOUNDED`) |
| deployment gate | `sim2real/preflight_deploy.sh` with the exported ONNX |

`migration/linux/run_allterrain_training.sh`, `run_skills_training.sh`, `run_training.sh`,
`run_final_*.sh`, `run_teacher_view.sh`, `run_spin_pure.sh`, `supervise_*.sh` and
`finalize_refine.sh` are the retired 0908/0910 serial-teacher pipeline. They now exit 2
unless `ALLOW_RETIRED_TEACHER=1` is set, and their checkpoints were never deployable.

## 3. Contracts you may not silently change

* Policy interface: 35-D observation, 6-D action in the exported order
  `[left_crank, left_hip, right_crank, right_hip, left_wheel_spin, right_wheel_spin]`
  (`train/deploy/contract_rm2025_later.json`). The passive knee is never an action.
* Motor envelope (plateau / stall / no-load): legs 40 / 53.333 / 16.755,
  wheels 5.7759 / 28.185 / 55.3557. Training and deployment must use the same numbers;
  `scripts/check_model_identity.py` reads them back out of the compiled model.
* Closed-chain guard: the six loop-closure anchors must stay within 2 mm in any engine
  (mjlab/MuJoCo and Isaac/PhysX both enforce this). If the guard fires, stop and fix the
  plant or the solver - do not raise the tolerance.
* A model swap voids every existing checkpoint, ONNX and sim2sim contract. Retrain and
  re-run the gates; never re-label old artefacts.

## 4. Isaac Lab notes that cost hours on 2026-09-10

* Isaac Lab 3.0/6.x uses (x, y, z, w) quaternions (identity `[0, 0, 0, 1]`); 2.x used
  (w, x, y, z). Code that hard-codes the 2.x order reports phantom geometry errors - the
  delivered `RuntimeGuard`/`smoke_test.py` did exactly that (a fake 0.36 m closure error).
  Use `isaaclab.utils.math.quat_apply` instead of hand-rolled quaternion maths.
* `SimulationCfg.physics` is `None` by default; solver settings only exist once you
  assign a `PhysxCfg` (`isaaclab_physx.physics`).
* Kit tears the interpreter down inside `app.close()` and can swallow a traceback, leaving
  an exit code of 0 with no error text. Always wrap the entry point, write the traceback to
  a file, then close (`isaac/mod4/train_mod4_ppo.py` and `isaac/mod4/probe_physx.py` show
  the pattern).
* Do not spawn terrain via the packaged "plane"/grid assets on a machine without Nucleus
  access; build a local collider instead.
* Local Isaac Lab venv: `.venv-isaaclab` (Isaac Sim 6.0.1, Isaac Lab 6.1.14, rsl-rl 5.x).
  Run scripts with `.venv-isaaclab\Scripts\python.exe`.

## 5. Where the evidence lives

* `docs/ISAACLAB_MOD4_20260910.md` - Isaac Lab / PhysX MOD4 bring-up, training task, DR list.
* `docs/SCUT_ALIGNMENT_AND_DEPLOY_20260909.md` - the SCUT/华南虎 randomization list.
* `docs/MODEL_0910_VS_CURRENT.md`, `docs/AUDIT_0910_ADOPTION_RM2025.md` - why 0908/0910
  were retired.
* `incoming/chassis_mod4_mjcf_usd_20260910/chassis_mod4/reports/` - the delivery evidence.
