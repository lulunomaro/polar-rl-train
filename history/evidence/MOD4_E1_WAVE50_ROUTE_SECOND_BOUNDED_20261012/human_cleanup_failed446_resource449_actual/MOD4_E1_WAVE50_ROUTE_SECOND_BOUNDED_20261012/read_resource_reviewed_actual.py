from route_second_io import *
s=(W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012/read_route_lifecycle_actual.py').read_text(encoding='utf8')
s=s.replace('from route_GPU_io import *',"from route_second_io import *\nROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'")
s=s.replace('supervise_wave50_route_source_reviewed_once','supervise_wave50_route_startup_resource_reviewed_once').replace("save('ROUTE_LIFECYCLE_ACTUAL_'","save('RESOURCE_REVIEWED_ACTUAL_'")
exec(compile(s,str(__file__)+'#readonly-own-source449','exec'),dict(__file__=__file__,__name__='__main__'))
