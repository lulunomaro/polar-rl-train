# Attempt02 — free-face stationarity, not H/tolerance tuning

## Attempt01 retained failure

[First run](<C_RUNS_01.jsonl>) has1302 outputs and402 honest nonconverged runs. At64pivots real cold18/18, shifted-warm14/18; warm25616/18 still had oneMAX and oneCYCLE. All non-OK returned valid0/zero z. Original [source](<revisions/build_attempt_01/active_box_qp.c>), [analysis](<revisions/run_attempt_01/COMPARISON.json>) and [all402 diagnostics](<revisions/run_attempt_01/ALL_NONCONVERGED.json>) remain untouched.

A [buffered read-only observer](<diagnose_warm01.c>) captured [all selected iteration data](<WARM01_TRACE.csv>) without IO/mutation inside the clock callback. For case14 atpivot256, free exact gradients were about1e−6 while previous Newton directions oscillated up to8e−6; bound-index13 still had a clearly wrong lower-active gradient −.382732. Case16 repeated a near-identical face with free gradients1e−6 and wrong active gradient −.315422, then correctly returned CYCLE.

The original code required both an iterate-ULP-sized Newton direction AND a tolerance-qualified free-face KKT before releasing active multipliers. H15 conditioning amplified f32 gradient noise into several-ULP tangent steps, preventing release even though the free face already met the declared optimization tolerance. This was not evidence of the H or box being wrong. The initial boundary-reactivation suspicion was not used as a reason to alter the boundary algorithm.

## Structural correction

[Current source:88–95](<active_box_qp.c#L88-L95>) uses the **already declared conservative free-face gradient upper≤the same tolerance** to qualify stationarity for active-sign release. It releases only a nonfixed active coordinate with a guaranteed positive sign violation beyond its gradient uncertainty. The ULP-small test remains a roundoff/no-progress diagnostic, rather than the sole gate to inspect active multipliers.

No H/f/box/warm vector, .002 tolerance, gradient-roundoff formula,64 primary pivot limit, source seed or acceptance budget changed. No restart, hidden CCD fallback, regularization or oracle-based direction was added. Every release and step consumes one pivot from the same global counter; no phase resets it. Clock start/elapsed state likewise persists across full validation, faces and iterations.

## Attempt02 evidence

[Second run](<C_RUNS_02.jsonl>):1302 configurations,910CONVERGED/392 honest nonconverged (insufficient diagnostic budgets retained). At64, real cold18/18 and warm18/18; active8/8 each, worst25/54pivots.75 independent stress cases cold/warm64 all pass. All success points independently double-regraded against exact f32 inputs: no feasibility/KKT certificate or declared actual-H15 accuracy failures.

The predeclared [budget](<NUMERICAL_BUDGET.json>) hash is unchanged from [source freeze](<SOURCE_FREEZE.json>) and both attempt snapshots. Attempt02 is a structural numerical-method repair, not retrospective loosening of the success definition. The previous warm failures remain part of the delivered evidence.
