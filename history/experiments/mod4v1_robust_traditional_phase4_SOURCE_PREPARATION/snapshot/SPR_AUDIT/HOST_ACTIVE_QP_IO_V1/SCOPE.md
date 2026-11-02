# HOST_ACTIVE_QP_IO_V1 — numerical resident stdio bridge only

New independent directory. Old ACTIVE_BOX_QP_V3/H2/C3/P25 IO/QP/physics artifacts are read-only. No Git, new agents, physics, GPU, BSP, CAN, ARM execution or WCET work. Parent-owned H4/R36/heading work is neither read for parameters nor modified. postR16 / PH3 pending; no enlargement of PH2 conclusions.

## Fixed contract before execution

- Python3.14 64-bit uses a resident MinGW32 PE32 child through bounded ASCII stdio, never cross-bitness ctypes.
- Exactly one sealed `ab3_solve` per SOLVE frame; direct compile from the unchanged sealed source and header. n=1..16, all external math inputs rounded once to finite float32; original symmetric-SPD/box/solver semantics remain authoritative. No new oracle, solver, warm substitution, retries or hidden restarts in this bridge.
- Each request explicitly carries n, H/f/lo/hi, optional warm presence/data, max_pivots, positive f32 tolerance and uint64 cooperative budget_us. No implicit retained warm, H or options. Magic/version/op/uint64 sequence/payload-token count are explicit.
- Only status CONVERGED with valid1 exposes an accepted decision vector. All other statuses retain status/pivots/clock stats but have zero accepted z/cost/KKT fields. An independently recomputed private-iterate diagnostic may be separately labeled; it never changes acceptance or supplies a usable vector.
- Production clock is QueryPerformanceCounter, exact integer quotient/remainder conversion with overflow checks. The ASQP relative budget begins at the sealed START callback, excludes protocol/SDK/fixed pre-START setup/post-return diagnostics, and is cooperative, not preemption or MCU3ms. Python records full solve-call wall time; the parent separately checks its complete control-cycle absolute deadline.
- Protocol/transport/SDK input or response faults stop only the owned worker. Numerical nonconvergence (MAX/DEADLINE/NO_PROGRESS/CYCLE/ROUNDOFF) is an invalid-zero solver outcome, not a fabricated success. No automatic worker restart.
- Default SDK accepts only the production QPC binary banner. A distinct TEST_CLOCK executable is solely deterministic I/O-contract evidence, never silently selected for production.

## Dedicated new evidence

1. 93 sealed real/stress input cases, both cold and explicit warm (186 frames), with budget_us0 and unchanged .002/64 limits, compared bit-for-bit to already-sealed direct C results. No old tests are rerun for convenience; direct results are read-only evidence.
2. Active warm branch/counters plus invalid warm even in all-fixed and zero-pivot branches; finite/shape/status/sequence checks.
3. Malformed/count/duplicate/truncated/nonfinite/oversize/uint32/uint64 boundary frames fail closed without hanging; uint64 values above 2^53 remain integers.
4. Exact tick-conversion edge/random vectors against Python big-integer arithmetic; logical early-abort harness proves invalid-zero inside full Cholesky after one cell. Real QPC calls are observed without a stochastic timing pass threshold.
5. Strict host compile, PE32 identification, source/input hashes, source closure, lifecycle/timeouts and preservation of every attempted source/log/output revision.
