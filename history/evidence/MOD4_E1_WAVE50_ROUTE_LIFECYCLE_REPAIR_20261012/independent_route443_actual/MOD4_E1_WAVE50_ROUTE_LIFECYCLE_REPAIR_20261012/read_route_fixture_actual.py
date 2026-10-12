from route_fixture_io import *
s=(D/'read_route_lifecycle_actual.py').read_text().replace('from route_GPU_io import *','from route_fixture_io import *').replace('supervise_wave50_route_source_reviewed_once','supervise_wave50_route_fixture_reviewed_once').replace("save('ROUTE_LIFECYCLE_ACTUAL_'","save('ROUTE_FIXTURE_ACTUAL_'")
exec(compile(s,'<readonly-actually-new-fixture443-scope>','exec'),dict(__name__='__main__',__file__=__file__))
