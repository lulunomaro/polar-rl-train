# Frozen Python → new C contract (before native code)

Source is [frozen Python](<../../FSM_DETECTOR_V1/fsm_detector.py>), SHA8aa2eb817cc095f2b3c470d37e24bbe91ba13a5e5a77b06e75aa54e45cce0b2e. [Budget](<NUMERICAL_BUDGET.json>) is fixed before first C execution: zero discrete/order differences, binary64 numeric error<=1e-12+1e-12*abs(reference), state-entered time exact.

|Python|New C mapping|
|---|---|
|Config defaults|Generated fields/defaults from exact inspected dataclass; no threshold selection. Scalar/proxy/trajectory arithmetic is binary64.|
|relative seconds, None timers|double seconds + explicit timer.present. Original comparisons and1e-12 dwell representation slack remain; no us quantization or wall-clock provider.|
|Mode/Profile/Phase/Valid/Support|Identical integer IDs. No torque6, CAN, board callback, jump-distance or success output.|
|None frame/command or malformed schema|Typed frame_type_valid/command_present/schema_version/shape flags. Core arrays fixed-size; invalid core shape maps explicit shape bit, not fake finite0. Null C pointers are separately typed BAD_ARGUMENT.|
|None force/None element/empty provenance|present/value_present/shape flags + nonzero provenance_id. Missing value is unknown, not0N; negative/nonfinite/low-confidence optional force resets that wheel unknown.|
|Motor/front optional fields|Explicit present and vector/value validity bits. Stale optional observation never becomes trusted, force/COM/front source/provenance declaration does not prove calibration.|
|positive arbitrary Python event/observation IDs|Explicit uint64 monotonic IDs (no internal increment/wrap); values outside typed width rejected by caller adapter, not truncated.|
|strings/reason tuples|[69 frozen IDs](<REASON_REGISTRY.json>):66 Python reason strings plus BAD_CONFIG/BAD_CONTEXT/BAD_ALIAS typed extensions. Two64-bit words (old proposal's one word is insufficient), AND ordered de-duplicated ID arrays for per-item parity.|
|ContactEstimate|Same support/wheel-unknown/confidence, explicit com_freefall_known/like and evidence enum0unobserved/1external proxy/2declared COM model; ordered contact reasons retained.|
|expected_q4=None|q4_reference_valid0 and all4 values0; inhibit always INHIBIT/NONE/u0/q_valid0/no permissions. q4 order absolute Lhip,Lcrank,Rhip,Rcrank, NOT state14 delta.|
|hard fault/reset|Preserve previous contact on immediate hard path; latch faults in original order, no normal fallthrough. Reset needs new event+disarm+healthy dwell and returns only DISARMED.|
|list/dict dynamic state|Fixed caller-owned context, owned config snapshot, no heap/VLA/mutable globals. Single owner; ordinary per-tick reinit would erase latch and is prohibited by contract.|

## Typed extension boundaries

C config bools/enums/binding flags are checked, partial electrical tier binding is rejected. Optional step range must bind both endpoints together (Python leaves some disabled partial ranges unchecked; these have no valid typed C range). A malformed/aliased context or pointer is not falsely counted as a Python array comparison. For output/context overlap, canonical output and an intact latch cannot occupy the same bytes: return FD1_E_ALIAS, latch the context, do not write the overlapping output; caller must discard that output and use the mandatory inhibit path. Other failures with disjoint output clear it and emit inhibited FAULT_LATCH. Config/context corruption requires explicit valid reinitialization, not reset-event bypass.

C3 float32 observations may be promoted to this double API; promotion adds no measurement precision or trust. Nothing here adds an FP64 qualification requirement to existing physics/RL/C3. New M4/M7 -c facts concern only this module; SP-hard ABI does not make its binary64 operations SP arithmetic. Software-double helpers, libm/BSP link, target timing and WCET are future bindings, not prerequisites for other already-authorized work.
