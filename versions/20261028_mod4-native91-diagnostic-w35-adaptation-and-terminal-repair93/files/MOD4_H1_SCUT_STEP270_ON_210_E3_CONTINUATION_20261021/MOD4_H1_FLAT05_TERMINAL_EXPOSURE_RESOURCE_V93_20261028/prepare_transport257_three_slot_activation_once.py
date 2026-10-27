from pathlib import Path
import ast
N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022'
s=(B/'same_authorized_session_compressed_transport_v256.py').read_text('utf8');a="        'repair_source210_CPU_backend_literal_metadata_only_once.py',";assert s.count(a)==1
s=s.replace(a,"        'activate_three93_actual_CPU_bound_original_single_writer_once.py',\n"+a,1);ast.parse(s)
with (B/'same_authorized_session_compressed_transport_v257.py').open('x',encoding='utf8') as f:f.write(s)
print('prepared exact257 activation basename only')
