from pathlib import Path
import os, json, time, heapq, collections, shutil

OUT=Path(__file__).resolve().parent
REPORT=OUT/'LOCAL_KNOWN_USER_CACHE_METADATA_READ_ONLY_ACTUAL.json'
assert not REPORT.exists(), 'once report exists'
roots=[('pip_http_and_wheel_cache',r'C:/Users/lulu/AppData/Local/pip/Cache'),('uv_download_build_cache',r'C:/Users/lulu/AppData/Local/uv/cache'),('npm_cache',r'C:/Users/lulu/AppData/Local/npm-cache'),('NVIDIA_DX_shader_cache',r'C:/Users/lulu/AppData/Local/NVIDIA/DXCache'),('NVIDIA_GL_shader_cache',r'C:/Users/lulu/AppData/Local/NVIDIA/GLCache'),('Direct3D_shader_cache',r'C:/Users/lulu/AppData/Local/D3DSCache'),('user_temp_metadata_only',r'C:/Users/lulu/AppData/Local/Temp'),('pip_dotcache',r'C:/Users/lulu/.cache/pip'),('conda_download_and_package_cache',r'C:/Users/lulu/miniconda3/pkgs'),('conda_local_package_cache',r'C:/Users/lulu/AppData/Local/conda/conda/pkgs')]
start=time.time(); results=[]; errors=[]; skipped=[]
for label,name in roots:
    root=Path(name);top=collections.defaultdict(lambda:[0,0]);largest=[];total=0;count=0;ext=collections.defaultdict(lambda:[0,0]);old_count=0;old_bytes=0
    if not root.exists():results.append({'kind':label,'path':str(root),'exists':False});continue
    stack=[root]
    while stack:
        if time.time()-start>90:
            skipped.append({'path':str(root),'why':'total 90s metadata scan bound hit; partial'});break
        folder=stack.pop()
        try:
            with os.scandir(folder) as it:entries=list(it)
        except OSError as e:errors.append({'path':str(folder),'error':repr(e)});continue
        for ent in entries:
            p=Path(ent.path)
            try:
                st=ent.stat(follow_symlinks=False)
                if ent.is_symlink() or (getattr(st,'st_file_attributes',0)&0x400):
                    skipped.append({'path':str(p),'why':'reparse/symlink not followed'});continue
                if ent.is_dir(follow_symlinks=False):stack.append(p);continue
                if not ent.is_file(follow_symlinks=False):continue
                b=st.st_size;total+=b;count+=1;parts=p.relative_to(root).parts;key=parts[0] if len(parts)>1 else '[root files]';top[key][0]+=b;top[key][1]+=1
                e=p.suffix.lower() or '[none]';ext[e][0]+=b;ext[e][1]+=1
                age=(start-st.st_mtime)/86400
                if age>7:old_count+=1;old_bytes+=b
                row={'path':str(p),'bytes':b,'mtime_ns':st.st_mtime_ns,'age_days':age}
                item=(b,str(p),row)
                if len(largest)<40:heapq.heappush(largest,item)
                elif b>largest[0][0]:heapq.heapreplace(largest,item)
            except OSError as e:errors.append({'path':str(p),'error':repr(e)})
    results.append({'kind':label,'path':str(root),'exists':True,'logical_bytes':total,'files':count,'age_gt7d_files':old_count,'age_gt7d_bytes':old_bytes,'top_children':[{'name':k,'bytes':v[0],'files':v[1]} for k,v in sorted(top.items(),key=lambda x:x[1][0],reverse=True)],'extensions':[{'ext':k,'bytes':v[0],'files':v[1]} for k,v in sorted(ext.items(),key=lambda x:x[1][0],reverse=True)],'largest_files':[x[2] for x in sorted(largest,reverse=True)]})
out={'scope':'Known local user software/download/shader caches and user Temp metadata only; contents not read; no deletion/Git/host interaction','started_epoch':start,'ended_epoch':time.time(),'C_drive_free_snapshot':shutil.disk_usage('C:/').free,'results':results,'errors':errors,'skipped':skipped,'limitations':['Cache location is not sufficient proof that each item is unused or safe to remove.','Conda package hardlinks may mean logical byte sums exceed actual recoverable allocation; installed environments are never proposed for deletion.','User Temp can include project evidence and live installers; requires exact provenance/process checks before removal.','All reports/errors and this script must be archived by coordinator.']}
REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(REPORT),'seconds':time.time()-start,'results':[{'kind':x['kind'],'path':x['path'],'exists':x['exists'],'bytes':x.get('logical_bytes'),'files':x.get('files'),'age_gt7d_bytes':x.get('age_gt7d_bytes'),'top_children':x.get('top_children',[])[:7]} for x in results],'errors':len(errors),'skipped':len(skipped)},ensure_ascii=False))
