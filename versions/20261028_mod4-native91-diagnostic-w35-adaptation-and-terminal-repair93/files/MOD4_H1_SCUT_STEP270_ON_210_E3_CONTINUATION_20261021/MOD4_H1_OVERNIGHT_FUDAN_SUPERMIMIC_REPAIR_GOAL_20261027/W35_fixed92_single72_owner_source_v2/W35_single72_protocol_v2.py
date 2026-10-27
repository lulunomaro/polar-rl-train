"""Human-authorized W35-only next slot while H1 is diagnostic hold; original72 only."""
from W35_mixed72_protocol_v1 import *
def validate_schedule(cfg):
 require(set(cfg['experts'])=={'w35'} and cfg['deferred_experts']==[],'one genuine W35 slot; H1 diagnostic hold, no fake registration')
 require(cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts','sole original72 authority')
 validate_spec(cfg['experts']['w35']);return True
