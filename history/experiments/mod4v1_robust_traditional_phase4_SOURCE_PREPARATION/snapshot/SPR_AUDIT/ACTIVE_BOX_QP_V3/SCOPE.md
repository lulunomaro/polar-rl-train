# ACTIVE_BOX_QP_V3 — independent feasible primal active-set boxQP

New API/files only here. No old QP ABI/source/manifest edits. No physics/robot MPC integration, Git, agent, BSP, board, ARM execution or WCET/3ms qualification. Current Office/ACL catalog does not match numerical C work; use existing Python314/MinGW/armclang CLI.

min .5 z'H z + f'z, finite exactly-symmetric SPD f32 H, finite box, n<=16. Start clip(warm); free-face Newton direction, feasible line to first bound, active KKT-sign release, fixed l=u excluded from release. No truth/episode-dependent H changes, diagonal regularization, hidden CCD fallback or free-only shortcut.

Finite pivot cap, exact state history/cycle and no-progress/roundoff-limit statuses. Only independently checked KKT certificate qualifies CONVERGED; MAX/deadline/clock/input/numeric failures valid0 and all z0. This is numerical status, not actuator permission.

Caller-owned fixed workspace, no heap/VLA/mutable globals in core. Nonblocking caller clock/context with relative uint64 budget, polled inside full/face Cholesky cells, gradient/triangular/line/iteration work and again at every qualified exit. Subtraction-based elapsed avoids start+budget overflow. Logical clocks test early abort/rollback/UINT64 edges, not actual MCU preemption or timing.

Use sealed real H15/f32 18 cases and exact quantized double oracle, cold and original shifted-previous-oracle warm (not closed-loop data). Separate independent SPD/random/active stress, double Python proof, feasibility/KKT/cost/error diagnostics, including all honest failures. Budget/source freeze precedes any new solver results. Old QP1/2 MAX records remain intact.
