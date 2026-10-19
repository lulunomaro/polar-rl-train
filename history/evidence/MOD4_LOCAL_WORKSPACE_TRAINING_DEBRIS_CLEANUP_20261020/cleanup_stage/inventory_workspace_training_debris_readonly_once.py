"""Inventory only the named workspace; never follow reparse points or delete files."""
from pathlib import Path
import collections,json,os,stat,time,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf').resolve();B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True)
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert B.is_relative_to(W);start=time.time();folders=collections.defaultdict(lambda:dict(bytes=0,files=0));ext=collections.defaultdict(lambda:dict(bytes=0,files=0));large=[];errors=[];skipped=[];stack=[W];count=0
 while stack:
  root=stack.pop()
  try:
   with os.scandir(root) as entries:
    for e in entries:
     p=Path(e.path)
     try:
      s=e.stat(follow_symlinks=False)
      if e.is_symlink() or getattr(s,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT:skipped.append(str(p));continue
      if e.is_dir(follow_symlinks=False):stack.append(p);continue
      if not e.is_file(follow_symlinks=False):continue
      rel=p.relative_to(W);top=rel.parts[0];suffix=p.suffix.lower() or '[none]';folders[top]['bytes']+=s.st_size;folders[top]['files']+=1;ext[suffix]['bytes']+=s.st_size;ext[suffix]['files']+=1;count+=1
      if s.st_size>=10*1024**2:large.append(dict(path=str(p),relative=rel.as_posix(),bytes=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,device=s.st_dev,inode=s.st_ino,links=s.st_nlink,attributes=getattr(s,'st_file_attributes',0)))
     except OSError as ex:errors.append(dict(path=str(p),type=type(ex).__name__,error=str(ex)))
  except OSError as ex:errors.append(dict(path=str(root),type=type(ex).__name__,error=str(ex)))
 out=dict(epoch=time.time(),workspace=str(W),read_only=True,no_symlink_or_reparse_traversal=True,elapsed_seconds=time.time()-start,files=count,total_logical_bytes=sum(x['bytes'] for x in folders.values()),top_directories=dict(sorted(folders.items(),key=lambda x:-x[1]['bytes'])),extensions=dict(sorted(ext.items(),key=lambda x:-x[1]['bytes'])),large_files=sorted(large,key=lambda x:-x['bytes']),skipped_reparse_points=skipped,errors=errors)
 put('WORKSPACE_SIZE_AND_LARGE_TRAINING_ARTIFACT_INVENTORY_ACTUAL.json',out);print(json.dumps(dict(files=count,total_logical_GiB=out['total_logical_bytes']/1024**3,top_directories=list(out['top_directories'].items())[:24],extensions=list(out['extensions'].items())[:18],largest_files=out['large_files'][:24],errors=errors[:12],skipped_reparse_count=len(skipped))))
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_INVENTORY_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_delete=True));raise
