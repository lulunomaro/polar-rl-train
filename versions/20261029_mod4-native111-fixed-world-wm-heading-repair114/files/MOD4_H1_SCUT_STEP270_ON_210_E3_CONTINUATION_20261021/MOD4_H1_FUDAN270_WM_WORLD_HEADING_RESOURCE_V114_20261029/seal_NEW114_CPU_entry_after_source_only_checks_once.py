from pathlib import Path
import hashlib,json,time,ast
N=Path(__file__).resolve().parent;R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=json.loads((R/'NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json').read_bytes());proof=R/'SOURCE114_V2_PREINSTALL_TASK_GO_HELPER_PRODUCER_CPU_ACTUAL.json';assert json.loads(proof.read_bytes())['passed']
entry=N/'install_NEW114_one_WM_heading_actual_sourceSDK_fullstate_CPU_UNUSED_once.py';ast.parse(entry.read_bytes())
assert H(Path(spec['payload'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==spec['manifest_SHA']
v=dict(epoch=time.time(),status='COMPLETE_FROZEN_UNUSED_NEW114_ONE_CPU_ENTRY',entry=str(entry),entry_SHA=H(entry),manifest_SHA=spec['manifest_SHA'],source_Task_GO_proof_SHA=H(proof),input111fullstate_and_normal86_each_once_only_after_actualSDK_metadata_and_source_gates=True,no_actual_GPU_GO=True)
with (R/'FROZEN_NEW114_ONE_ACTUAL_TARGET_CPU_ENTRY_SOURCE_INDEX_V1.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
