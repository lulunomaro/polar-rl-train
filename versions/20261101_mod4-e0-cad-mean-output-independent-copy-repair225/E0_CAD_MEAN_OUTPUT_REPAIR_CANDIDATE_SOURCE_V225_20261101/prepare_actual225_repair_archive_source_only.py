from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
src=T/'E0_ACTION_INPUT_MODE_CLAMP_DIAGNOSTIC_V223_20261101/archive_actual223_inherited_E0_diagnostic_and_frozen_sources_ONCE.py'
s=src.read_text(encoding='utf8')
s=s.replace("ID='mod4-e0-inherited-clamp-input-probe-and-frozen-reference-diagnostic223'", "ID='mod4-e0-cad-mean-output-independent-copy-repair225'")
s=s.replace("scope=read(R/'CAPTURE223_ACTUAL_FROZEN_SCOPE.json')", "scope=read(R/'CAPTURE225_ACTUAL_FROZEN_SCOPE.json')")
begin=s.index("assert read(R/'ROOT223_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json')")
end=s.index("request=read(",begin)
s=s[:begin]+"assert read(R/'ROOT225_ACTUAL_BOUND_COPY_AND_OWN_READBACK_CPU_RETURNED_ACTUAL.json')['passed']\nassert read(T/'E0_CANDIDATE225_CONTROLLED_PHYSICAL_REGRESSION_V230_20261101/reports/ROOT230_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'\n"+s[end:]
s=s.replace('==1505','==1506').replace('1505_old_objects','1506_old_objects').replace('protected1505','protected1506').replace('all1505','all1506').replace('tag_count=1506','tag_count=1507')
s=s.replace('ARCHIVE223_ACTUAL_DIAGNOSTIC_ONCE_CONSUMED_BEFORE_RECORD','ARCHIVE225_ACTUAL_REPAIR_ONCE_CONSUMED_BEFORE_RECORD')
s=s.replace("  for source in sorted(root.rglob('*')):","  for source in sorted(root.rglob('*')):")
s=s.replace(" for source in sorted(root.rglob('*')):"," for source in ([root] if root.is_file() else sorted(root.rglob('*'))):")
s=s.replace('rel=source.relative_to(root);size=',"rel=Path(source.name) if root.is_file() else source.relative_to(root);size=")
s=s.replace("V/root.name/", "V/(root.parent.name if root.is_file() else root.name)/")
s=s.replace('ACTUAL223_DIAGNOSTIC_EXPERIMENT_NOTE.md','ACTUAL225_REPAIR_EXPERIMENT_NOTE.md')
s=s.replace('Diagnose inherited E0 left-crank saturation and retain bounded original RM70 skill case','Create an independently bound E0 action-head repair copy and test original-guard physical regressions')
s=s.replace("'--kind','diagnostic'","'--kind','repair'")
s=s.replace('Actual32-control unchanged E0 input probe; exact installed RSL scalar STD source; two checkpoint CPU comparison; copy-only repair source synthetic only; original bounded W35 skill case; protect all1506 older objects/peels','Actual SDK action closure and optimizer identity; 259-finite-tensor independent copy with same-input mean target equivalence; four bounded physical regression purposes and all original failures; W35 continuation source only unless separately admitted; preserve 1506 old tag objects and peels')
s=s.replace('Existing actual223 phase is consumed','Existing actual225 repair phase is consumed')
ast.parse(s)
p=N/'archive_actual225_independent_copy_and_physical_regressions_ONCE.py'
assert not p.exists();p.write_text(s,encoding='utf8')
print(str(p))
