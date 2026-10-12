"""Continue the entirely unexecuted remote stage after placeholder-token syntax rejection."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'stage_detached_dispatch_reviewed_once.py').read_text();assert s.count('PY_TOKEN_TEXT')==2
s=s.replace('PY_TOKEN_TEXT','REFERENCE_EXECUTABLE_TEXT')
exec(compile(s,'<detached-reference-nonoverlapping-literal-review>','exec'),dict(__file__=__file__,__name__='__main__'))
