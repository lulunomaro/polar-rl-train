from pathlib import Path
import ast
N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022'
s=(B/'same_authorized_session_compressed_transport_v257.py').read_text('utf8');a="        'activate_three93_actual_CPU_bound_original_single_writer_once.py',";assert s.count(a)==1
s=s.replace(a,"        'observe_three93_two_native_NEW_Pi_then_E2_PPO_combined_once.py',\n"+a,1);ast.parse(s)
with (B/'same_authorized_session_compressed_transport_v258.py').open('x',encoding='utf8') as f:f.write(s)
ast.parse((N/'observe_three93_two_native_NEW_Pi_then_E2_PPO_combined_once.py').read_bytes())
print('prepared exact258 combined first observer basename only')
