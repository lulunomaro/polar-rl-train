from pathlib import Path
D=Path(__file__).resolve().parent
source=D/'verify_route443_hourly_monitor_actual_once.py'
s=source.read_text(encoding='utf8').replace('ROUTE443_HOURLY_MONITOR_UPDATE_REQUEST.json','ROUTE443_FINAL_HOURLY_MONITOR_UPDATE_REQUEST.json').replace('ROUTE443_HOURLY_MONITOR_ACTUAL_VERIFIED.json','ROUTE443_FINAL_HOURLY_MONITOR_ACTUAL_VERIFIED.json').replace('ROUTE443_MONITOR_VERIFY_ERROR_','ROUTE443_FINAL_MONITOR_VERIFY_ERROR_')
exec(compile(s,str(__file__)+'#actual-native-final-monitor','exec'),dict(__file__=__file__,__name__='__main__'))
