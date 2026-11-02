# POWER allocator — honest attempts and limits

## First executed host attempt: retained failure

[HOST_BUILD01](<HOST_BUILD_01.json>) records strict compiler/link commands with retained artifacts, then the actual [native01](<native_run_01.log>) reports **2290 checks / 1 failure**, endpoint memcmp at line28. The [first core source](<host_attempt_01/pa1_allocator.c>) SHA is `d1adc436615a3335bd8c84ea6212bd7fa3b15b302888400ec085dfed70d1a5a9`. The C++ executable was compiled but not run after the native stop. No artifact disappeared in this component.

All [219 first raw rows](<C_RUNS_01.jsonl>) were subsequently graded without rerunning the executables or oracle: [COMPARISON01](<COMPARISON_01.json>) has 38508 checks / **3 endpoint bit failures**, all in `signed_negative_zero_full_endpoint` axes0/2/4. The actual model constraints, enclosure checks, line budget and s gates have no other failure. Source branch `s==0 || a==b` ran before `s==1`; +0 and -0 compare equal but have different bits. The earlier shortcut chose reserve +0 rather than requested -0.

## Only revision: requested endpoint priority

The [current core](<pa1_allocator.c>) SHA `613723ccdb1021ec9cf04b4b1260261b73368c6cd6f4ca307eba88b50240c571` moves `s==1` before the equality shortcut and adds an explanatory comment. [Analysis receipt](<ANALYSIS_RECEIPT.json>) checks that undoing exactly this edit reproduces the first source bytes; all other build input sources are unchanged. Original219 cases, exact oracle, model contract, budget, limits and interval certification remain byte-identical. The current [header](<pa1_allocator.h>) SHA is `f5531a783d630457cd6e786d6ffe3cc2c23a6936a2c8168230e163c0ddffe0ca` in both attempts.

Second actual [HOST_BUILD02](<HOST_BUILD_02.json>) / [COMPARISON02](<COMPARISON_02.json>): 38508 numerical checks /0, [native02](<native_run_02.log>) 2290/0, actual [CPP](<cpp_run_02.log>) pass. Both attempt directories/logs/raw outputs/clock CSVs remain. First failed assertions are not overwritten or counted as passes.

## Expected invalid model cases are not execution failures

[ALL_INVALID02](<ALL_INVALID_02.json>) preserves7 proven reserve model-infeasible cases and3 reserve arithmetic-uncertified cases. The latter include the original braking box whose exact reserve sits on a charge-power boundary. These remain invalid without tolerance inflation or fixture repair. RESERVE_INFEASIBLE is a proof for the declared conservative envelope, not measured physical impossibility; an envelope upper value above a cap need not prove actual motor power above it. Reserve is never shrunk.

[36 logical clock inserts](<NATIVE_CLOCK_CASES_02.csv>) cover deadline/rollback/unavailable at12 predetermined locations, including final poll. They are mathematical branch/fault tests, not hardware timing or control qualification. No extra verification or tuning loop followed the agreed scope.

## Other evidence

One read-only guessed legacy ARM-script path was absent; [READ_ERROR01](<READ_ERROR_01.txt>) records it. Host glob found the actual old script; it was only read. New [ARM_BUILD01](<ARM_BUILD_01.json>) compiled both scheduled objects on the first target attempt, no warning suppression or option relaxation. [Object inspection](<object_inspection_01.log>) reads ELF bytes and compiler attributes only, no target execution.

Bare winding R counterexample and bus-referred narrowing were accepted before core implementation in the frozen [architecture](<ARCHITECTURE.md>) / [contract](<MODEL_CONTRACT.json>). Calibration, current convention, thermal/electrical domains and downstream driver validity remain unbound by default. No actual board/battery/electrical/thermal/HIL/stability/WCET or robot closed-loop result is inferred from the mathematical/native/object evidence.
