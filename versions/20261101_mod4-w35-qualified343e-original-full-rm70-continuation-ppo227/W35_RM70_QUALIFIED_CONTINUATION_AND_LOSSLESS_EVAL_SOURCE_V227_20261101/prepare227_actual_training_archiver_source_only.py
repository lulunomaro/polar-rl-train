from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
s=(T/'E0_CAD_MEAN_OUTPUT_REPAIR_CANDIDATE_SOURCE_V225_20261101/archive_actual225_independent_copy_and_physical_regressions_ONCE.py').read_text(encoding='utf8')
s=s.replace("ID='mod4-e0-cad-mean-output-independent-copy-repair225'","ID='mod4-w35-qualified343e-original-full-rm70-continuation-ppo227'")
s=s.replace('CAPTURE225_ACTUAL_FROZEN_SCOPE','CAPTURE227_ACTUAL_FROZEN_SCOPE')
start=s.index("assert read(R/'ROOT225_ACTUAL_BOUND_COPY")
end=s.index('request=read(',start)
s=s[:start]+"D=N/'D_BEFORE_USE_CWD_REPAIR_SOURCE'\nassert read(D/'reports/ROOT227D_W35_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')['passed']\nassert read(D/'reports/ROOT227D_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')['current_owner_matched']\nassert read(D/'reports/ROOT227D_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'\n"+s[end:]
s=s.replace('==1506','==1507').replace('1506_old_objects','1507_old_objects').replace('protected1506','protected1507').replace('all1506','all1507').replace('tag_count=1507','tag_count=1508')
s=s.replace('ARCHIVE225_ACTUAL_REPAIR_ONCE_CONSUMED_BEFORE_RECORD','ARCHIVE227_ACTUAL_PPO_ONCE_CONSUMED_BEFORE_RECORD')
s=s.replace('ACTUAL225_REPAIR_EXPERIMENT_NOTE','ACTUAL227_CONTINUATION_EXPERIMENT_NOTE')
s=s.replace('Create an independently bound E0 action-head repair copy and test original-guard physical regressions','Continue the qualified W35 PPO on original full RM70 with400N50DR')
s=s.replace("'--kind','repair'","'--kind','training'")
s=s.replace('Actual SDK action closure and optimizer identity; 259-finite-tensor independent copy with same-input mean target equivalence; four bounded physical regression purposes and all original failures; W35 continuation source only unless separately admitted; preserve 1506 old tag objects and peels','Actual qualified343e full-state continuation; native24 and one new20k PPO update; original400N50DR/CAD70 peak-to-trough/RM70 rewards and guards unchanged; C pre-use cwd mismatch retained and D actual original cwd bound; preserve1507oldobjects/peels')
s=s.replace('Existing actual225 repair phase is consumed','Existing actual227 phase is consumed')
ast.parse(s);p=N/'archive_actual227_qualified_W35_continuation_ONCE.py';assert not p.exists();p.write_text(s,encoding='utf8');print(str(p))
