from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'verify_hourly_monitor_actual_once.py').read_text().replace('DIRECTION_HOURLY_MONITOR_UPDATE_REQUEST','CANDIDATE150_PARTIAL_HOURLY_MONITOR_UPDATE_REQUEST').replace('DIRECTION_HOURLY_MONITOR_ACTUAL_VERIFIED','CANDIDATE150_PARTIAL_HOURLY_MONITOR_ACTUAL_VERIFIED')
exec(compile(s,'<actual-partial150-native-hourly-monitor-verification>','exec'),dict(__file__=str(D/'verify_partial150_hourly_monitor_actual_once.py'),__name__='__main__'))
