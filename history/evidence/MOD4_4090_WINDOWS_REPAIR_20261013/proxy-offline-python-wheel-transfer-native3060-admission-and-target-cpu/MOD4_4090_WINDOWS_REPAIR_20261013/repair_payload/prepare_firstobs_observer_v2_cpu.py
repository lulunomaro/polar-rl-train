from pathlib import Path
import json,time,hashlib
D=Path(__file__).parent
source=D/'review_firstobs_logger_detach_contract_cpu.py';text=source.read_text()
old='assert "\'actual_ground_query_error_m\'" in probe'
new="assert 'actual_ground_query_error_m=ground_error' in probe"
assert old in text
text=text.replace(old,new).replace('FIRSTOBS_LOGGER_DETACH_CPU_FINAL_READINESS_ACTUAL.json','FIRSTOBS_LOGGER_DETACH_CPU_V2_FINAL_READINESS_ACTUAL.json').replace('FIRSTOBS_LOGGER_DETACH_ORIGINAL_CPU_ERROR_','FIRSTOBS_LOGGER_DETACH_V2_ORIGINAL_CPU_ERROR_')
target=D/'review_firstobs_logger_detach_contract_cpu_v2.py';assert not target.exists();target.write_text(text)
report=D/'reports/FIRSTOBS_OBSERVER_LITERAL_SCHEMA_AND_SHELL_QUOTE_ERRORS_ACTUAL.json';assert not report.exists()
report.write_text(json.dumps(dict(epoch=time.time(),original_reader=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest()),original_read_error='AssertionError: observer looked for quoted dictionary field while actual source uses keyword actual_ground_query_error_m=ground_error',first_independent_shell_builder_error='Python -c SyntaxError: unexpected EOF while parsing from PowerShell quote forwarding, before target write',subsequent_reader_absent_error='Python cannot open review_firstobs_logger_detach_contract_cpu_v2.py before independent file builder completed',independent_v2=str(target),only_observer_literal_changed_no_production_tolerance_change=True,no_GPU_or_PPO_or_source_checkpoint_write=True,all_original_reader_and_tool_errors_retained=True),indent=2),encoding='utf8')
print(str(target))
