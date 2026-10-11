"""Native exact prompt/frequency/target proof; never rerun old verifier."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
s=(D/'verify_hourly_monitor_actual_once.py').read_text().replace('DIRECTION_HOURLY_MONITOR_UPDATE_REQUEST','DIRECTION_FORMAL_HOURLY_MONITOR_UPDATE_REQUEST').replace('DIRECTION_HOURLY_MONITOR_ACTUAL_VERIFIED','DIRECTION_FORMAL_HOURLY_MONITOR_ACTUAL_VERIFIED')
exec(compile(s,'<new-formal-native-monitor-verification>','exec'),dict(__file__=str(D/'verify_formal_hourly_monitor_actual_once.py'),__name__='__main__'))
