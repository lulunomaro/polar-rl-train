from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'verify_hourly_monitor_actual_once.py').read_text().replace('DIRECTION_HOURLY_MONITOR_UPDATE_REQUEST','DIRECTION_FINAL_HOURLY_MONITOR_UPDATE_REQUEST').replace('DIRECTION_HOURLY_MONITOR_ACTUAL_VERIFIED','DIRECTION_FINAL_HOURLY_MONITOR_ACTUAL_VERIFIED')
exec(compile(s,'<final-closeout-native-hourly-monitor-verification>','exec'),dict(__file__=str(D/'verify_final_hourly_monitor_actual_once.py'),__name__='__main__'))
