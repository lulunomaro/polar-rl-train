# 20000 environments: actual official rough PPO continuation

User explicitly requested 20000 environments after selecting official Isaac Lab
rough terrain and restoring PhysX/PPO/Warp sampling instead of SuperMimic.
This stage confirms actual updates and a complete save; skill acceptance is pending.

The source4096 run production06 finished iteration364 after3600.107s, saved the
complete learner, safely closed, and completed independent80 evaluation. Source
checkpoint SHA99ece254c743a7a1445445d6ecc188a07e1a7ff077fe57177310f8bd59cb7870.
All17Adam entries and actor/critic/STD/LR/RNG remain the continuation source.

Attempt production01 created20000 official rough environments and saved update365,
but native PhysX patch buffers overflowed915 times before interruption. Requested
capacity reached696124, above SDK default163840. Its updates are invalid and were
not resumed. Its log, native startup, restore, complete first checkpoint identity,
and interruption receipt remain preserved. The application returned0 on SIGINT
and its owner correctly rejected the missing final receipt. No SAFE_CLOSED receipt
was produced; do not claim a successful normal close. The last complete failed
checkpoint remains remote; the earlier valid source final remains unchanged.

Repair only sets gpu_max_rigid_patch_count=1048576 for populations>=20000. Other
PhysX capacities, TGS32/4,2.5ms physics,100Hz explicit PD feedback, nominal HW300N60
mechanics, raw actions, standing rewards,DR off and official rough defaults remain.
No aggregate-buffer2**28 allocation or easier terrain was introduced.

Attempt production02 runs on host72 GPU0 under the original private GPU lock.
It restored source364 with all saved learning tensors equal and17Adam entries.
Native STARTUP confirms20000, official rough and patch capacity1048576. Update365
changed the actor and saved a19241835-byte complete checkpoint, SHA
b6477a347bd12cb0b4f5fa5c61dd32df9d99b6753e704be9becfced2f6e1deec.
At the archived observation it reached367, early window13551.5 environment steps/s,
GPU19006MiB, and zero native log errors/overflows. This is an early window, not a
completed-hour speed claim. Individual closure resets remain active at10mm; the
first batch included a22.42m extreme reset event. Neither clean logs nor completed
PPO updates certify mechanical or skill success.

The source independent80 report has final_stable_count0; this is a final-sample
count rather than a full-episode success metric. Actual saved body poses were
rendered without policy reads or physics steps. Native visual review of env0,20,
40,60 shows persistent pitched posture and inconsistent speed; the standing-forward
target remains unachieved. The source NPZ omitted names and terrain mesh. Names
were associated from later native STARTUP with the identical USD/SDK; the replay
explicitly draws no terrain and cannot establish support/contact success.

The live run remains finite3600s with300s complete saves, then normal safe exit
and independent80. Its future evaluation writes native body-name metadata and
the exact imported rough mesh to support actual terrain replay. Current work order
records the live state. No new automation, chat or goal was created.

Local report mappings and external large artifact SHA/path indices accompany this
note. Preserved prior source revisions are the actual failed-attempt env/train;
the current package contains the small fix and the saved-pose renderer. Reader
path failures are explicitly recorded without reconstructing missing tracebacks.
