"""Freeze own source/small JSON only; no checkpoint/raw/original USD I/O."""
from pathlib import Path
import ast,json,hashlib,datetime
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in D.rglob('*.py'):ast.parse(p.read_bytes())
changes=json.loads((D/'EXACT_COMPATIBILITY_SOURCE_CHANGESET_NOT_ADMITTED.json').read_bytes())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (D/'FROZEN_SOURCE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,status='SOURCE_ONLY_FROZEN_NOT_DEPLOYED_NOT_SDK_ADMITTED',source_CPU_checks=17,
 replacements=changes['replacements'],additions=changes['additions'],unchanged_bank=changes['unchanged_bank'],
 target_CPU_hook='gas400_reset_bank_exact_compatibility_v1.check_runtime_source(actual_runtime_dir)',
 actual_SDK_scene_or_PhysX_or_training=False,models_read=0,originals_modified=False,root_ordinary_Git_pending=True),f,indent=2)
rows=[]
for p in sorted(D.rglob('*')):
 if p.is_file():
  assert p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip')
  rows.append(dict(relative=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
with (D/'INDEX_SHA256_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,files=rows,scope='complete own source/small JSON inventory except this self-index'),f,indent=2)
print(json.dumps(dict(frozen_UTC=now,index_SHA=H(D/'INDEX_SHA256_ACTUAL.json'),files=len(rows),replacements=changes['replacements'],additions=changes['additions']),indent=2))
