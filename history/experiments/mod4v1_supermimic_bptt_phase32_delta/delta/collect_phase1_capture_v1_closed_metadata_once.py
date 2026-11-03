"""NEW own-result metadata purpose, not a parent retry; preserve collector rc/status."""
from pathlib import Path
import sys,json,hashlib,runpy,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_result_collector_v1';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_V1_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json';pointer=R/'PHASE1_E3_CAPTURE_V1_LATEST_CLOSED_RESULT_PATH.json';assert not marker.exists()and not pointer.exists()
raw=(D/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c';seal=json.loads(raw);assert len(seal['files'])==9 and seal['content_root_sha256']=='5deb47562c45109d35ad6b502a047802ed29aee40dff349e34888f4c488abe51'
for row in seal['files']:
 p=D/row['relative'];assert p.resolve().is_relative_to(D);b=p.read_bytes();assert(len(b),hashlib.sha256(b).hexdigest())==(row['bytes'],row['sha256'])
out=R/'reports'/('PHASE1_E3_CAPTURE_V1_ACTUAL_CLOSED_'+time.strftime('%Y%m%d_%H%M%S'));assert not out.exists()
with marker.open('x',encoding='utf-8')as f:json.dump(dict(kind='NEW_OWN_CLOSED_CAPTURE_METADATA_COLLECTION_PURPOSE_V1',epoch=time.time(),output_root=str(out),collector_seal_SHA256=hashlib.sha256(raw).hexdigest(),parent_restarts_SDK_model_canonical_operations=0),f,indent=2)
sys.path.insert(0,str(D));sys.argv=[str(D/'collect_capture_result.py'),'--dispatch',str(R/'reports/PHASE1_E3_CAPTURE_V1_ORIGINAL_PARENT_DISPATCH_ONCE.json'),'--output-root',str(out)]
rc=0
try:runpy.run_path(str(D/'collect_capture_result.py'),run_name='__main__')
except SystemExit as e:rc=e.code if type(e.code)is int else 1
result_path=out/'CLOSED_RESULT.json';b=result_path.read_bytes();v=json.loads(b)
with pointer.open('x',encoding='utf-8')as f:json.dump(dict(path=str(result_path),bytes=len(b),SHA256=hashlib.sha256(b).hexdigest(),collector_returncode=rc,actual_closed_status=v['status'],epoch=time.time()),f,indent=2)
print(json.dumps(dict(pointer=str(pointer),report=str(result_path),collector_returncode=rc,status=v['status'],actual_parent_wait_returned=v['actual_parent_wait_returned'],parent_wait_returncode=(v['outer_actual_parent_wait']or{}).get('returncode'),EX_release=v['parent_exit_scope'],observed_controls=v['worker_observed']['controls'],gate1=v['gate1']),indent=2))
raise SystemExit(rc)
