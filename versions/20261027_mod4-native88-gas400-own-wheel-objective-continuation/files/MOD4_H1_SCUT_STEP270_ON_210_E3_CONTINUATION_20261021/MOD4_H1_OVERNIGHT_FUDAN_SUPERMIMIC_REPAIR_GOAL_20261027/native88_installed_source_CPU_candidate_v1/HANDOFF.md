Frozen source candidate, not installed/admitted/GO. Copy only these three Python
files into the new payload root and pin each in approved_python/candidate_pins:

- native88_source_guard_v1.py
- target_native88_source_sdk_cpu_v1.py
- native88_installed_cpu_helpers_v1.py

Do not copy fixtures or test scripts into a payload. In particular,
fixtures/SYNTHETIC_FULL_INVENTORY/unapproved.py is a deliberately retained
rejected Python-inventory negative case, not an approved addition.

Guard API: check_payload(B, verify_model_bytes=True), read(path), H(path),
validate_task_go(task,go,manifest_SHA), validate_precontrol_actual(...).
The False model-byte mode skips model bytes AND model stat/existence; it never
claims model admission. Actual target uses the default True full-byte mode.
All Python files are parsed, manifest-pinned, inventory-exact and individually
candidate-pinned. Protected old runtime pins are checked against the pinned R5
manifest. Only an explicit old_SHA/new_SHA/reason row can change such a pin.
No directory-level Python exemption was added. Metadata-helper c6e421... remains
2536 exact bytes, including CRLF. Original role-control metadata closure is used;
H1 target additionally calls the unchanged installed-dependency verifier offline.

Contract filename NATIVE88_SOURCE_CONTRACT_ACTUAL.json, schema
mod4.native88.changed_plant_objective.native_fullsource.v1. See
SOURCE_INTERFACE_ACTUAL.json for exact required fields/default relative paths.
Task source_filename is its own formal native R5 source; a different
bootstrap_source_filename is normal86 0c1edb.../832460. Their bytes must be
256224393 and 16868635 respectively. Input source_native_contract is the strict
old R5 contract; new changed-plant/output contract is rejected as an input.

Future target CLI: --slot h1|recovery --num-envs 4096 --seed 27|29
--source-scope native_models_only_fresh400N_environment.
Output job0/NATIVE88_CHANGED_PLANT_SOURCE_SDK_CPU_ACTUAL.json has the root
protocol KIND and all its exact READY_FLAGS. Each true flag follows a concrete
successful CPU/source check. It keeps actual_environment_count=null and
actual_GPU_runtime_readback_passed=false, with actual fresh GPU/DR/PhysX readback
mandatory before first control/new Pi. No blanket True READY_FLAGS generation.

Future target loads native R5 exactly once and the separate normal86 witness
exactly once. It finite-checks the whole source, verifies the strict old native
contract, original saved groups, publication counters and history dimensions,
constructs only original full-size WM/Pi/Critic CPU modules and their three Adam
optimizers, and strictly restores all module state including normalizers. It
does not construct a learner/replay, perform actor/WM/critic forward, restore old
DR/environment/history/RNG, or apply the PPO20Adam rule to native. Frozen actor9,
critic8, STD6 and all17Adam832460 state are literal-exact to the normal86 witness;
the installed RSL PPO.load then receives the witness for its strict roundtrip.

Actual installed encoder/data/math/RSL/version source checks and original V8
RewardManager, boundary and trace-publication functions are retained. Fresh
private USD readback opens only the new composed stage; it checks the two gas
stiffness/upper/lower values against the pinned actual composition proof. It
does not claim PhysX runtime or measured hardware calibration. No setter was
added. The actual400N asset source report is independent of all model proofs.

The new goal check imports the selected positive V2 head, new contract, geometry
461f6b... and unchanged9223 reference. It uses a newly declared synthetic
reference-derived CPU case, verifies obs86/future1460, positive bounded reward,
short-edge counterfactual ordering and a finite forward gradient. It never reads
R2 motion NPZ. The objective_runtime_contract must be precomputed using the
actual expected joint/encoder names with actual_SDK_readback scope. Target CPU
recomputes it with source_CPU_fixture scope and requires every other field exact;
it also checks Task objective_contract_SHA. This does not replace actual postGO
joint/encoder order or claim actual contact/skill/learning benefit.

Output contract source is independently checked for changed plant, explicit
native_objective_changed, preserved physical_V8 scope, fresh environment/history
and new-window64/64/640 readaptation. Old positive Pi is never new-window progress.
The fullsave/reward/command/physical success implementation is not edited here.

CPU evidence: 29 new source/metadata/tinyTorch cases +4 actual saved metadata and
real worker AST checks +5 output-contract negative/AST checks +1 manifest-cycle
AST regression, 39 total, all passed. The
first reports are retained; no previous once fixture was rerun. V1 tested source
pins are separately retained; final output-contract increment pins the final
three payload files; the later manifest-cycle increment pins the final target.
Ready receipt manifest_SHA comes from checked manifest bytes, never from Task,
so no Task/manifest hash cycle is introduced. No actual target CPU, real model, original USD, SDK App,
scene, physics, GPU, remote, account, Task/GO or Git operation occurred here.

All source-reader mistakes are preserved in SOURCE_READER_ERRORS_ACTUAL.json.
There were no CPU-test failures. The root alone must bind final source/contract/
manifest hashes, execute one fresh actual target admission per role, establish
actual immutable waited CPU proof, and later perform postGO fresh4096 PhysX/gas/
DR/ordered30/readback before control. Current closed snapshot569553.363275528 is
historical evidence only; no budget was written or canonical copied.
