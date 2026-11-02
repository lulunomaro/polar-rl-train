"""Freeze own published native startup/progress, with new sharing instruction.
Pure metadata processing; no remote calls/models/raw/SDK/GPU/canonical writes.
"""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parent;out=R/'reports/FIRST_NATIVE_START_AND_SHARED_GPU_REQUEST_V1.json';assert not out.exists()
pointer=json.loads((R/'SUPERMIMIC_EIGHT_V1_LATEST_METADATA_WATCH.json').read_bytes());v=json.loads(Path(pointer['current']).read_bytes());rows=[]
for r in v['rows']:
 if not r.get('startup'):continue
 rows.append(dict(role=r['role'],status=r['status'],iteration=r.get('iteration'),counts=r.get('counts'),startup=r['startup'],progress=r.get('progress'),final=r.get('final'),error=r.get('error')))
assert rows and any(r['role']=='E0'for r in rows)
value=dict(kind='ACTUAL_NATIVE_START_METADATA_NOT_SKILL_PASS',captured_local=datetime.datetime.now().astimezone().isoformat(),producer_epoch=v['epoch'],root=v['root'],parent_current=v['parent_current'],parent_exit=v.get('parent_exit'),parent_error=v.get('parent_error'),rows=rows,stale_wait_marker_note='PREGO_RESOURCE_WAIT may remain after actual GO; live parent_current/startup takes precedence.',human_shared_GPU_instruction='2026-11-02 18:48:07 allow low-occupancy shared GPU even with another person process',future_resource_policy='Original free>15669MiB/util<=30/RAM>64GiB/disk>50GiB remain; compute-app nonempty alone no longer blocks future unused owner. Original canonical/private/finite leases remain. No active hotpatch.',models_raw_SDK_GPU_GO_C_operations=0)
out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(out)
print(json.dumps(dict(producer_epoch=value['producer_epoch'],root=value['root'],workers=value['parent_current']['workers'],rows=[dict(role=r['role'],iteration=r['iteration'],counts=r['counts'],last_bptt_receipt=(r.get('progress')or{}).get('last_bptt_receipt'))for r in rows]),indent=2))
