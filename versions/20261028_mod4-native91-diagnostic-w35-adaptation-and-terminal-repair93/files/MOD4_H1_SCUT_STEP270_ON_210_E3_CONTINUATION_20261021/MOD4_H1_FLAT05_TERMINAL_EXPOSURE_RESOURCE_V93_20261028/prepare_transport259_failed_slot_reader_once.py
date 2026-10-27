from pathlib import Path
import ast
N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022'
s=(B/'same_authorized_session_compressed_transport_v258.py').read_text('utf8');a="        'observe_three93_two_native_NEW_Pi_then_E2_PPO_combined_once.py',";assert s.count(a)==1
s=s.replace(a,"        'collect_three93_failed210_original_fee_ownout_text_only_once.py',\n"+a,1);ast.parse(s)
with (B/'same_authorized_session_compressed_transport_v259.py').open('x',encoding='utf8') as f:f.write(s)
print('prepared exact259 failed slot text reader only')
