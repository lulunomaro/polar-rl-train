"""NEW own-result metadata purpose, not a parent retry; preserve collector rc/status."""
from pathlib import Path
import sys,json,hashlib,runpy,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_result_collector_v2';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_BOOTSTRAP_V2_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json';pointer=R/'PHASE1_E3_CAPTURE_BOOTSTRAP_V2_LATEST_CLOSED_RESULT_PATH.json';assert not marker.exists()and not pointer.exists()
raw=(D/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c';seal=json.loads(raw);assert len(seal['files'])==9 and seal['content_root_sha256']=='f810645b940445863ea4375f5b27b5fea15e5b2b0eaff53aacf88ffb08ffb1dd'
for row in seal['files']:
 p=D/row['relative'];assert p.resolve().is_relative_to(D);b=p.read_bytes();assert(len(b),hashlib.sha256(b).hexdigest())==(row['bytes'],row['sha256'])
out=R/'reports'/('PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_'+time.strftime('%Y%m%d_%H%M%S'));assert not out.exists()
with marker.open('x',encoding='utf-8')as f:json.dump(dict(kind='NEW_OWN_CLOSED_CAPTURE_METADATA_COLLECTION_PURPOSE_V1',epoch=time.time(),output_root=str(out),collector_seal_SHA256=hashlib.sha256(raw).hexdigest(),parent_restarts_SDK_model_canonical_operations=0),f,indent=2)
sys.path.insert(0,str(D));sys.argv=[str(D/'collect_capture_result.py'),'--dispatch',str(R/'reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json'),'--output-root',str(out)]
rc=0
try:runpy.run_path(str(D/'collect_capture_result.py'),run_name='__main__')
except SystemExit as e:rc=e.code if type(e.code)is int else 1
result_path=out/'CLOSED_RESULT.json';b=result_path.read_bytes();v=json.loads(b)
with pointer.open('x',encoding='utf-8')as f:json.dump(dict(path=str(result_path),bytes=len(b),SHA256=hashlib.sha256(b).hexdigest(),collector_returncode=rc,actual_closed_status=v['status'],epoch=time.time()),f,indent=2)
print(json.dumps(dict(pointer=str(pointer),report=str(result_path),collector_returncode=rc,status=v['status'],actual_parent_wait_returned=v['actual_parent_wait_returned'],parent_wait_returncode=(v['outer_actual_parent_wait']or{}).get('returncode'),EX_release=v['parent_exit_scope'],observed_controls=v['worker_observed']['controls'],gate1=v['gate1']),indent=2))
raise SystemExit(rc)
