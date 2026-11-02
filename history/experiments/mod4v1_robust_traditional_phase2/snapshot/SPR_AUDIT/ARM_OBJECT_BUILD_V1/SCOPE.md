# ARM compile-only evidence v1

- Existing compiler only: C:\Keil_v5\ARM\ARMCLANG\bin\armclang.exe. No download, license workaround, armcc invocation or toolchain installation.
- Inputs remain sealed/read-only: C1 ct_core.c, C2 ct_kinematics.c, QP v2-fast boxqp_fast.c and their headers.
- Compile-only -c: candidate Cortex-M4/fpv4-sp-d16/hard and Cortex-M7/fpv5-sp-d16/hard, Thumb, C99/-O2/Wall/Wextra/Werror/no-fast-math/ffp-contract=off. No host SSE flags.
- Outputs only here: six small ELF objects if compilation succeeds, exact commands/raw stdout+stderr/exit status/bytes/SHA, target macros, optional fromelf headers.
- No BSP link, BIN, board/HIL/flash, runtime math test, ARM WCET or board binding claim. Candidate CPUs are mathematical targets, not proof of DJIC/DM02 deployment.
- Any compiler/license failure stays original and explicit; do not modify license/environment or use alternate tool to bypass it.
