from pathlib import Path
import os, json, time, datetime, heapq, collections

ROOT=Path(r'C:/Users/lulu/Desktop/claude/mjcf')
OUT=Path(__file__).resolve().parent
start=time.time()
report=OUT/'LOCAL_WORKSPACE_METADATA_READ_ONLY_ACTUAL.json'
assert not report.exists(), 'once report exists; do not rerun'
errors=[]; skipped=[]; totals=collections.defaultdict(lambda:[0,0]); exts=collections.defaultdict(lambda:[0,0]); largest=[]; caches={}; assets=collections.defaultdict(list)
cache_names={'__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.cache'}
asset_ext={'.usd','.usda','.usdc','.zip','.obj','.stl','.ply','.dae','.fbx','.glb','.gltf'}
count=0; total=0
stack=[(ROOT,())]
while stack:
    folder, ancestors=stack.pop()
    try:
        with os.scandir(folder) as it:
            entries=list(it)
    except OSError as e:
        errors.append({'path':str(folder),'error':repr(e)});continue
    for ent in entries:
        p=Path(ent.path)
        try:
            if ent.is_symlink():
                skipped.append({'path':str(p),'why':'symlink not followed'});continue
            if ent.is_dir(follow_symlinks=False):
                # Repository internals are counted only through their filesystem metadata.
                stack.append((p, ancestors+(p,)))
                continue
            st=ent.stat(follow_symlinks=False)
            if not ent.is_file(follow_symlinks=False):continue
            rel=p.relative_to(ROOT); parts=rel.parts
            b=st.st_size;count+=1;total+=b
            top=parts[0] if len(parts)>1 else '[root files]'
            totals[top][0]+=b;totals[top][1]+=1
            ext=p.suffix.lower() or '[no extension]';exts[ext][0]+=b;exts[ext][1]+=1
            row={'path':str(p),'bytes':b,'mtime_ns':st.st_mtime_ns,'nlink':st.st_nlink,'inode':st.st_ino,'device':st.st_dev}
            key=(b,str(p),row)
            if len(largest)<120:heapq.heappush(largest,key)
            elif b>largest[0][0]:heapq.heapreplace(largest,key)
            for anc in ancestors:
                if anc.name.lower() in cache_names:
                    c=caches.setdefault(str(anc),{'path':str(anc),'bytes':0,'files':0,'newest_mtime_ns':0,'source_py_present':0,'source_py_missing':0,'non_bytecode_files':[]})
                    c['bytes']+=b;c['files']+=1;c['newest_mtime_ns']=max(c['newest_mtime_ns'],st.st_mtime_ns)
                    if p.suffix.lower()=='.pyc':
                        stem=p.name.split('.')[0]; src=p.parent.parent/(stem+'.py')
                        c['source_py_present' if src.is_file() else 'source_py_missing']+=1
                    else:c['non_bytecode_files'].append({'path':str(p),'bytes':b})
            if ext in asset_ext and b>=1024*1024 and '.git' not in parts:
                assets[(p.name.lower(),b)].append(row)
        except OSError as e:errors.append({'path':str(p),'error':repr(e)})
duplicate_candidates=[{'basename':k[0],'bytes_each':k[1],'count':len(v),'logical_duplicate_bytes':k[1]*(len(v)-1),'files':v,'hash_not_read':True,'candidate_not_content_proven':True} for k,v in assets.items() if len(v)>1]
duplicate_candidates.sort(key=lambda x:x['logical_duplicate_bytes'],reverse=True)
out={'scope':'workspace filesystem metadata only; no raw/PT/NPZ/USD/ZIP content read or hash, no deletion, no Git command, no host connection','started_epoch':start,'ended_epoch':time.time(),'workspace':str(ROOT),'files':count,'logical_bytes_including_hardlink_paths':total,'top_directories':[{'name':k,'bytes':v[0],'files':v[1]} for k,v in sorted(totals.items(),key=lambda x:x[1][0],reverse=True)],'extensions':[{'extension':k,'bytes':v[0],'files':v[1]} for k,v in sorted(exts.items(),key=lambda x:x[1][0],reverse=True)],'largest_files':[x[2] for x in sorted(largest,reverse=True)],'cache_directories':sorted(caches.values(),key=lambda x:x['bytes'],reverse=True),'immutable_asset_same_basename_size_candidates':duplicate_candidates,'skipped':skipped,'errors':errors,'limitations':['Logical sizes can exceed physical allocation for hardlinks/compression.','Matching basename and size do not prove duplicate bytes or immutable use. No asset deletion/hardlink authorized by this inventory.','No system-wide, user-session, credential, training-host or process audit performed.','All reports/errors and this source must be Git archived by coordinator.']}
report.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(report),'files':count,'logical_bytes':total,'seconds':time.time()-start,'errors':len(errors),'cache_bytes':sum(c['bytes'] for c in caches.values()),'largest_directories':out['top_directories'][:15],'largest_cache_directories':out['cache_directories'][:8],'asset_duplicate_group_count':len(duplicate_candidates)},ensure_ascii=False))
