# Export and report repairs

The CPU export completed, including 350 synthetic observation rows and independent
whole-action route comparisons. Its report constructor then raised
`TypeError: dict() got multiple values for keyword argument 'output'`, because the
metadata already has an output contract. ONNX and adjacent metadata had already been
written. The graph was reused, not exported again. Report construction now uses
`onnx_path` and the original error is retained.

The original error handler wrote to one filename; this second traceback replaced
the earlier missing-tensordict traceback file. The missing-dependency traceback is
retained in the chat's first export tool result; the local report overwrite is a
recording defect, not a claim that the original file bytes were preserved. Later error
reports use distinct timestamps.

The actual player rejected the first graph's symbolic second output dimension
`Clipaction_dim_1`. The graph always produced (batch,6); the legacy exporter did not
declare that dimension. The initial graph and adjacent JSON were preserved, and an
independent once helper changed only the fixed output shape declaration to six. It
verified node and initializer bytes unchanged and actual batches 1/2/7 before doing so.
The original reader failure, original graph size/SHA and corrected size/SHA are retained.

Initial runtime check: 700 actual MuJoCo observation rows, max Torch-to-ONNX clipped
action error 9.059906005859375e-06, zero key conflicts, finite normal/jump/recovery and
two spin scenarios. Adding the initial paused jump command queue required another
runtime check: 1000 rows, max error 8.58306884765625e-06. The first successful runtime
JSON was replaced by the second by the original verifier filename; its complete tool
output remains in this chat, and this note preserves the original result separately.
Subsequent verifier report filenames are timestamped. No old false was turned into pass.

The final local test has six scenarios, including jumping directly from the initial
paused state. Mode4 is published for exactly 80 controls after 100 normal controls;
the user can always cancel with X or N. This is a local operator command sequence,
not a training change, a success detector or a new learned gate. All max errors here
refer to deployment clipped outputs, not original GPU raw-mean qualification.

Only the workspace local player venv was supplemented with tensordict 0.15.1,
orjson 3.13.0 and pyvers 0.2.3. The production Python/SDK environments were untouched.
