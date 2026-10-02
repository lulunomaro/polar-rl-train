# MOD4 continuation on the SCUT V14 route

Upstream: `scutrobotlab/wheeled-legged_RL` commit
`b8ff79f3df855faf9dc92f4a282bd80c42649466`.
This stage keeps the MOD4 detailed USD, six-motor action order, closed-loop
constraints, five-frame policy encoder, and latest complete PPO checkpoint.

## Spring mapping

SCUT V14 Flat specifies `mode='linear'`, 400 N at minimum compression,
an additional 200 N per 70 mm compression, uniform per-spring episode offset
in [-50, 50] N, and `damping=False`. Its implementation applies the axial
force on the spring's sliding joint every physics step.

The MOD4 slide coordinate increases with mounting-eye separation. The two
authored upper stops coincide at `q_max=0.0352033350025 m`; the lower stops
are `q_min=-0.0267046843609 m`. Thus this continuation uses

```
k = 200 / 0.07 = 2857.142857 N/m
F_i(q) = 400 + k * max(0, q_max - q) + delta_i N
delta_i ~ U(-50,50), independently sampled for each side and episode
```

Within the authored slide range, the implicit drive target `F_ref_i/k` is
algebraically identical to this force law. Its spring stiffness is `k` and
damping is zero. At `q=0`, nominal force is 500.580957 N. At maximum
compression, it is 576.880055 N. Training forces including DR range from
350 N at maximum extension to 626.880055 N at maximum compression.

The literal SCUT `spring_offset=0.06076 m` is defined in SCUT's own joint
coordinate. Applying it numerically to MOD4 would put approximately 646 N
at MOD4's compressed posture and would be a coordinate error. Aligning
full extension preserves SCUT's physical force-stroke law. No gas spring
part number or bench force-stroke curve has yet been supplied, so this is
an upstream-based simulation prior, not a claim about fitted real hardware.

## Route and checks

1. Preserve the original 20,000-env flat run and its complete checkpoints.
   Transfer actor, critic, optimizer, iteration, and exploration std from
   the latest complete checkpoint into this isolated stage.
2. Continue SCUT V14 Flat PPO at 20,000 env x 48 steps with solver 16/4.
   The spring alone changes; all other MOD4 physics, rewards, command
   distribution, action mapping, and PPO hyperparameters remain unchanged.
3. Each hour, compare deterministic nominal flat validation with the
   transfer checkpoint using the same 64 env, seed, and 15 s horizon.
   Require repeated survival, tilt, contact, speed, smoothness, and closure
   acceptance before advancing.
4. After two passing flat validations, adapt SCUT V14 Rough v1 terrain
   and commands to MOD4 in isolation; then Rough v0 rotation terrain.
   Preserve a flat regression set at each promotion.

The SCUT repository exposes Flat and Rough tasks but does not prescribe an
automatic promotion order. This order follows the existing MOD4 acceptance
contract and the user's stable walking/running priority.

## A/B context before this stage

With checkpoint model_1720, 16 env x 15 s, nominal flat:

| Gas configuration | Tilt RMS | Mean pitch | Survived | Both-wheel contact |
| --- | ---: | ---: | ---: | ---: |
| Previous `500-3500q` N | 11.46 deg | -11.17 deg | 13/16 | 68.1% |
| No spring, no damping | 10.09 deg | -9.82 deg | 8/16 | 60.7% |

Removing the gas spring improves pitch by about 1.34 deg but harms survival
and wheel contact. This is a diagnostic, not a reason to remove the spring.
The above checkpoint was trained with the previous force law, so short A/B
results do not replace retrained-policy validation.

Upstream evidence:

- `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py`
- `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py::_apply_spring`
- `source/agent_tasks/agent_tasks/direct/wheelbipe/agents/rsl_rl_ppo_cfg.py`
