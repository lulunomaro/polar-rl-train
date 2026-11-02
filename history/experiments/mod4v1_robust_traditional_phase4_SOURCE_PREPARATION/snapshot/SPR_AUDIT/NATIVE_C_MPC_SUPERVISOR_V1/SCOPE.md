# Independent native MPC supervisor, new functionality only

Port the reviewed parent [Python v2](<../../C_ACTIVE_MPC_SUPERVISOR_V1/supervisor_v2.py>) supervisor and link the sealed [ASQP](<../ACTIVE_BOX_QP_V3/active_box_qp.c>) directly in-process. No SDK invocation, stdio/transport/parser/worker, old IO repair, physics/GPU/Git/agents/goal change. All old packages are read-only.

- Typed C3 base: valid, STATE14, REF14, MATH_TAU, GUARDED_TAU, SHAPER_V, same-packet drive6. Scalar input arrays are binary32 exactly as C3. Explicit epoch equality is an additional native typed guard, not new sampling evidence.
- Caller-owned context and workspace, no heap/VLA/mutable globals. Compile-time const model. Binary64 condensing/DC/caller KKT, unchanged binary32 ASQP. Returned torque6 is binary64 (fallback is exact promotion of the original C3 float).
- N15, fixed-leg8+nominal lag9, H15 exact existing f32 bits; tolerance float32(.002), one 64-pivot cap. No model/guard/tolerance tuning. Current-point signed four-quadrant wheel DC intersection frozen over N15; not future contact/state/power/energy constraints.
- Planned compression f = Mstate*state9 - Mref*ref8 - Mv*SHAPER_V. Different arithmetic order from BLAS, no bit-exact promise. Preregister numerical comparisons before any C execution.
- Independent copied GUARDED fallback; invalid base returns zero/invalid. Domain abs(yawrate)>2 or abs(pitch)>.25, disabled/latch/no-headroom/failed-QP/deadline paths use fallback. Fault/certificate/clock paths latch, expected nonconvergence/deadline do not. Explicit init is the only native latch reset.
- External cycle_start_ns may precede C3; bounded positive caller cycle budget. Monotonic u64-ns availability callback at native phases and ASQP polls; kernel receives only remaining whole microseconds. Final supervisor poll also covers disabled/domain/fallback paths. No commit of accepted/warm until that poll passes; output does not expose any failed private iterate as accepted.
- No claim about execution after final poll, caller serialization, final C3 enqueue, driver/BSP, target libraries, ARM execution/FPSCR/stack/WCET. A valid fallback is not a newly deadline-qualified driver command.
- Every actual attempt/source/log is retained. exit0 missing artifact stops its build line; no renaming/settings/protection changes to bypass it.
