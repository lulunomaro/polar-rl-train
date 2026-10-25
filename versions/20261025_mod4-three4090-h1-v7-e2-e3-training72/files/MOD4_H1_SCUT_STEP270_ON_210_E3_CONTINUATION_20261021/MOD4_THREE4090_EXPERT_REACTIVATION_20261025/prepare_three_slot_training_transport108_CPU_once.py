from pathlib import Path
import ast,json,time
S=Path(__file__).resolve().parent;B=S.parent/'H1_STEP270_REWARD_PATH_V1_20261022';source=(B/'same_authorized_session_compressed_transport_v107.py').read_text('utf8');needle="        'install_E2_on_third72_CPU_only_unused_once.py',";assert source.count(needle)==1;source=source.replace(needle,needle+"\n        'deploy_actual_three_experts72_original_writer_once.py',\n        'collect_three_experts72_first_PPO_finite_once.py',",1);ast.parse(source)
with (B/'same_authorized_session_compressed_transport_v108.py').open('x',encoding='utf8') as f:f.write(source)
with (S/'reports/THREE_SLOT_TRAINING_EXACT_TRANSPORT108_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,only_new_basenames=['deploy_actual_three_experts72_original_writer_once.py','collect_three_experts72_first_PPO_finite_once.py'],original_credential_memory_and_strict_pin_unchanged=True,no_remote_action=True),f,indent=2)
print(json.dumps(dict(prepared=True)))
