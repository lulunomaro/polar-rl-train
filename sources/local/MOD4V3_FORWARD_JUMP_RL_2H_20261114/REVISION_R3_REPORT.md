# R3: phase-balanced successful native demonstration guidance

R2was safely saved at iteration26348 after105updates and996.006612seconds of
owner time. Its fixed20/25/30minute and final tests had0/256complete jumps.
Sampling had begun to show takeoffs, but had no measured aerial retraction.
R2final SHA is c9c296e4f7a0e6c6d5930144a136478014cfb985823b8cb5ba809897eac57a2c.
R3continues this complete actor/critic/STD/Adam/RNG state. The root parent and
frozen action-label teacher remain the human-selected five-minute03884d68model.

The on-policy state distribution rarely visited successful crouch/air states.
GPU1therefore collected native teacher episodes with no optimizer. Seed20066
is separate from fixed evaluation seed10066. teacher_demos_r1recorded36complete
successful episodes out of128attempts:10800states, with phase counts
[3994,601,297,571,5337]. Failed episodes remain in its RESULT.json. Its dataset
SHA is ba3890d16f4cde62cd8079f80f7bbabfaf91e190a0da36d3b974c46319389c3d.

R3adds normalized phase progress in the last previously unused mode slot, so a
feedforward actor can represent time-varying within-phase labels. Normalization
durations are0.32s crouch,0.8s push,0.4s flight; progress clips to[0,1]. Critic
receives the same progress alongside its privileged phase. Actor35/critic78/
action6dimensions remain fixed. This is a policy conditioned on high-level phase
commands and a phase clock; autonomous phase sequencing is not established.

teacher_demos_r2recollected under the actual R3clock input producer and native
sensor delays. It again completed36successful episodes/10800frames, with the
same phase counts, datasetSHA
1e4a6713c9bf60f229f927f7024c522abe4885fafee207d70b8f2e64ec2783b7.
Both original datasets are preserved. The definitive PLAN_R3binds the latter.
PLAN_R3_BEFORE_DEMO and R3_FINAL_INPUT_BINDING preserve the input binding change.

Inside each existing native PPO minibatch, guidance samples205states from each
of the five successful demonstration phases,1025in total. The same backward
adds2.0times demo action-MSE plus the existing decaying on-policy teacher MSE.
There is no standalone BCoptimizer, no teacher execution overlay in training,
and no optimizer in GPU1collection/evaluation. PPO's learned sampled actions
exclusively drive the approved motor controller; fixed tests use actor means.

The no-update gradient check produced finite nonzero gradients while confirming
unchanged weights and zero optimizer steps. Final-clock data was checked again.
Native collection itself exercised finite35-D inputs,6-D teacher actions and
all phases over complete episodes under the R3input producer. Runtime asset,
mechanical and timing evidence from unchanged R2physics is reused. No new plant,
reward, DRrange, motor limit, closure/mimic guard or solver change occurred.

R1and R2source, checkpoints, failures and raw evaluations remain preserved.
The demonstration launch initially failed before spawning due to an overbroad
PYTHON token replacement altering PYTHONUNBUFFERED; source/error/repair are
recorded. An early final-clock data read occurred before SAFE_CLOSED existed;
it was recorded as not-ready and made no PLANor optimizer change.

The original deadline remains2026-11-14 03:08:37.400823CST. Preparation/data
collection consume wall time inside the same120minute window; actual owner
phase durations are reported separately. No extra7200second allocation exists.
Only one GPU0optimizer is active at any time. GPU1continues independent tests.

Selection uses the R3fixed input protocol, seed10066and205fullDR/51nominal cases.
A completed balanced sequence followed by an episode termination is separately
reported as a late failure and does not count as an accepted pass. Original
completed-event results remain unchanged. Independent learned-policy performance
is pending; early training-sampling takeoffs do not establish graduation.
