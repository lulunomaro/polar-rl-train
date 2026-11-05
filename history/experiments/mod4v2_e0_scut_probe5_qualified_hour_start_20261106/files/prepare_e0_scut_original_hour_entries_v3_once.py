"""Use observed preparer version tokens; actual qualified probe5 gates precede publication."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'prepare_e0_scut_original_hour_entries_once.py').read_text(encoding='utf8')
changes=[('E0_SCUT_PROBE_ADMISSION4_','E0_SCUT_PROBE_ADMISSION5_'),('worker_e0_scut_v14_hour_v1.py','worker_e0_scut_v14_hour_v3.py'),('worker_e0_scut_v14_probe_v3.py','worker_e0_scut_v14_probe_v5.py'),('stage_e0_scut_probe_nonpt_v3.py','stage_e0_scut_probe_nonpt_v5.py'),('e0_scut_probe_admission3_','e0_scut_probe_admission5_'),('E0_SCUT_THIRD_PROBE_ACTUAL_QUALIFIED_HOUR_READINESS.json','E0_SCUT_PROBE5_ACTUAL_QUALIFIED_HOUR_READINESS.json')]
for old,new in changes:
 assert old in s,old
 s=s.replace(old,new)
exec(compile(s,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
