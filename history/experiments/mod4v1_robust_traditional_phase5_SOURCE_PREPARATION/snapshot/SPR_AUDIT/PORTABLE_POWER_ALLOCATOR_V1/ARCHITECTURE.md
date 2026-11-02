# PORTABLE_POWER_ALLOCATOR_V1 — preregistered architecture

## Scope

A new independent fixed-six-axis binary64 C99 / extern-C module, caller-owned configuration/context/workspace/result, no heap/VLA/mutable globals. Only new files in this directory. No physics/board/codec/production IO/SDK/GPU/Git/agent/goal action, and no edit to sealed C3/ASQP/FSM/MPC/mini-hop or parent R39/R40/R43/R44 control. PH4 excludes this component; PH5 and later remain pending.

## A counterexample requires narrowing the suggested electrical model

If R means bare winding resistance, the proposed `Pmech+/eta + R I^2 + Pe` need not upper-bound bus power. At stall I=1 A, winding R=1 ohm and inverter transfer efficiency .8, supplying the 1 W winding dissipation requires 1.25 W before other loads; the suggested expression counts only 1 W.

This version therefore takes **Cbus_loss_upper_W_per_A2**, a caller-certified bus-referred effective quadratic-loss upper coefficient, not bare winding ohms. It must cover copper loss and electrical losses omitted by the positive-mechanical conversion term. A caller may derive it from a proven winding/current convention and path-efficiency bound, but this core does not derive or guess that calibration. The electronics/other fixed-load upper bound must cover remaining losses throughout the declared domain, including braking/stall. The complete expression is an explicit caller-supplied envelope assumption, not a motor identification result.

For each load-side axis:

- `Iaxis_upper = abs(tau)/Kload_lower_Nm_per_A`.
- `Pbus_positive_upper = sum(max(tau*wlo,tau*whi,0)/eta_drive_lower + Cbus_loss_upper*Iaxis_upper^2) + Pelec_upper`.
- `Pcharge_upper = sum(max(-tau*wlo,-tau*whi,0)*eta_regen_upper)`; **no regen credit** in positive bus power.
- Bus discharge/charge current upper bounds divide the respective power bound by fresh positive bus-voltage lower bound. Vhi is also checked against the caller's calibrated voltage domain.

All quantities share explicitly declared load-side torque/speed coordinates and current conventions. Calibration, all four quadrants, direction/reduction mapping, loss/thermal domain, live voltage and reachable speed interval sources are **unbound by default**. No DM3519 CAN, Kt, R, gear ratio, temperature, efficiency or bus limit is inferred. A caller binding flag/evidence id is a contract assertion, not hardware qualification.

## Reserve and feasibility

Caller provides tau0 reserve and tau1 requested, each finite and already inside the same fresh signed-DC load-side box. There is no default reserve, no zero fallback and no zero-at-overspeed assumption. Constraints are convex in torque; the feasible intersection on tau0+s*(tau1-tau0) is an initial interval if tau0 is feasible.

Evaluate reserve independently first. A proven reserve violation is RESERVE_INFEASIBLE/invalid; rounding overlap at a boundary is distinct RESERVE_UNCERTIFIED/invalid. Neither silently scales down reserve. The requested endpoint is returned bit-exact at s=1 if certified. Otherwise use exactly 40 bisection iterations and return the certified inward/lower endpoint. No random retries or hidden alternate allocator. All constraints are checked with outward-rounded binary64 intervals; the final torque tuple is enclosed/certified again before final clock poll and commit. Finite line-representation error is explicitly budgeted, not claimed bit-exact in the interior.

The upper search endpoint means NOT CERTIFIED, not a proof of physical infeasibility. Near-flat/degenerate constraints can cause conservative loss of s; there is no unconditional true-optimum error promise. A predeclared well-conditioned oracle cohort has a separate quantitative s gate.

## Fault and time boundary

Invalid result has valid=0, s=0, tau6=0, no accepted state. Caller reserve/request are never modified, remain independent and are not replaced by failed workspace values. An invalid zero payload is **not** permission to apply zero torque in a nonzero braking box. Upper layer must inhibit or choose its own independently qualified fallback. Structural/nonfinite/alias/stale/clock/numeric faults latch until explicit re-init; reserve-budget infeasibility/uncertainty and ordinary deadline expiry are invalid but not permanent hardware faults.

Clock callback reports availability and monotonic uint64 ns; external cycle_start may predate entry. Positive caller budget and source freshness/valid-until intervals are mandatory. Poll at entry, validation, each axis/evaluation, bisection and final commit. A final failed/late poll returns no valid request. This is cooperative checking, not preemption, WCET or coverage of return-to-driver latency. Caller must recheck at actual driver enqueue and ensure the speed interval remains reachable over actuation validity.

## Placement

Use at the **actual driver-rate load-side torque request**, after any processing that can change torque. Old inversePD, D4, gain, quantization or stale feedback can change actual torque, so a 100 Hz front-end scaling is not certified physical protection. Missing thermal bounds/future thermal model, battery behavior, real HIL and electrical binding stay pending. No stability/balance certificate or C3 final enqueue claim.

Host/native/independent high-precision checks, actual C++ calls and M4/M7 object-only compilation are separate receipts. SP-hard ABI does not imply SP arithmetic; double/libm runtime, target FPSCR and timing are not qualified.
