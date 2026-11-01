from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
s=(T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/archive_actual227_qualified_W35_continuation_ONCE.py').read_text('utf8')
s=s.replace("ID='mod4-w35-qualified343e-original-full-rm70-continuation-ppo227'","ID='mod4-e2-metadata-reader-order-repair-and-world-skill232'")
s=s.replace('CAPTURE227_ACTUAL_FROZEN_SCOPE','CAPTURE232_ACTUAL_FROZEN_SCOPE')
start=s.index("extra=read(R/'CAPTURE227_ADDITIONAL")
end=s.index('request=read(',start)
s=s[:start]+"assert read(R/'ROOT232_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'\n"+s[end:]
s=s.replace('==1507','==1508').replace('1507_old_objects','1508_old_objects').replace('protected1507','protected1508').replace('preserve1507','preserve1508').replace('tag_count=1508','tag_count=1509')
s=s.replace('ARCHIVE227_ACTUAL_PPO_ONCE_CONSUMED_BEFORE_RECORD','ARCHIVE232_ACTUAL_DIAGNOSTIC_ONCE_CONSUMED_BEFORE_RECORD')
s=s.replace('ACTUAL227_CONTINUATION_EXPERIMENT_NOTE','ACTUAL232_READER_AND_SKILL_EXPERIMENT_NOTE')
s=s.replace('Continue the qualified W35 PPO on original full RM70 with400N50DR','Repair the same-line E2 metadata reader and retain actual world-skill diagnostic evidence')
s=s.replace("'--kind','training'","'--kind','diagnostic'")
s=s.replace('Actual qualified343e full-state continuation; native24 and one new20k PPO update; original400N50DR/CAD70 peak-to-trough/RM70 rewards and guards unchanged; C pre-use cwd mismatch retained and D actual original cwd bound; preserve1508oldobjects/peels','Original231 source-reader failure preserved; V2 no-signal and V3 source-column order proof; fresh original authority and new necessary metadata/actor case with unchanged213 worker/400N50DR; full UTF8/partial/failure preserved; W35 closing if actuallycompleted,protect1508oldobjects/peels')
s=s.replace('Existing actual227 phase is consumed','Existing actual232 phase is consumed')
ast.parse(s);p=N/'archive_actual232_E2_reader_repair_and_diagnostic_ONCE.py';assert not p.exists();p.write_text(s,encoding='utf8');print(str(p))
