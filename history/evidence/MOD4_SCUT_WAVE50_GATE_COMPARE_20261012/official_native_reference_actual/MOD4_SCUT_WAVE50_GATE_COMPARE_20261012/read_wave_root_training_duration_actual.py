"""Expand read-only duration selection to Wave-owned roots, including generic prechecks."""
from scut_wave_io import *
s=(D/'read_wave_actual_training_duration.py').read_text(encoding='utf8')
s=s.replace("'wave' in str(x.get('kind','')).lower()","'wave' in (str(x.get('kind',''))+' '+str(x.get('log',''))).lower()").replace('WAVE_CANONICAL_NAMED_SEGMENTS_ACTUAL.json','WAVE_CANONICAL_ROOT_SEGMENTS_ACTUAL.json')
exec(compile(s,'<readonly-wave-root-duration-schema>','exec'),dict(__name__='__main__',__file__=__file__))
