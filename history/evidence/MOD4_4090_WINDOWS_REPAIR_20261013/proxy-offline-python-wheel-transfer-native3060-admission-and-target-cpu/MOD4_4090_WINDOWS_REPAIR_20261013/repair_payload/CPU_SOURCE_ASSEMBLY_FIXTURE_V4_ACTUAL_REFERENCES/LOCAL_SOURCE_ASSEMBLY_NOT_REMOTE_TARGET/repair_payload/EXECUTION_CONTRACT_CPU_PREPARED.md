This payload is CPU prepared. No GPU stage, SSH, installation or canonical write
was performed by its author. All old failed factor/candidate evidence remains.

Root paths on the authorized Windows4090 host:

- environment: C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013
- scope: environment/training_scope_full20k_left_repair_20261013
- Python: environment/env/python.exe
- shared native lock: environment/WINDOWS4090_GPU_EXCLUSIVE.lock (one lock for
  all independent scopes, never a second per-scope GPU lock)
- runtime: scope/runtime20k assembled from immutable source459 plus the
  reviewed six ABI overlays and local_physx_api.py. Never use the unused128
  projection file or the local128 capacity override worker.
- payload: this new directory copied independently, with sourcefreeze SHA.

Input remains original full20k model32264 d05c, 19,043,064bytes. Do not restore a
CPU-migrated candidate as if it had original startup identity. Actual runtime:
complete donor -> five approved ABI metadata paths -> all12 original fullstate
CPU/CUDA startup markers and episode+1 -> actual20k API offsets/default_q exact
-> once-only offset-aware left initializer -> own CUDA actor/Adam disk roundtrip
->120controls0PPO physical probe and complete107 own saved checkpoint. Formal
3600s uses this actual own probe checkpoint and all12 same-repaired markers;
it does not repeat the initializer or clear Adam moments again.

Stages are distinct fresh attempts and leases: sdk (10G4,300controls1200callback,
selected reset), native (20k,24warm+120timed,576callbacks), fullrestore (20k,
120controls480callbacks0PPO), train (20k,target3600s inclusive of load/save/exit).
Each stage uses run_windows4090_stage_once.py. The parent requires actual prior
stage EXIT+PASSED receipts before fullrestore and formal; a CPU proof cannot fill
a GPU-stage receipt. Each2actual updates are saved atomically with r+b fsync.
15s guardian and STOP_AFTER_SAVE request own save/natural exit without kill.

For SSH-independent lifetime, prepare a unique demand-only ScheduledTask with
register_windows4090_demand_task_once.ps1. Registration has no GPU start unless
-StartApprovedLease is explicitly passed by root after exact lease approval.
The task has0triggers/no boot/no periodic restart, Win10 interactive logon and no
stored credential; user must be logged in. Its hidden PowerShell wrapper runs
the Python parent as a Task Scheduler descendant, independently of SSH. No old
task or running process is changed. A consumed attempt/task is never replayed.

Manifest required fields (root must supply actual absolute paths and hashes):

- approved_for_new_Windows4090_scope, num_envs=20000, seed=20260928
- source: path,sha256 of the exact coherent donor or own probe fullsave
- source_environment: all original run_manifest RM variables (USD path overridden
  only to the same byteSHA new runtime asset).
- sourcefreeze_files: every consumed runtime/payload/ABI/asset path and SHA
- approved_ABI_metadata_bindings: exact old/new/ABI_code_or_derived_hash_only for
  five paths: terrain+entry fullpose a281...->c90d..., terrain+entry input
  dc4e...->21d3..., route parentBoundary5704...->b3a0.... All other metadata and99
  perenv tensors are strict unchanged. Original20k entry_runtime57c7... exact.
- admitted_leg_offsets=[0,0,0,0]: conditional savedraw CPU fixture. Actual new20k
  legs._offset and actual default_q must match allenv before initializer; there
  is no assumption that default/reset pose equals action offset.
- admitted_Windows20k_GPU_buffer_capacities: actual reviewed newSDK defaults.
  Original task has no gpu_* overrides; no Linux-default numerical equivalence
  is claimed. New Windows native must pass before PPO. Expected b054 SDK0.54.4
  default contact2**23,patch5*2**15,foundlost2**21,aggregatefoundlost2**25,
  totalaggregate2**21,collision_stack/heap2**26,temp_buffer2**24,partitions8,
  soft_body_contacts/particle_contacts2**20, but actual cfg receipt is decisive.
  Materializer derives all11 actual values from the verified SDK source AST;
  the GPU worker compares all11 actual constructed cfg values to that record.
