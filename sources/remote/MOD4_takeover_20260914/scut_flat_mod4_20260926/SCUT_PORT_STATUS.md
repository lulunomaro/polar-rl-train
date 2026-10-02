# MOD4 flat-ground SCUT-style port (isolated)

This stage retains the detailed MOD4 USD and its import contract. The robot is 14.22014 kg,
31 bodies, 30 tree joints, six external closures, four mimics, eight passive guide rollers,
and six controlled joints. The SCUT V14 reference is
`scutrobotlab/wheeled-legged_RL` commit `b8ff79f3df855faf9dc92f4a282bd80c42649466`.
Its hard-coded robot joint/body names are not loaded directly. The MOD4 task keeps its
validated actuator and observation semantics while adapting V14's flat-ground reward
families and PPO settings.

Action order: `left_crank`, `left_hip`, `right_crank`, `right_hip`,
`left_wheel_spin`, `right_wheel_spin`. Legs are position targets; drive wheels are
velocity targets. `run/mapping/report.json` proves each isolated pulse reaches only
its intended action channel. The two wheel contacts and eight guide-roller contacts
are measured separately. The gas-spring reference frame returns 500 N on each side.
The mapping probe measured max closure error 0.052 mm and mimic error 0.00156 rad.

`run/dryrun/report.json` is the 64-environment, 100-step zero-action engine check:
six actions, no terminations, maximum closure error 0.171 mm. The previous
five-frame latent observation encoder is retained so the existing checkpoint can
warm-start. Initial leg action noise is reset to 0.3 (MOD4-proven) rather than
copying V14's 1.0. PPO uses the V14 policy/critic `[256,128,64]` ELU networks,
five epochs, four minibatches, adaptive learning rate, value coefficient 4.0,
entropy coefficient 0.005, gamma 0.99, lambda 0.95, and KL target 0.01.
The rollout uses 48 steps/environment because this is the measured efficient
MOD4 setting on the 4090; SCUT V14 uses 24.

Same-seed 64-environment, 15-second nominal flat comparison (`20260926`):

| Policy | Survived | Passed strict gate | Tilt RMS | Both drive wheels | Velocity error RMS | Root height |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Previous model_385 | 19/64 | 0/64 | 17.17 deg | 75.7% | 0.189 m/s | 0.223 m |
| Isolated model_19 | 32/64 | 0/64 | 15.45 deg | 80.4% | 0.197 m/s | 0.214 m |

The new policy is still **not** stable enough to declare walking or running.
The target is 0.30 m, but actual root height is near 0.21 m; pitch and loss
of main-wheel contact remain the principal failures. Training reward or episode
length alone is not an acceptance result. The formal gate is 15 s survival,
tilt <=8 deg, planar angular velocity <=1.5 rad/s, velocity error <=0.75 m/s,
both main wheels >=90% contact, and action delta/delta2 <=0.18/0.25.

`run/walk_12000_50b` continues low-speed walking from model_19 using 12,000
environments, 48 steps/environment, PhysX solver 16/4, fixed 500 N gas springs.
It saves every five PPO updates. Evaluate nominal 15 s on the same seed after this
stage. Do not start high-speed running or 300-700 N gas DR merely because PPO
reward rises. If tilt/contact stall, inspect pitch, root height, actuator targets
and roller forces before changing topology or the USD.
