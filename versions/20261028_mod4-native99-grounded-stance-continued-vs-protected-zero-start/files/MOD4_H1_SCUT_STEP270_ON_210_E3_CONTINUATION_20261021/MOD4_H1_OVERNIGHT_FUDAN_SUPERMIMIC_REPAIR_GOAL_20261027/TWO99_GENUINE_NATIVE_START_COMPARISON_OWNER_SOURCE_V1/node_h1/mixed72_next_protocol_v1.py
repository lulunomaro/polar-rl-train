"""Exactly two genuine target72 slots; no account IO on import."""
KEYS={'h1','restart'}
GENERATION='MOD4_SINGLE_WRITER72_20261026'
def module_for(spec):
 key=spec['key'];assert key in KEYS
 if key=='h1':import h1_next72_protocol_actual95_v2 as p
 else:import restart_next72_protocol_v99 as p
 return p
def validate_schedule(cfg):
 assert set(cfg['experts'])==KEYS and cfg['deferred_experts']==[] and cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts'
 specs=cfg['experts'];assert len({s['GPU_UUID'] for s in specs.values()})==2
 for key,spec in specs.items():
  assert key==spec['key'] and spec['run_id']==cfg['run_id'] and spec['max_parent_seconds']==3900 and spec['exit_headroom_seconds']==300
  module_for(spec).validate_spec(spec)
 return True
def nativeflat_valid_ready(row,spec):return module_for(spec).nativeflat_valid_ready(row,spec)
def flat_go_fields(spec):return module_for(spec).flat_go_fields(spec)
