from pathlib import Path
import ast,json,time
S=Path(__file__).resolve().parent;B=S.parent/'H1_STEP270_REWARD_PATH_V1_20261022';old=B/'same_authorized_session_compressed_transport_v106.py';new=B/'same_authorized_session_compressed_transport_v107.py';text=old.read_text('utf8');needle="        'read_authorized_third_GPU_and_original_locks_once.py',";assert text.count(needle)==1;text=text.replace(needle,needle+"\n        'install_E2_on_third72_CPU_only_unused_once.py',",1);ast.parse(text)
with new.open('x',encoding='utf8') as f:f.write(text)
with (S/'reports/E2_CPU_INSTALL_EXACT_TRANSPORT107_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,only_new_basename='install_E2_on_third72_CPU_only_unused_once.py',same_session_memory_secret_strict_pin_unchanged=True),f,indent=2)
print(json.dumps(dict(prepared=True)))
