"""Route two genuine registered slots in a NEW cohort; no writer/account I/O."""
import h1_next72_protocol as h1
import W35_mixed72_protocol_v1 as w35

def validate_schedule(cfg):
 assert set(cfg['experts'])=={'h1','w35'} and cfg['deferred_experts']==[]
 assert cfg['authority_generation']==w35.GENERATION and cfg['scheduling_authority']=='human_requested_available_experts'
 h1.validate_spec(cfg['experts']['h1']);w35.validate_spec(cfg['experts']['w35'])
 assert cfg['experts']['h1']['GPU_UUID']!=cfg['experts']['w35']['GPU_UUID']
 return True

def nativeflat_valid_ready(row,spec):
 return w35.W35_valid_ready(row,spec) if spec['key']=='w35' else h1.nativeflat_valid_ready(row,spec)

def nativeflat_go_fields(spec):
 return w35.W35_go_fields(spec) if spec['key']=='w35' else h1.nativeflat_go_fields(spec)
