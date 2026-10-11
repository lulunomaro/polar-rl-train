from wave_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import os,json,time
out=[]
for p in (Path.home()/'.cache/pip',Path.home()/'anaconda3/pkgs'):
 row=dict(path=str(p),exists=p.is_dir(),bytes=0,files=0,largest=[])
 if p.is_dir():
  files=[]
  for root,dirs,names in os.walk(p,followlinks=False):
   if p.name=='pkgs':dirs[:]=[]
   for name in names:
    f=Path(root)/name
    if f.is_symlink():continue
    s=f.stat();row['bytes']+=s.st_size;row['files']+=1
    if s.st_size>100000000:files.append(dict(path=str(f),bytes=s.st_size,mtime=s.st_mtime))
  row['largest']=sorted(files,key=lambda x:x['bytes'],reverse=True)[:15]
 out.append(row)
install=[]
for proc in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=proc.read_bytes().split(b'\0');names=[Path(x.decode(errors='replace')).name for x in a[:3]]
  if any(x in ('pip','pip3','conda') for x in names):install.append(dict(pid=int(proc.parent.name),executables=names))
 except OSError:pass
print(json.dumps(dict(epoch=time.time(),download_caches=out,actual_installer_processes=install,read_only=True)))
''');save('WAVE_DOWNLOAD_CACHE_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
