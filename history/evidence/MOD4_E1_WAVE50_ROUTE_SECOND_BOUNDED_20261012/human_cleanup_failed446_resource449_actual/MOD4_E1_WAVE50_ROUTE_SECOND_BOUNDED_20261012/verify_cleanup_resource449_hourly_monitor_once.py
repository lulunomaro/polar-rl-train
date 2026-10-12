from route_second_io import *
s=(W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012/verify_route443_hourly_monitor_actual_once.py').read_text(encoding='utf8')
s=s.replace('from route_fixture_io import *','from route_second_io import *').replace('ROUTE443_HOURLY_MONITOR_UPDATE_REQUEST.json','CLEANUP_RESOURCE449_MONITOR_UPDATE_REQUEST.json').replace('ROUTE443_HOURLY_MONITOR_ACTUAL_VERIFIED.json','CLEANUP_RESOURCE449_HOURLY_MONITOR_ACTUAL_VERIFIED.json').replace('ROUTE443_MONITOR_VERIFY_ERROR_','CLEANUP_RESOURCE449_MONITOR_VERIFY_ERROR_')
exec(compile(s,str(__file__)+'#native-hourly-actual','exec'),dict(__file__=__file__,__name__='__main__'))
