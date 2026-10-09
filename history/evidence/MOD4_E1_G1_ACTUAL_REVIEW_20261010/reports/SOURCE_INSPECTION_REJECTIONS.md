# Local source-inspection rejections retained

These were read-only inspection errors, not SDK physics or training trials. Their original tool output remains in this task. They did not modify files, launch GPU/PPO, or touch the canonical ledger.

- E1-G1-INSPECT-PATH-01: requested `MOD4_E1_G1_ACTUAL_REVIEW_20261010/returned_rejection` but returned files actually reside under `reports/returned_rejection`. Resolved by reading the saved RETURNED_ROUTE_REJECTION index.
- E1-G1-INSPECT-GLOB-02: literal `MOD4*` and `record*` paths were not shell-expanded for rg on Windows. Resolved using rg --files and concrete existing paths.
- E1-G1-INSPECT-CWD-03: a report read was issued while working in the repository subdirectory, so its workspace-relative path was missing. Git status read itself succeeded; subsequent report reads used the workspace cwd.
- E1-G1-INSPECT-PATH-04: guessed `record_stage_once.py`, `prepare_g1_repair.py`, and shallow `payload/g1_cad_wave_geometry.py` names did not exist. The actual files were located with rg --files: record_repair_stage_once.py, prepare_g1_profile.py, and payload/isaac/mod4/g1_cad_wave_geometry.py. No requested old script was executed.
- E1-G1-CAUSE-HYPOTHESIS-05: variable shadowing was considered while interpreting the traceback, but installed primary SDK source proves the actual cause is ProxyArray.dtype returning Warp ctypes. The shadowing hypothesis was not deployed or presented as the verified cause. Installed SDK source hashes, original traceback and successful .torch interface proof are retained separately.

Before executing the new metadata writer, its unexecuted draft ledger-key assumptions were checked against the existing actual collector and corrected to authorized_training_seconds/charged_training_seconds. No failed central mutation occurred from that draft.
