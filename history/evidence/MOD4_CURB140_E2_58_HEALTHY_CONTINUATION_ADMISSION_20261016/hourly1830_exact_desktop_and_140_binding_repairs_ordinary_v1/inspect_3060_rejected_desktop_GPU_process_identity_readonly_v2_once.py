"""V1 parser rejected Windows path escape before any transport; raw literal only."""
from pathlib import Path
import json,time,traceback
D=Path(__file__).resolve().parent;P=D/'inspect_3060_rejected_desktop_GPU_process_identity_readonly_once.py';s=P.read_text('utf8');p=D/'reports/DESKTOP_ROLE_V1_LOCAL_PARSE_ERROR_V2_LITERAL_READER_ACTUAL.json';assert not p.exists()
try:compile(s,str(P),'exec')
except SyntaxError:error=traceback.format_exc()
else:raise AssertionError('Original parse rejection expected')
assert s.count('t.ps(c,"$s=')==1;s=s.replace('t.ps(c,"$s=','t.ps(c,r"$s=',1);compile(s,str(Path(__file__)),'exec');p.write_text(json.dumps(dict(epoch=time.time(),original_source=str(P),original_error=error,no_V1_network_or_GPU_or_credential_lookup=True,V2_change='Only raw Python literal prefix for readonly Authenticode PowerShell Windows path',original_source_retained=True),indent=2),encoding='utf8');exec(compile(s,str(Path(__file__)),'exec'),dict(__file__=__file__,__name__='__main__'))
