"""Freeze new219 source/metadata purpose before its sole LOCAL execution."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent.parent;R=N/'reports';T=N.parent
def main():
 paths=list(N.rglob('*.py'))
 paths += [T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/control/mixed210_finite_owner_authority72.py',
  T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/control/three_slot_common_v1.py',
  T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/run210_mixed_E0_JUMP_worker.py']
 rows=[]
 for p in sorted(paths):
  b=p.read_bytes();rows.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
 assert rows[-1] or rows
 value=dict(purpose_id='NEW219_W35_SOLO_INSTALLER_CLOSING_SCHEMA_AND_ORIGINAL_CONTROL_SOURCE_CPU_V1',
  frozen_epoch=time.time(),groups=3,expected_rejections=9,source_files=rows,
  scope='New installer/reader/payload syntax and first closure gate;original HMAC/account source preservation;new closing JSON bridge schema.',
  model_raw_NPZ_USD_SDK_GPU_SSH_Git_reads_or_calls=0,old218_fixture_replays=0,execution='ONCE_NO_REENTRY')
 with (R/'CPU219_PURPOSE_FROZEN.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
 print(json.dumps(dict(purpose_frozen=True,groups=3,rejections=9,source_rows=len(rows))))
if __name__=='__main__':main()
