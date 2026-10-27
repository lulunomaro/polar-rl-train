"""One actual240 metadata fixture then freeze, never load a model or run owner."""
from pathlib import Path
import ast,hashlib,json,runpy,shutil,time
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
OLD=L/'E0_PPO50_gas400_single72_controller_source_preparation_v1/V2_LR'
EXTENSION='a51a28b52c6c3a5ab01bbb346db48de78730c77274dc59655ec4b2275986f80a'
COST_SHA='e90bda2d34777c60661880f9aa390bd6974437e21a4a9adfade71b933d096ef1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(p,rel=None):return dict(path=str(p),relative=rel,bytes=p.stat().st_size,SHA=H(p))
def main():
 index=HERE/'E0_89D_V5_SINGLE72_FROZEN_INDEX_ACTUAL.json';assert not index.exists()
 actual=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json';assert H(actual)==EXTENSION
 cost=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/reports/E0_89C_ORIGINAL_LOGGER_FAILURE_SETTLED_FEE_ALLOUT_V3_RETURNED_ACTUAL.json';assert H(cost)==COST_SHA
 installed_cost=HERE/'E0_89C_RESOURCE_COST_SETTLED_ACTUAL.json';assert not installed_cost.exists();shutil.copy2(cost,installed_cost)
 source=(OLD/'test_E0_V2LR_actual_extension_contract_once.py').read_text('utf8')
 source=source.replace('T=HERE.parents[2]','T=HERE.parents[1]\nEXTENSION_SHA=\''+EXTENSION+'\'')
 source=source.replace('E0_V2LR_ACTUAL_EXTENSION_READY_GO_DISPATCH_COST_CPU_PASSED.json','E0_89D_V5_ACTUAL240_READY_GO_DISPATCH_COST_CPU_PASSED.json')
 source=source.replace('MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/reports/E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json','MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json')
 source=source.replace('H(extension)==p.CPU==p.digest(value)','H(extension)==EXTENSION_SHA==p.digest(value)').replace('SHA=p.CPU','SHA=EXTENSION_SHA')
 source=source.replace("CPU_returned_proof_SHA='b'*64,run_id=","CPU_returned_proof_SHA='b'*64,source_CPU_SHA=EXTENSION_SHA,run_id=")
 source=source.replace('exact_single_CLI_literal_change','exact_existing_writer_assignment_move').replace('E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py','E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py')
 fixture=HERE/'test_89D_V5_actual240_contract_once.py';assert not fixture.exists();fixture.write_bytes(source.encode());ast.parse(source)
 runpy.run_path(str(fixture),run_name='__main__')
 passed=HERE/'E0_89D_V5_ACTUAL240_READY_GO_DISPATCH_COST_CPU_PASSED.json';assert json.loads(passed.read_bytes())['passed']
 exact=['three_slot_common_v1.py','single_writer72_authority_V85M_source.py','E0_single72_finite_owner_authority72_v1.py','E0_single72_finite_node_v1.py','E0_single72_resource_guard_v1.py','E0_single72_detached_launcher_v1.py','E0_first_metadata_observer_readonly_v1.py','E0_ACTUAL89C_CPU_RETURNED_PROOF.json']
 for name in exact:assert H(HERE/name)==H(OLD/name)
 runtime=exact+['E0_single72_protocol_v1.py','E0_single72_bound_cfg_v1.py','E0_89C_RESOURCE_COST_SETTLED_ACTUAL.json']
 manifest=dict(key='e0',source_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371',worker_SHA='ec8eba0365f0129b2799ef4e1ae7f3673beb585f87d4e25d2c36cf7bdb33b08c',
  source_CPU_SHA=EXTENSION,base_actual_fullstate_CPU_SHA='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c',
  base_V4_worker_only_LR_source_migration_SHA='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e',
  failed89C_original_ending_SHA=COST_SHA,files=[dict(relative=name,bytes=(HERE/name).stat().st_size,SHA=H(HERE/name)) for name in runtime])
 mf=HERE/'E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';assert not mf.exists();mf.write_text(json.dumps(manifest,indent=2),encoding='utf8')
 proof=HERE/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json'
 handoff=HERE/'E0_89D_V5_FROZEN_LAUNCH_HANDOFF.md'
 handoff.write_text('''# E0 V5 new89D source package, one original72 writer

Install all11 manifest files plus E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json unchanged into BOTH new89D sibling owner and node_e0 directories. JOB is exactly /home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0. Existing89C failed job/controller/GO remain untouched. New job retains original typed54f model, not any failed89C partial checkpoint. V5 worker filename E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py has SHAec8eba0365f0129b2799ef4e1ae7f3673beb585f87d4e25d2c36cf7bdb33b08c.

Actual240 V5 source-only extension filename E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json has SHAa51a28b52c6c3a5ab01bbb346db48de78730c77274dc59655ec4b2275986f80a. It contains unchanged base actual89C fullstateCPU d06 and actualV4 LR-source migration5509. New89D copy/runtime/model verification and V5 publisher passed;240 did not reload PT/SDK/GPU. Original239 nested-newline metadata SyntaxError is retained by root and is not a model failure. Protocol validates all base values and their existing hashes, the exact writer-assignment move, and actual failed89C ending proof e90b. That failure is resource/cost only:397.61036682128906s fully charged, closing remaining561777.961785078 snapshot; no refund or new model source. Fresh worker CUDA restore/native24/first PPO are still required.

Root creates a fresh89D TASK: roleE0, source54f/originalb109/original manifest1db, worker ec8e, source_CPU a51, num_envs20000/GPUc27, new run_id, original72 authority generation/canonical and actual resource/asset guard fields. No token in TASK and no manual GO. The public launcher stdin request fields are owner_root, node_root, manifest_SHA, CPU_returned_proof_SHA, source_CPU_SHA=a51a28b52c6c3a5ab01bbb346db48de78730c77274dc59655ec4b2275986f80a, run_id. Bound cfg producer is E0_single72_bound_cfg_v1.bound_cfgs. Launcher E0_single72_detached_launcher_v1.py generates the HMAC token internally; memory/stdin only, never cfg/TASK/report/argv/Git.

Owner/common/node/authority/resource/launcher/observer are exact bytes of the prior frozen source. Only newJOB, V5 dispatch and typed source-only extension/cost-evidence bindings change in protocol/config. Original charge_values/account/locks/strictreserve3900/3600save/300exit remain untouched. Exactly one E0 slot, no placeholder second expert, second writer, ledger copy, refund, rounding, clamp, idle fee or clear-active. Root must use fresh newlaunch once; prior89C startup/GO/once are consumed and cannot be replayed.

First metadata observer and finite close interfaces are unchanged and now resolve89D through protocol JOB: adaptation/SOURCE_FULLRESTORE_ZERO_VERIFIED.json, CLOCK_GAS400_NATIVE24_ACTUAL.json, PPO_POSITIVE_CURRENT.json/latest_complete.json; then FINAL.json/APP_CLOSED.json, node_e0/NODE_TERMINAL_ACTUAL.json/NODE_EXIT_ACTUAL.json and owner/COHORT_FINAL.json/OWNER_EXIT_ACTUAL.json. Only original owner and actualC72 closure establish settled fees.

One source fixture used actual240 JSON, validated READY→GO and the actual dispatch function with a synthetic Popen spy, eight negatives, and original fractional sum-once accounting in memory. No process/SDK/GPU/PT/ledger was used. No WM transition collection is claimed. This stage concerns E0 basic standing/walking adaptation only; H1 curriculum/GPU work remains root-owned. All files now frozen; ordinary Git supplement of existing89 trial, no new record/tag.
''',encoding='utf8')
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
 data=dict(epoch=time.time(),frozen=True,runtime_file_count=len(runtime),runtime_manifest=row(mf),CPU_returned_proof_SHA=H(proof),
  current_source_CPU_SHA=EXTENSION,failed89C_original_ending_SHA=COST_SHA,unchanged_original_controller_files=exact,
  all_files=[row(p,p.name) for p in sorted(HERE.iterdir()) if p.is_file() and p!=index],
  no_actual_launch_GPU_PT_or_ledger=True,Git_status='ordinary_supplement_existing89trial_no_new_tag')
 index.write_text(json.dumps(data,indent=2),encoding='utf8')
 print(json.dumps(dict(index=row(index),manifest=row(mf),runtime_files=len(runtime),source_CPU_SHA=EXTENSION,CPU_returned_proof_SHA=H(proof),frozen=True)))
if __name__=='__main__':main()
