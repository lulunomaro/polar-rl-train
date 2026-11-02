# Actual MPC8 Hessian — pure numerical comparison scope

- New writes only in this directory. Sealed boxQP, C1/C2/ODOM and parent files remain read-only.
- Read scalar_ground_mpc_v1.py and MPC8_V1/MODEL_AND_QP_CHECKS.json as source/data only; never import parent controller/plant modules.
- Assemble F/G/Qbar/H with installed NumPy/SciPy/stdlib; no new packages.
- Use explicitly symmetric float32 H with sealed boxqp.c, compare to independent float64 oracle for the actual model's small state/reference errors and active boxes.
- No MjData/mj_step/simulation/physics/HIL/board/CAN/SSH/Git/new agents. Host results are not ARM WCET.
- Keep every source, attempt/error log, original status, numerical KKT check and source hash. Budget exhaustion is a truthful fallback signal, not convergence.
