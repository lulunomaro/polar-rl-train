"""Only one exact new human-requested nonidentifying GPU resource reader entry."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022'
old=B/'same_authorized_session_compressed_transport_v104.py';new=B/'same_authorized_session_compressed_transport_v105.py';s=old.read_text('utf8');needle="        'collect_current71_finals_original_cost_unused_once.py',";assert s.count(needle)==1;s=s.replace(needle,needle+"\n        'read_three4090_nonidentifying_utilization_for_human_once.py',",1);ast.parse(s)
with new.open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/HUMAN_GPU_RESOURCE_READER_EXACT_ALLOWLIST105_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,only_new_basename='read_three4090_nonidentifying_utilization_for_human_once.py',old_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),same_session_memory_secret_and_strict_pin_unchanged=True),f,indent=2)
print(json.dumps(dict(prepared=True,exact_human_resource_reader_only=True)))
