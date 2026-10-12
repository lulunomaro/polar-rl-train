from pathlib import Path
D=Path(__file__).resolve().parent
previous=D.parent/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012/review_direction_complete_dynamic_family_trace_actual.py'
s=previous.read_text().replace('from wave_direction_io import *','from wave_direction_second_io import *').replace('DIRECTION_OWN_FORMAL_CPU_ACTUAL_','SECOND_DIRECTION_OWN_FORMAL_CPU_ACTUAL_').replace("==424","==426").replace("save('DIRECTION_FULL_TRAINING_TRACE_ACTUAL_'","save('SECOND_DIRECTION_FULL_TRAINING_TRACE_ACTUAL_'")
exec(compile(s,'<readonly-own426-complete-dynamic-trace>','exec'),dict(__file__=__file__,__name__='__main__'))
