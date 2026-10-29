from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
entry=N/'install_NEW116_one_actual_target_sourceSDK_fullstate_CPU_UNUSED_once.py'
ast.parse(entry.read_bytes());prep=json.loads((R/'NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json').read_bytes())
proof=R/'SOURCE116_PREINSTALL_TASK_GO_OWN_FK_COUNTEREXAMPLE_CPU_ACTUAL.json';assert json.loads(proof.read_bytes())['passed']
with (R/'FROZEN_NEW116_ONE_TARGET_CPU_ENTRY_SOURCE_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),entry=str(entry),entry_SHA=H(entry),manifest_SHA=prep['manifest_SHA'],source_CPU_SHA=H(proof),source_only=True,not_executed=True),f,indent=2)
print('116 CPU entry sealed, not executed')
