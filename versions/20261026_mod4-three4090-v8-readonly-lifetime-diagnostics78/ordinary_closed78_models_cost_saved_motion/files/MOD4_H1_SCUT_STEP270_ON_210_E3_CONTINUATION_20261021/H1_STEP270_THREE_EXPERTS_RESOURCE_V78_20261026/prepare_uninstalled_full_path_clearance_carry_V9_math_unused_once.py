"""Uninstalled reward-math hypothesis only. No present training or admission changes."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;M=T/'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026'
assert not M.exists();M.mkdir();(M/'reference_sources').mkdir();(M/'candidate_v1').mkdir();(M/'reports').mkdir()
p=N/'payloads/h1/h1_step270_path_reward_v1.py';raw=p.read_bytes();s=raw.decode('utf8')
with (M/'reference_sources/actual78_V8_reward.original_bytes.txt').open('xb') as f:f.write(raw)
old="joint=((current-.10)/.25).clamp(0.,1.)*clearance.square()"
new="joint=((current-.10)/(RECIPE['path_target_x_m']-.10)).clamp(0.,1.)*clearance.square()"
assert s.count(old)==1 and s.count("version='step270_sampled_leg_excess_v8_reward_only'")==1
s=s.replace(old,new,1).replace("version='step270_sampled_leg_excess_v8_reward_only'","version='step270_full_path_clearance_carry_v9_reward_only'",1);ast.parse(s)
q=M/'candidate_v1/h1_step270_path_reward_v1.py'
with q.open('x',encoding='utf8',newline='\n') as f:f.write(s)
with (M/'reports/V9_REWARD_MATH_HYPOTHESIS_SOURCE_ONLY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),status='UNINSTALLED_MATH_HYPOTHESIS_ONLY',base_source=str(p),base_SHA=hashlib.sha256(raw).hexdigest(),candidate=str(q),candidate_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),changes=['recipe version','clearance-carry potential ramp extends to the already existing path_target_x_m=.60 rather than saturating at leading edge .35'],same_total_scale8_and_signed_potential_difference=True,no_actor_input_action_command_physics_success_or_current78_change=True,no_new79_payload_or_reward_authorization_claim=True,not_proven_rootcause_or_learning_improvement=True,future_actual_SDK_source_allowlist_and_explicit_runtime_admission_still_required=True),f,indent=2)
print(json.dumps(dict(source_only_V9_math=True,not_installed_or_admitted=True)))
