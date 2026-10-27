from pathlib import Path
import ast
N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022'
s=(B/'same_authorized_session_compressed_transport_v255.py').read_text('utf8');a="        'install_native93_two_distinct_targets_identity_V2_actual_CPU_UNUSED_once.py',";assert s.count(a)==1
s=s.replace(a,"        'repair_source210_CPU_backend_literal_metadata_only_once.py',\n"+a,1);ast.parse(s)
with (B/'same_authorized_session_compressed_transport_v256.py').open('x',encoding='utf8') as f:f.write(s)
ast.parse((N/'repair_source210_CPU_backend_literal_metadata_only_once.py').read_bytes())
print('prepared exact256 metadata-only basename')
