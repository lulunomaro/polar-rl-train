from wave_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,time,shutil,os
out=[]
for line in Path('/proc/mounts').read_text().splitlines():
 source,mount,fs,*_=line.split()
 if fs not in ('ext4','xfs','btrfs','ntfs','fuseblk','zfs','nfs','nfs4','cifs'):continue
 mount=mount.replace('\\040',' ');p=Path(mount)
 if not p.exists():continue
 d=shutil.disk_usage(p);out.append(dict(source=source,mount=mount,filesystem=fs,total=d.total,used=d.used,free=d.free,writable=os.access(p,os.W_OK)))
old=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010');f=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes())['sha256'];bytes_total=sum((old/name).stat().st_size for name in f)
print(json.dumps(dict(epoch=time.time(),mounts=out,actual366_source_total_bytes=bytes_total,no_GPU_or_budget_write=True)))
''');save('WAVE_STORAGE_MOUNTS_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
