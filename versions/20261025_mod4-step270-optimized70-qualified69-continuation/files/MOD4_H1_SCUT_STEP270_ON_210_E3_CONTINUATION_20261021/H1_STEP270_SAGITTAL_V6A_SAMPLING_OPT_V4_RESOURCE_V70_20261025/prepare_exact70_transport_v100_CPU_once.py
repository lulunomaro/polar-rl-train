"""Extend compressed transport by two exact new70 entry basenames only."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022'
old=B/'same_authorized_session_compressed_transport_v99.py';new=B/'same_authorized_session_compressed_transport_v100.py'
s=old.read_text('utf8');needle="        'read_current69d_timing_snapshot_for_human_once.py',";assert s.count(needle)==1
s=s.replace(needle,needle+"\n        'deploy_same_optimized70_pinned_route_once.py',\n        'collect70_first_PPO_pinned_route_once.py',",1)
ast.parse(s)
with new.open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/EXACT70_TRANSPORT_ALLOWLIST_V100_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST=True,old_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_new_entry_basenames=['deploy_same_optimized70_pinned_route_once.py','collect70_first_PPO_pinned_route_once.py'],same_session_memory_secret_and_pin_unchanged=True,no_remote_action=True),f,indent=2)
print(json.dumps(dict(prepared=True,exact_two_basenames_only=True)))
