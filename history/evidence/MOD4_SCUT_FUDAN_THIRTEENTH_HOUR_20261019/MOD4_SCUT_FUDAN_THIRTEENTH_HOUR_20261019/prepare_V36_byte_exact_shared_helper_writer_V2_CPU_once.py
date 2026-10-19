"""Retain a never-executed draft and preserve original CRLF resource-helper bytes."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;R=B/'reports'
p=B/'prepare_actual_thirteenth_three_learning_monitor_V36_once.py'
resource=B/'three_real_gpu_resource_shared_user_v2.py';raw=resource.read_bytes();normalized=resource.read_text('utf8').encode()
assert raw!=normalized and raw.count(b'\r\n')==32
source=p.read_text('utf8');needle="for q in (P/'future_same_recipe_hour_templates').glob('*.py'):\n s=q.read_text('utf8')"
replacement="for q in (P/'future_same_recipe_hour_templates').glob('*.py'):\n if q.name=='three_real_gpu_resource_shared_user_v2.py':\n  shutil.copy2(q,F/q.name);continue\n s=q.read_text('utf8')"
assert source.count(needle)==1;source=source.replace(needle,replacement);ast.parse(source)
target=B/'prepare_actual_thirteenth_three_learning_monitor_V36_V2_once.py'
with target.open('x',encoding='utf8',newline='\n') as stream:stream.write(source)
H=lambda b:hashlib.sha256(b).hexdigest()
with (R/'PREPARED_V36_TEXT_NORMALIZATION_BYTE_MISMATCH_AND_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:
 json.dump(dict(epoch=time.time(),preflight_observation='Original sharing helper has CRLF bytes. Draft future writer would normalize it to LF, and its later exact-byte assertion would reject the result.',original_draft=dict(path=str(p),SHA=H(p.read_bytes()),retained=True,not_executed=True,no_actual_AssertionError_or_remote_failure_claim=True),resource=dict(path=str(resource),bytes=len(raw),SHA=H(raw),CRLF=raw.count(b'\r\n'),draft_LF_normalized_SHA=H(normalized),normalized_bytes_not_equal=True),new_writer=dict(path=str(target),SHA=H(target.read_bytes()),AST_parsed=True,resource_helper_uses_shutil_copy2_before_text_normalization=True),byte_preservation_validated_against_current_payload=raw==(B/'payload/h1/three_real_gpu_resource_v1.py').read_bytes(),no_GPU_Task_native_behavior_case_or_transport_replay=True,no_live_source_reward_PPO_runtime_account_or_player_change=True),stream,indent=2)
print(json.dumps(dict(V2_prepared=str(target),original_draft_retained_not_executed=True,resource_copy_exact_bytes=True)))
