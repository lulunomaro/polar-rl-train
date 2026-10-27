"""Freeze this source-only audit. No imported robot/learner/model code."""
from pathlib import Path
import ast
from datetime import datetime, timezone
import difflib
import hashlib
import json

D=Path(__file__).resolve().parent
def put(name,value):
 with (D/name).open('x',encoding='utf-8',newline='\n') as f:
  if isinstance(value,str):f.write(value)
  else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def H(raw):return hashlib.sha256(raw).hexdigest()

lineage=json.loads((D/'SOURCE_LINEAGE_AND_LINES_ACTUAL.json').read_text(encoding='utf-8'))
audit=json.loads((D/'AST_AND_RATIO_SOURCE_AUDIT_ACTUAL.json').read_text(encoding='utf-8'))
diffs=[]
for stem,names in [('learner',('_imag_step','_wm_rollout','collect','train')),('replay',None)]:
 a=Path(lineage['upstream_'+stem]['path']).read_text(encoding='utf-8-sig')
 b=Path(lineage['actual_'+stem]['path']).read_text(encoding='utf-8-sig')
 if names:
  aa={n.name:ast.get_source_segment(a,n) for n in ast.walk(ast.parse(a)) if isinstance(n,ast.FunctionDef)}
  bb={n.name:ast.get_source_segment(b,n) for n in ast.walk(ast.parse(b)) if isinstance(n,ast.FunctionDef)}
  for name in names:diffs.extend(difflib.unified_diff(aa[name].splitlines(),bb[name].splitlines(),fromfile='pinned/'+name,tofile='actualC/'+name,n=3))
 else:diffs.extend(difflib.unified_diff(a.splitlines(),b.splitlines(),fromfile='pinned/replay.py',tofile='actualC/replay.py',n=3))
put('EXACT_ADAPTER_LOOP_SOURCE_DIFFS_ACTUAL.txt','\n'.join(diffs)+'\n')
put('AUDIT_V1_V2_FAILURE_SUPPLEMENT_ACTUAL.json',dict(
 preserved_original_source_files=['audit_source_only_v1.py','audit_source_only_v2.py'],
 errors=[dict(version='V1',exit_code=1,exception='AssertionError',message="('actual_static', 'class')",
   scope='source evidence anchor lookup',explanation='compact static module is functions/FIELDS, not class; no source/model/runtime validation conclusion was emitted.',
   raw_trace_location='Original tool transcript; this JSON records the exact final exception and source line context, not a reconstructed full raw traceback.'),
  dict(version='V2',exit_code=1,exception='SyntaxError',message='invalid syntax',line=49,
   scope='local audit helper edit',explanation='An incorrect apply_patch removed if isinstance(value,str) before else. V2 file and raw stdout/stderr preserved; V3 derived from original V1 rather than editing failed V2.')],
 repair='V3 changes only missing evidence anchors class->FIELDS= and V2 inherited reward method anchor->objective_terms; original source algorithms untouched.',
 actual_training_failure=False,real_models_opened=False))

def ref(key):
 r=lineage[key];return f"`{r['path']}` — SHA `{r['SHA']}`"
