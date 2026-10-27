"""Explicit2active/1deferred schedule; original per-slot source validator retained."""
from pathlib import Path
import hashlib,json,re
from native87_protocol_v1 import validate_spec,AUTHORITY_GENERATION,GPUS
ACTIVE=('h1','recovery');DEFERRED=('e2',)
BOUNDARY_NAME='AVAILABLE_TWO_RESOURCE_BOUNDARY_ACTUAL.json'
def require(v,message):
 if not v:raise ValueError(message)
def validate_boundary(value):
 require(value['actual_finite_returned'] is True,'actual resource boundary required')
 a=value['account'];require(a['sole72_current_None'] and a['original_owner_locks_free'] and a['no_account_write'],'sole72 closed boundary')
 require(a['remaining']==577055.9868602753 and a['remaining']>86412.86069250107,'original finite snapshot')
 r=value['resources'];g={x['GPU_UUID']:x for x in r['gpus']}
 require(g[GPUS['e2']]['compute_application_count']>0 and g[GPUS['e2']]['free_MiB']<=15669,'honest occupied deferred e2')
 require(g[GPUS['recovery']]['compute_application_count']==0 and g[GPUS['recovery']]['free_MiB']>15669,'available recovery boundary')
 require(r['available_RAM_bytes']>32*1024**3 and r['free_task_disk_bytes']>25*1024**3,'original workload resources')
 require(r['no_peer_PID_exe_argv_identity_query'] and r['no_signal_lock_delete_or_account_write'],'unknown peer untouched')
 return True
def validate_schedule(cfg):
 require(set(cfg['experts'])==set(ACTIVE) and cfg['deferred_experts']==list(DEFERRED),'exact twoactive/onedeferred required')
 require(cfg['scheduling_authority']=='human_requested_available_experts' and cfg['authority_generation']==AUTHORITY_GENERATION,'same sole72 authority')
 for key,spec in cfg['experts'].items():require(spec['key']==key and validate_spec(spec),'original per-slot admission')
 require(cfg['resource_boundary_relative']==BOUNDARY_NAME and re.fullmatch('[0-9a-f]{64}',cfg['resource_boundary_SHA']) is not None,'external resource boundary pin required')
 raw=(Path(__file__).resolve().parent/BOUNDARY_NAME).read_bytes()
 require(hashlib.sha256(raw).hexdigest()==cfg['resource_boundary_SHA'],'resource boundary byteSHA')
 return validate_boundary(json.loads(raw))
