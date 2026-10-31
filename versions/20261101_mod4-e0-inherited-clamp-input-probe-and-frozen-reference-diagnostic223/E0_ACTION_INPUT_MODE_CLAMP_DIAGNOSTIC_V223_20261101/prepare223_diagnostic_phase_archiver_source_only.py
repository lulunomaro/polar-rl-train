"""Build new actual-diagnostic archiver; do not execute it during an SDK finite."""
from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
s=(T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/archive_actual219_PPO_and210_closing_frozen_scope_ONCE.py').read_text('utf8')
s=s.replace("ID='mod4-w35-original-full-rm70-shared-material-400n50-ppo219'","ID='mod4-e0-inherited-clamp-input-probe-and-frozen-reference-diagnostic223'")
s=s.replace('CAPTURE219_ACTUAL_FROZEN_SCOPE.json','CAPTURE223_ACTUAL_FROZEN_SCOPE.json')
start=s.index("first=read(R/'ROOT219V3_W35_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')")
end=s.index("request=read(R/scope['automation_request_file'])",start)
s=s[:start]+"assert read(R/'ROOT223_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json')['passed_execution']\nassert read(T/'E0_FROZEN_REFERENCE_VS_NEW_BRANCH_INPUT_CPU_V224_20261101/reports/ROOT224_FROZEN_E0_VS_NEW_BRANCH_SAME_INPUT_CPU_RETURNED_ACTUAL.json')['passed']\nassert read(T/'W35_FULL_RM70_CLOSED_SKILL_SOURCE_V222_20261101/reports/ROOT222_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'\n"+s[end:]
s=s.replace('1504','1505').replace('tag_count=1505','tag_count=1506')
s=s.replace('ARCHIVE219_ACTUAL_NEW_PPO_ONCE_CONSUMED_BEFORE_RECORD.json','ARCHIVE223_ACTUAL_DIAGNOSTIC_ONCE_CONSUMED_BEFORE_RECORD.json')
s=s.replace('ACTUAL219_EXPERIMENT_NOTE_WITH_CLOSED210.md','ACTUAL223_DIAGNOSTIC_EXPERIMENT_NOTE.md')
s=s.replace('Start W35 full original RM70 PPO219 after shared-material repair and preserve complete E0 three-hour closure','Diagnose inherited E0 left-crank saturation and retain bounded original RM70 skill case')
s=s.replace("'--kind','training'","'--kind','diagnostic'")
s=s.replace('Actual20k full W35 restore/native24/firstnewPPO; original pre-GO role failure and fixes retained; E0275updates/132M transitions/wholeCPU passed; protect all1505 older tag objects/peels','Actual32-control unchanged E0 input probe; exact installed RSL scalar STD source; two checkpoint CPU comparison; copy-only repair source synthetic only; original bounded W35 skill case; protect all1505 older objects/peels')
s=s.replace('Existing actual219 phase is consumed','Existing actual223 phase is consumed')
s=s.replace('all_pre_GO_false_and_repairs_preserved=True','all_original_source_reader_errors_and_before_use_repairs_preserved=True')
ast.parse(s)
p=N/'archive_actual223_inherited_E0_diagnostic_and_frozen_sources_ONCE.py'
with p.open('x',encoding='utf8')as f:f.write(s)
print('New223 diagnostic archiver prepared only; no Git/model/remote operation.')
