"""Source119: remove the declared-neutral backward position cue before request.
No reward/physics/model/SDK/remote change or admission is performed.
"""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';B=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27/source'
D=L/'native119_pre_request_neutral_X_goal_source_v1';assert not D.exists();(D/'reports').mkdir(parents=True)
source=B/'native_fudan_step_adapter_candidate_v2.py';raw=source.read_bytes()
a=b"value[...,0]=torch.where(active,value.new_tensor(p.goal_root_x_m),value.new_tensor(0.))"
b=b"value[...,0]=torch.where(active,value.new_tensor(p.goal_root_x_m),self.neutral[0])"
c=b'goal_and_goal_normalizer_unchanged=True'
d=b'goal_and_goal_normalizer_unchanged=False,goal_normalizer_tensors_unchanged=True,pre_request_X_goal_uses_declared_neutral=True'
assert raw.count(a)==raw.count(c)==1
candidate=raw.replace(a,b).replace(c,d);assert candidate.replace(b,a).replace(d,c)==raw
ast.parse(candidate.decode('utf8'))
(D/'native116_original_adapter_exact_bytes.txt').write_bytes(raw)
(D/'native119_pre_request_neutral_X_adapter_SOURCE_ONLY.py').write_bytes(candidate)
goal=B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json';goalbytes=goal.read_bytes();(D/goal.name).write_bytes(goalbytes)
report=dict(epoch=time.time(),source_only=True,not_installed_or_runtime_admitted=True,original_source=str(source),original_SHA=hashlib.sha256(raw).hexdigest(),candidate_SHA=hashlib.sha256(candidate).hexdigest(),original_goal_artifact=str(goal),goal_artifact_SHA=hashlib.sha256(goalbytes).hexdigest(),changes=['query pre-request X: literal0 to declared neutral_packed73[0]','contract metadata explicitly says goal behavior changed, normalizer tensors retained'],inverse_byte_exact=True,
    no_reward_or_mask_or_request_clock_or_goal_width_or_network_or_model_normalizer_or_optimizer_change=True,no_SDK_GPU_model_raw_remote_or_account_reads=True,
    scope='This removes a backward position cue relative to the declared neutral pose; it is not a per-environment position hold, source promotion, physical improvement, jump-process repair, closure repair or unique cause proof.')
(D/'reports/SOURCE119_EXACT_DERIVATION_NOT_RUNTIME.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(source_only=True,folder=str(D),candidate_SHA=report['candidate_SHA'])))
