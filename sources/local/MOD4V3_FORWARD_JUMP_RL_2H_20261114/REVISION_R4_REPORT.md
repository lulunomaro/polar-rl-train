# R4: observable descending-flight landing preparation

R3's teacher labels switch from aerial tuck to landing extension when measured
world vertical velocity is below-0.10m/s. Actor35does not observe linear velocity;
critic78does. The added phase clock did not explicitly identify that branch.
Nominal fixed cases continued to take off and balance but missed the0.9rad tuck
depth. R4therefore exposes descending flight through the existing landed-mode
slot: it is true during descending phase3or after measured landing. Air/contact,
crouch/push commands and phase progress disambiguate the two situations.

Only this policy observation cue changes. Teacher execution, rewards, objective
thresholds, approved assets, physical controller, DRranges,2.5msphysics,TGS32/4,
100Hzlegs,400Hzwheels,50Hzpolicy,10mmclosure and0.01radmimic guards are retained.
The cue requires the versioned input producer and a vertical-state estimate for
deployment. The actor remains a phase-conditioned learned policy, not an
autonomous phase scheduler. No joint-action overlay, pose clamp or jump force
is applied in PPO or fixed evaluation.

R4source/data preparation ran while R3kept learning on GPU0. GPU1collected
teacher_demos_r3under the actual R4input schema, seed20066:36complete successful
episodes/128attempts,10800frames, phase counts[3994,601,297,571,5337]. DatasetSHA
fa88c8e7cc56a9d6ccfbacd532d8caf4ecf973c5c9b16fa114a8f8c0242c3632.
The complete raw results include failed episodes. Collection has no optimizer.
The finite-gradient/no-weight-change guidance check passed on the actual data.

After all R4inputs were ready, R3honored REQUEST_STOP and atomically saved its
complete final state at iteration26729, SHA
146d20cef5cfc94ab2d9b9b4fc041b2ea6a2a6c01acf04283a9321d025e902ae,
after381updates and3644.069288seconds. Its subsequent frozen final test is
nominal0/51andfullDR20/205complete. All R3updates and checkpoints remain preserved
and charged even where they are not selected.

R4loads the full PPO state from R3's best completed fixed evaluation at selection
time: model_080m.pt, SHA
eb8a6d42b17332100935201530a82688e9bad273af2ef5a8c28d49aa0e29f104,
nominal0/51andfullDR26/205complete, no late failures. Actor/critic/STD/Adam/RNG
are continued from this trial's own best point. This is a rollback within the
same task, not an external parent replacement. Root parent and frozen teacher
remain the human-selected upstream five-minute03884d68checkpoint.

The one shared wall window retains the original absolute deadline
2026-11-14 03:08:37.400823CST. R4has no additional7200second allocation. Only one
GPU0optimizer is active at a time; R3closed before R4launch. Actual update work
is summed across all four owner phases, including the unselected R3tail. Model
iteration numbers alone are not used to infer spent work after the rollback.

R3andR4fixed results keep their input revision and original raw reports. They
share seed10066,205fullDR/51nominal initial cases and the same physical success
criteria. Selection compares accepted complete sequences with no later episode
termination; raw completed events and late failures remain separately visible.
This record establishes the correction and launch, not final graduation.
