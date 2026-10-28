from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent
s=(B/'prepare_fudan103_native270_payloads_v2_once.py').read_text('utf8')
old='  s=rep(s,"flat_real_physics_events=flat_counter.snapshot(),flat_floor_support_basis=flat_floor_basis","fudan_real_reward_tracking=bridge.reward_tracking_snapshot()")'
assert s.count(old)==1
s=s.replace(old,"  s=rep(s,',flat_floor_support_basis=flat_floor_basis','')").replace("N/'payloads_v2'","N/'payloads_v3'")
ast.parse(s)
with (B/'prepare_fudan103_native270_payloads_v3_once.py').open('x',encoding='utf8') as f:f.write(s)
with (B/'reports/ENTRY103_SOURCE_REPLACEMENT_ORDER_V3_CORRECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_v2_false_partial_namespace_retained=True,replacement_order_consumed_prefix_so_remove_only_remaining_legacy_floor_basis=True,no_runtime_or_model_or_GPU=True),f,indent=2)
