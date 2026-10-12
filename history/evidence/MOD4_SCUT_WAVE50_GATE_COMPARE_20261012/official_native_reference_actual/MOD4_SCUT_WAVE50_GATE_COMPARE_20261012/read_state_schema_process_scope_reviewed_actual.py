from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'read_reference_actual.py').read_text().replace('from scut_wave_io import *','from scut_wave_schema_io import *').replace("save('SCUT_REFERENCE_ACTUAL_'","save('PROCESS_SCOPE_SCUT_REFERENCE_ACTUAL_'").replace('*scut_wave50_gate_compare_20261012*','*scut_wave50_gate_compare*')
exec(compile(s,'<readonly-reference-exact-scope-prefix-reviewed>','exec'),dict(__file__=__file__,__name__='__main__'))
