"""Finish only package/receipt after V2 compiled retained failed V1 source by mistake."""
from pathlib import Path
import ast,json,hashlib,time,zipfile
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'payload';OLD=W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014';B=W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=R/'BODYFRAME_FIRST_RETENTION_CPU_PREPARED_ACTUAL.json';z=D/'BODYFRAME_FIRST_RETENTION_V8_SOURCE_PAYLOAD_CPU_PREPARED.zip';assert not out.exists() and not z.exists()
 assert list(R.glob('PREPARATION_ORIGINAL_ERROR_*.json'))
 m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes());row=m['sources']['bodyframe_first_f516'];assert row['sha256']=='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139' and row['bytes']==19894311
 source=Q/'source/model_32830_bodyframe_first.pt';assert H(source)==row['sha256'] and source.stat().st_size==row['bytes']
 active=['transport_249_own_f516_retention.py','dispatch_new_bodyframe_retention_case_actual.py','collect_bodyframe_retention_actual_boundary.py','run_bodyframe_retention_fixed_three_candidate_batch_once.py','upload_bodyframe_retention_source_namespace_CPU_once.py','review_bodyframe_retention_full_actual_CPU.py','aggregate_bodyframe_retention_complete_actual_CPU.py']
 for name in active:compile((D/name).read_text(encoding='utf8'),str(D/name),'exec')
 for item in m['package_files_v8']:
  p=Q/item['relative'];assert H(p)==item['sha256'] and p.stat().st_size==item['bytes']
  if p.suffix=='.py':compile(p.read_text(encoding='utf8'),str(p),'exec')
 for p in (Q/'cpu_contracts').rglob('*.py'):compile(p.read_text(encoding='utf8'),str(p),'exec')
 assert ast.dump(ast.parse((Q/'retention_worker_v8.py').read_text().replace(D.name,OLD.name)),include_attributes=False)==ast.dump(ast.parse((OLD/'payload/retention_worker_v8.py').read_text()),include_attributes=False)
 for kind in ('flat','spin','world'):
  inp=json.loads((R/(kind+'_BASELINE_AND_REUSED_NATIVE_INPUTS_CPU_PREPARED.json')).read_bytes());assert inp['new_checkpoint_SHA']==row['sha256'] and inp['baseline_checkpoint_SHA']=='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
  for key in ('native_proof','baseline_boundary','baseline_collection','baseline_full_review'):assert H(inp[key])==inp[key+'_SHA']
  for name in (f'retention_{kind}_native_v8.py','retention_native_witness_v8.py','retention_plane_reference_v8.py','retention_parent_v8.py'):assert (Q/name).read_bytes()==(OLD/'payload'/name).read_bytes()
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
  for item in m['package_files_v8']:f.write(Q/item['relative'],item['relative'])
  f.write(Q/'RETENTION_CPU_MANIFEST_V8.json','RETENTION_CPU_MANIFEST_V8.json');f.write(source,'source/model_32830_bodyframe_first.pt')
 final=B/'reports/BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json'
 value=dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,original_physics_witness_three_main_bytes_exact=True,worker_only_namespace_AST_exact=True,reused_native120_all_three_actual_data_pass=True,source_complete_file_SHA=row['sha256'],source_bytes=row['bytes'],final_closeout_report=str(final),final_closeout_SHA=H(final),previous_e3_full_three_review_SHA=H(OLD/'reports/SECOND_E3_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json'),package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),newsource_or_case_results_pending=True,no_PPO_budgetwrite_or_qualification=True,Git_pending_root_stage_archive=True,CPU_preparation_V2_except_final_compile_completed_not_repeated=True,retained_V1_invalid_source_not_an_active_runtime=True,original_V2_wrong_compile_scope_error_preserved=True)
 out.write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(dict(prepared=str(out),package=value['package'],no_SSH_GPU=True)))
if __name__=='__main__':main()
