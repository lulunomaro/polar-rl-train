"""Freeze own source/metadata/fixtures only. No model or original asset access."""
from pathlib import Path
import json,hashlib,ast,datetime
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in D.glob('*.py'):ast.parse(p.read_bytes())
core=['observe_native88_first_new_policy_finite_unused_once.py','native88_closing_protocol_v1.py','native88_observer_readonly_remote_v1.py','collect_native88_finals_actual_cost_unused_once.py','native88_close_readonly_remote_v1.py','review_native88_finals_initial_CPU_unused_once.py','native88_initial_CPU_reader_primitives_v1.py','native88_event_curve_summary_v1.py']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (D/'FROZEN_SOURCE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,status='SOURCE_ONLY_FROZEN_NOT_EXECUTED',stage='H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027',
 observer_ready=True,collector_ready=True,initial_CPU_reviewer_ready=True,actual_GO_metadata_source_interface_checked=True,
 source_check_reports=dict(initial_metadata=31,worker_launch_and_recycled_identity_increment=2,actual88B_receipt_AST_increment=8),
 superseded_V1_own_children_required_negative_retained=True,actual_models_or_raw_read=0,network_GPU_or_actual_observer_executed=False,
 core=[dict(relative=n,bytes=(D/n).stat().st_size,SHA=H(D/n)) for n in core],Git_archive_pending_root=True),f,indent=2)
rows=[]
for p in sorted(D.rglob('*')):
 if p.is_file():
  assert p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip')
  rows.append(dict(relative=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
with (D/'INDEX_SHA256_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,files=rows,scope='complete own directory except this index'),f,indent=2)
print(json.dumps(dict(frozen_UTC=now,index_SHA=H(D/'INDEX_SHA256_ACTUAL.json'),indexed_files=len(rows),core=[r for r in rows if r['relative'] in core]),indent=2))