- resource_guards: durable_free_bytes,RAM_available_bytes,GPU_free_bytes from
  approved genuine20k resource planning; never lower guards or delete evidence.
- original005_budget_reference: authorized_seconds1188000,base_seconds36000,
  seven actual extension_seconds summing1152000,remaining_snapshot_seconds,
  pending_unique_actual_parent_cost_seconds,canonical_reconciliation_pending=true,
  new_budget_authority=false. Use actual saved original reference, not invented
  extension values. Otherexpert/gate planning protection is checked without
  creating a ledger reservation. Parent load/learn/save/exit is the unique cost;
  worker-before-Kit ended fields are separate and must not be added/recharged.
- required_stage_receipts: fullrestore=>sdk+native, train=>sdk+native+fullrestore.
  Each row kind,path,sha256,owner_EXIT_path,owner_EXIT_sha256. Formal source must
  exactly equal the actual fullrestore receipt latest checkpoint.

Lease requires case_id,environment_root,scope_root,shared_gpu_lock,
approved_GPU_scope=true,mode,attempt_path,
python,runtime_root,manifest_sha256,worker_sha256,source_sha256. Attempts must be
new scope/attempts subdirectories. Wrapper files and all source SHAs belong in
prelaunch freeze. No user credential is written to these manifests or reports.

CPU reports under reports distinguish fulltree/negative/offset fixture from
future GPU and PPO. The original gradient observer's inplace-autograd error is
retained; its independent functional shadow proves equal numerical targets and
synthetic derivative only. It is not real PPO reward or training success.

Own formal checkpoint107/99fields/PID/start/sourcefreeze/12markers/progress/
health/EXIT/OSlock and full traces require independent post-exit review. Do not
call a complete save50mm-qualified or infer unique failure causality. No local
GPU, remote oldmain, independent expert, budget copy or WASD intervention.

Fresh target CPU assembly operations, run only by the root's sole remote owner:

1. After all three immutable packages are extracted with their actual member
   SHAs, run materialize_windows20k_target_cpu_once.py --operation materialize.
   It creates only the independent scope above, copies original20k runtime and
   real asset/contract/bank files, applies the six exact ABI overlays to that new
   copy, and retains original20k entry_runtime. No old immutable or installed
   SDK file is written. This operation has no Torch/Kit/CUDA requirement.
2. Once actual target Torch is installed, run its --operation verify-targetCPU
   with environment/env/python.exe. It validates d05c107/99, actual target
   source paths, all five restricted metadata bindings and negative fixtures,
   all12 restore implementation source bindings, disk CPU roundtrip and source
   geometry/DR/RNG exactness. It does not run any GPU startup marker and does
   not certify runtime API offsets/physics. A CPU fixture is not a GPU donor.
3. prepare_windows20k_sdk_manifest_cpu_once.py emits only an ungranted SDK10
   manifest and lease. Without genuine original005 saved-reference, all unique
   actual parent pendingcosts, genuine approved20k guard requirements and actual
   installation-ready receipts, it records missing_inputs. No placeholder
   extension values, resource bytes, future PASSED or fabricated target path
   can enable launch. Root must preserve the draft and independently grant a
   reviewed manifest/lease before a ScheduledTask is registered or started.

The builder's root-input JSON selects actual JSON field paths explicitly:
budget_original_saved_reference(path,SHA), budget_schema_paths(authorized,
base,extensions,each_extension_seconds,remaining_snapshot_seconds);
pending_parent_cost_index(path,SHA), pending_cost_schema_paths(rows,unique
segment_identity,already_accounted_original_canonical,no_PPO_cost_excluded,
parent_EXIT_reference,actual_parent_EXIT_seconds,classification);
resource_guard_review(path,SHA), resource_guard_schema_paths(planning_passed,
three byte requirements,values_are_guard_requirements_not_available_snapshots);
installation_ready_receipt(path,SHA), installation_schema_paths(passed).
The actual JSONs remain evidence references, never a second budget authority.
Cost values come only from original parent EXIT tail segments; worker ENDED and
formal-before-Kit fields cannot be substituted or added to those parent costs.
