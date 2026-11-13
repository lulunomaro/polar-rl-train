# R2: observable phase commands within the original window

The R1five-minute,ten-minute and safe-final deterministic tests each produced
0/256takeoffs and0/256complete jumps. Training sampling produced6takeoffs but
no aerial retraction or complete success over80updates. Source review found
that phase1(crouch) and phase2(push) had identical policy mode inputs for a
feedforward actor. An unsuccessful push also lasted until the6second episode
limit while continuing to earn extension shaping. These task design problems
were corrected in an isolated support_r2 snapshot; R1source/evidence are retained.

R1received a REQUEST_STOP marker and completed its current update, atomic full
save and scene close. The marker was created by SFTP exclusive-open; writing
text through that handle failed because exclusive mode lacked a write flag.
The empty marker was sufficient, and the owner honored it normally. R1final
iteration26243,SHA4fe6b2d41da9eeda5466e81e32e3ba174ca7e35bc400219949be6d1a7f84213e,
elapsed688.938845seconds. The real failure and marker behavior are preserved.

R2restores that full actor/critic/STD/Adam/RNG state, retaining the explicitly
selected root parent03884d68 (five-minute upstream checkpoint). The frozen
action-label teacher remains the selected five-minute parent. It is not a new
external parent, a fresh optimizer, or an additional training budget.

Two previously unused actor mode slots now carry crouch and push phase commands.
Policy dimensions stay35/78/6. The environment still supplies forward/jump cue,
contact and recovery state. PPO's learned actions exclusively drive the motors.
This is a policy conditioned on a high-level phase command; it does not establish
autonomous phase timing from a single unchanging deployment input. Deployment
would require the documented versioned task input producer.

A push with no takeoff after0.8seconds now terminates as a failed task attempt.
This is an added task timeout, not a physics guard relaxation. Other reward terms,
original motor envelopes, approved MOD4v3assets, TGS32/4,2.5msphysics,100Hzlegs,
400Hzwheels,50Hzpolicy, fullDR ranges, fixed80/20DRmixture,10mmclosure and
0.01radmimic resets remain unchanged. Both revisions use the same complete-jump
success criterion and separate nominal/fullDR reporting.

R2admission completed128episodes, with verified hashes,mechanical limits,timing,
finite observations/rewards, and no closure/mimic/numerical reset. Peak closure
was0.000505348m. These runtime checks do not count as learning or jumping success.

The only training wall window began2026-11-14 01:08:37.400823CST and retains the
absolute deadline2026-11-14 03:08:37.400823CST. R2checks this original deadline
before each new rollout/update iteration. Revision preparation and admission
consume time inside that window. The R2launch receipt's training_seconds=7200
denotes the shared total target; it is not another phase allocation. Actual
phase durations, full save overhead and total charged window are recorded in
the final budget ledger. No automatic extension is allowed.

GPU0has one optimizer at a time. R1was safely closed before R2launch. GPU1runs
fixed-seed actor-only tests without an optimizer; the root parent is also tested
under the R2phase-input protocol to provide a correctly matched baseline.
Host210, production weights and the existing viewer remain untouched.
