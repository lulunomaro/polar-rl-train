V2 is the independent before-use repair of the unused V1 timeout signal branch.
V1 source and INDEX01d1d8bb... remain unchanged and its rejection is preserved.
Only the runner's TimeoutExpired block changes. No terminate/kill/send_signal/
signal call remains in the selected runner or its embedded metadata-child code.
Contract9e95df01... and finalizer0de25036... are byte-identical to V1; original226
probe/authority semantics/213 typed ABI/model read counts are unchanged.

On timeout the runner immediately records E2_FROM226_METADATA_TIMEOUT_ORIGINAL_FALSE.json
with passed=false,actual_waited=false,all_own_children_waited=false,FREE/EX-release
claim=false and original child still pending. It then continues that exact
child's original communicate() and finally wait(). It sends no signal and
starts no replacement. The final wait report is written only after actual wait;
timed_out remains true,so the result remains passed=false even after RC0. The
existing finalizer refuses that timeout result. Do not rerun the consumed probe.
ROOT must keep its original finite handle/serial control occupied until the
actual child is waited out; an outer client timeout is not proof of FREE.

ROOT stages the three selected V2 interface .py files from INSTALL_SOURCE_V2.json
instead of V1 (same installed filenames), into its new real226 job. Existing
frozen226 source/expected/install/postcopy and E2b3ae formal identities remain.
No old model/raw/asset is read by this package. No new Task/Ready/authority receipt
is fabricated. Current227D may only be an expected binding for a separate ROOT
fresh owner/run/GO/canonical match; freshCNone remains its own explicit mode.

Target metadata command (ROOT supplies actual paths/current receipts/IDs):

`ACTUAL_SDK_PYTHON -u -B run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py --job-root ACTUAL_JOB --actual-authority NEW_AUTHORITY.json --metadata-admission NEW_CPU_ADMISSION.json --sdk-python-launcher ACTUAL_SDK_LAUNCHER --purpose-id NEW_E2_METADATA_SCOPE --timeout-seconds ROOT_BOUND_LE360`

JSON-only typed evidence command, unchanged:

`ACTUAL_PYTHON -B finalize_e2_from226_actual_evidence_ROOT_ONLY.py --job-root ACTUAL_JOB --actual-wait ACTUAL_JOB/E2_FROM226_ORIGINAL_METADATA_CHILD_WAIT_ACTUAL.json --actual-authority NEW_CURRENT_AUTHORITY.json --purpose-id SAME_E2_METADATA_SCOPE`

Without actual held runtime/private-GPU/shared/resource/source-symlink evidence,
the Task remains READY only. Optional --actual-runtime-admission retains V1's
exact current-authority after-metadata join,independent GPU rule,0-byte same-host
link and no learning GO/account write. V1 HANDOFF remains the complete schema
reference except its obsolete timeout termination description, superseded here.

New verification is AST/source-only with an explicit zero-signal-call check.
No child,probe,old fixture,SDK/model/asset/raw/GPU/network/Git action is run.
Actual metadata and complete E2 24s/20k sameUID skill evaluation remain pending.
All source and errors await ROOT's ordinary Git append.
