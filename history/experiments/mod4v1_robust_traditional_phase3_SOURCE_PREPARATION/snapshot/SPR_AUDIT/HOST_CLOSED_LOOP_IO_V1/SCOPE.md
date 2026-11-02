# HOST_CLOSED_LOOP_IO_V1 — local resident P25 adapter only

New standalone host executable over stdin/stdout. Link the sealed V3-current and C2 sources read-only; never edit V3. One profile=P25 initialization per process, persistent C estimator/controller/gate state, complete packet+command+logical time input, version/count/sequence checked ASCII lines. stdout is protocol only, stderr diagnostic logs. No network/CAN/board/BSP, no ARM execution/WCET.

Python64 talks to the MinGW32 executable through subprocess, not ctypes DLL. It has timeout/EOF/error handling and no silent restart/rearm. Fault responses zero every payload field and latch; a fresh process is an explicit reset. Tests use only existing frozen numerical fixtures and malformed software frames, never a plant/new physics/parameter selection.

Bindings here are LOCAL_STDIO_MOCK_ONLY, not hardware verified. Logical simulation before/after clocks are explicit wire inputs and do not measure host/ARM elapsed time. Reply names distinguish final DC-guarded tau6 from pre-DC P25 mathematical tau6; parent inverse-PD/driver may enforce limits again. No root/contact/world-position truth fields are accepted.

This is postR16/PH3-pending integration tooling. It does not expand the PH2 cutoff or qualify H2, terrain, jumping, hardware, or physical closed-loop success. Parent owns all NEW-scene physics and its four-core budget; this child runs software protocol tests only.
