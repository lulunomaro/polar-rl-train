"""Freeze the already-passed source package; no fixture or model rerun."""
from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent;OLD=HERE.parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(p,relative=None):return dict(path=str(p),relative=relative,bytes=p.stat().st_size,SHA=H(p))
def main():
 index=HERE/'E0_SINGLE72_V2_LR_FROZEN_INDEX_ACTUAL.json';assert not index.exists()
 passed=HERE/'E0_V2LR_ACTUAL_EXTENSION_READY_GO_DISPATCH_COST_CPU_PASSED.json';assert json.loads(passed.read_bytes())['passed']
 exact=['three_slot_common_v1.py','single_writer72_authority_V85M_source.py','E0_single72_finite_owner_authority72_v1.py','E0_single72_finite_node_v1.py','E0_single72_resource_guard_v1.py','E0_single72_detached_launcher_v1.py']
 for name in exact:assert H(HERE/name)==H(OLD/name)
 before=(OLD/'E0_single72_bound_cfg_v1.py').read_bytes();after=(HERE/'E0_single72_bound_cfg_v1.py').read_bytes()
 assert after.replace(b'E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py',b'E0_PPO50_gas400_finite_worker_v1.py')==before
 runtime=exact+['E0_single72_protocol_v1.py','E0_single72_bound_cfg_v1.py','E0_first_metadata_observer_readonly_v1.py','E0_ACTUAL89C_CPU_RETURNED_PROOF.json']
 manifest=dict(key='e0',source_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371',worker_SHA='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19',
  source_CPU_SHA='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e',base_actual_fullstate_CPU_SHA='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c',
  files=[dict(relative=name,bytes=(HERE/name).stat().st_size,SHA=H(HERE/name)) for name in runtime])
 mf=HERE/'E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';assert not mf.exists();mf.write_text(json.dumps(manifest,indent=2),encoding='utf8')
 proof=HERE/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json'
 handoff=HERE/'E0_SINGLE72_V2_LR_FROZEN_HANDOFF.md'
 handoff.write_text('''# Frozen E0 single-slot sole72 package V2_LR

Install the ten manifest runtime files unchanged into BOTH `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/owner` and sibling `node_e0`. The existing e0 job/model/runtime/asset and V3 fixed-v1 file remain unchanged. New additive V4 worker filename is E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py, SHA87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19. Actual233 worker-only source migration SHA5509 is current source_CPU_SHA; it embeds the complete original89C d06 CPU value unchanged. The protocol verifies both without loading a model again.

Root creates e0/TASK.json with roleE0, run_id, source54f, original sourceb109, original manifest1db, worker8774, source_CPU5509, num_envs20000/GPUc27, actual resource/asset admission, original72 canonical path/generation, and remaining guard_task_go fields. No HMAC token belongs in TASK. Do not create GO manually.

Runtime public request keys are owner_root, node_root, manifest_SHA, CPU_returned_proof_SHA, run_id. The exact bound cfg producer is E0_single72_bound_cfg_v1.bound_cfgs(request, token). Invoke E0_single72_detached_launcher_v1.py through the approved72 wrapper with this public request on stdin. It generates the random HMAC token internally, passes it only in owner/node memory/stdin, and never writes cfg/TASK/report/argv/Git token data. It starts exactly one owner and one real e0 node, same72 loopback, no SSH/tunnel or invented registration. Exact owner/node exe/argv/create/root receipts are saved from only those known PIDs.

Original charge_values, account, canonical paths, two original locks, strict remaining>86412.86069250107, finite mode, historical9/new[] and3900/3600save/300exit remain unchanged. Original privatec27 GPU lock plus brief shared validation lock remain. The worker completes valid saves and SDK close; the node waits its real child before terminal handoff; only the original owner settles through its terminal receipt once and releases locks. No refund, rounding, clamp, idle fee, canonical copy, clear-active or second writer.

First metadata: execute E0_first_metadata_observer_readonly_v1.py once in the installed source directory. It reads predefined JSON and exact owned PID/create records only, with no PT/GPU/ledger/unknown PID access. Progress paths: e0/adaptation/SOURCE_FULLRESTORE_ZERO_VERIFIED.json, CLOCK_GAS400_NATIVE24_ACTUAL.json, PPO_POSITIVE_CURRENT.json, latest_complete.json. Close paths: e0/adaptation/FINAL.json and APP_CLOSED.json; node_e0/NODE_TERMINAL_ACTUAL.json and NODE_EXIT_ACTUAL.json; owner/COHORT_FINAL.json and OWNER_EXIT_ACTUAL.json. Worker FINAL alone is not fee closure; use original owner and actual C72 receipt.

The passed source fixture uses actual5509/baseD06 metadata, READY→GO binding and the actual dispatch function with a synthetic Popen spy. It rejects eight negatives and verifies original fractional12.75s sum-once/repeated-terminal behavior in memory. No owner/node/worker, GPU or ledger ran here. Earlier fixture locator/import/scaffold failures and source remain preserved; these were not robot failures. All current files are frozen. Root performs actual postcopy/source reconciliation and one-owner launch. Ordinary Git supplement of existing89 trial; never record/tag again.

No WM transition tap exists in this worker. PPO checkpoints are not WM transition datasets. Typed read-only transition collection is a later separate phase.
''',encoding='utf8')
 errors=HERE/'E0_V2LR_ALL_SOURCE_FIXTURE_READER_ERRORS_FINAL.json'
 errors.write_text(json.dumps(dict(epoch=time.time(),all_earlier_sources_retained=True,no_actual_spawn_or_model_GPU_or_ledger=True,
  errors=[dict(tool_chunk='bc5892',phase='first V2 fixture',error='Nested local metadata root depth inherited V1; FileNotFound before reading actual extension JSON.'),
   dict(tool_chunks=['3e22c9','a84824'],phase='repair command',error='PowerShell quote ParserError before Python; follow-on repair filename absent.'),
   dict(tool_chunk='3db244',phase='nested runpy fixture',error='PathFinder ModuleNotFound for sibling protocol despite file existing; source fixture harness only.'),
   dict(note='The temporary E0_V2_LR_FIXTURE_ORIGINAL_ERROR.json diagnostic was overwritten by the second failed fixture harness. Both actual error descriptions and tool chunks are retained here with the original failing scripts; this is not represented as preserved original diagnostic bytes.')],
  resolution='Standalone exact-source fixture compiled local modules explicitly, used actual metadata and passed without touching production processes.',
  final_pass_report=str(passed),Git_status='ordinary_supplement_existing89trial'),indent=2),encoding='utf8')
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
 value=dict(epoch=time.time(),frozen=True,runtime_manifest=row(mf),CPU_returned_proof_SHA=H(proof),runtime_file_count=len(runtime),
  unchanged_V1_owner_common_node_authority_resource_launcher=exact,bound_cfg_only_new_worker_basename=True,
  full_files=[row(p,p.name) for p in sorted(HERE.iterdir()) if p.is_file() and p!=index],
  actual_GO_or_worker_or_ledger_ran=False,PT_normalizer_asset_or_NPZ_read=False,Git_status='ordinary_supplement_existing89trial_no_new_tag')
 index.write_text(json.dumps(value,indent=2),encoding='utf8')
 print(json.dumps(dict(index=row(index),manifest=row(mf),CPU_returned_proof_SHA=H(proof),runtime_files=len(runtime),frozen=True)))
if __name__=='__main__':main()
