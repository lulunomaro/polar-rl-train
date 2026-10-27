"""Exact unused alternate host after zero-App c27 resource rejection."""
from pathlib import Path
import hashlib,json,time,shutil
S=Path(__file__).resolve().parent;T=S.parent
O=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R2_20261027'
def main():
 assert not O.exists()
 boundary=json.loads((S/'reports/PREAPP_BOUNDARY_AND_OTHER_CARD_RETURNED_ACTUAL.json').read_bytes());a=boundary['rows'];assert boundary['actual_finite_transport_returned']
 assert not a['target72']['eval_root_exists'] and a['target72']['selected_compute_UUID_rows']>0
 assert a['source210']['selected_compute_UUID_rows']==0 and a['source210']['memory_free_MiB']>15669 and 'EF3105C85DD986BD' in a['source210']['original_mount'] and 'rw,' in a['source210']['original_mount']
 q=json.loads((S/'BINDING.json').read_bytes());collection=json.loads(Path(q['evidence_pins']['collection'].get('path',T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/reports/NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json')).read_bytes())
 root='/mnt/mod4_linux_durable_20261013/H1native88C_gas400_fixed_single_diagnostic_source210r2_20261027'
 q.update(eval_root=root,runtime_root=root+'/runtime',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',execution_backend='source210',selected_GPU_original_locks=[r['path'] for r in collection['nodes']['h1']['locks']],external72_guard_parent_keeps_live_stdin_and_requires_waited_exit_proof=True)
 q['external72_readonly_guard']=dict(eval_relative='evidence/actual72_readonly_guard_ready.json',SHA='PENDING_ACTUAL_LIVE72_GUARD')
 O.mkdir();(O/'reports').mkdir();(O/'code').mkdir()
 for p in (S/'code').glob('*.py'):shutil.copy2(p,O/'code'/p.name)
 with (O/'PLANNED_BINDING_NEEDS_ACTUAL72_LIVE_GUARD.json').open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
 index=json.loads((S/'INPUT_TRANSFER_INDEX.json').read_bytes())
 with (O/'STATIC_SOURCE_INPUT_INDEX.json').open('x',encoding='utf8') as f:json.dump(index,f,indent=2)
 with (O/'reports/ALTERNATE_CARD_SOURCE_TEMPLATE_NOT_EXECUTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_c27_pre_App_rejection_preserved=True,no_original_remote_root_model_upload_or_actor=True,fresh_source210_snapshot=a['source210'],same_one_case_seed_no_actual_retry=True,new_source210_runtime_and_live_original72_readonly_guard_required=True,no_canonical_copy_or_new_writer=True),f,indent=2)
 print(str(O))
if __name__=='__main__':main()
