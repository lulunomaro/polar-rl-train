# R15 software-failure classification erratum

[R15 batch](<../batches/r15_jump_roll_train33/BATCH_RESULT.json>) exitednormally at launcherlevel, but ALL33 childprocesses returned1 before completingtheirjumpcontrol. Therefore its printed DR_end2s=0/10 summaries are NOT a robot capability score: valid completed controller evaluations=0, software failures=33.

Root cause preserved in eachcase ERROR.json/log and sealed batchsource: generated [rollV2:35](<../run_jump270_roll_v2.py#L35>) called nonexistent `LinkageGeometry.jacobian`. The actual [sensor geometry API](<../sensor_core_v4.py#L53-L59>) returns its3x2 footJacobian as resultindex2 of `wheel_kinematics`. Error occurredatfirstpushbranch, e.g case r15_roll_0 had170completedcontrolframes/3400physicssteps; thoseprefixes countas consumedwork, notsuccessfuljumptrials.

Original R15source/configs/errors/logs remainunchanged. A newV3 source/newR16caseIDs will correcttheAPI call and addpuremathAPIpreflight plusfourcasechunkfail-fast. No overwrite/replayofR15IDs. Existingerrorhandler retainedprefixcounts butdidnotpersistprefixrowtrace; thatdata isunavailable, not reconstructed or claimed. V3willpersistfuturepartialtraces onerrors.
