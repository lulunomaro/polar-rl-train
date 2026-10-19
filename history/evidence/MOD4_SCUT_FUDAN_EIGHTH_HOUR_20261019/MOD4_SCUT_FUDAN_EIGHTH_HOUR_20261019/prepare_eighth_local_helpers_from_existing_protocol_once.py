"""Advance the existing local diagnostic template by one closed source; no new control."""
from pathlib import Path
import re,ast
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_SEVENTH_HOUR_20261019'
s=(P/'prepare_sixth_closed_source_local_diagnostic_once.py').read_text('utf8')
mapping={'FOURTH':'FIFTH','FIFTH':'SIXTH','SIXTH':'SEVENTH','fourth':'fifth','fifth':'sixth','sixth':'seventh','hour5':'hour6','hour6':'hour7'}
s=re.sub('|'.join(re.escape(x) for x in sorted(mapping,key=len,reverse=True)),lambda m:mapping[m.group()],s)
ast.parse(s);p=B/'prepare_seventh_closed_source_local_diagnostic_once.py';assert not p.exists();p.write_bytes(s.encode('utf8'))
print('New-source-only local helper prepared from the already instrumented protocol.')
