"""Continue partial CPU package; fix only fake hardware field collision, never replay target or GPU."""
from pathlib import Path
import ast,hashlib,json,sys,time,types,zipfile
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';E=D/'e2_closed109_frozen_prepared_v4';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=R/'E2_CLOSED109_V4_CPU_FIXTURE_ORIGINAL_TYPEERROR_AND_V2_REFERENCE.json';assert not proof.exists()
proof.write_text(json.dumps(dict(epoch=time.time(),original_CPU_preparer='prepare_E2closed109_frozen_V4_lossless_callback_guard_CPU_once.py',original_error="TypeError: dict() got multiple values for keyword argument 'force'",location='actual measured callback CPU fake hardware fixture',cause='Fake hardware arrays used force key already declared by actual measured callback; real hardware arrays have independent names.',only_fix='Use independent joint_vel NaN CPU fake field; actual callback and guards unchanged.',old_partial_sources_retained=True,no_target_GPU_or_Task=True),indent=2),encoding='utf8')
original=(D/'prepare_E2closed109_frozen_V4_lossless_callback_guard_CPU_once.py').read_text('utf8');suffix=original.split('# Execute the actual nested callback\'s statement order with CPU fake sensor/arrays, not a mirror implementation.\n',1)[1]
suffix=suffix.replace("arrays={'force':np.array([float('nan')])}","arrays={'joint_vel':np.array([float('nan')])}").replace("np.isnan(fake.sub[0]['force'])","np.isnan(fake.sub[0]['joint_vel'])").replace("z['physical_force']","z['physical_joint_vel']")
s=(Q/'retention_native_witness_v8.py').read_text('utf8');signature=json.loads((R/'E2_CLOSED109_249_CHANGED_DESKTOP_EXACT_SIGNATURES_0820_READONLY_ACTUAL.json').read_bytes());expected={r['name']:{k:r[k] for k in ('process','parent','binary_SHA')} for r in signature['exact_new_desktop_roles']};negatives=[name+':'+field for name in expected for field in ('pid','creation','exe','parent','hash','argv')]
assert not (Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V4.json').exists() and not (E/'CPU_actual_callback_failure_fixture').exists()
exec(compile(suffix,'<V2 actual callback fixture and sealed V4 CPU completion>','exec'))
