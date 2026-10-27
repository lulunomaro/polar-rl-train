"""One next original72 writer, exact H1 + W35 typed registration. No ledger IO."""
from pathlib import Path
import h1_next72_protocol as h1
import W35_mixed72_protocol_v1 as w35
KEYS={'h1','w35'}
GENERATION=w35.GENERATION
H1_GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'

def validate_schedule(cfg):
 assert set(cfg['experts'])==KEYS and cfg['deferred_experts']==[]
 assert cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts'
 h=cfg['experts']['h1'];w=cfg['experts']['w35'];h1.validate_spec(h);w35.validate_spec(w)
 assert h['GPU_UUID']==H1_GPU and w['GPU_UUID']==w35.GPU and h['GPU_UUID']!=w['GPU_UUID']
 assert h['execution_backend']==w['execution_backend']=='target72'
 assert h['run_id']==w['run_id']==cfg['run_id']
 assert all(s['max_parent_seconds']==3900 and s['exit_headroom_seconds']==300 for s in (h,w))
 return True

def nativeflat_valid_ready(row,spec):
 if spec['key']=='w35':return w35.W35_valid_ready(row,spec)
 if spec['key']=='h1':return h1.nativeflat_valid_ready(row,spec)
 return False

def flat_go_fields(spec):
 if spec['key']=='w35':return w35.W35_go_fields(spec)
 assert spec['key']=='h1';return h1.flat_go_fields(spec)

def validate_both_preinstalled(s_h1,s_w35,node_h1,node_w35):
 # JSON/source-only metadata validation; never load weights or rerun sourceCPU.
 h1.validate_payload(s_h1,Path(node_h1));w35.validate_payload(s_w35,Path(node_w35))
 h=h1.load_actual_flat_preinstalled_CPU(s_h1,Path(node_h1));w=w35.load_W35_preinstalled_CPU(s_w35,Path(node_w35))
 return dict(h1=h,w35=w)
