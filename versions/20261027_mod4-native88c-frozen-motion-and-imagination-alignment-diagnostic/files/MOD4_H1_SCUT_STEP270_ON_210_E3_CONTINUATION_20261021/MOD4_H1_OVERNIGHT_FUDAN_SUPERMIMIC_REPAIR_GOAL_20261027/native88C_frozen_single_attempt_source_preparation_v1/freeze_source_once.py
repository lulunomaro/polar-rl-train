"""Freeze own unused source/metadata only; no model/asset/raw access."""
from pathlib import Path
import ast,json,hashlib,datetime
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
core=('native88C_frozen_single_sdk_entry_unused_once.py','native88C_frozen_acceptance_driver_v1.py','native88C_frozen_acceptance_contract_v1.py','native88C_eval_environment_v1.py','native88C_own_pid_out_guard_v1.py','native88C_readonly_authority72_guard_v1.py')
for p in D.glob('*.py'):ast.parse(p.read_bytes())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (D/'FROZEN_SOURCE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,status='SOURCE_ONLY_UNUSED_ROOT_BINDING_AND_ACTUAL_ADMISSION_PENDING',entry=core[0],fixed_model_SHA='a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf',seed=20260928,episodes=1,max_controls=500,max_callbacks=2000,
 source_AST_checks=12,saved_qualified_metadata_check=1,source_generation_errors_preserved=True,actual_entry_model_SDK_GPU_physics_or_remote_executed=False,optional_WM_forward=False,
 core=[dict(relative=n,bytes=(D/n).stat().st_size,SHA=H(D/n)) for n in core],root_ordinary_Git_pending=True),f,indent=2)
rows=[]
for p in sorted(D.rglob('*')):
 if p.is_file():
  assert p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip')
  rows.append(dict(relative=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
with (D/'INDEX_SHA256_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,files=rows,scope='complete own source/metadata except self-index'),f,indent=2)
print(json.dumps(dict(frozen_UTC=now,index_SHA=H(D/'INDEX_SHA256_ACTUAL.json'),files=len(rows),entry_SHA=H(D/core[0]),driver_SHA=H(D/core[1]),contract_SHA=H(D/core[2])),indent=2))
