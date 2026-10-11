"""Read-only final-frame reset binding; retain exact actor/age/formula tolerances."""
from pathlib import Path
import json,hashlib
import numpy as np
import review_curb132_actual as original
D=Path(__file__).resolve().parent
def recipe_manager(p,folder):
 a=p['frozen_actor'];s=p['sensor_manager']
 assert a['variant']=='A0' and a['current_actor_dimension']==35 and a['actual_command_error']==0
 assert a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
 assert s['actor35'] and s['critic38_clean'] and s['command_lastaction_mode_wheel_slots_exact'] and s['same_tick_draws_unchanged'] and s['formula_max_error']<=2e-6
 assert s['delay_recipe']['reset_warmup_actual_age_us']==0 and s['tick']==1500
 freeze=json.loads((D/'reports/ENTRY_SEED_SOURCE_FREEZE.json').read_bytes())['sha256'];base=D.parent/'MOD4_D7_RESET_PERFORMANCE_REVIEW_20261009/baseline'
 for name in ('feedback_delay_mild.py','feedback_delay_runtime.py','sensor_a0_runtime.py'):
  assert hashlib.sha256((base/name).read_bytes()).hexdigest()==freeze['isaac/mod4/'+name]
 channels=s['actual_feedback_sample_apply'];assert set(channels)=={'base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel'}
 raw=folder/p['full_route_raw']['name'];assert hashlib.sha256(raw.read_bytes()).hexdigest()==p['full_route_raw']['sha256']
 with np.load(raw) as data:
  final_trunc=np.flatnonzero(data['truncated'][-1]).tolist();final_ordinary=np.flatnonzero(data['terminated'][-1]).tolist()
  assert not final_ordinary
  idx=p['reason_names'].index('rough_route_boundary');assert p['declared_time_outs']['rough_route_boundary']
  for i in final_trunc:assert data['reasons'][-1,i,idx] and data['episode'][-1,i]==data['episode'][-2,i]
  for channel,row in channels.items():
   assert row['control_period_us']==10000 and row['apply_tick']==1500 and row['warmup_uses_current_new_episode_sample']
   assert len(row['actual_age_us'])==len(row['actual_sample_tick'])==len(row['requested_delay_us'])==len(row['warmup_valid'])==80
   assert row['actual_age_us']==[(1500-t)*10000 for t in row['actual_sample_tick']]
   assert all(x in (0,10000) for x in row['actual_age_us']) and all(x in (0,10000) for x in row['requested_delay_us'])
   invalid=[i for i,ready in enumerate(row['warmup_valid']) if not ready];assert invalid==final_trunc
   for i in range(80):
    if i in final_trunc:assert row['actual_sample_tick'][i]==1500 and row['actual_age_us'][i]==0
    else:assert row['warmup_valid'][i] and row['actual_age_us'][i]==row['requested_delay_us'][i]
 return dict(original_actor35_critic38_formula_2e6_and_sample_tick_age_contract_exact=True,original_reset_warmup_actual_age0_contract=True,actual_final_declared_route_truncation_rows=final_trunc,all_other_rows_original_requested_age_and_warmup_valid_exact=True,actual_source_identity_exact=True,no_production_threshold_or_source_change=True)
def audit(p,folder):
 proof=recipe_manager(p,folder);old=original.recipe_manager
 try:
  original.recipe_manager=lambda actual:recipe_manager(actual,folder)
  result=original.audit(p,folder)
 finally:original.recipe_manager=old
 result['actual_final_reset_sensor_receipt_review']=proof
 return result
