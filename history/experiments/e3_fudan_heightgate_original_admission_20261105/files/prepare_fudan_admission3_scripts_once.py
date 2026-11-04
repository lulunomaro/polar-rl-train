"""Create isolated Admission3 helpers after W2 CLOSED and original owner-None observation. No learning/source-physics changes."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent
release=json.loads((D/'FDN_AFTER_W2_ORIGINAL_AUTHORITY_WATCH_RESULT.json').read_text(encoding='utf8'))
assert release['returncode']==0 and any(x.get('status')=='ORIGINAL_CANONICAL_OWNER_NONE_OBSERVED' for x in release['events'])
marker=D/'FDN_W3_HELPERS_DERIVED_ONCE.json';assert not marker.exists()
rows=[]
for old,new in [('prepare_stage_fudan_w2_once.py','prepare_stage_fudan_w3_once.py'),('dispatch_fudan_w2_original_owner_once.py','dispatch_fudan_w3_original_owner_once.py'),('collect_fudan_w2_window_once.py','collect_fudan_w3_window_once.py')]:
 src=(D/old).read_text(encoding='utf8');dst=src.replace('FDN_W2_','FDN_W3_')
 if old.startswith('prepare_stage_'):
  assert src.count("native_payload_v2")==1 and src.count('W2_MAPPING_')==1
  dst=dst.replace('native_payload_v2','native_payload_v3_admission').replace('W2_MAPPING_','W3_MAPPING_ADMISSION_')
 assert 'FDN_W2_' not in dst;ast.parse(dst);p=D/new;assert not p.exists();p.write_text(dst,encoding='utf8');rows.append(dict(source=old,new=new))
marker.write_text(json.dumps(dict(epoch=time.time(),helpers=rows,only_new_purpose_run_and_local_output_names=True,worker_owner_core_task_and_nonPT_stager_sources_unchanged_V2=True,not_replay_of_consumed_W2=True),indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
