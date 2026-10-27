"""Inverse source proof only; no model, binary, SDK, GPU or remote access."""
from pathlib import Path
import hashlib,importlib.util,json,time
HERE=Path(__file__).resolve().parent
def main():
 sp=importlib.util.spec_from_file_location('derive_CPU_V2_source_only',HERE/'derive_E0_CPU_admission_CUDA_structural_V2_source_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 old=(HERE/'E0_target_source_SDK_CPU_admission_v1.py').read_bytes();raw=(HERE/'E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py').read_bytes();s=raw.decode()
 assert s.count(m.HELPER)==1;s=s.replace(m.HELPER,'')
 s=s.replace("queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue_structure_proof=validate_original_CUDA_queue_structure_CPU(queue,ck['physical_action_delay_state'])","queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue.validate_state(ck['physical_action_delay_state'])")
 s=s.replace("report=root/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'","report=root/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json'")
 s=s.replace("queue20ms_fields_CPU_structurally_valid=True,queue_structure_proof=queue_structure_proof,admission_reader_version='V2_CUDA_structural_only',reset_bank_source_CPU=reset","queue20ms_state_CPU_valid=True,reset_bank_source_CPU=reset")
 assert s.encode()==old
 proof=dict(epoch=time.time(),V1_SHA=hashlib.sha256(old).hexdigest(),V2_SHA=hashlib.sha256(raw).hexdigest(),
  inverse_remove_helper_restore_call_report_basename_and_truthful_scope_fields_reconstructs_entire_V1_bytes=True,
  all_other_checks_literal_original=True,no_model_binary_SDK_or_GPU_read=True,
  preceding_reader_command_error=dict(tool_chunk='0b79a5',kind='PowerShell ParserError before Python execution',
   error="Quoted python -c source used backslash-quote inside PowerShell; ParserError: ',' 后面缺少表达式。",
   no_source_or_model_or_report_was_read_by_failed_command=True,resolution='Use this exact standalone script instead; no experiment replay.'),
  Git_status='pending_root_ordinary_supplement')
 p=HERE/'reports/E0_CPU_ADMISSION_V2_ALL_OTHER_SOURCE_BYTES_UNCHANGED_PROOF.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
 print('INVERSE_ENTIRE_V1_BYTES_EXACT')
if __name__=='__main__':main()
