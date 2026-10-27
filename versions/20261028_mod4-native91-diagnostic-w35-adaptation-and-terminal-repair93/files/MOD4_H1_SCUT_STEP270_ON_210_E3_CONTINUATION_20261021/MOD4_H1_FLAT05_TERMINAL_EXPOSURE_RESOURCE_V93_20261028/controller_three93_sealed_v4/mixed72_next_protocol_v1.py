"""Strict genuine target dispatch. Import has no model/account/host IO."""
KEYS={'h1','h1_210','e2'}
GENERATION='MOD4_SINGLE_WRITER72_20261026'
def module_for(spec):
 key=spec['key'];assert key in KEYS
 if key=='h1':import h1_native93_protocol as p
 elif key=='h1_210':import h1_210_native93_protocol as p
 else:import E2_next72_protocol_v1 as p
 return p
def validate_schedule(cfg):
 assert set(cfg['experts'])==KEYS and cfg['deferred_experts']==[] and cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts'
 specs=cfg['experts'];assert len({s['GPU_UUID'] for s in specs.values()})==3
 for key,spec in specs.items():
  assert key==spec['key'] and spec['run_id']==cfg['run_id'] and spec['max_parent_seconds']==3900 and spec['exit_headroom_seconds']==300
  module_for(spec).validate_spec(spec)
 return True
def nativeflat_valid_ready(row,spec):return module_for(spec).nativeflat_valid_ready(row,spec)
def flat_go_fields(spec):return module_for(spec).flat_go_fields(spec)
