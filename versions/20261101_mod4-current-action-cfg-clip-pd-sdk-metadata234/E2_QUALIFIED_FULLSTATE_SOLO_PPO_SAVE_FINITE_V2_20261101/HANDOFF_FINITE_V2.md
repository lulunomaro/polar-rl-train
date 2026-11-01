V1 is preserved. Select this independent V2 worker with
`reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json`; the remote worker filename
remains `worker_e2_original_fullPPO.py`. V1's frozen contract, Task generator
and original sole-owner controls are unchanged. The generator accepts this
INSTALL and binds its actual worker SHA into Task/manifest.

The consumed entry enables runner `check_for_nan=True`, and D0-D7 save
wrappers validate their local state. This does not establish a recursive
finite check of the whole decoded save tree or returned PPO losses in the
new worker's complete-save path. V2 checks tensors and floating/complex
scalar numbers recursively before complete serialization/replace/receipt,
and returned losses before update accounting and FIRST/save.

One independent source CPU purpose passed: new worker AST, one finite
synthetic tree, four nonfinite refusals, and save/loss/readcount ordering.
No Torch, model, asset, telemetry, SDK, network or Git access occurred.
No training/physical/command/reward/STD/optimizer setting changed. Source
b3ae/42822/859300/LR.000225 and the original single cached read/decode remain.
ROOT's new callers must pin this V2 INDEX/INSTALL, not the V1 worker row.
