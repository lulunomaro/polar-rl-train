from pathlib import Path
D=Path(__file__).resolve().parent
p=D/'verify_route443_hourly_monitor_actual_once.py'
s=p.read_text(encoding='utf8').replace('ROUTE443_HOURLY_MONITOR_UPDATE_REQUEST.json','COMPLETE152_SECOND_STORAGE_MONITOR_UPDATE_REQUEST.json').replace('ROUTE443_HOURLY_MONITOR_ACTUAL_VERIFIED.json','COMPLETE152_SECOND_STORAGE_MONITOR_ACTUAL_VERIFIED.json').replace('ROUTE443_MONITOR_VERIFY_ERROR_','COMPLETE152_STORAGE_MONITOR_VERIFY_ERROR_')
exec(compile(s,str(__file__)+'#actual-native-complete152-storage','exec'),dict(__file__=__file__,__name__='__main__'))
