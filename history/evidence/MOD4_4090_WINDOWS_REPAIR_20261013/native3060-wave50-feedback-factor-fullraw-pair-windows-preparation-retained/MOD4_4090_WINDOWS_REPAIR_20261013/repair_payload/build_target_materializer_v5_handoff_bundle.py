"""Package CPU-prepared executables and genuine read-only references only."""
from pathlib import Path
import json,time,zipfile
from materialize_windows20k_target_cpu_once import EXECUTABLES,ref,H,fresh_json

P=Path(__file__).resolve().parent

def main():
 passed=P/'reports/TARGET_MATERIALIZER_SOURCE_CPU_V5_FINAL_BOUND_SOURCE_REVIEW.json'
 review=json.loads(passed.read_bytes());assert review['passed'] and not review['actual_remote_target_CPU_passed']
 for row in review['prepared_sources']:assert H(row['path'])==row['sha256'],'core code changed after final CPU review'
 files=[P/n for n in EXECUTABLES]
 files.extend(sorted((P/'admission_reference_data').glob('*.json')))
 reports=['TARGET_MATERIALIZER_SOURCE_CPU_V3_ACTUAL_REVIEW.json','TARGET_MATERIALIZER_SOURCE_CPU_V4_ACTUAL_REFERENCES_REVIEW.json','TARGET_MATERIALIZER_SOURCE_CPU_V5_FINAL_BOUND_SOURCE_REVIEW.json','ACTUAL_BUDGET_COST_REFERENCE_DATA_CPU_PREPARED.json','MATERIALIZER_PREWRITE_OBSERVER_ERRORS_RETAINED.json','FIRSTOBS_LOGGER_DETACH_CPU_V2_FINAL_READINESS_ACTUAL.json','OFFSET_AWARE_V3_FULL20K_CPU_ACTUAL_REVIEW.json','OFFSET_AWARE_V3_EFFECTIVE_GRADIENT_FUNCTIONAL_CPU_V2_ACTUAL.json']
 files.extend(P/'reports'/n for n in reports)
 files.extend(P/n for n in ['review_target_materializer_source_cpu_v3.py','review_target_materializer_source_cpu_v4_actual_references.py','review_target_materializer_source_cpu_v5_final_bound_source.py','prepare_actual_saved_reference_data_cpu_once.py','build_target_materializer_v5_handoff_bundle.py'])
 z=P/'WINDOWS4090_TARGET_MATERIALIZER_V5_CPU_PREPARED.zip';assert not z.exists()
 rows=[dict(source=ref(p),archive='repair_payload_materializer_v5/'+p.relative_to(P).as_posix()) for p in files]
 manifest=dict(epoch=time.time(),file_rows=rows,actual_remote_environment_root='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013',target_scope_subdirectory='training_scope_full20k_left_repair_20261013',input_three_packages_already_actual_uploaded_but_extraction_and_install_ready_pending_owner_actual=True,CPU_source_fixture_passed_only=True,actual_target_CPU_SDK_native_CUDA_PPO_not_run=True,SDK_manifest_lease_prepared_only_not_granted=True,global_environment_native_GPU_lock_required=True,all_new_reports_Git_ordinary_supplement_pending_root=True,no_SSH_GPU_Task_start_canonicalwrite_or_oldsource_change=True)
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  for row,p in zip(rows,files):archive.write(p,row['archive'])
  archive.writestr('TARGET_MATERIALIZER_V5_BUNDLE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 fresh_json(P/'reports/TARGET_MATERIALIZER_V5_EXECUTABLE_HANDOFF_ACTUAL.json',dict(epoch=time.time(),passed=True,ZIP=ref(z),manifest=manifest,old34304byte_package_retained_unmodified=True,no_GPU_or_remote_target_CPU_pass_claim=True,Git_ordinary_supplement_pending_root=True))
 print(json.dumps(ref(z)))
if __name__=='__main__':main()
