# Forward moving jump: authorized two-hour PPO run

The human explicitly selected the five-minute checkpoint from
MOD4V3_STAIRS_PHASE_HEIGHT_REPAIR_2H_20261113 after correcting their newer-model
request. The frozen parent is weights/frozen_best_parent.pt, SHA256
03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd,
iteration26163. Its recorded MuJoCo results are flat60/60, straight stairs4/5,
actual-oblique6/20 and descent5/5. Native fullDR/rough acceptance of that upstream
parent remains pending. This experiment does not promote a production policy.

## Workspace and time

Only the new version directory and its isolated host72 directory are used.
Remote root: /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_RL_2H_20261114_R1.
Host: amax, lc01@10.24.0.72. GPU0 is the sole PPO optimizer owner; GPU1 runs
evaluations with no optimizer. Host210 and the existing viewer are untouched.
The actual optimizer window started at 2026-11-14 01:08:37.400823 CST and targets
7200seconds, about03:08:37 CST plus final save/current-iteration close overhead.
No automatic extension is configured. Checkpoints save every300seconds.

## Method and task contract

Native RSL5 PPO is continued with actor, critic, STD,17Adam entries and saved RNG.
The new learning rate is1e-4, fixed schedule, clip0.2,5epochs,24step rollouts,
2048environments. A frozen five-minute parent supplies training-only staged action
labels; an auxiliary action MSE is added inside the same PPO backward, with
coefficient0.5 decaying to0.15 over5400seconds. Actual training actions always
come from the learned stochastic actor. The teacher never replaces executed
actions in the PPO owner. Independent tests use deterministic learned actions.

The commanded skill is forward motion0.4-0.8m/s, crouch, extend to push off,
retract in flight, and land while continuing forward. Episode length is6seconds.
A complete success requires measured crouch and extension, actual unsupported
upward forward takeoff, measured aerial retraction, at least0.16seconds airborne,
wheel lower rim peak at least0.12m, airborne pitch at most10degrees and roll at
most5degrees, then0.5seconds of stable forward recovery with wheel support.

Only approved MOD4v3 HW300N60R3 assets are used. Identity hashes are verified.
Physics2.5ms, TGS32/4, leg feedback100Hz, wheel feedback400Hz and policy50Hz are
retained. Original motor envelopes and action order are retained. Closure0.01m
and mimic0.01rad are per-environment episode reset guards; ordinary contact and
40degree/0.2second attitude guards are retained with separate dwell counters.

Actor35/critic78/action6 dimensions are retained. This new task versions the
seven mode slots: actor gets jump request, measured flight and landed cues;
critic gets a privileged phase one-hot. The actor infers crouch/push progression
from proprioception and previous action. The current deployment input producer
does not yet provide these task cues. This is a simulation training candidate.

The fullDR parameter ranges and fixed80percent fullDR/20percent nominal mixture
are retained. Resets change to upright mechanically feasible poses, small yaw
and zero velocity for this task. They do not retain the old ground/fall reset
distribution. The inherited DR summary contains a legacy normal/ground wording;
the explicit reset_distribution field and PLAN task contract supersede it.

## Admission and preserved attempts

admit_r1 completed128actor-only episodes over300policy steps, with finite
observations/rewards, correct35/78/6interface, original mechanical limits and
timing, verified assets, no optimizer update and no closure/mimic/numerical reset.
Peak closure was0.000314506m; motor plateau limits were respected. Runtime
admission passed. Its learned parent jump success was0/128.

teacher_native_r1 completed simulation and wrote its trajectory but failed JSON
serialization on a NumPy int64 aggregate. ERROR, incomplete RESULT, original
source and trajectory are retained. The repair casts the aggregate count to a
Python int; no physics or task change occurred. teacher_native_r2 repeats the
same no-learning diagnostic with the repaired reporter: nominal25/25 complete
balanced jumps; fullDR101/103takeoffs,19/103retractions,11/103complete successes.
These are teacher-controller results, not learned-policy success.

eval_parent_fixed uses seed10066 and256fixed native cases independently of the
checkpoint training RNG. Parent result: nominal0/51 and fullDR0/205complete
successes, no takeoffs. This exact evaluator is used on periodic learned weights.
No optimizer is created by the fixed evaluator.

## Actual learning evidence

FIRST_UPDATE.json records iteration26164,8.156seconds into the PPO window.
Actor MLP, critic, STD and all Adam step counters changed. The first full child
checkpoint is6,348,927bytes, SHA256
3e3fc5a3e89e48e03f10be435a1b037bc58f907f28bd8915961e5c52e603c587.
It includes complete actor/critic/STD/Adam/RNG and new task/DR checkpoint state.
Old stair demonstration replay is not part of the new task checkpoint.

Training is active at this launch stage. Jump graduation is not yet established.
observe72.py freezes complete periodic checkpoints and finished reports, queues
one GPU1evaluation at a time, and never launches another optimizer owner. Final
weights, paired evaluation, actual elapsed budget and safe close remain pending.
Full checkpoint bodies are retained in Git under the existing human instruction;
large plant/trajectory originals have actual path/size/SHA indexes.
