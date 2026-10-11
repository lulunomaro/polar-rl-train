from entry_io import *
n,w=io.connect_both()
try:
 v=run(n,"from pathlib import Path\nimport json,shutil,time\nbase=Path("+repr(BASE)+");new=Path("+repr(ROOT)+")\nprint(json.dumps(dict(epoch=time.time(),new_root_exists=new.exists(),disk=shutil.disk_usage(base)._asdict(),old384_frozen_source_bytes=sum((base/k).stat().st_size for k in json.loads((base/'reports/SOURCE_FREEZE.json').read_bytes())['sha256']),memavailable=next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')),pipcache_present=Path('/home/egde/.cache/pip').exists(),home_disk=shutil.disk_usage('/home/egde')._asdict())))")
 p=save('RESOURCE_GUARD_ACTUAL_REVIEW_'+str(time.time_ns())+'.json',v);print(json.dumps(v))
finally:io.cleanup(n,w)
