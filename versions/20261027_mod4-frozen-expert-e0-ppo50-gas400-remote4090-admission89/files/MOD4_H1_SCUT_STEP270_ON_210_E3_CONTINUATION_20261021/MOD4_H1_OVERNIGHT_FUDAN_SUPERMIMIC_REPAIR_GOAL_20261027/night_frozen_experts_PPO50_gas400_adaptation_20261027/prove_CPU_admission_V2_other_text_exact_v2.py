"""Explicit CRLF-aware inverse source proof; retain both earlier reader errors."""
from pathlib import Path
import hashlib,importlib.util,json,time,traceback
HERE=Path(__file__).resolve().parent
def main():
 sp=importlib.util.spec_from_file_location('derive_CPU_V2_text_only',HERE/'derive_E0_CPU_admission_CUDA_structural_V2_source_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 old=(HERE/'E0_target_source_SDK_CPU_admission_v1.py').read_bytes();raw=(HERE/'E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py').read_bytes()
 s=raw.replace(b'\r\n',b'\n').decode();assert s.count(m.HELPER)==1;s=s.replace(m.HELPER,'')
 s=s.replace("queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue_structure_proof=validate_original_CUDA_queue_structure_CPU(queue,ck['physical_action_delay_state'])","queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue.validate_state(ck['physical_action_delay_state'])")
 s=s.replace("report=root/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'","report=root/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json'")
 s=s.replace("queue20ms_fields_CPU_structurally_valid=True,queue_structure_proof=queue_structure_proof,admission_reader_version='V2_CUDA_structural_only',reset_bank_source_CPU=reset","queue20ms_state_CPU_valid=True,reset_bank_source_CPU=reset")
 assert s.encode()==old.replace(b'\r\n',b'\n')
 proof=dict(epoch=time.time(),V1_SHA=hashlib.sha256(old).hexdigest(),V2_SHA=hashlib.sha256(raw).hexdigest(),
  CRLF_pairs_V1=old.count(b'\r\n'),CRLF_pairs_V2=raw.count(b'\r\n'),
  V2_write_text_Windows_line_endings_explicit=True,
  normalized_inverse_remove_helper_restore_call_report_basename_and_scope_fields_reconstructs_entire_V1_text=True,
  other_code_checks_literal_original_after_explicit_line_ending_normalization=True,
  no_claim_all_raw_bytes_unchanged=True,no_model_binary_SDK_or_GPU_read=True,
  preceding_reader_errors=[dict(tool_chunk='0b79a5',kind='PowerShell ParserError before Python execution',
   error="Backslash-quote inside PowerShell python-c command was not shell escaping; ParserError: ',' 后面缺少表达式。",no_python_or_model_execution=True),
   dict(tool_chunk='0cd397',script=str(HERE/'prove_CPU_admission_V2_other_bytes_exact_v1.py'),kind='AssertionError at s.count(m.HELPER)==1',
   cause='V2 Path.write_text translated LF source to CRLF on Windows; the LF helper string was absent as raw substring.',
   old_proof_source_retained=True,actual_model_or_GPU_failure=False)],
  resolution='This standalone source-only proof explicitly normalizes CRLF/LF and preserves actual V2 bytes/SHA. No target admission is repeated.',
  Git_status='pending_root_ordinary_supplement')
 p=HERE/'reports/E0_CPU_ADMISSION_V2_OTHER_TEXT_EXACT_AND_READER_ERRORS_V2.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(normalized_inverse_V1_text_exact=True,V2_SHA=proof['V2_SHA'],V1_CRLF=proof['CRLF_pairs_V1'],V2_CRLF=proof['CRLF_pairs_V2'],no_model_read=True)))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/('reports/CPU_ADMISSION_TEXT_PROOF_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc(),no_model_or_GPU=True),indent=2),encoding='utf8');raise
