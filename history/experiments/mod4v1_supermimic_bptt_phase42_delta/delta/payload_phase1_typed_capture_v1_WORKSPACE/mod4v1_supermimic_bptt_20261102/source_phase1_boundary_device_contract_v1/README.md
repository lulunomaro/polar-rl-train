# Boundary device contract V1 — SOURCE fixture, not native root-cause proof

Catalog: Office/ACL skills do not match this RL source task. Filesystem and Python3.14 -B stdlib only are used here. This child reads no actual V3 reports and executes no Torch/SDK/SSH/native/GPU/model/resource/canonical/lock operations. The parent's V3 failure description is historical evidence supplied by the parent, not newly observed flags.

## Exact source candidate

Complete fixed canonical: 37927 bytes, SHA256 `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e`.

- OriginalEpisodeBoundary.__init__(self, torch_module, device, n=80) stores `device` unchanged.
- OriginalEpisodeBoundary.after_original_step(self, terminated, truncated) requires each tensor shape `(80,)`, bool dtype, and `value.device == self.device` before assigning `(terminated | truncated).clone()`.
- Complete original bridge 13125/`8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29` already stores `self.device=torch.device(env.device)` and returns separate `term.bool()` / `trunc.bool()`.
- Frozen V3 worker constructs `OriginalEpisodeBoundary(torch,env.device,n=80)`.
- Proposed V4 changes only that argument to **the existing `bridge.device`**. No new SDK getter, conversion of flags, boundary-class change, predicate relaxation, physical parameter, loop, deadline, resource, close or policy change.

Real `env.device` type and actual V3 term/trunc shape/dtype/device were not published. Status is **SOURCE_CANDIDATE_NOT_ACTUAL_V3_ROOT_CAUSE_CONFIRMED**. A successful synthetic fixture proves the explicit synthetic str/device case, not the actual cause of the V3 native failure.

## Parent-run CPU fixture (not executed by this child)

Transfer the two complete neighboring Python files [boundary_device_contract.py](<boundary_device_contract.py>) and [torch_cpu_fixture.py](<torch_cpu_fixture.py>). Supply the COMPLETE canonical Python source already materialized in the original V3 root. No AST extraction or stub replacement is used.

```sh
python -B torch_cpu_fixture.py --canonical-source /FULL/PINNED/CANONICAL37927.py --output /OWN/NEW_BOUNDARY_DEVICE_CPU_RECEIPT.json
```

The CLI verifies the full canonical pin BEFORE importing Torch; SOURCE import/tests never invoke the CLI. `--output` uses exclusive creation, or omit it for stdout JSON. The parent chooses its own CPU environment and receipt path; this package is not a dispatcher.

The function `run_torch_cpu_fixture(torch_module,canonical_source=None)` runs CPU-only synthetic N80 bool flags. It checks: old `'cpu'` boundary rejects with original error; normalized `torch.device('cpu')` passes; first/all-fresh and previous true term|trunc masks; two actions→two supplied synthetic step calls; both original flag objects and values unchanged; shape79/80x1, float/int, wrong step order and N79 negatives; Torch global CPU RNG and Python global RNG unchanged. The supplied step counter is explicitly synthetic and is not an environment/SDK observation. The full original canonical module/class and strict predicate are used.

## SOURCE-only seal

The local stdlib suite verifies all13 frozen V3 members/root, complete canonical/bridge source pins and API, actual full canonical metadata import, fixture source/CLI shape and scope. It does NOT execute Torch or assert a real CPU result. The [SOURCE_RECEIPT.json](<SOURCE_RECEIPT.json>) and [SOURCE_SEAL.json](<SOURCE_SEAL.json>) record this distinction. All original sealed packages remain unchanged. Gate1 UNKNOWN, capture/exact/stage2 false.
