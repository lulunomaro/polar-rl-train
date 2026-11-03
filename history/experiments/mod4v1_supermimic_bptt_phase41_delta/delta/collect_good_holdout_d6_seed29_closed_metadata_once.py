"""Sole one-seed observer; full original terminal cache and original waits, no control."""
from pathlib import Path
import sys,json,hashlib,time
R=Path(__file__).resolve().parent;D=R/'source_good_holdout_lifecycle_routes_v4';marker=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D6_SEED20260929_COLLECTION_STARTED_ONCE.json';pointer=R/'GOOD_HOLDOUT_D6_SEED20260929_LATEST_CLOSED_RESULT_PATH.json';assert not marker.exists()and not pointer.exists();H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(2975,'4ca6cdf8e6f86d25ca3ebedb0ad92bb9252e536846c9677b2a2539bc67c22396')
for row in json.loads(raw)['files']:
 b=(D/row['name']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256'])
sys.dont_write_bytecode=True;sys.path.insert(0,str(D));import good_holdout_contract as C
from source_pins import verify_sources
from collect_good_holdout_result import collect
verify_sources();dispatch_raw=(R/'reports/GOOD_HOLDOUT_D6_SEED20260929_TYPED_PARENT_DISPATCH_V1.json').read_bytes();dispatch=json.loads(dispatch_raw);C.validate_dispatch(dispatch);stage=json.loads((R/'reports/GOOD_HOLDOUT_D6_SEED20260929_ACTUAL_STAGE_V1.json').read_bytes());assert dispatch['root']==stage['root']and dispatch['seed']==20260929 and dispatch['stage_receipt_SHA256']==stage['stage_receipt_SHA256'];output=R/'reports'/('GOOD_HOLDOUT_D6_SEED20260929_ACTUAL_CLOSED_'+time.strftime('%Y%m%d_%H%M%S'));assert not output.exists()
with marker.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),root=dispatch['root'],output_root=str(output),typed_dispatch_SHA256=H(dispatch_raw),original_collector_cap6000_interval20_unchanged=True,original_deadlines_not_extended=True,parent_lock_SDK_model_C_or_foreign_signal_operations=0),f,indent=2)
path,result=collect(dispatch,output)
with pointer.open('x',encoding='utf8')as f:json.dump(dict(result=str(path),root=dispatch['root'],seed=20260929,status=result['status'],passed_closed_good_reference_execution=result['passed_closed_good_reference_execution'],report_references_existing_complete_result_not_new_read=True),f,indent=2)
print(json.dumps(dict(report=str(path),status=result['status'],passed_closed_good_reference_execution=result['passed_closed_good_reference_execution'],errors=result['errors'],observed_counts=result['observed_counts'],conditional_original_scope_results=result['conditional_original_scope_results'],stage2_GO=False),indent=2));raise SystemExit(0 if result['passed_closed_good_reference_execution']else 1)
