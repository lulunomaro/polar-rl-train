"""Freeze own derived source/metadata only."""
from pathlib import Path
import ast,json,hashlib,datetime
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in D.glob('*.py'):ast.parse(p.read_bytes())
names=['observe_native88_first_new_policy_finite_unused_once.py','native88_closing_protocol_v1.py','native88_observer_readonly_remote_v1.py','collect_native88_finals_actual_cost_unused_once.py','native88_close_readonly_remote_v1.py','review_native88_finals_initial_CPU_unused_once.py','native88_initial_CPU_reader_primitives_v1.py','native88_event_curve_summary_v1.py']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (D/'FROZEN_SOURCE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,status='SOURCE_ONLY_FROZEN_NOT_EXECUTED',stage='H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027',
 new_metadata_checks=13,derivation_exact_checks=11,old31_fixture_not_rerun=True,failures=[],actual_network_model_GPU_SDK_or_account=False,
 core=[dict(relative=n,bytes=(D/n).stat().st_size,SHA=H(D/n)) for n in names],root_ordinary_Git_pending=True),f,indent=2)
rows=[dict(relative=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file()]
with (D/'INDEX_SHA256_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,files=rows,scope='complete own directory except this index'),f,indent=2)
print(json.dumps(dict(frozen_UTC=now,index_SHA=H(D/'INDEX_SHA256_ACTUAL.json'),files=len(rows),core=[r for r in rows if r['relative'] in names]),indent=2))
