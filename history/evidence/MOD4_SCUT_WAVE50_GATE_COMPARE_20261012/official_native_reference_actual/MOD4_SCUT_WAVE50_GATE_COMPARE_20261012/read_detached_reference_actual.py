from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'read_reference_actual.py').read_text().replace('from scut_wave_io import *','from scut_wave_detached_io import *').replace("save('SCUT_REFERENCE_ACTUAL_'","save('DETACHED_SCUT_REFERENCE_ACTUAL_'")
exec(compile(s,'<read-only-detached-reference-actual>','exec'),dict(__file__=__file__,__name__='__main__'))
