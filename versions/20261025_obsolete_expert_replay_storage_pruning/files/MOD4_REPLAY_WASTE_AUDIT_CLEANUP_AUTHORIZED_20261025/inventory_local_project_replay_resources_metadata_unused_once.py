from pathlib import Path
import collections,hashlib,heapq,json,os,stat,time,traceback,shutil
S=Path(__file__).resolve().parent;W=S.parent;R=S/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 assert json.loads((R/'HUMAN_NEW_REPLAY_WASTE_AUDIT_CLEANUP_AUTH_ACTUAL.json').read_bytes())['human_request'].startswith('继续详细排查')
 start=time.time();deadline=time.monotonic()+150;errors=[];skip=[];totals=collections.defaultdict(lambda:collections.Counter());classes=collections.Counter();candidates=[];largest=[];count=0
 selected=[p for p in W.iterdir() if p.is_dir() and (p.name.lower().startswith(('mod4','rm2026','remote_')) or p.name in ['runs','output','tmp','downloads','audits','deliveries']) and p!=S]
 stack=list(selected);out=R/'LOCAL_PROJECT_FILE_METADATA_FULL.jsonl';assert not out.exists();before=shutil.disk_usage(W)
 with out.open('x',encoding='utf8') as f:
  while stack:
   if time.monotonic()>deadline:skip.append(dict(reason='bounded150s_partial',remaining_roots=[str(p) for p in stack]));break
   folder=stack.pop()
   try:entries=list(os.scandir(folder))
   except OSError as e:errors.append(dict(path=str(folder),error=repr(e)));continue
   for e in entries:
    p=Path(e.path)
    try:
     st=e.stat(follow_symlinks=False)
     if e.is_symlink() or getattr(st,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT:skip.append(dict(path=str(p),reason='symlink_or_reparse_not_followed'));continue
     if e.is_dir(follow_symlinks=False):
      if p.name.lower() in ['.git','.venv','venv','node_modules']:skip.append(dict(path=str(p),reason='protected_repository_or_installed_dependency_tree'));continue
      stack.append(p);continue
     if not stat.S_ISREG(st.st_mode):continue
     rel=p.relative_to(W);top=rel.parts[0];ext=p.suffix.lower();parts=[x.lower() for x in rel.parts];kind='report_source_or_other'
     if ext in ['.pt','.pth','.onnx']:kind='model_or_preupdate_metadata_only'
     elif ext in ['.npz','.npy','.mp4','.avi','.mkv','.gif']:kind='array_or_replay_candidate_only'
     elif ext in ['.zip','.gz','.zst','.whl','.conda','.bz2']:kind='archive_or_package_candidate_only'
     if any(x in ['cache','__pycache__','.cache','tmp'] for x in parts):kind='cache_or_temporary_candidate_only'
     row=dict(path=str(p),relative=rel.as_posix(),bytes=st.st_size,mtime_ns=st.st_mtime_ns,ctime_ns=st.st_ctime_ns,device=st.st_dev,inode=st.st_ino,nlink=st.st_nlink,kind=kind)
     f.write(json.dumps(row,ensure_ascii=False)+'\n');count+=1;totals[top]['files']+=1;totals[top]['bytes']+=st.st_size;classes[kind]+=st.st_size
     item=(st.st_size,str(p),row)
     if len(largest)<120:heapq.heappush(largest,item)
     elif item[:2]>largest[0][:2]:heapq.heapreplace(largest,item)
     if kind!='report_source_or_other' and st.st_size>1024**2:candidates.append(row)
    except OSError as e:errors.append(dict(path=str(p),error=repr(e)))
 sha=hashlib.sha256(out.read_bytes()).hexdigest()
 result=dict(epoch=time.time(),started_epoch=start,elapsed_seconds=time.time()-start,metadata_only=True,selected_project_roots=[str(p) for p in selected],files=count,classes_logical_bytes=dict(classes),top_directories=[dict(name=k,**v) for k,v in sorted(totals.items(),key=lambda x:x[1]['bytes'],reverse=True)],large_candidates=sorted(candidates,key=lambda r:r['bytes'],reverse=True),largest_files=[r[2] for r in sorted(largest,reverse=True)],errors=errors,skipped=skip,complete_within_explicit_scope=not any(x.get('reason')=='bounded150s_partial' for x in skip),C_free_before_snapshot=before.free,full_metadata=dict(path=str(out),bytes=out.stat().st_size,SHA=sha),not_deletion_selection_or_content_duplicate_proof=True,no_PT_raw_content_hash_or_load_no_GPU_or_host=True)
 put('LOCAL_PROJECT_REPLAY_RESOURCE_METADATA_INVENTORY_ACTUAL.json',result)
 print(json.dumps(dict(files=count,logical_bytes=sum(v['bytes'] for v in totals.values()),elapsed_seconds=result['elapsed_seconds'],complete=result['complete_within_explicit_scope'],top=result['top_directories'][:18],errors=errors[:8],largest=result['largest_files'][:10])))
except BaseException:
 put('LOCAL_NEW_REPLAY_INVENTORY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_delete=True));raise
