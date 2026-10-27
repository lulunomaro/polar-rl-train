from pathlib import Path
import ast,json,hashlib
N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022'
with (N/'reports/LOCAL_TRANSPORT254_QUOTING_SOURCE_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_error='SyntaxError: unexpected EOF while parsing',scope='PowerShell nested -c quote ended Python input before source mutation; no transport execution/network/GPU/ledger',correction='file-based exact source derivation'),f,indent=2)
p=B/'same_authorized_session_compressed_transport_v254.py';assert not p.exists()
s=(B/'same_authorized_session_compressed_transport_v253.py').read_text('utf8')
a="        'install_native91_actual_source_SDK_CPU_once.py',"
assert s.count(a)==1
s=s.replace(a,"        'install_native93_two_distinct_targets_actual_source_SDK_CPU_UNUSED_once.py',\n"+a,1)
ast.parse(s)
with p.open('x',encoding='utf8') as f:f.write(s)
ast.parse((N/'install_native93_two_distinct_targets_actual_source_SDK_CPU_UNUSED_once.py').read_bytes())
print(json.dumps(dict(prepared_only=True,exact_one_basename_added=True,SHA=hashlib.sha256(p.read_bytes()).hexdigest())))
