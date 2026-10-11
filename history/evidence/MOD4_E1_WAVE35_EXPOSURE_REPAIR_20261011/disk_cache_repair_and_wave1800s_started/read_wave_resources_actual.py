from wave_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,time,shutil
old=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010');mem={x.split(':')[0]:int(x.split()[1])*1024 for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemAvailable:','SwapFree:'))};disk=shutil.disk_usage(old)
print(json.dumps(dict(epoch=time.time(),memory=mem,disk=dict(total=disk.total,used=disk.used,free=disk.free),new_root_exists=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_EXPOSURE_REPAIR_20261011').exists(),no_GPU_or_budget_write=True)))
''');save('WAVE_RESOURCE_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
