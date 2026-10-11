from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
p=D/'stage_slope_snapshot_actual_receipts_once.py';assert not p.exists()
s=(D/'stage_slope_snapshot_reviewed_once.py').read_text()
s=s.replace('SNAPSHOT_REPAIR_','SNAPSHOT_ACTUAL_RECEIPTS_')
old="p=D/name;r=j(p);assert r['passed'];native[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),passed=True,no_PPO=True)"
new="p=D/name;r=j(D/'reports'/(p.stem+'_PASSED.json'));assert r['passed'] and r['no_PPO'] and r['path']==str(p) and r['sha256']==h(p);native[name]=dict(r,bytes=p.stat().st_size)"
assert old in s;s=s.replace(old,new);compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
(D/'reports/SNAPSHOT_NATIVE_SCHEMA_READER_REVIEW.json').write_text(json.dumps(dict(epoch=time.time(),original_KeyError_preserved=True,raw_native_not_PASSED_schema=True,actual_own_PASSED_path_SHA_required=True,old_stage_no_remote_newroot_or_GPU_write=True,local_inline_PowerShell_parser_rejected_before_any_Python_or_remote_execution=True),indent=2))