handoff=f'''# Native88C local pinned native-algorithm source audit — FROZEN

This is source + AST + scalar arithmetic evidence only. No model was read, statted, hashed or forwarded; no SDK scene, physics, actor/WM forward, GPU, process inspection, SSH, network, Git, Task or GO was performed. This directory is pending ordinary Git supplementation by root, not a new trial/tag or a training qualification.

## Result

CurrentC does retain native supervised WM learning and imagination BPTT. `wm_update`, `_wm_err`, `_sample_valid_starts`, `_critic_input` and `lr_at` match the pinned local learner AST exactly. `policy_update` matches after only the two `range(7)` state-stack loops are normalized to the upstream `range(6)`. Freezing WM/critic **parameters** leaves the input/action gradient graph intact. Pi loss still backpropagates through H32 WM transitions, future observations, soft reward/survival and terminal critic value. No PPO objective was substituted.

The remaining original-loop differences are fully saved in `EXACT_ADAPTER_LOOP_SOURCE_DIFFS_ACTUAL.txt`: imagined action clip6 to match actual ingress, original pre-action publication hook, State7 stacking, explicit6-action/127-state replay dimensions, and new-window world-only admission predicate. Replay sampling/history/window/masking algorithms were retained. There is no evidence here of detached BPTT or using the raw unclipped Pi proposal as actual replay action.

## Actual work ratio, not iteration labels

| Setting | CurrentC | Pinned Motphys config | Screenshot, conditional same UTD meaning |
|---|---:|---:|---:|
| environments |4096|4096|4096|
| UTD |.4|.4|2|
| mean vector-controls/iteration |2.5|2.5|.5|
| WM batches × batch |10×1024|10×2048|5×8192|
| WM window starts/new physical transition |1|2|20|
| WM loss timepoints/new transition, before terminal mask |8|16|unknown window|
| Pi batch / horizon |1024/32|4096/32|unknown/16|
| imagined policy timepoints/new physical transition |3.2|12.8|unknown|
| precision / compile |FP32 / false|BF16 / true|not verified|
| fresh new-plant world-only iterations |64|500|not verified|

Thus the screenshot does not describe the same training budget: its conditional WM window-start ratio is20× ours; currentC Pi batch is¼ pinned. This is a clear configuration divergence, **not proof that raising UTD or batch would solve the task**. Overlapping window points are not independent data; warmup/world-only work and terminal masks change finite-window totals. Screenshot UTD definition, code identity and wall-clock conditions still need the project link. Our detailed closed-chain400Hz physics, FP32/no compile, and protected periodic fullsave/hash work also differ from a speed-control demo; no timing profile was executed.

The Motphys README explicitly says *independent downstream reproduction*, not original-author official implementation. The saved connector receipt pins `faf7818e8abac3ec6abb8f00e6e904d3577f800b`; do not equate that code to the unlinked screenshot project.31-minute vx/yaw/height control evidence is relevant to native method capability but does not establish dual-wheel270mm stair success.

## Continuation semantics and what is ruled out

All three model/normalizer/Adam states are deliberately retained through the700→nominal400 changed plant and new objective. Replay/history/environment are fresh. GlobalLR phase is retained, but coefficient at h1 global6469 is `{audit['global_LR']['6469']['coefficient']:.10f}` (LR `{audit['global_LR']['6469']['lr']:.12g}`), recovery2677 `{audit['global_LR']['2677']['coefficient']:.10f}`. The near-zero-LR explanation is ruled out by source arithmetic. GroupLR is overwritten with this schedule every iteration, irrespective of restored groupLR.

Old critic and optimizer states can affect the adaptation beginning.64 new world-only iterations update WM, not critic; first newPi uses the old-objective critic bootstrap and only then trains critic. This is an adaptation design risk, not an implementation mismatch with upstream Pi/V update order. No reset is proposed or performed. Analytic Adam old second-moment weights at final new counts are in the JSON and decay strongly; do not claim old moments dominate forever. RunningNorm is exact upstream cumulative pooling, no exponential forgetting; max_count2e8 freezes updates after reaching the cap. The theoretical critic norm cap is around5919 successfulPi updates with H32/Pi1024. Actual norm counts/values were **not** read, so actual cap state is pending.

SourceR5 globals3317/1409 become C6469/2677; fresh C iterations are3152/1268, newWM31520/12680, newPi3088/1204, controls7944/3235 (root's completed metadata). Restored positive counts are not fresh work. Root's actual text reports takeoff203/678 and cross/land/recovery0. Imagined last reward ratios.94796/.93214 are diagnostic imagined returns, not physical success/probability. This audit does not infer a cause from zero success.

## Concrete differences to examine next

1. **Imagined state manifold.** Current WM independently predicts30q,30dq and aux54 residuals. Aux includes contact18, applied torque30 and processed applied target6; staticxi31 holds real episode-fixed DR. Exact four-substep queue helper exists but is not called in active WM. No closed-chain projection, explicit joint-limit cost or constraint termination is imposed on imagined states; pinned G1 MDP has a joint-limit cost. Real queue/limits/reset/hard callbacks are unchanged. Test actual same-state real-vs-predicted wheel geometry, closure, q-limits, action saturation and contact before deciding whether learned off-manifold shortcuts occur. No new physical graduation threshold is added.
2. **Phase/reset distribution.** Pinned manager adapts reference-phase starts and initializes from reference state; current MOD4 must start on real flat bank, age0, request100..179. Current all-valid imagination includes held goal after300 and starts near real timeout500; imagined soft termination models only height/tilt. These are meaningful task-adapter differences. Inspect existing phase coverage and survival/timeout mismatch before changing replay/reset semantics; do not spawn an airborne reference pose or fabricate success.
3. **Contact quantity label.** Active task code is signed world-Z `relu(1-force_z)`, not vector magnitude. Its own contract says worldZ, while a precontrol flag names soft_magnitude. That metadata wording is inconsistent. Sign correctness is unproved: compare signedZ/norm/actual support on admitted same-state records. Do not silently replace sign/norm or claim every contact means platform support.
4. **Initial critic / normalization adaptation.** Use existing qualified metadata when possible; any newly authorized checkpoint-purpose inspection must distinguish initial carryover from persistent objective/model mismatch. Consider bounded critic adaptation/config comparison only after evidence, with typed provenance and no automatic state reset.

The smallest next work is the already-planned single frozenC attempt and same-state diagnostic fields, followed by verifying the demo project/config identity. This source audit itself authorizes no execution or training window and makes no convergence claim.

## Evidence and errors

Full24-file source-only SHA/definition-line inventory: `SOURCE_LINEAGE_AND_LINES_ACTUAL.json`. Each finding in `AST_AND_RATIO_SOURCE_AUDIT_ACTUAL.json` has exact path/SHA/line anchors. Principal files:

- {ref('actual_learner')}
- {ref('actual_training')}
- {ref('actual_augmented_WM')}
- {ref('actual_migration')}
- {ref('upstream_learner')}
- {ref('upstream_config')}

V1 source-anchor AssertionError and V2 local SyntaxError are preserved, including both source versions, V2 raw output, failure supplement; V3 completed AST/scalar audit passed. Source-reader output truncations are separately recorded. None was a training/SDK/model failure. Do not rerun the write-once audit as an actual runtime or fixture qualification.

All old frozen/payload/runtime/report directories remain unmodified. Root owns subsequent Git supplementation, actual N1 binding/source/resource/account admission and any execution. No pending helper implementation remains.
'''
put('HANDOFF.md',handoff)
put('FREEZE_STATUS_ACTUAL.json',dict(schema='mod4.source_only.freeze.v1',frozen_UTC=datetime.now(timezone.utc).isoformat(),
 completed=True,scope='local pinned native learner/source/config audit',runtime_or_model_qualification=False,
 archived_to_Git_by_helper=False,ordinary_Git_supplementation='PENDING_ROOT',
 previous_errors_retained=True,old_directories_modified=False,pending_actual_work='Root-owned freshN1 admission and demo project identity, not helper source completion.'))
rows=[]
for p in sorted(D.iterdir(),key=lambda p:p.name):
 if p.is_file() and p.name!='INDEX.json':
  raw=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
put('INDEX.json',dict(schema='mod4.complete_source_artifact_index.v1',files=rows,
 self_excluded='INDEX.json',external_model_or_raw_files_read=False))
print(json.dumps(dict(frozen=True,directory=str(D),files=len(rows),INDEX_SHA=H((D/'INDEX.json').read_bytes()),HANDOFF_SHA=H((D/'HANDOFF.md').read_bytes())),ensure_ascii=False))
