"""Final controller source fixture and package freeze, no owner or worker launch."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,sys,time
HERE=Path(__file__).resolve().parent;OLD=HERE.parent;T=HERE.parents[2]
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(p,rel=None):return dict(path=str(p),relative=rel,bytes=p.stat().st_size,SHA=H(p))
def main():
 index=HERE/'E0_SINGLE72_V2_LR_FROZEN_INDEX_ACTUAL.json';assert not index.exists()
 source=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/reports/E0_V89C_ACTUAL_REMOTE4090_SOURCE_SDK_CPU_ADMITTED_RETURNED_ACTUAL.json'
 proof=HERE/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json';assert proof.exists() and H(proof)==H(source)
 # Preserve V1 fixture failures; V2_LR fixture uses actual233 extension JSON.
 fixture=(OLD/'test_E0_single72_source_fixture_v3_once.py').read_text('utf8')
 fixture=fixture.replace('T=HERE.parents[1]','T=HERE.parents[2]')
 fixture=fixture.replace('E0_SINGLE72_READY_GO_SPAWN_CHARGE_SOURCE_FIXTURE_ACTUAL_V3.json','E0_SINGLE72_V2_LR_SOURCE_FIXTURE_ACTUAL.json')
 fixture=fixture.replace('E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json','E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json')
 fixture=fixture.replace("bad['closed_source_CPU']['value']['queue_structure_proof'][field]","bad['closed_source_CPU']['value']['base_actual_fullstate_CPU_value']['queue_structure_proof'][field]")
 fp=HERE/'test_E0_single72_V2_LR_source_fixture_path_fixed_once.py';assert not fp.exists();fp.write_bytes(fixture.encode())
 process=subprocess.run([sys.executable,'-X','utf8','-B',str(fp)],capture_output=True,text=True)
 if process.returncode:
  (HERE/'E0_V2_LR_FIXTURE_ORIGINAL_ERROR.json').write_text(json.dumps(dict(returncode=process.returncode,stdout=process.stdout,stderr=process.stderr,no_actual_spawn_or_ledger=True),indent=2),encoding='utf8')
 assert process.returncode==0,(process.stdout,process.stderr)
 print(process.stdout.strip())
 # Existing original accounting and node loops are still byte-for-byte V1.
 exact=['three_slot_common_v1.py','single_writer72_authority_V85M_source.py','E0_single72_finite_owner_authority72_v1.py','E0_single72_finite_node_v1.py','E0_single72_resource_guard_v1.py','E0_single72_detached_launcher_v1.py']
 for name in exact:assert H(HERE/name)==H(OLD/name)
 before=(OLD/'E0_single72_bound_cfg_v1.py').read_bytes();after=(HERE/'E0_single72_bound_cfg_v1.py').read_bytes()
 assert after.replace(b'E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py',b'E0_PPO50_gas400_finite_worker_v1.py')==before
 runtime=exact+['E0_single72_protocol_v1.py','E0_single72_bound_cfg_v1.py','E0_first_metadata_observer_readonly_v1.py','E0_ACTUAL89C_CPU_RETURNED_PROOF.json']
 manifest=dict(key='e0',source_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371',worker_SHA='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19',
  source_CPU_SHA='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e',base_actual_fullstate_CPU_SHA='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c',
  files=[dict(relative=name,bytes=(HERE/name).stat().st_size,SHA=H(HERE/name)) for name in runtime])
 mf=HERE/'E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';assert not mf.exists();mf.write_text(json.dumps(manifest,indent=2),encoding='utf8')
 handoff=HERE/'E0_SINGLE72_V2_LR_FROZEN_HANDOFF.md'
 handoff.write_text('''# E0 one-slot sole72 launch interface, V2_LR

Install the manifest runtime files unchanged into BOTH `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/owner` and sibling `node_e0`. Existing job `e0` and its V3 fixed-v1 file, original fullstate CPU d06 witness, model/runtime/asset remain unchanged. V4 is already installed as a new additive filename. Actual233 source-only migration SHA5509 is the current source_CPU_SHA. The protocol verifies its complete original89C d06 base value plus the exact worker-only LR CLI migration. It never calls another model CPU reader.

Root creates e0/TASK.json with source54f, worker8774, source_CPU5509, original sourceb109/original manifest1db, roleE0/num_envs20000/GPUc27, actual resource/asset admission, canonical original72 path and generation, and a new run_id. No token belongs in TASK. Required worker fields remain as guard_task_go defines. Do not create GO manually.

Bound cfg producer is `E0_single72_bound_cfg_v1.bound_cfgs(request, token)`. Runtime request keys: owner_root, node_root, manifest_SHA (exact package manifestSHA), CPU_returned_proof_SHA (the packaged original89C return proofSHA), run_id. Launcher `E0_single72_detached_launcher_v1.py` reads this public request on stdin and generates the random HMAC token internally. The token remains only in memory and owner/node stdin, never a cfg file/TASK/report/argv/Git. It creates exactly one owner and one real e0 node on same72 loopback, no SSH/tunnel and no second placeholder slot. Owner/node logical wrapper argv and actual loader exe/argv/create/root are saved from their exact own PIDs.

The original charge_values, nested account function, canonical paths, two locks, strict remaining>86412.86069250107, finite mode, historical9 extensions/new[] and3900/3600save/300exit are unchanged. The owner alone writes the original C72. Private GPUc27 lock and brief shared validation lock remain original. The node waits for the actual worker/SDK close before terminal handoff; the owner charges through its terminal receipt once, releases original locks and writes COHORT_FINAL/OWNER_EXIT. No refund, idle fee, rounding, clamp, ledger copy, clear-active or second writer.

First finite read-only metadata: run `E0_first_metadata_observer_readonly_v1.py` once in installed owner or node source directory. It reads only known owner/node/worker JSON and exact owned PID/create records; no PT/GPU/ledger or unknown process lookup. Progress paths are e0/adaptation/SOURCE_FULLRESTORE_ZERO_VERIFIED.json, CLOCK_GAS400_NATIVE24_ACTUAL.json, PPO_POSITIVE_CURRENT.json and latest_complete.json. Existing fullsave remains original. Final paths are e0/adaptation/FINAL.json and APP_CLOSED.json; node_e0/NODE_TERMINAL_ACTUAL.json and NODE_EXIT_ACTUAL.json; owner/COHORT_FINAL.json and OWNER_EXIT_ACTUAL.json. Only original owner and an actual C72 closure read establish settled fee; a worker FINAL alone does not.

This is source preparation and source-only fixture validation, with no actual owner/worker/GO/ledger operation. Original V1 controller/fixtures/errors remain frozen in parent. Current source fixture uses actual5509 JSON, validates ready→GO binding and the actual dispatch functions with a synthetic subprocess spy, tests eight negatives and original fractional sum-once/no-idle accounting in memory. Windows fixture path rendering is not an actual Linux argv receipt. No WM transition tap exists in this frozen worker; adaptation checkpoints are not WM transition datasets. Read-only typed transition collector remains a later separate phase.

All files are now frozen. Root installs and performs actual source reconciliation/launch/first-update/close under its exclusive finite SSH lease. This is ordinary Git supplementation of the existing89 trial, no record/tag again.
''',encoding='utf8')
 for f in HERE.glob('*.py'):ast.parse(f.read_bytes())
 metadata=dict(epoch=time.time(),frozen=True,runtime_manifest=row(mf),CPU_returned_proof_SHA=H(proof),owner_node_common_authority_resource_launcher_bytes_exact_V1=exact,
  bound_cfg_only_dispatch_filename_changed=True,all_files=[row(p,p.name) for p in sorted(HERE.iterdir()) if p.is_file() and p!=index],
  active_actual_GO_or_training=False,no_PT_normalizer_USD_NPZ_read=True,Git_status='ordinary_supplement_existing89trial_no_new_tag')
 index.write_text(json.dumps(metadata,indent=2),encoding='utf8')
 print(json.dumps(dict(index=row(index),manifest=row(mf),CPU_returned_proof_SHA=H(proof),runtime_files=len(runtime),frozen=True)))
if __name__=='__main__':main()
